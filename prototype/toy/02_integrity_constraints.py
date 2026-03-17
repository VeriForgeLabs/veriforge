"""
VeriForge Toy Example — Pattern 2: Integrity Constraints
Demonstrates SAT (valid state) and UNSAT (constraint violation)
by running the solver twice with different ABox facts.
"""

import clingo


def run(label: str, extra_facts: str) -> None:
    """Run the solver with base program plus extra_facts injected."""
    ctl = clingo.Control()
    ctl.load("prototype/toy/02_integrity_constraints.lp")

    # add() injects additional ASP source at ground time.
    # "base" names the theory; [] means no parameters.
    # This is how VeriForge will inject per-turn ABox state.
    ctl.add("base", [], extra_facts)
    ctl.ground([("base", [])])

    with ctl.solve(yield_=True) as handle:
        for model in handle:
            atoms = sorted(str(atom) for atom in model.symbols(shown=True))
            print(f"{label} — Stable model:")
            for atom in atoms:
                print(f"  {atom}")
        result = handle.get()

    print(f"{label} — Satisfiable: {result.satisfiable}\n")


def main() -> None:
    # Test 1: prisoner in cell — no constraint violation — expect SAT.
    run("VALID STATE", "")

    # Test 2: override prisoner location to corridor — violates constraint — expect UNSAT.
    # In a real VeriForge turn, this override represents a proposed ABox delta.
    run("INVALID STATE", "located_at(prisoner, corridor).")


if __name__ == "__main__":
    main()
