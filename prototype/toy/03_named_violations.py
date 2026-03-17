"""
VeriForge Toy Example — Pattern 3: Named-Violation Predicates
ABox state is always injected via ctl.add(), never hardcoded.
The enforcement loop checks for violation atoms in the SAT model.
"""

import clingo


def run(label: str, abox_facts: str) -> None:
    ctl = clingo.Control()
    ctl.load("prototype/toy/03_named_violations.lp")

    # Inject all mutable ABox state at runtime.
    # In VeriForge, this call will receive the current ABox JSON
    # serialised as ASP ground facts.
    ctl.add("base", [], abox_facts)
    ctl.ground([("base", [])])

    violations = []

    with ctl.solve(yield_=True) as handle:
        for model in handle:
            violations = [
                str(atom) for atom in model.symbols(shown=True)
                if str(atom).startswith("violation(")
            ]
        result = handle.get()

    if violations:
        print(f"{label} — Constraint violation detected")
        for v in violations:
            print(f"  {v}")
    else:
        print(f"{label} — SAT, no violations")
    print()


def main() -> None:
    # Test 1: prisoner in cell — no violation expected.
    run(
        "VALID STATE",
        "located_at(guard, corridor). located_at(prisoner, cell). located_at(merchant, corridor)."
    )

    # Test 2: prisoner in corridor — violation expected.
    run(
        "INVALID STATE",
        "located_at(guard, corridor). located_at(prisoner, corridor). located_at(merchant, corridor)."
    )


if __name__ == "__main__":
    main()
