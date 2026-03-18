
# learning-notes.md

## VeriForge Implementation — Personal Learning Reference
Pedagogical companion to the implementation phase.
Captures conceptual explanations, pattern walkthroughs, and "why this works" reasoning produced during Implementation Chats (INN).
Populated directly by the developer from NOTE-READY blocks flagged in INN output.
No Ankyra oversight required for learning-notes.md entries.
Covers Phase 0 forward — research phase concepts are archived in research-log.md.

Load order: INN chats load this file last — protocols.md → implementation-log.md → learning-notes.md.

---

## ASP Fundamentals

### Ground Facts

An Answer Set Programming (ASP) program is a set of logical statements.
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

### Integrity Constraints

An **integrity constraint** is an ASP rule with an empty head — nothing on the left side of the `:-` operator:

```asp
asp:- body.
```
Read it as: **"it must not be the case that body is true."**

If the body conditions are all satisfied by the current facts, the solver rejects the entire program as UNSATISFIABLE (UNSAT). 
There is no stable model — no valid world state exists under these facts and rules combined.
This is the mechanism VeriForge uses to enforce hard rules. 
The constraint doesn't derive any new facts. 
It eliminates any world state where the prohibited condition holds.

**Mapping to WorldDSL Category 4:**

Category 4 (integrity constraints) encodes two types of hard rules, both using identical ASP syntax:

|Type | Description | Example| 
|---|---|---|
| Type A — State consistency | A condition that must never be true regardless of how the state was reached | `a dead entity cannot act` |
|Type B — Transition validity | A move or state change that is structurally prohibited | `an entity can only move to an adjacent location` |

Both encode as `:- body.` — the distinction is semantic, not syntactic.

**The toy constraint:**
```asp
aspimprisoned(prisoner).

:- character(X), imprisoned(X), located_at(X, L), L != cell.
```

Read: **"it must not be the case that an imprisoned character is located somewhere other than the cell."**

Two things to notice. First, `imprisoned(prisoner).` is a **static property** (Category 2) — it never changes. 
Second, the constraint uses a **variable** `X` rather than the constant `prisoner` directly. 
This generalises the rule: any character marked imprisoned is covered, not just this one. Variables in ASP are uppercase; constants are lowercase.

**SAT vs. UNSAT — the core of the enforcement loop:**

The solver is run twice in `02_integrity_constraints.py` using different ABox states:

```python
# Test 1: prisoner in cell — no violation — expect SAT.
run("VALID STATE", "")

# Test 2: prisoner in corridor — violates constraint — expect UNSAT.
run("INVALID STATE", "located_at(prisoner, corridor).")
```

The second call uses `ctl.add("base", [], extra_facts)` to **inject additional ASP facts at ground time**.
This is the exact mechanism VeriForge will use to inject proposed ABox deltas for validation — the delta arrives as a string of ASP facts, the solver checks whether they violate any integrity constraint, and the result is SAT (commit) or UNSAT (surface conflict).

**Expected output:**
```bash
VALID STATE — Stable model:
  character(guard)
  character(merchant)
  character(prisoner)
  has_bars(cell)
  imprisoned(prisoner)
  located_at(guard,corridor)
  located_at(merchant,corridor)
  located_at(prisoner,cell)
  location(cell)
  location(corridor)
VALID STATE — Satisfiable: True

INVALID STATE — Satisfiable: False
```

Note what is absent in the INVALID STATE case: no stable model is printed, because none exists.
The solver found a contradiction and stopped.
`result.satisfiable` is `False`.
This boolean is what VeriForge's enforcement loop interrogates after every proposed ABox delta.

What `ctl.add()` does:

| Argument| Value | Role| 
|---|---|---|
| First | `"base"` | Names the theory to add facts into — must match `ctl.ground([("base", [])])` | 
| Second | `[]` | Parameter list — empty at prototype scope|
| Third | `extra_facts` | A string of valid ASP source injected before grounding |

This is the first appearance of `ctl.add()`.
In Pattern 1, the entire program came from a `.lp` file.
`ctl.add()` lets you inject additional ASP source programmatically — without modifying the file. At runtime, VeriForge will call `ctl.add()` to inject the current ABox state before each solve call.

### Named-Violation Auxiliary Predicates — Initial Approach (superseded — see corrected section below)

**The problem with pure UNSAT:**
Pattern 2 correctly rejects invalid states with `Satisfiable: False`.
But `False` tells you nothing about *which* constraint fired or *which* entity caused it.
VeriForge's session loop needs a human-readable identifier to surface to the operator.

**The solution — two rules working together:**

The first rule *derives* a named atom when a violation condition holds:

```asp
violation(prisoner_not_in_cell) :-
    imprisoned(X),
    located_at(X, L),
    L != cell.
```

Read: "derive the atom `violation(prisoner_not_in_cell)` if any imprisoned character is located outside the cell."

The second rule *enforces* the constraint by rejecting any model containing a violation:

```asp
:- violation(prisoner_not_in_cell).
```

Read: "it must not be the case that `violation(prisoner_not_in_cell)` is true."

**Why keep both rules?**
The derivation rule alone produces the named atom but doesn't reject the world — the solver would accept an invalid state as long as it can name the violation.
The constraint rule alone produces UNSAT but no identifier.
Together: the derivation fires first (naming the iolation), then the constraint fires (rejecting the world).
The violation atom appears in the solver's conflict analysis and can be extracted before UNSAT is finalised.

**Reading violation atoms from the Python API:**
Instead of checking `result.satisfiable`, the enforcement loop inspects the model for `violation(...)` atoms.
This requires a different solve pattern:

```python
violations = []

with ctl.solve(yield_=True) as handle:
    for model in handle:
        # Check for violation atoms before the constraint fires
        violations = [
            str(atom) for atom in model.symbols(shown=True)
            if str(atom).startswith("violation(")
        ]
    result = handle.get()

if violations:
    print(f"Constraint violation detected: {violations}")
else:
    print("SAT — no violations")
```

**Mapping to VeriForge:**
Each integrity constraint in the WorldDSL will have a paired violation predicate.
When the ASP validation layer runs after a proposed ABox delta, it reports not just SAT/UNSAT but the specific named violation — e.g., `violation(prisoner_not_in_cell)` —
which the session loop surfaces to the human operator.

**Key structural point:**
The violation predicate name is the human-readable error message.
Name it descriptively: `violation(prisoner_not_in_cell)`, not `violation(c1)`.
The operator reading "prisoner_not_in_cell" knows immediately what happened.

### Named-Violation Auxiliary Predicates (corrected)

**Why pure UNSAT is insufficient:**
Pattern 2 correctly rejects invalid states — `result.satisfiable` is `False`.
But when a program is UNSAT, the solver yields zero models. 
No atoms can be read.
`False` tells you a violation occurred; it cannot tell you which one.

**The correct architecture for named violations:**

Derive a named atom when the violation condition holds, with NO paired constraint:

```asp
violation(prisoner_not_in_cell) :-
    imprisoned(X),
    located_at(X, L),
    L != cell.
```

The program is now always SAT — the solver always yields a model.
The enforcement loop reads that model and checks for `violation(...)` atoms.

| Model contains `violation(...)` atoms? | Enforcement decision |
|---|---|
| No | SAT — clean state, commit the ABox delta |
| Yes | Violation — surface the named identifier to the operator |

**Why this is correct for VeriForge:**
VeriForge does not need UNSAT. It needs to know *which* rule was violated.
Named atoms in a SAT model provide that information directly.
The enforcement loop's signal changes from `result.satisfiable` to `if violations`.

**Critical fix — ABox state must never be hardcoded in the .lp file:**
ASP accumulates facts — it does not override them.
If `located_at(prisoner, corridor)` is in the `.lp` file and you inject `located_at(prisoner, cell)` via `ctl.add()`, both atoms are simultaneously true.
The prisoner is in two places at once — every location-based constraint fires.

The `.lp` file encodes rules and static structure only.
All mutable state (Category 3) is injected via `ctl.add()` at runtime.
This is exactly how VeriForge will work: the ABox JSON is loaded and injected as ground facts at the start of each enforcement call, never hardcoded.

**Reading violation atoms from the Python API:**

```python
violations = []

with ctl.solve(yield_=True) as handle:
    for model in handle:
        # The program is always SAT now — this loop always executes once.
        violations = [
            str(atom) for atom in model.symbols(shown=True)
            if str(atom).startswith("violation(")
        ]
    result = handle.get()

if violations:
    print(f"Constraint violation: {violations}")
else:
    print("SAT — no violations")
```

### Python Enforcement Loop

Pattern 4 composes the three prior patterns into a single callable function — `validate_delta()` — that represents the complete per-turn symbolic validation cycle.

**Function signature:**

```python
def validate_delta(
    rules_file: str,
    current_abox: str,
    proposed_delta: str,
) -> ValidationResult:
```

**What it does:**
Loads the rules file, injects current ABox state, injects the proposed delta on top, runs the solver, and returns a `ValidationResult` — a named tuple carrying a `clean` boolean and a `violations` list.

**The enforcement signal:**
`clean=True` and an empty `violations` list means commit.
`clean=False` with one or more named violation identifiers means block and surface the identifiers to the operator.
`result.satisfiable` is never interrogated — the signal is `len(violations) == 0`.

**Why current_abox and proposed_delta are separate arguments:**
Both are injected via `ctl.add()` before grounding.
Keeping them as separate strings preserves the distinction between "what the world looks like now" and "what the LLM wants to change."
In Phase 2, the current ABox will be serialised from JSON; the proposed delta will be extracted from the LLM's structured output. The separation is architectural, not cosmetic.

**The boundary this function represents:**
Everything inside `validate_delta()` is symbolic — deterministic, inspectable, and independent of any LLM all.
Everything outside it is session management.
This boundary is the core of VeriForge's architectural separation between the symbolic enforcement layer and the generative layer.

### The Two-File Architecture (Phase 1)

The Phase 1 tavern world artifact splits across two files with distinct roles.

| File | WorldDSL Categories | Changes during play? |
|---|---|---|
| `tavern_rules.lp` | 1 (entity registry), 2 (static props), 4 (constraints) | Never |
| `abox.json` | 3 (mutable state) only | Yes — updated by committed ABox deltas |

`tavern_rules.lp` is the TBox: schema, static facts, and constraint rules.
`abox.json` is the ABox: the current instance of the world state.

**Category 3 is never hardcoded in the rules file.** 
(IMP-I01-F02 — doing so causes silent dual-assertion failures when the Python module also injects the same facts via `ctl.add()`.)

For CLI testing in Phase 1, hand-crafted test `.lp` files stand in for the Python module.
The solver loads the rules file and a test state file together:

```bash
clingo prototype/tavern/tavern_rules.lp prototype/tavern/tests/t02_unauthorized_cellar.lp
```

In Phase 2+, the Python module reads `abox.json`, converts it to ASP ground facts, and injects them via `ctl.add()` — replacing the test `.lp` files.

**The JSON is an interface contract, not just documentation.** 
The `_asp_mapping` fields in `abox.json` document exactly how each JSON key maps to an ASP predicate.
Phase 2's parser implements that mapping.

**Parameterized violation predicates:** 
Phase 0 used flat constants (`violation(prisoner_not_in_cell)`).
Phase 1 extends this to compound arguments (`violation(unauthorized_in_cellar(guard))`).
The compound term names the offending entity.
The enforcement loop filters the same way — `str(atom).startswith("violation(")` — and the argument is visible in the string for the Phase 2 module to parse.

**Type A vs. Type B constraints:**
All three Phase 1 constraints are Type A (state consistency — a prohibited condition in the current snapshot).
Type B constraints (transition validity — a prohibited *move*) require knowing both old and new locations, which the Phase 2 delta-injection mechanism will supply.
Type B constraints are introduced in Phase 2.

### The Closed-World Assumption in Practice

The closed-world assumption is the rule that anything not explicitly asserted in the stable model is treated as false.
It is the default in ASP and is what makes ASP suitable for closed-world constraint enforcement.

The practical consequence: **omission is semantically equivalent to negation.**

In the tavern world, Constraint 2 catches a dead character with a location:

```asp
    violation(dead_character_located(X)) :-
        character(X),
        located_at(X, _),
        not alive(X).
```

`not alive(X)` is **negation-as-failure**: it succeeds when `alive(X)` is absent
from the stable model.
There is no `dead(X)` predicate — the absence of `alive(X)` is the complete statement.

CLI test t03 confirms this: the test file contains no `alive(patron)` fact.
The stable model also contains no `alive(patron)` atom.
The solver treats the patron as dead on that basis alone, and the violation fires correctly.

**Design implication for ABox management:** 
When an ABox delta represents a character death, the delta must remove `alive(X)` from the ABox JSON.
It does not need to assert anything affirmative.
The solver's closed-world assumption does the rest.

**Contrast with open-world formalisms (OWL/RDF):**
Under the open-world assumption, the absence of `alive(patron)` would mean only that the system
does not know whether the patron is alive — not that the patron is dead.
OWL reasoners cannot enforce "the patron is dead" from an absent fact alone.
This is why OWL was disqualified as the WorldDSL formalism (OQ-01 [RESOLVED]).
