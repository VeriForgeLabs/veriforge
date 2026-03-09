# vision.md

_Document version: 0.10 — March 2026_
_Next review trigger: OQ-09 (Evaluation Protocol) research complete_

## Semantics-Driven Worldbuilding DSL Project
Project Knowledge File — Hypothesis Document

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
  → [OQ-05a — RESOLVED — S06]
  → [OQ-02 — RESOLVED — S05]

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
  → [OQ-08 — RESOLVED — S08]

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
  → [OQ-08 — RESOLVED — S08]

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
  → [OQ-05a — RESOLVED — S06]

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
  OQ-08 RESOLVED — mechanism is specified as per-turn symbolic state injection plus reactive ASP validation (OQ-02b); the design is now specified; sufficiency is the remaining load-bearing empirical claim, delegated to OQ-09 [RESOLVED — S10] — evaluation protocol designed; empirical test is prototype phase.

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
  Whether per-turn injection is sufficient to maintain constraint adherence at interactive RP pace is [Unverified] — this is the load-bearing empirical claim of Step 4, now delegated to OQ-09 [RESOLVED — S10] — evaluation protocol designed; empirical test is prototype phase.

---

## OPEN QUESTIONS (UNRESOLVED — REQUIRE RESEARCH)

These are the most important parts of this document.

**OQ-01 — DSL Formalism** [RESOLVED — S04] — Hybrid JSON + ASP (Clingo) selected. → [research-log.md](research-log.md#oq-01)

**OQ-02 — Stateful Session Layer** [RESOLVED — S05] — ASP-Gated Automatic State Commit with Audit Log; JSON file storage; full load at session start. → [research-log.md](research-log.md#oq-02)

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
Decomposed into two sub-questions, both resolved:

**OQ-05b — Scale Threshold** [RESOLVED — S02] — Hypothesis testable at minimal scale: 2–5 entities, one location cluster, 2–3 hard constraints. → [research-log.md](research-log.md#oq-05b)

**OQ-05a — Representational Scope** [RESOLVED — S06] — Four functional categories confirmed: entity registry, static properties, mutable state, and integrity constraints (Type A state consistency + Type B transition validity), all expressible in ASP/Clingo. → [research-log.md](research-log.md#oq-05a)

**OQ-06 — Developer Toolset Fit** [RESOLVED — S04] — ASP/Clingo confirmed tractable for a solo non-professional developer via novice documentation, game design course materials, and a solo hobbyist project. → [research-log.md](research-log.md#oq-06)

**OQ-07 — Meta-Questionnaire Design** [OPEN]
No hard dependencies identified.
What makes a questionnaire both comprehensive and self-consistent?
How are co-evolution and self-reference implemented structurally?
Is there prior work on structured worldbuilding elicitation in literature?

**OQ-08 — LLM Output Enforcement Mechanism** [RESOLVED — S08] — Per-turn symbolic state injection plus reactive ASP validation selected as the enforcement mechanism; whether this is sufficient to constrain LLM extrapolation at interactive RP pace is the load-bearing empirical claim delegated to OQ-09. → [research-log.md](research-log.md#oq-08)

**OQ-09 — Prototype Evaluation Protocol** [RESOLVED — S10] — Three-condition ablation (raw LLM / system-prompt-only / VeriForge per-turn), primary metric Constraint Violation Rate, falsification criterion ≥75% CVR reduction vs. Condition A AND statistically lower than Condition B, 12+ pre-registered test cases across Type A and Type B constraint pairs. → [research-log.md](research-log.md#oq-09)

---

## CLAIMS REQUIRING TARGETED VERIFICATION

Open items requiring literature search before the architecture can be treated as ground truth.
Closed items have been migrated to [research-log.md](research-log.md#closed-verification-items).

- [ ] Does a named formalism exist for "zero-decoherence" as defined here? | Origin: S01 | Influences: OQ-09 | [Unverified]

- [ ] Is the meta-questionnaire approach novel, or does prior work cover it? | Origin: S01 | Influences: OQ-07 | [Unverified]

- [ ] What does DSL-Xpert 2.0 actually do for automatic error correction? | Origin: S03 | Influences: OQ-03 | [Unverified]

- [ ] What is the documented scope of hand-built worldbuilding DSLs in practice? | Origin: S01 | Influences: OQ-07 | [Unverified]

- [ ] What is the actual failure rate of NL→ASP translation for domain specification tasks (vs. logical reasoning tasks studied in literature)? | Origin: S03 | Influences: OQ-03 | [Unverified]

- [ ] Is there a benchmark measuring formal constraint-specification violation rates specifically (as opposed to personality/style drift)?
  RPEval covers personality/style drift; a direct measurement standard for zero-decoherence does not yet exist in this project's research log. | Origin: S02 | Influences: OQ-09 | [Unverified]

- [ ] Is the enforcement mechanism (ASP-derived context injection) sufficient to constrain LLM extrapolation within constraint boundaries at prototype scope?
  This is the central unverified empirical claim of Step 4 of the hypothesis.
  Delegated to OQ-09 [RESOLVED — S10] — evaluation protocol designed; empirical test is prototype phase. | Origin: S08 | Influences: OQ-09 | [Unverified]

- [ ] Does reactive ASP validation of ABox deltas catch constraint violations
  that appear in LLM surface narrative without triggering a delta at all?
  The VDR metric in OQ-09 is designed to measure this gap, but the
  architectural vulnerability is [Inferred] — not yet tested. | Origin: S10 | Influences: OQ-09 | [Inferred]

- [ ] Confirm primary source and URL for [Paper:Wang2024] DSPy-ASP framework;
  the accuracy figure (up to 50% improvement) is a precision claim on a secondary source only.
  | Origin: S01 | Influences: OQ-01 (historical) | [Unverified]

```