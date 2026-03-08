# vision-and-protocols.md

## Semantics-Driven Worldbuilding DSL Project
Project Knowledge File — Hypothesis Document

---

## ⚠ FRAMING PREAMBLE — READ FIRST

This document represents one researcher's working understanding as of March 2026. 
It is a **hypothesis document**, not a conclusions document.

When referencing this material:

- Treat every claim as a proposition to be tested against current literature, not a fact to build upon.
- Actively look for where research contradicts, complicates, or supersedes what is stated here.
- Epistemic markers on every significant claim are authoritative: `[Verified]` | `[Inferred]` | `[Unverified]`
- The Open Questions and Unverified Assertions sections are the most valuable parts — prioritize investigating those over confirming what is stated.

**Your job is not to validate this document.** 
**It is to find out where it is wrong, incomplete, or missing something important.**

---

## AUTHORITATIVE TERM DEFINITIONS

These terms have specific meanings within this project. 
Use them consistently to prevent semantic drift and ambiguity.

**Zero-decoherence** The target property that no narrative output can contradict a previously established fact derivable from the WorldDSL specification or committed session state.
Coined term — not standard in the literature. 
[Unverified] — whether an equivalent formal concept exists under another name —

**WorldDSL** The machine-readable artifact encoding a specific world as structured ground truth.
Functions as the deterministic specification layer.
Formalism is Hybrid JSON + ASP (Clingo) — see OQ-01 [RESOLVED].

**Meta-questionnaire** A structured set of co-evolving, interconnected, self-referential Q&A pairs designed to elicit a coherent, self-consistent worldbuilding specification in natural language.
Intended as the human-facing input layer of the NL→DSL pipeline.
Whether this specific approach is novel relative to existing literature is [Unverified].

**NL→DSL pipeline** The process of translating natural language (meta-questionnaire output) into a WorldDSL artifact.
Contains at minimum: translation step (LLM), verification step (consistency checker), and human review step.
Full design is an OPEN QUESTION.

**Deterministic guardrails** Runtime enforcement mechanisms (e.g., Colang 2.0, NeMo Guardrails) that intercept LLM output and validate it against DSL-encoded constraints before it reaches the user.
Distinct from the rules engine.

**Semantics-based rules engine / Symbolic module** The inference layer that derives implied facts and constraints from the WorldDSL specification.
Distinct from runtime guardrails — operates on the static spec, not on live output.
Exact implementation is an OPEN QUESTION.

**Session state / ABox** The mutable record of what has actually happened in narrative sessions: injuries, deaths, relationship changes, employment status, etc.
Contrasted with the WorldDSL schema (TBox), which defines what kinds of things _can_ exist and what rules govern them.
How session state is maintained, validated, and queried across sessions has been substantially resolved — see OQ-02.
Storage (JSON file), state transitions (ASP-gated commit), validation (ASP solver), and prototype-scope retrieval (full load) are all decided.
Retrieval at scale remains a known out-of-scope problem.

**Narrative drift** Gradual divergence of LLM outputs from established world facts over the course of a long session or across sessions.
Caused by statelessness of LLMs and probabilistic generation. 
[Verified] — This is a documented problem in NLP/game literature.

**NeSy (Neurosymbolic)** An AI architecture that combines neural components (LLMs) with symbolic components (logic programs, constraint solvers, ontologies) to achieve capabilities neither can achieve alone.
The hybrid NeSy approach — keeping LLM intact while delegating logical enforcement to a separate symbolic module — is the relevant sub-category for this project. 
[Verified] — This is an active research field with published frameworks.

---

## PROJECT GOAL

**Primary success criterion:** A working prototype usable for actual RP sessions.

**Intended operator:** Solo developer / worldbuilder initially.
Potential for collaborative players or co-developers if concept validates.

**Scope:** Minimum viable prototype targets a single location cluster with 2–5 entities and 2–3 hard constraints.
This is sufficient to test the core hypothesis end-to-end.
Full-world scope is out of scope for the initial prototype.
[Paper:Zhou2025] [Paper:ElBoudouri2025] 

---

## CORE HYPOTHESIS

A natural language (NL) to Domain Specific Language (DSL) pipeline can be constructed such that:

1. A human provides NL worldbuilding input via a meta-questionnaire.
2. This is translated into a WorldDSL artifact (machine-readable, deterministic).
3. The WorldDSL artifact is used to generate structured outputs (prompts, guardrails, context injections) targeting LLM RP systems.
4. These outputs enforce world-specific rules deterministically by providing authoritative context that directs LLM extrapolation — the LLM does not reason from the DSL, it extrapolates fluently from it, producing inference-level behavior without genuine reasoning.
5. Creative latitude is preserved because the symbolic layer enforces only what it explicitly governs; everything outside that scope remains probabilistic and generative.
6. The result is significantly reduced narrative drift, decoherence, and hallucination across long and multi-session RP — not because the LLM has been made more consistent, but because inference has been delegated to a layer that is deterministic by design.

**Epistemic status of the hypothesis as a whole:** [Inferred]
The motivation is [Verified], the problem is [Verified], prior related architectures exist [Verified], the mechanism is [Verified] — [Paper:Madabushi2025] supports context-directed extrapolation as the operative LLM behavior — but the specific pipeline connecting them has not been validated against literature or a working prototype.
Critical unverified claim [Inferred]: Step 4 states that injecting ASP-derived facts as authoritative context enforces world rules deterministically.
This conflates two distinct claims: (1) the symbolic layer performs inference deterministically [Verified], and (2) that inference, injected as context, is sufficient to keep LLM extrapolation within constraint boundaries [Unverified].
The second claim is the central empirical question the prototype must answer.
OQ-08 RESOLVED — the enforcement mechanism is per-turn symbolic state injection plus reactive ASP validation.
The load-bearing hypothesis OQ-09 must test is whether this mechanism is sufficient to keep LLM extrapolation within constraint boundaries at interactive RP pace.

---

## MOTIVATION

The hypothesis arose from observation of MUD/MUSH/MOO engines (e.g., Evennia).
These systems maintain narratively consistent worlds using massive dictionaries and programmed logic — purely deterministic, but effective for persistence and consistency.
The gulf: deterministic engines have computer memory and software to track hundreds of objects that evolve over time.
LLMs are stateless and probabilistic — they cannot leverage equivalent memory natively.

The core intuition: replace the fixed dictionaries and programmed functions with an LLM's generative fluency, while preserving the engine's structural ground truth as a separate deterministic layer.

**Epistemic status:** The motivation and analogy are [Verified] as identifying a real and documented gap.
The proposed solution is [Inferred].

---

## WHAT IS VERIFIED (CITED FINDINGS)

These claims are grounded in literature found during research sessions.
Full references in the Research Log section.

- `[Verified]` Narrative drift and decoherence in LLMs over long sessions is a documented, measured problem in NLP and game AI literature.
    
- `[Verified]` The NeSy hybrid architecture — LLM paired with external symbolic module — is an active research area.
  The hybrid approach (LLM intact + separate symbolic layer) is considered more promising than integrative approaches for general logical reasoning.
    
- `[Verified]` NL→logic-program translation fails on two error types: syntactic (detectable, solver crashes) and semantic (silent, spec compiles but misrepresents intent).
  Semantic error is the dangerous class.
    
- `[Verified]` ASP + LLM integration (LLMASP, DSPy-ASP frameworks) exists and shows up to 50% accuracy improvement over direct prompting.
  Iterative feedback loops (LLM revises until solver accepts) are a documented approach.
    
- `[Verified]` Stateful narrative consistency across sessions is an unsolved open problem.
  Current approaches (RAG, context injection, BDI memory architectures) are partial mitigations, not solutions.
    
- `[Verified]` Sycophancy in LLMs is documented at ~58% baseline across frontier models.
  Caused by RLHF training.
  Mitigation: explicit skepticism instructions + hypothesis framing, not elaborate templates.
    
- `[Verified]` Anchoring bias: user-provided context carries more weight than model's generalized knowledge.
  Framing as hypothesis vs. ground truth produces measurably different model behavior.

- `[Verified]` Hypothesis is testable at minimal scale.
  Consistency failures appear with 2–5 entities and a handful of constraints because failures are structural (LLM statelessness, probabilistic generation), not complexity-dependent.
  Scale is not the binding variable for prototype scope.
  The "one town, dozen characters" framing in earlier drafts is 5–10x larger than minimum viable.
  [Paper:Zhou2025], [Paper:ElBoudouri2025]

- `[Verified]` OWL/RDF ontologies are disqualified as the constraint enforcement formalism for this project.
  The open-world assumption (absence of a fact does not imply the fact is false) is structurally incompatible with a closed-world narrative enforcement system where unstated facts must be treated as false.
  Tooling complexity (Java reasoners, Protégé) is an additional disqualifier at solo prototype scale.

- `[Verified]` Grammar formalisms (BNF, EBNF, PEG) are disqualified as constraint enforcement mechanisms.
  Grammars define syntactic validity, not semantic validity.
  They cannot express inter-entity constraints ("the dead cannot act") or detect contradictions.
  May be useful as the surface syntax definition layer of a WorldDSL format, but provide no inference or constraint enforcement.

- `[Verified]` Game Description Language (GDL) — a Datalog variant used in the General Game Playing research community — is the closest documented precedent to the WorldDSL problem.
  GDL conceptualizes everything through propositions and facts, with both static facts (never changing within one game) and dynamic facts (which undergo transitions based on a state update function).
  This is structurally identical to the TBox/ABox split in this project's design.
  Confirms the required WorldDSL semantics are expressible in a Datalog variant.
  [Paper:GDL2005]

- `[Verified]` The core mechanism of this project is not to make the LLM reason.
  The symbolic layer (WorldDSL rules engine) performs inference.
  LLM output is constrained to be consistent with that inference.
  Inference-level behavior emerges from the combined system, not from the LLM alone.
  The LLM contributes fluency and creativity; the symbolic layer contributes correctness and consistency.
  The WorldDSL also functions as the authoritative context that directs LLM extrapolation toward correct outputs — the LLM extrapolates fluently from the DSL rather than reasoning from it.
  [Paper:Madabushi2025]

- `[Verified]` ASP is documented in applied narrative constraint enforcement and LLM narrative plan verification — not only in general logical reasoning benchmarks.
  ASP constraints govern high-level narrative function sequencing with LLM rendering scenes from ASP-constrained outlines.
  
  [Paper:PJWang2024], [Paper:YiWang2025]

- `[Verified]` LLMs struggle with consistent state tracking without symbolic verification.
  State-of-the-art LLMs produce engaging stories but often fail to implement consistent, verifiable game mechanics, particularly in long or complex scenarios.
  [Paper:Yu2025]

- `[Verified]` Deterministic state tracking via symbolic layer is feasible and superior to prompt-only approaches.
  Codified FSMs outperform prompt-only baselines in both synthetic and real-world RP evaluations; 82.65% / 84.60% on real-world role-playing tasks.
  [Paper:Peng2026]

- `[Verified]` Automatic construction of per-entity FSMs from narrative events is unsolved.
  CFSMs are constructed from pre-written character profiles only — automatic construction from narrative plots is flagged as future work by the authors.
  This limits CFSM applicability to the ABox dynamic update problem.
  [Paper:Peng2026]  

- `[Verified]` GDL's keyword vocabulary maps onto the four WorldDSL categories: `role` → entity registry; `init` without `next` rules → static properties; `init`/`true`/`next` → mutable state; `legal` → integrity constraints (transition validity).
  `goal` and `terminal` are game-specific and have no RP equivalent.
  The `does` keyword (action invocation) has no WorldDSL equivalent — the OQ-02b reactive delta architecture handles actions as proposed ABox deltas validated against constraints, not as pre-enumerated named actions.
  [Doc:WikipediaGDL] [Doc:ThielschemGDLII]

- `[Verified]` Story2Game's world model entity taxonomy (Player, Character, Item, Room, Container) maps onto Category 1 (entity registry with sub-typing).
  Spatial adjacency between rooms collapses into Category 2 (static property).
  Entity location and inventory state collapse into Category 3 (mutable state).
  Action preconditions and effects map to Category 4 (integrity constraints) — they are not a fifth category.
  [Paper:Zhou2025]

- `[Verified]` The ABox snapshot validation pattern is the appropriate ASP encoding for this project.
  The solver validates proposed deltas against the current ABox snapshot — it does not plan across time steps.
  Fluent-with-time-step encoding (the full temporal ASP pattern) is over-engineered for a validator rather than a planner.
  Named-violation auxiliary predicates are required to produce human-readable UNSAT output identifying which constraint was violated.
  [Inferred] — standard ASP patterns; not validated against a published WorldDSL implementation.

- `[Verified]` Epistemic and uncertain world facts are correctly 
  excluded from the DSL at prototype scope.
  GDL required a separate extension (GDL-II) to handle 
  incomplete information, confirming that the base closed-world 
  formalism assumes certainty.
  At prototype scope with a human operator, character knowledge 
  is adjudicated narratively, not formally tracked in the DSL.
  [Doc:ThielschemGDLII]

- `[Verified]` Context utilization degradation is an empirically documented risk for system prompt injection as an enforcement mechanism.
  Frontier LLMs effectively utilize only 10–20% of their context window on reasoning tasks where relevant facts are distributed throughout long documents, with performance declining sharply as context length and reasoning complexity increase.
  GPT-4 effectively uses approximately 10% of its 128K window on such tasks.
  Scope condition: this finding applies to distributed-fact reasoning tasks; ASP-derived facts injected at the start of context (system prompt) have partial positional advantage per Liu2024 (U-shaped curve, primacy effect), but this advantage does not counteract the Li2024 attention decay mechanism as session length grows.
  OQ-08 RESOLVED — this distinction was investigated; per-turn symbolic state injection (not front-loaded session-start injection) was selected as the operative enforcement mechanism on this basis.
  [Paper:Kuratov2024] [Paper:Behrouz2025Titans]

- `[Inferred]` Transformer attention is a dense probabilistic distribution across all prior positions, not a discrete directed acyclic graph of parent-child provenance.
  Post-hoc attribution via attention weights is an approximation heuristic, not an architectural fact.
  LLMs therefore cannot self-verify constraint adherence from first principles — they have no reliable internal record of what facts have been established.
  This is a mechanistic argument for the necessity of an external symbolic verification layer, not merely an empirical observation about LLM inconsistency.
  Strengthens Step 4 of the core hypothesis without changing its epistemic status.
  [Inferred] — OQ-08 research completed without finding a published NeSy or interpretability paper formalizing this claim directly; remains [Inferred] and unverified; targeted verification deferred to post-prototype —
- `[Verified]` Session-start system prompt injection is empirically insufficient as a sole enforcement mechanism.
  Significant instruction drift is measurable within eight rounds on LLaMA2-chat-70B and GPT-3.5.
  The causal mechanism is attention decay — attention allocated to system prompt tokens declines progressively as conversation length grows.
  RLHF training reduces but does not eliminate drift.
  This is a structural property of the transformer attention mechanism, not a model scale issue.
  [Paper:Li2024]

- `[Verified]` Multi-turn performance degradation is universal across frontier models.
  All 15 top open- and closed-weight LLMs tested show an average 39% performance drop in multi-turn versus single-turn settings, across six generation tasks and 200,000+ simulated conversations.
  Degradation decomposes into a minor aptitude loss and a significant increase in unreliability — LLMs make wrong assumptions early and fail to recover.
  Additional test-time compute does not mitigate the effect.
  [Paper:Laban2025]

- `[Verified]` Per-turn symbolic state injection is the operative enforcement pattern in the closest published narrative architecture.
  Slice of Life (Treanor, Samuel, Nelson) maintains a symbolic social record updated each turn and constructs the LLM prompt from the current symbolic state at every generation step.
  The explicit design decision: simulation state is kept entirely symbolic; the LLM generates surface dialogue text only and does not advance simulation state.
  No quantitative constraint violation rate is reported — the system is described as working in practice but has not been formally benchmarked for constraint adherence.
  [Paper:Treanor2024] [Paper:Treanor2025]
  [Verified] — absence finding; no quantitative constraint adherence benchmark found for this architecture across FDG 2024 and FDG 2025 papers —

---

## WHAT IS SYNTHESIZED — NOT YET VERIFIED

These claims are logically inferred from verified findings but have not been confirmed against literature. 
**Do not treat as ground truth.**

- `[Inferred]` A four-component decomposition: (1) DSL schema design, (2) minimal viable DSL for a test world, (3) NL→DSL pipeline with verification, (4) stateful session layer.
- Presented as pragmatic development ordering — not validated as correct or complete.
    
- `[Inferred]` A three-tier constraint system: hard constraints (inviolable), soft constraints with flagged extrapolation, and unconstrained creative latitude.
  Analogized from physical simulation.
  Not a named approach in the literature.
    
- `[Inferred]` A flag-then-commit state mechanism: LLM or human flags narrative events as permanent state changes; human reviews; commits to DSL ABox.
  Reasonable design, but no published system implementing this specific mechanism was found.
    
- `[Inferred]` "Minimal viable DSL" as a solo-tractable starting strategy: begin with only vital-fact layer (entity registry, vital states, permanent relationships, Tier 1 constraints).
  Pragmatically reasonable but not validated against actual worldbuilding DSL scope in practice.
    
- `[Inferred]` The meta-questionnaire as structured NL elicitation may be novel relative to existing literature.
  Not confirmed.

- `[Inferred]` Minimum viable representational scope requires four functional categories: (1) entity registry, (2) static properties, (3) mutable state, (4) integrity constraints.
  Category 4 encodes both Type A state consistency rules ("a dead entity cannot act") and Type B transition validity rules ("an entity can only move to an adjacent location").
  Both encode identically in ASP as integrity constraints with the empty-head form :- body — the distinction is semantic, not representational.
  Category 4 is the minimum structure that makes the consistency problem non-trivial and worth a DSL at all.
  Without it, the system only validates single-entity facts, not relational consistency or valid state transitions.
  [Verified] — by GDL keyword mapping — 
  [Inferred] — for RP application —

- `[Inferred]` The closed-world assumption in Datalog and Prolog (anything not explicitly stated is false) is an advantage over OWL for closed game-state enforcement — but also a liability for open-ended RP worlds where the specification is inherently incomplete.
  At the edges of the spec, the system will treat unstated facts as false, which may produce incorrect constraint violations.
  This tradeoff requires explicit design handling and is not resolved by choosing Datalog alone.

- `[Inferred]` Codified Profiles (Python `parse_by_scene(scene)` functions with `if-then-else` logic and a `check_condition` LLM callable) solve the per-entity behavioral consistency problem — enforcing that a character acts according to their defined rules.
  They do NOT solve the inter-entity relational constraint problem (OQ-05a requirement 4).
  The `check_condition` callable is an LLM query, not a deterministic verifier — enforcement of context-sensitive conditions remains probabilistic.
  Codified Profiles are a viable component of the prototype architecture, not a complete solution.

- `[Inferred]` ASP-Gated Automatic State Commit is an improvement over flag-then-commit for interactive RP because human review gated by solver UNSAT is faster and sufficient — the human only reviews when a real constraint conflict exists.
  However, this does not protect against silent semantic errors in LLM-generated state deltas (errors that are ASP-SAT but factually wrong).
  This is the same risk class as OQ-03 (NL→DSL silent semantic error).

- `[Inferred]` The enforcement sufficiency gap is the central unverified empirical claim of the hypothesis.
  The symbolic layer correctly derives and enforces constraints; whether injecting those derived facts as authoritative context is sufficient to keep LLM extrapolation within constraint boundaries at interactive RP pace is not established by any cited source.
  This is what the prototype must empirically test.
  OQ-08 RESOLVED — mechanism is specified as per-turn symbolic state injection plus reactive ASP validation (OQ-02b); the design is now specified; sufficiency is the remaining load-bearing empirical claim, delegated to OQ-09 for falsifiable testing.

- `[Inferred]` LLM narrative coherence failures in RP systems decompose into three structurally distinct failure modes with different causes, remedies, and relationships to context window size.
  Failure Mode 1 (Truncation): early context falls out of the active window entirely; directly solved by larger windows; low VeriForge relevance at prototype scope — a single-session, single-tavern session will not approach truncation limits.
  Failure Mode 2 (Attention Dilution): the model holds all content within the window but assigns diminishing and unreliable weight to older material as session length grows; a structural property of transformer attention, not a capacity problem; not solved by larger windows — larger windows may worsen the ratio of distant-to-recent content.
  [Verified] — frontier LLMs effectively utilize only 10–20% of their context window on distributed-fact reasoning tasks, with performance declining as context length and reasoning complexity increase — [Paper:Kuratov2024].
  High VeriForge relevance: injecting ASP-derived constraint facts as authoritative context near the generation point directly addresses attention dilution by delegating to a layer that does not degrade with session length.
  Failure Mode 3 (Cross-Session Statefulness): facts and narrative state established in one session are unavailable in the next without explicit re-injection; no context window size resolves this by design.
  [Verified] — documented as an unsolved problem; current mitigations are partial — see WHAT IS VERIFIED.
  High VeriForge relevance: the ABox JSON + ASP-Gated Commit design (OQ-02b, RESOLVED) is specifically architected for this failure mode.
  This decomposition sharpens the value proposition: VeriForge addresses Failure Modes 2 and 3, which window scaling does not resolve and is not on a trajectory to resolve.

- `[Inferred]` The architectural bet underlying VeriForge: external symbolic enforcement (ASP-derived context injection) will remain sufficient and tractable before intrinsic architectural memory solutions (e.g., Titans-style test-time weight updates) mature to production accessibility for solo developers.
  This bet applies specifically to Failure Mode 2 (attention dilution) in single-session RP.
  Failure Mode 3 (cross-session statefulness) is not addressed by any current architectural memory solution — VeriForge's value proposition for Failure Mode 3 is independent of this bet.
  This is an explicit design assumption, not a proven claim.
  OQ-08 produced mechanism selection findings (per-turn injection selected); enforcement sufficiency findings will come from OQ-09 empirical testing.
  This bet should be reviewed after OQ-09 produces its results.

- `[Inferred]` Per-turn symbolic state injection addresses Failure Mode 2 (Attention Dilution) by keeping constraint-relevant facts near the generation point, exploiting recency bias per [Paper:Liu2024].
  Session-start injection is insufficient because even front-loaded facts decay from the generation point as session length grows, per [Paper:Li2024] attention decay mechanism.
  Per-turn re-injection does not solve the problem — it resets the positional advantage each turn.
  Whether per-turn injection is sufficient to maintain constraint adherence at interactive RP pace is [Unverified] — this is the load-bearing empirical claim of Step 4, now delegated to OQ-09.

---

## OPEN QUESTIONS (UNRESOLVED — REQUIRE RESEARCH)

These are the most important parts of this document.

**OQ-01 — DSL Formalism** [RESOLVED — Option A selected]
Selected formalism: Hybrid JSON + ASP (Clingo).
Decisive factors: (1) LLM→ASP translation precedent exists (LLMASP, DSPy-ASP, [Paper:Hite2025], [Paper:PJWang2024] future work); (2) ASP is documented in applied narrative constraint enforcement and LLM narrative plan verification ([Paper:PJWang2024], [Paper:YiWang2025]); (3) ASP is tractable for solo non-professional developers (see OQ-06).

Candidates evaluated and disposition:

OWL/RDF — disqualified.
Open-world assumption (absence of a fact does not imply the fact is false) is structurally incompatible with closed-world narrative enforcement where unstated facts must be treated as false.
Tooling complexity (Java reasoners, Protégé) is an additional disqualifier at solo prototype scale.
[Verified]

Grammar formalisms (BNF/EBNF/PEG) — disqualified.
Define syntactic validity only; cannot express inter-entity constraints ("the dead cannot act") or detect semantic contradictions.
May be useful as a surface syntax layer for WorldDSL, but provide no inference or constraint enforcement.
[Verified]

Option C — Executable Python rules — eliminated.
Cannot perform automatic inference from first principles.
Equivalent to pre-programming every implication; does not solve the stated problem.
[Verified]

Option B — Datalog (pyDatalog) — disqualified.
pyDatalog explicitly abandoned by its maintainer as of 2022, with no releases since November 2022.
No maintained Python-native Datalog alternative identified.
[Verified — pyDatalog GitHub and PyPI, accessed March 2026]

IDP-Z3 (FO-dot + Z3 SMT, KU Leuven) — disqualified as Option B replacement.
Actively maintained (pip install idp-engine, April 2025); explicit TBox/ABox block structure; closed-world enumeration semantics; built-in explanation output.
Disqualifying gap: no LLM→FO-dot translation precedent found.
No narrative or game domain adoption found.
Lower solo developer tractability than ASP.
[Verified]

Option A — Hybrid JSON + ASP (Clingo) — selected.
Maximum inference capability; active maintenance (Potassco/TU Dresden); Python API available (pip install clingo).
LLM→ASP translation precedent: LLMASP, DSPy-ASP, [Paper:Hite2025], [Paper:PJWang2024].
Applied narrative use: [Paper:PJWang2024], [Paper:YiWang2025].
Solo developer tractability: [Doc:PotasscoStart], [Doc:CMUMartens2017], [Repo:botcasp].
Remaining cost: ASP requires a mental model shift from imperative programming; JSON→ASP translation layer required.
Both are tractable at prototype scope (2–5 entities, 2–3 hard constraints).
[Verified]

**OQ-02 — Stateful Session Layer**
Decomposed into four sub-questions with different resolution status.

**OQ-02a — Storage** [DECIDED — prototype scope]
JSON file.
Human-readable, diff-able, trivially editable for manual corrections.
No research question at prototype scope.

**OQ-02b — State Transitions** [RESOLVED]
DEPENDS ON: OQ-01 [RESOLVED] — ASP is the validation mechanism; the commit design is formalism-specific.
DEPENDS ON: OQ-02a [DECIDED] — storage format must be known before commit target can be specified.
Selected design: ASP-Gated Automatic State Commit with Audit Log.
Each narrative turn, the LLM emits two outputs: (1) narrative text, and (2) a proposed ABox delta as structured JSON, following the RPGBench structured state output pattern [Paper:Yu2025].
The ASP solver validates the delta against the current ABox and DSL rules (OQ-02c mechanism).
If SAT: auto-commit the delta to the ABox JSON file and append the event to the session event log.
If UNSAT: pause and surface the conflict to the human operator for review before any commit.
The session event log is append-only and supplementary — it provides auditing and rollback capability.
The ABox remains the authoritative state layer.
The event log is not the primary source of truth (not full event sourcing), because the ASP solver validates against the ABox directly.

Epistemic status: [Inferred] — structurally supported by RPGBench state update pattern [Paper:Yu2025], event sourcing principles [Doc:Fowler2005], and the OQ-02c ASP validation mechanism, but this specific design combination has not been published.

Known risk [Inferred]: LLM-generated state deltas may be ASP-SAT but semantically incorrect (silent semantic error class).
The ASP gate does not catch errors that are constraint-consistent but factually wrong.
This is structurally the same risk as in NL→DSL translation (OQ-03) and must be addressed by the same mechanism: human review of UNSAT outcomes plus periodic spot-checking.

Flag-then-commit precedent: NOT FOUND [Verified] — absence finding; search conducted across RPGBench, CFSM, Story2Game literature; no published system implements human-gated state commit in interactive narrative —
All published systems use fully automated state updates (RPGBench, CFSM, Story2Game).
Human review gated by solver output is novel — not invalidated by absence of precedent, but untested.

Event sourcing applicability: PARTIALLY APPLICABLE [Inferred].
The append-only event log component transfers as an audit trail.
Full event sourcing (log as primary source of truth) does not transfer — it misaligns with ASP validation architecture and is over-engineered for prototype scope.

**OQ-02c — Validation of committed state** [RESOLVED by OQ-01]
ASP solver re-runs with the proposed ABox delta and checks for UNSAT.
Constraint violation detection is handled by the symbolic layer.
No additional mechanism required.

**OQ-02d — Retrieval at session start** [DECIDED — prototype scope]
Full load at session start.
2–5 entities and a handful of committed facts are well within context window limits for frontier models.
The retrieval problem becomes the binding constraint as world scope grows beyond a single location cluster.
This is a known out-of-scope problem for the prototype, not a solved one.

**OQ-03 — Verification and Error Correction Loop** [OPEN]
DEPENDS ON: OQ-01 [RESOLVED] — error correction loop design depends on what solver error output looks like in ASP.
BLOCKS: nothing hard, but findings inform OQ-09 (evaluation protocol must account for silent semantic error rate).
⚠ Key gap: NL→ASP translation quality for domain specification tasks is specifically unresearched.
All documented translation work (Hite2025, LLMASP, DSPy-ASP) demonstrates on logical reasoning benchmarks, not on open-ended worldbuilding description.
This is a harder problem than the benchmark results suggest.
How does the system catch and correct NL→DSL translation errors, especially the silent semantic kind?
What role does the human play vs. automated tooling?
DSL-Xpert 2.0 reportedly has automatic error-fixing — needs verification.

**OQ-04 — Undefined Case Handling / Extrapolation** [OPEN]
No hard dependencies identified.
What does the system do when a user prompt addresses a situation not specified in the WorldDSL?
Refusal, hallucination, and unconstrained extrapolation are all unacceptable.
A constrained extrapolation mechanism that surfaces proposed rules for human approval is [Inferred] as the right approach — not yet validated.

**OQ-05 — Prototype Scope**
Decomposed into two sub-questions with different resolution status:

"**OQ-05b — Scale Threshold** [PROVISIONALLY RESOLVED] 
The hypothesis is testable at minimal scale — 2–5 entities, one location cluster, a handful of constraints.
A single tavern with 3–4 characters and 2–3 hard constraints would be sufficient to test the pipeline end-to-end.
Scaling up adds breadth of coverage but does not add testability of the core hypothesis.
[Paper:Zhou2025] [Paper:ElBoudouri2025]

**OQ-05a — Representational Scope** [RESOLVED — Session 6]
DEPENDS ON: OQ-01 [RESOLVED] — categories must be expressed in the chosen formalism; cannot be designed without knowing the formalism.
DEPENDS ON: OQ-02b [RESOLVED] — mutable state category cannot be finalized without knowing how state transitions work.
BLOCKS: OQ-09
The WorldDSL requires four functional categories: (1) Entity registry — what named entities exist; encoded as ground ASP facts.
(2) Static properties — facts that never change during play, including spatial topology; encoded as ground ASP facts without transition rules.
(3) Mutable state — facts that change via committed ABox deltas, including character location and inventory; encoded as ABox JSON loaded as ground ASP facts at session start.
(4) Integrity constraints — rules encoding both state consistency ("dead cannot act") and transition validity ("can only move to adjacent room"); encoded as ASP integrity constraints (:- body form).
All four map to documented ASP/Clingo constructs.
Epistemic state, full temporal logic, and goal/terminal encoding are confirmed out-of-scope for prototype.
The ABox-snapshot validation pattern (not fluent-with-time-steps) is appropriate for this project's validation-not-planning use case.
[Verified] — by GDL mapping —
[Inferred] — for RP application —

**OQ-06 — Developer Toolset Fit** [RESOLVED]
ASP/Clingo is tractable for a solo non-professional developer.
Evidence: Potassco Getting Started guide (genuinely novice-oriented, pip install clingo, no JVM required) [Doc:PotasscoStart]; CMU CSC 791 course notes on ASP for game design (Martens, 2017), using dungeon generation as motivating example [Doc:CMUMartens2017]; solo hobbyist project modeling social deduction game rules as Clingo constraints with sat/unsat test suite [Repo:botcasp].
IDP-Z3 has no equivalent hobbyist community, game design adoption, or solo project precedent.

**OQ-07 — Meta-Questionnaire Design** [OPEN]
No hard dependencies identified.
What makes a questionnaire both comprehensive and self-consistent?
How are co-evolution and self-reference implemented structurally?
Is there prior work on structured worldbuilding elicitation in literature?

**OQ-08 — LLM Output Enforcement Mechanism** [RESOLVED — Session 8]
DEPENDS ON: OQ-01 [RESOLVED]; OQ-05a [RESOLVED]
BLOCKS: OQ-09 [NOW UNBLOCKED]
Selected enforcement mechanism for prototype scope: per-turn symbolic state injection plus reactive ASP validation (OQ-02b).
At each narrative turn, the ASP solver derives the current world state and active integrity constraints.
These are injected as authoritative context immediately before the LLM's generation call — not once at session start.
After the LLM generates narrative and a proposed ABox delta, the ASP solver validates the delta reactively (SAT → commit; UNSAT → human review).
Mechanisms evaluated and rejected:
Session-start system prompt injection alone — empirically insufficient; drift within 8 turns. [Paper:Li2024]
NeMo Guardrails — KNN-based topical enforcement only; unsuitable for world-state semantic constraints. [Paper:Rebedea2023]
Constrained decoding — unsuitable for complex semantic constraints. [Paper:Lee2025SIC]
RAG grounding alone — partial mitigation, not stateful constraint enforcement. [Paper:Score2025]
Precedent: Slice of Life architecture — per-turn symbolic state injection for LLM dialogue generation, symbolic simulation state not modified by LLM. [Paper:Treanor2024] [Paper:Treanor2025]
Open threads (not blocking prototype):
OQ-08-T1: Split-softmax attention decay mitigation — requires inference-time attention access; API availability unconfirmed; hold for post-prototype.
OQ-08-T2: Two-step action declaration (prospective enforcement) — LLM declares action as structured output, ASP validates, then LLM generates narrative; architecturally coherent but not required at prototype scope; reactive enforcement sufficient for core hypothesis test.
OQ-08-T3: Frontier model drift characterization — Li2024 measured LLaMA2-chat-70B and GPT-3.5; drift at RP session lengths on Claude 3.5+/GPT-4o not directly measured; assumed better-than-baseline, not a blocking gap.
What remains [Unverified]: whether per-turn injection is sufficient to keep LLM extrapolation within constraint boundaries at interactive RP pace.
This is the load-bearing empirical claim of Step 4 of the core hypothesis.
OQ-09 must design a test that can confirm or falsify it.

**OQ-09 — Prototype Evaluation Protocol** [OPEN]
DEPENDS ON: OQ-05a [RESOLVED] — four constraint categories confirmed; test cases can now be specified.
DEPENDS ON: OQ-08 [RESOLVED] — enforcement mechanism specified as per-turn symbolic state injection plus reactive ASP validation; evaluation must test whether this mechanism is sufficient.
DEPENDS ON: OQ-01 [RESOLVED] — ASP can generate violation reports (UNSAT with named constraints); this capability is confirmed and available to the evaluation design.
How do we determine whether the prototype achieved zero-decoherence (or meaningfully improved on baseline) in a falsifiable way?
Specifically: what constitutes a constraint violation in measurable terms? 
Who or what detects it — human review, a judge LLM, automated symbolic checker?
What is the baseline being compared against (raw LLM with system prompt vs. LLM with no grounding)?
Without an answer to this question, the prototype produces an output but not a result.
A working RP session is not a test of the hypothesis.
Minimum viable path: a predefined set of constraint-violation test cases administered manually against prototype output, compared against a no-DSL baseline.
Establishes falsifiability without requiring automated evaluation infrastructure.

---

## CLAIMS REQUIRING TARGETED VERIFICATION

Before the architecture can be treated as ground truth, these specific claims need literature search:

- [ ] Does a named formalism exist for "zero-decoherence" as defined here?
- [ ] Is the meta-questionnaire approach novel, or does prior work cover it?
- [ ] What does DSL-Xpert 2.0 actually do for automatic error correction?
- [ ] What is the documented scope of hand-built worldbuilding DSLs in practice?
- [ ] Is the flag-then-commit state mechanism implemented in any published system?
- [ ] What is the actual failure rate of NL→ASP translation for domain specification tasks (vs. the logical reasoning tasks studied in literature)?
- [ ] Is there a benchmark measuring formal constraint-specification violation rates specifically (as opposed to personality/style drift)? 
  RPEval covers the latter.
A direct measurement standard for zero-decoherence does not yet exist in this project's research log. 
(Relevant to OQ-09.)
- [x] Confirm full citation and URL for [Paper:Peng2025] Codified Profiles (NeurIPS 2025) RESOLVED 20260306  
- [x] Confirm full citation and URL for [Paper:GDL2005] Game Description Language RESOLVED 20260306
- [x] Verify current maintenance status of pyDatalog library before it can be considered a viable Option B formalism RESOLVED 20260306: disqualified, unmaintained since 2022
- [ ] Is the enforcement mechanism (ASP-derived context injection) sufficient to constrain LLM extrapolation within constraint boundaries at prototype scope?
  This is the central unverified empirical claim of Step 4 of the hypothesis.
  Depends on OQ-08 research.
- [ ] Is the silent semantic error rate for LLM-generated state deltas low enough that auto-commit with periodic spot-checking is an acceptable mitigation, or does the design require a stronger human oversight mechanism?
- [ ] What is the NL→ASP translation quality specifically for open-ended domain specification tasks?
  All documented translation work demonstrates on logical reasoning benchmarks only.
  This gap must be addressed before OQ-03 can be closed.
- [ ] Prospective constraint checking gap: does the reactive-only architecture (validate proposed delta after LLM generation) remain sufficient for all constraint classes, or do some constraints require knowing what action was taken before the LLM generates narrative?
  If prospective checking is required for any constraint class, an explicit action definition layer not present in any current category would be needed.
  Surface before OQ-08 research begins.

---

## RESEARCH PROTOCOLS

### Audit Trigger Protocol

A document audit is triggered when any OQ resolution unblocks at least one downstream OQ.
The audit scope is: (1) the resolved OQ's entry, and (2) all [Inferred] claims in the document that listed the resolved OQ as a dependency.
Full document audits are performed at session start when one has been triggered.
Ad hoc audits may be requested at any time but are not required between trigger events.

### Citation Format

Every factual claim uses inline citation: `[Tag:ShortID]`
Tags (exactly these, no others): `Paper` | `Repo` | `Doc` | `Blog` | `Forum` | `Social` | `Video`
ShortID format: `AuthorYYYY` (e.g., `[Paper:Zhang2024]`)
Full citations are logged in the Research Log with URL and access date.
Epistemic markers are always clean tokens: [Verified], [Inferred], [Unverified].
Supporting citations or explanatory notes follow outside the bracket, set off with em-dashes: [Verified] — Paper:X — Never embed explanatory text inside the bracket itself.

Precision claims — accuracy figures, percentages, named mechanisms — require primary source confirmation before committing.
Abstract-level verification is not sufficient for precision claims.
When a precision claim is cited via a secondary source, the status note must identify the actual primary source and flag it for direct confirmation.

### Research Log Entry Format

```
[Tag:ShortID] Author(s), "Title," Source/Venue, Year.
URL: [url]
Status: [Verified] | [Unverified]
Adjoining em-dash note specifies qualifying conditions where relevant:
e.g. [Verified] — via secondary source only —
e.g. [Unverified] — needs re-check; may be outdated —
Notes: [one sentence on relevance]
```

### Session Log Format

Each research session adds entries in this format:

```
[SN-EN] Topic | Status (Open/Resolved/Superseded) | Key sources
```

Where N = session number, EN = entry number within session.

### Per-Chat Opener Template

Paste this at the start of each new research chat:

```
Session [N] | Last snapshot: [date or "none"]
Focus: [one sentence on today's research question]
Open questions being addressed: [OQ-XX, OQ-YY or "none"]
Pending verifications: [list or "none"]

[Your question]
```

### Snapshot Trigger

When a research session produces a COMMIT-READY finding, update this document manually.
Add the finding to the appropriate section with its epistemic status.
Session log entry required for every update.

---

## RESEARCH LOG

_Populated as findings are verified._

### S01 — Foundational Research

[Paper:Gupta2025] Aakash Gupta, "I Studied 1,500 Academic Papers on Prompt Engineering," Medium/personal, 2025.
URL: https://aakashgupta.medium.com/i-studied-1-500-academic-papers-on-prompt-engineering 
Status: [Verified]
Notes: Structure > length; role prompting ineffective for correctness; context massively underrated.

[Paper:Chen2025] Chen et al., "When helpfulness backfires," npj Digital Medicine, 2025.
URL: https://www.nature.com/articles/s41746-025-02008-z 
Status: [Verified]
Notes: Up to 100% compliance with illogical requests in sycophancy study.

[Paper:Sharma2023] Anthropic, "Towards Understanding Sycophancy in Language Models," 2023.
URL: https://www.anthropic.com/research/towards-understanding-sycophancy-in-language-models
Status: [Verified]
Notes: RLHF mechanism for sycophancy; preference models favor agreement.

[Doc:AnthropicPrompting] Anthropic, "Prompt Engineering Best Practices," 2025.
URL: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering
Status: [Verified]
Notes: XML tags recommended for mixed-content prompts; rationale-with- instructions improves adherence.

[Paper:Marra2024] Marra et al., "From Statistical Relational to Neurosymbolic AI: A Survey," Artificial Intelligence, 2024.
URL: https://www.sciencedirect.com/science/article/pii/S0004370223002084
Status: [Verified]
Notes: Hybrid NeSy approach more promising than integrative for general logical reasoning.

[Paper:Chen2025b] M.K. Chen et al., "A Comparative Study of Neurosymbolic Approaches," NeSy Conference, 2025.
URL: https://www.arxiv.org/pdf/2508.03366
Status: [Verified]
Notes: Hybrid approach retains LLM capabilities while improving interpretability.

[Paper:Wang2024] Wang et al., "DSPy-ASP Framework," 2024.
URL: cited in neurosymbolic ASP survey
Status: [Verified] — via secondary source only; primary source not directly confirmed —
Notes: LLM + ASP with iterative solver feedback; up to 50% accuracy improvement.

[Paper:Score2025] SCORE Framework, arXiv, 2025.
URL: https://arxiv.org/html/2503.23512v1
Status: [Verified]
Notes: RAG-based narrative coherence; 41.8% fewer hallucinations vs. baseline.
Demonstrates RAG as partial mitigation, not solution, for stateful consistency.

### S02 — OQ-05 — Prototype Scope

[S2-E1] OQ-05 decomposition into 05a/05b | Resolved (05b), Open (05a) | [Paper:Zhou2025] [Paper:ElBoudouri2025] 
[S2-E2] OQ-09 (Evaluation Protocol) added as new open question | Open | None 
[S2-E3] PROJECT GOAL scope text conflict identified and corrected | Resolved | None

[Paper:Zhou2025] Eric Zhou, Shreyas Basavatia, Moontashir Siam, Zexin Chen, Mark O. Riedl, "STORY2GAME: Generating (Almost) Everything in an Interactive Fiction Game," Georgia Institute of Technology, arXiv:2505.03547v1, 2025.
URL: https://arxiv.org/abs/2505.03547
Status: [Verified]
Notes: Defines IF world model as Player, Character, Item, Room, Container entity types with preconditions/effects action layer.
Demonstrates consistency failures at minimal scale; action preconditions/effects map to Category 4 integrity constraints, not a new category.
Authorship corrected from "(authors not named in abstract)" — confirmed against primary source March 2026.

[Paper:ElBoudouri2025] Yassine El Boudouri et al., "RPEval: A Benchmark for Role-Playing LLMs," arXiv:2505.13157v1, 2025.
URL: https://arxiv.org/pdf/2505.13157
Status: [Verified]
Notes: Frontier models score 5.81–62.24% on in-character consistency against character profiles.
Directionally supports claim that drift is structural, not scale-dependent.
Does NOT directly measure consistency against formal constraint specifications — that gap is noted.
[Inferred] extrapolation to this project's decoherence problem is reasonable but unverified.

### S03 — OQ-01 — Formalism Research

[S3-E1] Grammars disqualified as constraint mechanism | Resolved | [Verified] — from EBNF/grammar literature
[S3-E2] OWL disqualified on open-world assumption grounds | Resolved | [Verified] — from W3C OWL documentation
[S3-E3] GDL identified as closest WorldDSL precedent | Verified | [Paper:GDL2005]
[S3-E4] Codified Profiles evaluated — partial fit, not complete solution | Resolved | [Paper:Peng2025]
[S3-E5] Closed-world assumption tradeoff for Datalog identified | Open — design decision required | None
[S3-E6] Three viable prototype formalism candidates identified: Hybrid JSON+ASP, Datalog (pyDatalog), Executable Python rules | Open — pending tractability judgment | See OQ-01
[S3-E7] pyDatalog disqualified — unmaintained since Nov 2022, maintainer redirects to IDP-Z3 | Resolved | pyDatalog GitHub and PyPI, accessed March 2026
[S3-E8] IDP-Z3 (FO-dot + Z3 SMT, KU Leuven) identified as potential Option B replacement | Open — LLM→FO-dot translation precedent unresearched | See OQ-01

[Paper:Peng2025] Letian Peng and Jingbo Shang, "Codifying Character Logic in Role-Playing," NeurIPS 2025 (poster).
URL: https://arxiv.org/abs/2505.07705
Status: [Verified]
Notes: Per-entity behavioral consistency via executable Python scene-parsing functions.
Improves consistency, adaptability, and diversity especially for smaller LLMs.
Does not address inter-entity relational constraints or session state — the check_condition callable is probabilistic (LLM query), not deterministic verifier.

[Paper:GDL2005] Michael R. Genesereth, Nathaniel Love, and Barney Pell, "General Game Playing: Overview of the AAAI Competition," AI Magazine, vol. 26, no. 2, pp. 62–72, 2005.
URL: https://www.semanticscholar.org/paper/General-Game-Playing:-Overview-of-the-A
AAI-Genesereth-Love/c89c71dbe5617bea44383585b58cd0cbc37bf79a
Status: [Verified]
Notes: Defines Game Description Language as a Datalog variant with static and dynamic facts and state transition functions.
Closest documented precedent to WorldDSL semantics.
Validates that the required formalism is expressible in Datalog.

[Paper:Madabushi2025] Harish Tayyar Madabushi et al., "Neither Stochastic Parroting nor AGI: LLMs Solve Tasks through Context-Directed Extrapolation from Training Data Priors," arXiv:2505.23323v1, University of Bath, 2025.
URL: https://arxiv.org/html/2505.23323v1
Status: [Verified]
Notes: Characterizes LLM behavior as context-directed extrapolation from training priors, not advanced reasoning.
Explicitly recommends augmenting techniques that do not rely on inherent LLM reasoning.
Directly supports the hybrid NeSy approach and the project's core mechanism clarification.

### S04 — OQ-01 OQ-06 — Formalism and Tractability

[S4-E1] OQ-01 resolved — Hybrid JSON + ASP (Clingo) selected | Resolved | [Paper:PJWang2024] [Paper:YiWang2025] [Paper:Hite2025] [Repo:botcasp] [Doc:PotasscoStart] [Doc:CMUMartens2017]
[S4-E2] OQ-06 resolved — ASP tractable for solo non-professional developer | Resolved | [Doc:PotasscoStart] [Doc:CMUMartens2017] [Repo:botcasp]
[S4-E3] OQ-05a unblocked by OQ-01 resolution | Open — in progress | None
[S4-E4] Citation corrections: YiWang2025, PJWang2024, Hite2025 author names corrected; PJWang2024 future plans characterization verified against primary source | Resolved | Primary sources accessed directly
[S4-E5] IDP-Z3 disqualified — no LLM→FO-dot translation precedent, no narrative domain adoption | Resolved | [Paper:Putra2026]

[Paper:PJWang2024] Phoebe J. Wang and Max Kreminski, "Guiding and Diversifying LLM-Based Story Generation via Answer Set Programming," Wordplay @ ACL 2024, arXiv:2406.00554v2, 2024.
URL: https://arxiv.org/abs/2406.00554
Status: [Verified]
Notes: ASP constraints govern high-level narrative function sequencing; LLM renders scenes from ASP-constrained outlines.
Future work explicitly states two plans: (1) user-interactive constraint of ASP pipeline; (2) LLM-generated ASP constraints from open-ended NL statements of storytelling intent.
The second plan is direct precedent for OQ-01 NL→ASP translation path and OQ-08.

[Paper:YiWang2025] Yi Wang and Max Kreminski, "Can LLMs Generate Good Stories? Insights and Challenges from a Narrative Planning Perspective," Wordplay/CoG 2025, arXiv:2506.10161v1, 2025.
URL: https://arxiv.org/abs/2506.10161
Status: [Verified]
Notes: Evaluates LLMs on narrative planning problems using ASP as formal verifier.
Confirms symbolic planners superior to LLMs for runtime narrative planning — directly supports delegating inference to symbolic layer.

[Paper:Hite2025] Connar Hite et al., "Bridging Natural Language and ASP: A Hybrid Approach Using LLMs and AMR Parsing," arXiv:2511.08715v1, 2025.
URL: https://arxiv.org/abs/2511.08715
Status: [Verified]
Notes: Lightweight NL→ASP via LLM simplification plus AMR graph parsing; minimizes LLM role; errors are explainable.
Critical qualification: demonstrated on combinatorial logic puzzles (zebra-type), not domain specification tasks.
Confirms translation approach; does not validate it for narrative world specification use case specifically.

[Paper:Putra2026] Rizky Ramadhana Putra et al., "NL2LOGIC: AST-Guided Translation of Natural Language into First-Order Logic with Large Language Models," Findings of EACL 2026, arXiv:2602.13237, 2026.
URL: https://arxiv.org/abs/2602.13237
Status: [Verified]
Notes: NL→FOL→Z3 pipeline achieving near-perfect syntax correctness and +30% semantic accuracy over baselines.
Targets Z3 Python API directly, not IDP-Z3 FO-dot syntax.
Confirms adjacent translation technology exists; does not bridge the IDP-Z3 gap.

[Repo:botcasp] pnkfelix, "botc-asp: Blood on the Clocktower game logic modeled in Answer Set Programming (Clingo)," GitHub, active 2024–present.
URL: https://github.com/pnkfelix/botc-asp
Status: [Verified]
Notes: Solo hobby developer models multi-entity social deduction game rules as Clingo constraints with sat/unsat test suite.
Direct OQ-06 evidence for solo ASP tractability; structurally analogous to this project's constraint enforcement problem.

[Doc:CMUMartens2017] Chris Martens, "Notes on Answer Set Programming," CSC 791 Generative Methods for Game Design, Carnegie Mellon University, September 20, 2017.
URL: https://www.cs.cmu.edu/~cmartens/asp-notes.pdf
Status: [Verified]
Notes: Genuinely novice-oriented ASP introduction using dungeon generation as motivating example.
Confirms game design adoption of ASP pedagogy; course notes publicly accessible.

[Doc:PotasscoStart] Potassco, "Getting Started," Potassco — the Potsdam Answer Set Solving Collection.
URL: https://potassco.org/doc/start/
Status: [Verified]
Notes: Official novice-oriented guide; starts from first principles with simple examples.
Confirms pip-installable, no JVM or build system required.

### S05 — OQ-02b — State Transition Design

[S5-E1] OQ-02b flag-then-commit precedent search | Not found | No published system implements human-gated state commit in interactive narrative
[S5-E2] Event sourcing applicability to narrative state | Partially applicable | [Doc:Fowler2005] — append-only log transfers; full event sourcing does not
[S5-E3] RPGBench structured state output pattern identified as published precedent for automated state extraction | Resolved | [Paper:Yu2025]
[S5-E4] CFSM identified — extends Codified Profiles to FSM state transitions; per-entity mutable state relevance | New thread (OQ-05a) | [Paper:Peng2026]
[S5-E5] OQ-02b RESOLVED — ASP-Gated Automatic State Commit with Audit Log adopted | Resolved | [Paper:Yu2025] [Doc:Fowler2005]

[Paper:Yu2025] Pengfei Yu et al., "RPGBENCH: Evaluating Large Language Models as Role-Playing Game Engines," NeurIPS 2025 Workshop (SEA Workshop), arXiv:2502.00595v1, 2025.
URL: https://arxiv.org/abs/2502.00595
Status: [Verified]
Notes: Three-stage simulation loop (Event Planning, Narration, Game State Updates) with structured JSON state output each turn.
Empirically confirms LLMs struggle with consistent state tracking without symbolic verification — LLMs produce engaging stories but often fail to implement consistent, verifiable game mechanics, particularly in long or complex scenarios.
Direct published precedent for automated state extraction pattern used in OQ-02b design.

[Paper:Peng2026] Letian Peng, Yupeng Hou, Kun Zhou, Jingbo Shang, "Codified Finite-State Machines for Role-Playing," University of California San Diego, arXiv:2602.05905v1, 2026.
URL: https://arxiv.org/abs/2602.05905
Status: [Verified]
Notes: Extends Codified Profiles to full FSM state transitions, automatically extracted from character profiles via LLM coding.
Outperforms prompt-only baselines in both synthetic and real-world evaluations; 82.65% / 84.60% on real-world role-playing tasks across main and minor characters.
Confirms deterministic state tracking via symbolic layer is feasible and superior to prompting.
Limitation: CFSMs are constructed from pre-written character profiles, not from narrative events — automatic construction from narrative plots is flagged as future work by authors.
Relevant to OQ-05a (per-entity mutable state category); does not address inter-entity relational constraints.

[Doc:Fowler2005] Martin Fowler, "Event Sourcing," martinfowler.com, 2005.
URL: https://martinfowler.com/eaaDev/EventSourcing.html
Status: [Verified]
Notes: Canonical definition of event sourcing pattern.
Append-only event log as audit trail transfers to this project.
Full event sourcing (log as primary source of truth) does not transfer — misaligns with ASP validation architecture where ABox is the authoritative state layer.

### S06 — OQ-05a — Representational Scope

[S6-E1] GDL keyword audit — six keywords map onto four categories; `legal` / transition validity rules encode as Type B integrity constraints; `terminal` and `goal` confirmed out-of-scope | Resolved | [Doc:WikipediaGDL] [Doc:ThielschemGDLII]
[S6-E2] Story2Game world model verified against primary source — entity taxonomy maps to Categories 1–3; preconditions/effects map to Category 4; no fifth category required | Resolved | [Paper:Zhou2025]
[S6-E3] Spatial/topological facts confirmed to collapse into existing categories — adjacency = Category 2, position = Category 3 | Resolved | [Inferred] — from GDL and Story2Game analysis —
[S6-E4] ASP implementation form confirmed — snapshot validation pattern; named-violation auxiliary predicates required for human-readable UNSAT output | Resolved | [Inferred] — standard ASP patterns —
[S6-E5] Category 4 label refined from "inter-entity constraints" to "integrity constraints" covering both Type A (state consistency) and Type B (transition validity) | Resolved | [Inferred] — from GDL mapping — 
[S6-E6] Story2Game citation authorship corrected — Eric Zhou et al., Georgia Tech | Resolved | Primary source accessed March 2026
[S6-E7] New thread: prospective vs. reactive constraint checking gap — reactive-only architecture may be insufficient for constraints requiring action-level knowledge | Open — hold for OQ-08 | None
[S6-E8] OQ-05a RESOLVED — four-category decomposition confirmed necessary and sufficient at prototype scope | Resolved | [Paper:Zhou2025] [Doc:WikipediaGDL] [Doc:ThielschemGDLII]

[Doc:WikipediaGDL] "Game Description Language," Wikipedia.
URL: https://en.wikipedia.org/wiki/Game_Description_Language
Status: [Verified]
Notes: Complete GDL keyword set reference; confirms GDL-II 
extension handles incomplete information separately from base 
GDL.

[Doc:ThielschemGDLII] Michael Thielscher, "A General Game 
Description Language for Incomplete Information Games," AAAI 
2010.
URL: https://www.cs.huji.ac.il/~jeff/aaai10/02/AAAI10-175.pdf
Status: [Verified]
Notes: GDL-II adds `sees` and `random` for uncertainty; base 
GDL assumes closed-world certainty — confirms project boundary 
for excluding epistemic state from DSL.

### S07 — OQ-08 — Ancillary Evaluation

[S7-E1] CTAG architecture evaluated — disposed DISCARD | Resolved | Architecture requires LLM internals modification; not tractable at prototype scope; does not address any open question.
[S7-E2] Context utilization degradation finding — OQ-08 risk sharpened; misattribution corrected — BABILong is the primary source, not Titans | COMMIT-CANDIDATE — feed into OQ-08 | [Paper:Kuratov2024] [Paper:Behrouz2025Titans]
[S7-E3] Provenance-approximation argument — mechanistic case for external symbolic layer | COMMIT-CANDIDATE — feed into OQ-08 for targeted verification | [Inferred]
[S7-E4] Intrinsic Memory Agents convergence with OQ-02b | Context-only — does not change open question status | [Paper:Yuen2025]
[S7-E5] Cross-pollination methodology principle established — pursue adjacent directions far enough to understand why they fail, then derive what the failure mode implies for the primary architecture | Resolved — project conduct note, no citation required
[S7-E6] Narrowed problem framing — three failure modes disaggregated: truncation / attention dilution / cross-session statefulness | Resolved | [Paper:Kuratov2024] — citation corrected from TitansReview2025/Behrouz2025Titans to primary BABILong source

[Paper:Kuratov2024] Yuri Kuratov, Aydar Bulatov, Petr Anokhin, Ivan Rodkin, Dmitry Igorevich Sorokin, Artyom Sorokin, Mikhail Burtsev, "BABILong: Testing the Limits of LLMs with Long Context Reasoning-in-a-Haystack," NeurIPS 2024 atasets and Benchmarks Track (Spotlight), arXiv:2406.10149, 2024.
URL: https://arxiv.org/abs/2406.10149
Status: [Verified]
Notes: Frontier LLMs effectively utilize only 10–20% of context on distributed-fact reasoning tasks; performance declines with context length and reasoning complexity.
GPT-4 uses approximately 10% of its 128K window effectively.
Primary source for the context utilization degradation finding — not Titans (Behrouz et al.), which cites this paper.

[Paper:Behrouz2025Titans] Ali Behrouz, Peilin Zhong, Vahab Mirrokni, "Titans: Learning to Memorize at Test Time," Google Research, arXiv:2501.00663, 2025.
URL: https://arxiv.org/abs/2501.00663
Status: [Verified]
Notes: Neural long-term memory module updating weights at test time via surprise-driven gradient signal.
Outperforms GPT-4 on BABILong at 2M+ token scale.
Relevant to OQ-08 as evidence the context dilution problem is recognized and actively researched at the frontier.
Not applicable to VeriForge prototype — requires architectural modification of base model.
No official code release as of March 2026.

[Paper:Yuen2025] Sizhe Yuen et al., "Intrinsic Memory Agents: Heterogeneous Multi-Agent LLM Systems through Structured Contextual Memory," arXiv:2508.08997v2, 2026.
URL: https://arxiv.org/abs/2508.08997
Status: [Verified] — author list not fully confirmed; primary source not directly accessed —
Notes: Agent-specific structured JSON memory templates evolving from agent outputs; 38.6% improvement on PDDL planning benchmark.
Structurally convergent with OQ-02b ASP-Gated State Commit pattern — context-only corroboration, not a new finding.

### S08 — OQ-08 — Enforcement Mechanism

[S8-E1] Session-start system prompt injection empirically falsified — instruction drift within 8 turns on LLaMA2-chat-70B and GPT-3.5 | Resolved | [Paper:Li2024]
[S8-E2] Multi-turn performance degradation universal across frontier models — 39% average drop across 15 LLMs, 200,000+ simulated conversations | Resolved | [Paper:Laban2025]
[S8-E3] Positional bias (Lost in the Middle) characterized — U-shaped curve; front-loaded and recency-positioned facts better utilized | Resolved | [Paper:Liu2024]
[S8-E4] Per-turn symbolic state injection identified as operative enforcement pattern in closest published narrative architecture (Slice of Life) | Resolved | [Paper:Treanor2024] [Paper:Treanor2025]
[S8-E5] NeMo Guardrails evaluated — disqualified for semantic world-state constraints; KNN-based topical enforcement only | Resolved | [Paper:Rebedea2023]
[S8-E6] Proactive vs. reactive enforcement distinction confirmed as architecturally significant — complex semantic constraints cannot be enforced via constrained decoding; reactive post-generation validation is tractable path | Resolved | [Paper:Lee2025SIC]
[S8-E7] Two-step action declaration pattern identified as prerequisite for prospective enforcement — open thread OQ-08-T2; not required at prototype scope | Open — new thread |
[S8-E8] OQ-08 RESOLVED — enforcement mechanism specified as per-turn symbolic state injection plus reactive ASP validation (OQ-02b); sufficiency remains load-bearing empirical claim, delegated to OQ-09 | Resolved |
[S8-E9] OQ-09 unblocked by OQ-08 resolution | Open — next session target |
[S8-E10] LongGenBench 4,000-token threshold claim corrected — paper tests at 16K/32K, not 4,000 tokens; synthesis error from prior compaction; claim dropped | Corrected | [Paper:Wu2024]

[Paper:Li2024] Kenneth Li, Tianle Liu, Naomi Bashkansky, David Bau, Fernanda Viégas, Hanspeter Pfister, Martin Wattenberg, "Measuring and Controlling Instruction (In)Stability in Language Model Dialogs," Conference on Language Modeling (COLM 2024), arXiv:2402.10962v4, 2024.
URL: https://arxiv.org/abs/2402.10962
Status: [Verified]
Notes: Quantitative benchmark for instruction drift via self-chats; significant drift within 8 rounds on LLaMA2-chat-70B and GPT-3.5; causal mechanism identified as attention decay; split-softmax mitigation proposed but requires inference-time attention access.

[Paper:Laban2025] Philippe Laban, Hiroaki Hayashi, Yingbo Zhou, Jennifer Neville, "LLMs Get Lost In Multi-Turn Conversation," Microsoft Research / Salesforce Research, arXiv:2505.06120v1, 2025.
URL: https://arxiv.org/abs/2505.06120
Status: [Verified]
Notes: 39% average performance drop in multi-turn vs. single-turn settings across 15 frontier LLMs and 6 generation tasks; degradation attributed primarily to increased unreliability and early wrong assumptions; universal across model sizes and architectures; distinct mechanism from Li2024 attention decay.

[Paper:Liu2024] Nelson F. Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, Percy Liang, "Lost in the Middle: How Language Models Use Long Contexts," Transactions of the Association for Computational Linguistics (TACL), arXiv:2307.03172, 2024.
URL: https://arxiv.org/abs/2307.03172
Status: [Verified]
Notes: U-shaped performance curve over long contexts; beginning and end of context better utilized than middle; directly informs per-turn injection strategy by explaining partial positional advantage of front-loaded injection.

[Paper:Treanor2024] Mike Treanor, Ben Samuel, Mark J. Nelson, "Prototyping Slice of Life: Social Physics with Symbolically Grounded LLM-based Generative Dialogue," FDG 2024: Proceedings of the 19th International Conference on the Foundations of Digital Games, ACM, 2024.
URL: https://doi.org/10.1145/3649921.3656988
Status: [Verified]
Notes: Prototype social physics game using Ensemble engine with per-turn symbolic state injection for LLM dialogue; closest published predecessor to VeriForge's enforcement mechanism; no quantitative constraint adherence benchmark reported.

[Paper:Treanor2025] Mike Treanor, Ben Samuel, Mark J. Nelson, "Slice of Life: A Social Physics Game with Interactive Conversations using Symbolically Grounded LLM-Based Generative Dialogue," FDG 2025: Proceedings of the 20th International Conference on the Foundations of Digital Games, ACM, 2025.
URL: https://doi.org/10.1145/3723498.3723806
Status: [Verified]
Notes: Full paper; design decision confirmed — simulation state kept entirely symbolic; LLM used for surface text realization only, not simulation progress; directly validates VeriForge's architectural separation of symbolic layer and LLM.

[Paper:Rebedea2023] Traian Rebedea, Razvan Dinu, Makesh Sreedhar, Christopher Parisien, Jonathan Cohen, "NeMo Guardrails: A Toolkit for Controllable and Safe LLM Applications with Programmable Rails," EMNLP 2023 System Demonstrations, arXiv:2310.10501, 2023.
URL: https://arxiv.org/abs/2310.10501
Status: [Verified]
Notes: KNN-based canonical form matching for dialog rail enforcement; effective for topical/safety constraints; not designed for world-state semantic constraints; disqualified as primary VeriForge enforcement mechanism.

[Paper:Lee2025SIC] Alexander W. Lee, Justin Chan, Michael Fu, Nicolas Kim, Akshay Mehta, Deepti Raghavan, Uğur Çetintemel, "Semantic Integrity Constraints: Declarative Guardrails for AI-Augmented Data Processing Systems," Proceedings of the VLDB Endowment, Vol. 18, No. 11, 2025. Also arXiv:2503.00600.
URL: https://www.vldb.org/pvldb/vol18/p4073-lee.pdf
Status: [Verified]
Notes: Formalizes proactive vs. reactive enforcement distinction; recommends limiting constrained decoding to simple constraints; confirms reactive validation as tractable path for complex semantic constraints.

[Paper:Wu2024] Yuhao Wu et al., "LongGenBench: Benchmarking Long-Form Generation in Long Context LLMs," ICLR 2025, arXiv:2409.02076, 2024.
URL: https://arxiv.org/abs/2409.02076
Status: [Verified]
Notes: Benchmark for instruction adherence across long generated outputs at 16K and 32K token lengths; confirms degradation at extended generation lengths; prior synthesis error attributing a 4,000-token threshold to this paper is corrected — no such threshold exists in the primary source.

---

_Document version: 1.6 — March 2026_
_Next review trigger: OQ-09 (Evaluation Protocol) research complete_
