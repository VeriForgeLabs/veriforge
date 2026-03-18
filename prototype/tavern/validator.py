# prototype/tavern/validator.py
"""
Phase 2 ASP Validation Layer.

Public interface:
    validate_delta(rules_file, abox_path, proposed_delta) -> ValidationResult

Per IMP-I01-D05: the program is always SAT. Violations are read as atoms
from the yielded model. result.satisfiable is never interrogated.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import clingo


# ─── Return Type ─────────────────────────────────────────────────────────────

@dataclass
class ValidationResult:
    """Typed return value of validate_delta().

    clean:
        True  → no violations; the caller may commit proposed_delta to abox.json.
        False → one or more named violations; the delta must not be committed.
    violations:
        List of named violation atom strings, e.g.
        ['violation(unauthorized_in_cellar(guard))'].
        Empty when clean is True.
    committed_delta:
        The proposed_delta dict, echoed back when clean is True.
        None when clean is False.
        Carrying the delta in the result lets the caller commit it without
        holding a separate reference.
    """
    clean: bool
    violations: list[str] = field(default_factory=list)
    # Optional[dict] means this field can hold a dict or None.
    committed_delta: Optional[dict] = None


# ─── Internal Helpers ────────────────────────────────────────────────────────

def _apply_delta(current_abox: dict, proposed_delta: dict) -> dict:
    """Read the current ABox and apply the delta, returning a normalized flat dict.

    The ABox uses the Phase 1 schema:
        state.located_at  — dict of character → location
        state.alive       — list of living character names

    The delta uses a flat schema:
        character_locations — dict of character → location (fields being changed)
        character_alive     — dict of character → bool (fields being changed)

    This function bridges the two. It reads from the ABox schema and returns
    a flat normalized dict that _serialize_for_validation can work with directly.
    The caller never needs to know the ABox schema exists.

    Returning a flat dict (not a copy of the ABox structure) is deliberate:
    the normalized format is simpler to iterate over and does not require
    _serialize_for_validation to handle either schema variant.
    """
    # ── Extract current state from ABox schema ─────────────────────────────
    # .get("state", {}) means: if "state" key is missing, use an empty dict
    # rather than raising a KeyError. Defensive but not essential at prototype
    # scope where the ABox structure is controlled.
    state = current_abox.get("state", {})

    # Copy the location dict so the original is never mutated.
    locations: dict[str, str] = dict(state.get("located_at", {}))

    # Convert the alive list to a dict: {"innkeeper": True, "guard": True, ...}
    # This normalizes the list representation into the bool-keyed format that
    # the merge logic below and _serialize_for_validation both expect.
    alive: dict[str, bool] = {char: True for char in state.get("alive", [])}

    # ── Apply the delta (flat schema) ──────────────────────────────────────
    for char, loc in proposed_delta.get("character_locations", {}).items():
        locations[char] = loc

    for char, status in proposed_delta.get("character_alive", {}).items():
        alive[char] = status

    return {"character_locations": locations, "character_alive": alive}


def _serialize_for_validation(
    current_abox: dict,
    proposed_delta: dict,
) -> str:
    """Produce the ASP fact string to inject before grounding.

    Generates three kinds of facts:
      was_at(X, L)     — current location, for Type B transition constraints.
      located_at(X, L) — proposed location (post-delta), for Type A checks.
      alive(X)         — proposed alive status (post-delta), for Type A checks.

    Reads was_at directly from the ABox schema (state.located_at).
    Reads proposed state from _apply_delta, which returns a normalized flat dict.
    """
    facts: list[str] = []

    # ── was_at/2: current locations, before this delta ─────────────────────
    # Read directly from the ABox nested structure.
    # The _ prefix filter is not needed here because we are accessing a known
    # sub-key ("located_at") rather than iterating top-level keys.
    state = current_abox.get("state", {})
    for char, loc in state.get("located_at", {}).items():
        facts.append(f"was_at({char}, {loc}).")

    # ── Proposed state: normalized flat dict from _apply_delta ─────────────
    proposed_state = _apply_delta(current_abox, proposed_delta)

    # ── located_at/2: proposed locations, after delta ──────────────────────
    for char, loc in proposed_state["character_locations"].items():
        facts.append(f"located_at({char}, {loc}).")

    # ── alive/1: proposed alive status, after delta ────────────────────────
    # Only living characters receive an alive/1 fact.
    # False entries produce nothing — closed-world assumption handles them.
    for char, alive in proposed_state["character_alive"].items():
        if alive:
            facts.append(f"alive({char}).")

    return "\n".join(facts)


# ─── Public Interface ─────────────────────────────────────────────────────────

def validate_delta(
    rules_file: str | Path,
    abox_path: str | Path,
    proposed_delta: dict,
) -> ValidationResult:
    """Validate a proposed ABox delta against the current world state and rules.

    Loads the rules file and current ABox, assembles the ASP fact string
    for the proposed state, runs the solver, and returns a ValidationResult.

    Args:
        rules_file:
            Path to the .lp file encoding Categories 1, 2, and 4.
            Typically 'prototype/tavern/tavern_rules.lp'.
        abox_path:
            Path to the committed abox.json encoding current Category 3 state.
        proposed_delta:
            Dict describing the proposed change. Only the fields being
            changed need to be present. Example:
                {"character_locations": {"guard": "cellar"}}
            Unchanged fields are inherited from the current ABox.

    Returns:
        ValidationResult with clean=True and committed_delta if no violations,
        or clean=False with a list of named violation identifier strings.
    """
    rules_file = Path(rules_file)
    abox_path = Path(abox_path)

    # ── Load the committed ABox ────────────────────────────────────────────
    with abox_path.open() as f:
        current_abox = json.load(f)

    # ── Assemble the ASP facts for this validation call ───────────────────
    asp_facts = _serialize_for_validation(current_abox, proposed_delta)

    # ── Run the solver ─────────────────────────────────────────────────────
    # ctl.Control() manages the full solver lifecycle: load → ground → solve.
    ctl = clingo.Control()

    # Load the TBox rules file (Categories 1, 2, 4).
    ctl.load(str(rules_file))

    # Inject the ABox facts (was_at, located_at, alive) into the base theory.
    # "base" must match the theory name used in ctl.ground() below.
    # [] is the parameter list — empty at prototype scope.
    ctl.add("base", [], asp_facts)

    # Ground before solving. Always required. "base" is the default theory.
    ctl.ground([("base", [])])

    # ── Collect violation atoms from the model ────────────────────────────
    # Per IMP-I01-D05: the program is always SAT because violation predicates
    # are derivation-only (no paired :- violation(X) constraint).
    # The for-model loop always executes exactly once.
    violations: list[str] = []
    with ctl.solve(yield_=True) as handle:
        for model in handle:
            violations = [
                str(atom)
                for atom in model.symbols(shown=True)
                if str(atom).startswith("violation(")
            ]
        # result.satisfiable is intentionally not read here — see IMP-I01-D05.

    # ── Return result ─────────────────────────────────────────────────────
    if violations:
        return ValidationResult(clean=False, violations=violations)

    return ValidationResult(
        clean=True,
        violations=[],
        committed_delta=proposed_delta,
    )