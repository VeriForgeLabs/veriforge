

## VeriForge Implementation — Governing Document
Append-only record of implementation decisions, failures, and open threads, governed by the implementation phase map below.

---

## IMPLEMENTATION PHASE MAP

Tracks the five implementation phases from Phase 0 through the OQ-09 evaluation harness.
Status tokens: [NOT STARTED] | [BLOCKED] | [IN PROGRESS — INN] | [RESOLVED — INN]
The resolution criterion for each phase is pre-registered and cannot be changed once a phase is [IN PROGRESS].

---

### PHASE-0 — Clingo Fundamentals

DEPENDS ON: nothing
BLOCKS: Phase 1
Status: [IN PROGRESS — I01]

Resolution criterion:
Given the toy example (guard, prisoner, merchant, one cell, one hard constraint), all four ASP patterns execute correctly and produce expected output via the Python API.
Pattern 1: ground facts load and all entities are queryable as atoms.
Pattern 2: an integrity constraint fires correctly — the expected violation produces UNSAT.
Pattern 3: a named-violation auxiliary predicate produces a human-readable violation identifier in the output, not just UNSAT.
Pattern 4: the Python API loop — load program, call solve, read SAT/UNSAT and any violation atoms — runs without errors.
Done means: Will can write all four patterns from scratch, run them, read the output, and explain what each line does.
Execution without understanding does not meet this criterion.

---

### PHASE-1 — Tavern WorldDSL Artifact

DEPENDS ON: Phase 0 [IN PROGRESS — I01]
BLOCKS: Phase 2
Status: [BLOCKED]

Resolution criterion:
A committed JSON + ASP artifact representing the tavern world — 3–4 named entities, static properties and initial mutable state in JSON, and 2–3 hard constraints as ASP integrity constraints with named-violation predicates.
The artifact must be inspectable and human-readable without tooling.
No Python session loop yet — this is a design and encoding exercise.
Done means: loading the .lp file in the Clingo CLI produces expected SAT/UNSAT behavior on hand-crafted test inputs.

---

### PHASE-2 — ASP Validation Layer

DEPENDS ON: Phase 1 [BLOCKED]
BLOCKS: Phase 3
Status: [BLOCKED]

Resolution criterion:
A Python module that accepts a proposed ABox delta as structured JSON, loads the current ABox and ASP rules, runs the solver, and returns SAT with the committed delta or UNSAT with the named violation identifier.
Tested against at least one Type A violation and one Type B violation from the tavern artifact.
Done means: the module is callable, returns correct results on known-good and known-bad inputs, and has passing pytest tests for both cases.

---

### PHASE-3 — Session Loop

DEPENDS ON: Phase 2 [BLOCKED]
BLOCKS: Phase 4
Status: [BLOCKED]

Resolution criterion:
A working end-to-end turn: derive current ASP state from ABox → inject as context → call LLM API → extract proposed delta from response → validate via Phase 2 module → commit or surface conflict.
Demonstrated on a single scripted prompt that exercises at least one constraint.
Conditions A and B of the OQ-09 ablation are implemented as configuration flags on this loop, not as separate builds.
Done means: the loop runs without errors, the LLM receives injected context, and a constraint-violating proposed delta is caught before committing.

---

### PHASE-4 — Evaluation Harness

DEPENDS ON: Phase 3 [BLOCKED]
DEPENDS ON: OQ-09-T1 disposition [OPEN] — Condition D inclusion must be decided before test cases are pre-registered.
BLOCKS: OQ-09 empirical test
Status: [BLOCKED]

Resolution criterion:
12 pre-registered test cases committed to the repo before any condition is run — 4 Type A, 4 Type B, 4 compound — each as a scripted prompt sequence.
CVR and VDR measurement infrastructure in place.
All three conditions (A, B, C) runnable via the Phase 3 loop with configuration flags.
Done means: the harness can run a full condition and produce a CVR figure without manual tallying.

---

## IMPLEMENTATION LOG

_Entries are appended here as implementation work proceeds. Each chat appends one section block._

### I01 — Phase 0: Clingo Fundamentals | March 2026 | [IN PROGRESS]

[DECISION] IMP-I01-D01 — Development environment
Chosen: WSL Ubuntu filesystem, bash shell, VS Code with Remote-WSL extension pointing at WSL.
Alternative not taken: Windows filesystem with PowerShell.
Reason: pyenv is a Unix tool with no reliable Windows equivalent; the clingo Python bindings compile against a Linux Python interpreter; all tooling in this stack is native Linux; developing in WSL eliminates cross-filesystem path translation issues entirely.

[DECISION] IMP-I01-D02 — Python version
Chosen: 3.12.9.
Alternative not taken: 3.13.x (current latest).
Reason: clingo PyPI wheels are published and tested against 3.12; 3.13 support exists but is newer and less battle-tested for the clingo bindings specifically; pinning to 3.12 reduces wheel compatibility risk.

[DECISION] IMP-I01-D03 — venv location
Chosen: .venv in repo root.
Alternative not taken: named venv outside the repo (e.g., ~/.venvs/veriforge).
Reason: VS Code Remote-WSL extension finds and activates a .venv in the repo root automatically; keeps the project self-contained so clone-and-setup produces the same structure for any contributor.

[DECISION] IMP-I01-D04 — CLI clingo installation
Chosen: system gringo package via sudo apt install gringo for CLI access alongside pip-installed Python bindings.
Alternative not taken: Python API only, relying solely on pip-installed clingo bindings.
Reason: CLI is useful for rapid .lp iteration without writing a Python wrapper each time; the system apt binary (5.6.2) and the venv Python bindings (5.8.0) are independent with no conflict; version difference is immaterial for CLI testing use.

[FAIL] IMP-I01-F01 — Incorrect build-backend string in pyproject.toml
Error: build-backend = "setuptools.backends.legacy:build" does not exist in any version of setuptools.
Cause: config string generated from training knowledge without primary source verification.
Resolution: pyproject.toml overwritten with correct value "setuptools.build_meta"; install succeeded.
Methodology patch recommended: yes — implementation conduct rules updated to require primary source verification for any configuration string, API method name, or package-specific syntax included in a command the user will execute verbatim; patch applied to protocols.md by human operator.

[THREAD] IMP-I01-T01 — Learning Notes format for pedagogical capture
Description: INN chats produce conceptual explanations and pattern walkthroughs that are not captured by [DECISION] or [FAIL] entries and are lost when the chat context closes; a dedicated format and file home is needed to capture this content for the developer's ongoing reference.
Routes to: implementation phase — format and file home must be designed before I02 opens.
Disposition trigger: Phase 1 start; if learning notes have proven unnecessary by then the thread closes without action; if useful, the format question resolves at that point with actual evidence of what is needed.
Resolution: knowledge/learning-notes.md created and NOTE-READY workflow defined in Ankyra-02; format is topic-organized markdown populated directly by the developer from INN NOTE-READY blocks without Ankyra oversight.

[DECISION] IMP-I01-D05 — Named-violation detection mechanism
Chosen: derivation-only violation predicates with SAT model inspection.
Alternative not taken: paired derivation + integrity constraint (:- violation(X)) producing UNSAT.
Reason: when a program is UNSAT the clingo Python API yields zero models — the for model in handle loop never executes and no atoms are readable. Derivation-only predicates keep the program always SAT; the enforcement loop reads violation(...) atoms from the yielded model directly. This produces a human-readable violation identifier rather than a bare boolean.

[FAIL] IMP-I01-F02 — Hardcoded mutable state in Pattern 3 .lp file
Error: located_at facts hardcoded in 03_named_violations.lp while also injected via ctl.add() — both became simultaneously true; constraints fired on both atoms regardless of injected state.
Cause: failure to apply the four-category framework before writing the file; Category 3 mutable state must always be injected at runtime, never hardcoded in the rules file.
Resolution: removed all located_at facts from the .lp file; all ABox state now injected exclusively via ctl.add() in the Python script.
Methodology patch recommended: no — the principle is already established in OQ-05a; this was a failure to apply it, not a gap in the protocol.

[FAIL] IMP-I01-F03 — Paired constraint design makes violation atoms unreachable
Error: violation(X) derived then immediately rejected via :- violation(X); program becomes UNSAT; Python API yields zero models; for model in handle loop never executes; violations list permanently empty.
Cause: correct ASP reasoning about the paired pattern combined with insufficient reasoning about Python API behavior under UNSAT — zero model yield is a consequence that required empirical discovery.
Resolution: dropped paired constraint entirely; violation predicates are derivation-only; program is always SAT; enforcement loop checks for presence of violation(...) atoms in the yielded model rather than interrogating result.satisfiable.
Methodology patch recommended: no — this is expected implementation trial-and-error; the corrected design is now the documented pattern.

