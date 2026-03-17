
# learning-notes.md

## VeriForge Implementation — Personal Learning Reference
Pedagogical companion to the implementation phase.
Captures conceptual explanations, pattern walkthroughs, and "why this works" reasoning produced during Implementation Chats (INN).
Populated via NOTE-READY blocks flagged in INN output and committed by Ankyra.
Covers Phase 0 forward — research phase concepts are archived in research-log.md.

Load order: INN chats load this file last — protocols.md → implementation-log.md → learning-notes.md.

---

## ASP Fundamentals

### Ground Facts

An ASP program is a set of logical statements.
The simplest statements are *ground facts* — assertions that something is unconditionally true.
There is no `if`, no condition, no variable.
Just a predicate name and its arguments, terminated with a period.
```asp
character(guard).
```

This asserts: "guard is a character."
The solver accepts it as unconditionally true.

**Structure of a ground fact:**

| Component | Role |
|---|---|
| Predicate name (`character`) | What kind of thing this is |
| Argument (`guard`) | The specific entity being asserted |
| Period (`.`) | Required terminator for every ASP statement |

**Mapping to WorldDSL categories:**

Ground facts encode three of the four WorldDSL categories directly.

| Category | Function | Example |
|---|---|---|
| 1 — Entity registry | Declares that a named entity exists | `character(guard).` |
| 2 — Static properties | Facts that never change during play | `has_bars(cell).` |
| 3 — Mutable state | Current state, loaded from ABox JSON at session start | `located_at(prisoner, cell).` |

Category 4 (integrity constraints) uses a different encoding — see [Integrity Constraints](#integrity-constraints).

In a live VeriForge session, Category 3 facts are generated from the ABox JSON at runtime.
In Phase 0, they are written directly to understand the structure.

**Design decision — two locations in a "one-location" toy world:**

The toy world specifies one location (the cell).
But the constraint "a prisoner cannot leave the cell" is untestable without a second location to move to.
The toy example therefore includes `cell` and `corridor`.
The prisoner starts in the cell; the guard and merchant can be anywhere; Pattern 2 (integrity constraints) enforces the constraint.
This is the minimum structure that makes the constraint non-trivial and worth encoding.

**Running ground facts — CLI:**
```bash
clingo prototype/toy/01_ground_facts.lp
```

A program of pure ground facts always produces exactly one stable model — the only possible world consistent with the stated facts.
Nothing is derived, nothing is inferred.
Pure ground truth.

**Running ground facts — Python API:**
```python
ctl = clingo.Control()            # Manages the solver lifecycle: load → ground → solve
ctl.load("prototype/toy/01_ground_facts.lp")
ctl.ground([("base", [])])        # "base" is the default theory name; always use at prototype scope
with ctl.solve(yield_=True) as handle:
    for model in handle:
        atoms = sorted(str(atom) for atom in model.symbols(shown=True))
    result = handle.get()
```

Key API objects:

| Object | Role |
|---|---|
| `clingo.Control()` | Main entry point; manages full solver lifecycle |
| `ctl.ground([("base", [])])` | Required before every solve call; "base" is the default theory |
| `model.symbols(shown=True)` | All atoms in the stable model; "shown" means all atoms when no `#show` directives are present |
| `result.satisfiable` | Boolean VeriForge's enforcement loop interrogates — `True` for SAT, `False` on constraint violation (Patterns 2–4) |