"""
VeriForge Toy Example — Pattern 1: Ground Facts
Loads a ground fact program via the clingo Python API,
grounds it, solves it, and prints the resulting stable model.
"""

import clingo


def main() -> None:
    ctl = clingo.Control()
    ctl.load("prototype/toy/01_ground_facts.lp")
    ctl.ground([("base", [])])

    with ctl.solve(yield_=True) as handle:
        for model in handle:
            atoms = sorted(str(atom) for atom in model.symbols(shown=True))
            print("Stable model:")
            for atom in atoms:
                print(f"  {atom}")
        result = handle.get()

    print(f"\nSatisfiable: {result.satisfiable}")


if __name__ == "__main__":
    main()
