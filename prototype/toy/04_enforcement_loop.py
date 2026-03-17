"""
VeriForge Toy Example — Pattern 4: Enforcement Loop

This module contains the function VeriForge's session layer will call
on every turn: validate_delta().

Given the current ABox state and a proposed delta, it returns either
a clean commit signal or the list of named violations that blocked it.

This is the complete per-turn symbolic validation cycle.
"""

import clingo
from typing import NamedTuple


class ValidationResult(NamedTuple):
    """The return value of validate_delta().

    clean: True if no violations were detected; False otherwise.
    violations: List of named violation identifiers, empty if clean.
    """
    clean: bool
    violations: list[str]


def validate_delta(
    rules_file: str,
    current_abox: str,
    proposed_delta: str,
) -> ValidationResult:
    """Validate a proposed ABox delta against the current world state.

    Loads the rules file, injects current ABox state plus the proposed
    delta, runs the solver, and returns a ValidationResult.

    Args:
        rules_file: Path to the .lp file containing rules and static structure.
        current_abox: ASP ground facts representing the current ABox state.
        proposed_delta: ASP ground facts representing the proposed state change.

    Returns:
        ValidationResult(clean=True, violations=[]) if no violations detected.
        ValidationResult(clean=False, violations=[...]) if violations detected.
    """
    ctl = clingo.Control()
    ctl.load(rules_file)

    # Inject current ABox state — where things are right now.
    ctl.add("base", [], current_abox)

    # Inject the proposed delta on top of current state.
    # If the delta contradicts a constraint, the violation atom will appear.
    ctl.add("base", [], proposed_delta)

    ctl.ground([("base", [])])

    violations = []

    with ctl.solve(yield_=True) as handle:
        for model in handle:
            violations = [
                str(atom) for atom in model.symbols(shown=True)
                if str(atom).startswith("violation(")
            ]

    return ValidationResult(clean=len(violations) == 0, violations=violations)


def main() -> None:
    rules = "prototype/toy/04_enforcement_loop.lp"

    # Current ABox: prisoner is in the cell, others in the corridor.
    current_abox = (
        "located_at(guard, corridor). "
        "located_at(prisoner, cell). "
        "located_at(merchant, corridor)."
    )

    print("=== VeriForge Enforcement Loop — Pattern 4 ===\n")

    # Turn 1: merchant moves to cell — no imprisoned character moves — expect clean.
    delta_1 = "located_at(merchant, cell)."
    result_1 = validate_delta(rules, current_abox, delta_1)
    print(f"Turn 1 — proposed delta: {delta_1}")
    print(f"  Result: {'COMMIT' if result_1.clean else 'BLOCK'}")
    if not result_1.clean:
        print(f"  Violations: {result_1.violations}")
    print()

    # Turn 2: prisoner moves to corridor — violates imprisonment constraint — expect block.
    delta_2 = "located_at(prisoner, corridor)."
    result_2 = validate_delta(rules, current_abox, delta_2)
    print(f"Turn 2 — proposed delta: {delta_2}")
    print(f"  Result: {'COMMIT' if result_2.clean else 'BLOCK'}")
    if not result_2.clean:
        print(f"  Violations: {result_2.violations}")
    print()

    # Turn 3: guard moves to corridor (already there) — no change, no violation — expect clean.
    delta_3 = "located_at(guard, corridor)."
    result_3 = validate_delta(rules, current_abox, delta_3)
    print(f"Turn 3 — proposed delta: {delta_3}")
    print(f"  Result: {'COMMIT' if result_3.clean else 'BLOCK'}")
    if not result_3.clean:
        print(f"  Violations: {result_3.violations}")
    print()


if __name__ == "__main__":
    main()
