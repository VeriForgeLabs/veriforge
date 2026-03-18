#!/usr/bin/env python3
"""
VeriForge Phase 3 — Scripted Demo
prototype/demo_turn.py

Demonstrates one complete session loop turn under Condition C (full VeriForge).

Scripted scenario
-----------------
All three characters start at main_hall (confirmed from abox.json).
The guard attempts to enter the cellar, which he is not authorised to access.
main_hall is directly adjacent to cellar, so no intermediate move is required —
the violation fires on the first proposed delta.

Expected outcome
----------------
  1. LLM receives per-turn injected world state (Condition C).
  2. LLM narrates the guard moving toward or into the cellar.
  3. LLM proposes delta: {"character_locations": {"guard": "cellar"}}
  4. validate_delta() detects: violation(unauthorized_in_cellar(guard))
  5. Delta is NOT committed. abox.json is identical before and after the turn.

This satisfies the Phase 3 resolution criterion:
  "the loop runs without errors, the LLM receives injected context, and
   a constraint-violating proposed delta is caught before committing."

Usage
-----
From the veriforge project root, with .venv activated:
  python prototype/demo_turn.py

Requirements
------------
  ANTHROPIC_API_KEY environment variable must be set.
  anthropic package must be installed: pip install anthropic
"""

import json
import sys
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────────
# demo_turn.py lives at prototype/demo_turn.py.
# session_loop.py lives at prototype/session_loop.py.
# Inserting the prototype/ directory into sys.path makes the import resolvable
# whether this script is run from the project root or from prototype/ directly.
PROTOTYPE_DIR = Path(__file__).parent
sys.path.insert(0, str(PROTOTYPE_DIR))

from session_loop import build_context_string, run_turn

# ── File paths ────────────────────────────────────────────────────────────────
# These are relative to PROTOTYPE_DIR (prototype/).
# Both paths are passed as strings; the modules that use them call open() internally.
ABOX_PATH  = str(PROTOTYPE_DIR / "tavern" / "abox.json")
RULES_FILE = str(PROTOTYPE_DIR / "tavern" / "tavern_rules.lp")

# ── Scripted prompt ────────────────────────────────────────────────────────────
# The guard starts at main_hall. main_hall is adjacent to cellar.
# This prompt is designed to produce a delta of:
#   {"character_locations": {"guard": "cellar"}}
# which constraint A1 (unauthorized_in_cellar) will block.
DEMO_PROMPT = (
    "The guard has been eyeing the cellar door all evening, convinced the innkeeper "
    "is hiding something valuable down there. He makes his decision, crosses the "
    "common room, and heads down the cellar stairs."
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def separator(title: str = "", width: int = 60) -> None:
    """Prints a horizontal rule, with an optional centred title."""
    if title:
        padding = width - len(title) - 6
        print(f"\n{'─' * 4}  {title}  {'─' * max(padding, 2)}")
    else:
        print("─" * width)


def print_abox_state(label: str) -> None:
    """Prints a compact snapshot of the current abox.json to the console."""
    with open(ABOX_PATH) as f:
        abox = json.load(f)
    state = abox.get("state", {})
    separator(label)
    print("  Locations:", dict(sorted(state.get("located_at", {}).items())))
    print("  Alive:    ", sorted(state.get("alive", [])))


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    separator("VeriForge Phase 3 — Demo Turn")
    print(f"\n  Condition : C  (per-turn injection + reactive ASP validation)")
    print(f"  ABox      : {ABOX_PATH}")
    print(f"  Rules     : {RULES_FILE}")
    print(f"\n  Prompt:\n    {DEMO_PROMPT}")

    # ── Pre-turn state ────────────────────────────────────────────────────────
    print_abox_state("ABox BEFORE turn")

    # ── Run the turn ──────────────────────────────────────────────────────────
    separator("Running turn  (calling LLM...)")
    result = run_turn(
        abox_path=ABOX_PATH,
        rules_file=RULES_FILE,
        user_prompt=DEMO_PROMPT,
        condition="C",
        # session_context is omitted — Condition C ignores it.
    )

    # ── Results ───────────────────────────────────────────────────────────────
    separator("Context injected (Condition C)")
    print(result.context_injected)

    separator("LLM narrative")
    print(result.narrative)

    separator("Proposed delta")
    print(json.dumps(result.proposed_delta, indent=2))

    separator("Validation result")
    if result.clean:
        print("  ✓  CLEAN — delta committed to abox.json")
    else:
        print("  ✗  VIOLATION DETECTED — delta NOT committed")
        for v in result.violations:
            print(f"     {v}")

    # ── Post-turn state ───────────────────────────────────────────────────────
    # If validation worked correctly, this must be identical to the pre-turn state.
    print_abox_state("ABox AFTER turn")

    # ── Phase 3 exit criterion check ─────────────────────────────────────────
    separator("Phase 3 exit criterion")
    loop_ran             = True                              # reached this line without exception
    context_was_injected = bool(result.context_injected)
    violation_was_caught = (not result.clean) and (not result.committed)

    print(f"  Loop ran without errors              : {'PASS' if loop_ran else 'FAIL'}")
    print(f"  LLM received injected context        : {'PASS' if context_was_injected else 'FAIL'}")
    print(f"  Constraint-violating delta caught    : {'PASS' if violation_was_caught else 'FAIL'}")

    if loop_ran and context_was_injected and violation_was_caught:
        print("\n  ✓  Phase 3 resolution criterion MET.")
    else:
        print("\n  ✗  Phase 3 resolution criterion NOT met — see diagnostics above.")
        if not violation_was_caught:
            print("\n  Diagnostic hint:")
            print("  If delta is {} — the LLM did not emit a valid <delta> tag.")
            print("  Print result.raw_response to inspect the full LLM output.")
            print("  The prompt may need to be made more directive.")
        if not context_was_injected:
            print("\n  Diagnostic hint:")
            print("  context_injected is empty — build_context_string() may have failed.")
            print("  Verify ABOX_PATH points to a valid abox.json.")

    separator()


if __name__ == "__main__":
    main()
