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
[Unverified whether equivalent formal concept exists under another name.]

**WorldDSL** The machine-readable artifact encoding a specific world as structured ground truth.
Functions as the deterministic specification layer.
The exact formalism (ASP, OWL, JSON+rules, etc.) is an OPEN QUESTION.

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
How session state is maintained, validated, and queried across sessions is an OPEN QUESTION and considered the hardest sub-problem.

**Narrative drift** Gradual divergence of LLM outputs from established world facts over the course of a long session or across sessions.
Caused by statelessness of LLMs and probabilistic generation. 
[Verified as documented problem in NLP/game literature.]

**NeSy (Neurosymbolic)** An AI architecture that combines neural components (LLMs) with symbolic components (logic programs, constraint solvers, ontologies) to achieve capabilities neither can achieve alone.
The hybrid NeSy approach — keeping LLM intact while delegating logical enforcement to a separate symbolic module — is the relevant sub-category for this project. 
[Verified as active research field with published frameworks.]

---

## PROJECT GOAL

**Primary success criterion:** A working prototype usable for actual RP sessions.

**Intended operator:** Solo developer / worldbuilder initially.
Potential for collaborative players or co-developers if concept validates.

**Scope:** Minimum viable prototype targets a single location cluster with 2–5 entities and 2–3 hard constraints.
This is sufficient to test the core hypothesis end-to-end.
[Paper:Story2Game2025] [Paper:ElBoudouri2025] Full-world scope is out of scope for the initial prototype."

---

## CORE HYPOTHESIS

A natural language (NL) to Domain Specific Language (DSL) pipeline can be constructed such that:

1. A human provides NL worldbuilding input via a meta-questionnaire
2. This is translated into a WorldDSL artifact (machine-readable, deterministic)
3. The WorldDSL artifact is used to generate structured outputs (prompts, guardrails, context injections) targeting LLM RP systems
4. These outputs enforce world-specific rules deterministically, constraining the LLM without eliminating creative latitude
5. The result is significantly reduced narrative drift, decoherence, and hallucination across long and multi-session RP

**Epistemic status of the hypothesis as a whole:** [Inferred] The motivation is [Verified], the problem is [Verified], prior related architectures exist [Verified], but the specific pipeline connecting them has not been validated against literature or a working prototype.

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
  [Paper:Story2Game2025] [Paper:ElBoudouri2025]
  Scale is not the binding variable for prototype scope.
  The "one town, dozen characters" framing in earlier drafts is 5–10x larger than minimum viable.

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
  [Paper:GDL2005] — citation pending full verification.

- `[Verified]` The core mechanism of this project is not to make the LLM reason.
  The symbolic layer (WorldDSL rules engine) performs inference.
  LLM output is constrained to be consistent with that inference.
  Inference-level behavior emerges from the combined system, not from the LLM alone.
  The LLM contributes fluency and creativity; the symbolic layer contributes correctness and consistency.
  The WorldDSL also functions as the authoritative context that directs LLM extrapolation toward correct outputs — the LLM extrapolates fluently from the DSL rather than reasoning from it.
  [Paper:Madabushi2025]

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

- `[Inferred]` Minimum viable representational scope requires four functional categories: (1) entity registry, (2) static properties, (3) mutable state, (4) at least one inter-entity constraint.
  The fourth category is the minimum structure that makes the consistency problem non-trivial and worth a DSL at all.
  Without it, the system is only testing single-entity fact recall, not  relational consistency.
  Dependent on OQ-01 for implementation form.

- `[Inferred]` The closed-world assumption in Datalog and Prolog (anything not explicitly stated is false) is an advantage over OWL for closed game-state enforcement — but also a liability for open-ended RP worlds where the specification is inherently incomplete.
  At the edges of the spec, the system will treat unstated facts as false, which may produce incorrect constraint violations.
  This tradeoff requires explicit design handling and is not
  resolved by choosing Datalog alone.

- `[Inferred]` Codified Profiles (Python `parse_by_scene(scene)` functions with `if-then-else` logic and a `check_condition` LLM callable) solve the per-entity behavioral consistency problem — enforcing that a character acts according to their defined rules.
  They do NOT solve the inter-entity relational constraint problem (OQ-05a requirement 4).
  The `check_condition` callable is an LLM query, not a deterministic verifier — enforcement of context-sensitive conditions remains probabilistic.
  Codified Profiles are a viable component of the prototype architecture, not a complete solution.

---

## OPEN QUESTIONS (UNRESOLVED — REQUIRE RESEARCH)

These are the most important parts of this document.

**OQ-01 — DSL Formalism** What is the correct knowledge representation formalism? 
Candidates: JSON/YAML (data only), Logic programs (Prolog/Datalog), Answer Set Programming (ASP/Clingo), Ontology (OWL/RDF), or hybrid.
Each has different trade-offs for inference, contradiction detection, temporal state, LLM compatibility, and solo developer tractability. 
_This choice determines everything downstream._

**OQ-02 — Stateful Session Layer** How is world state maintained, validated, and queried across sessions? Three documented approaches: context injection, RAG retrieval, symbolic state tracking.
None fully solves the problem.
Likely requires a hybrid.
Who or what performs state transitions (human, LLM, automated)?

**OQ-03 — Verification and Error Correction Loop** How does the system catch and correct NL→DSL translation errors, especially the silent semantic kind? 
What role does the human play vs. automated tooling?
Is a consistency checker (ASP solver, OWL reasoner) feasible for a solo developer? 
DSL-Xpert 2.0 reportedly has automatic error-fixing — needs verification.

**OQ-04 — Undefined Case Handling / Extrapolation** What does the system do when a user prompt addresses a situation not specified in the WorldDSL? 
Refusal, hallucination, and unconstrained extrapolation are all unacceptable.
A constrained extrapolation mechanism that surfaces proposed rules for human approval is [Inferred] as the right approach — not yet validated.

**OQ-05 — Prototype Scope**
Decomposed into two sub-questions with different resolution status:

OQ-05b (PROVISIONALLY RESOLVED): Scale threshold.
The hypothesis is testable at minimal scale — 2–5 entities, one location cluster, a handful of constraints.
A single tavern with 3–4 characters and 2–3 hard constraints would be sufficient to test the pipeline end-to-end.
Scaling up adds breadth of coverage but does not add testability of the core hypothesis.
[Paper:Story2Game2025] [Paper:ElBoudouri2025]

OQ-05a (OPEN PENDING OQ-01): Representational scope.
What *categories* of world fact does the WorldDSL need to encode? 
Four functional categories identified [Inferred] but implementation form is blocked on OQ-01 (DSL formalism).
See Synthesized section for current best hypothesis.

**OQ-06 — Developer Toolset Fit** What is the actual implementation barrier for each formalism candidate for a solo non-professional developer? 
ASP, OWL, and JSON+rules have radically different learning curves and tooling ecosystems.

**OQ-07 — Meta-Questionnaire Design** What makes a questionnaire both comprehensive and self-consistent? 
How are co-evolution and self-reference implemented structurally?
Is there prior work on structured worldbuilding elicitation in literature?

**OQ-08 — LLM Output Enforcement Mechanism** Given a WorldDSL, what is the most effective mechanism for enforcing it at inference time?
Options: system prompt injection, Colang guardrails, RAG grounding, structured output constraints, or combination.
What does the literature say about effectiveness of each?

**OQ-09 — Prototype Evaluation Protocol**
How do we determine whether the prototype achieved zero-decoherence (or meaningfully improved on baseline) in a falsifiable way?
Specifically: What constitutes a constraint violation in measurable terms? Who or what detects it — human review, a judge LLM, automated symbolic checker? 
What is the baseline being compared against (raw LLM with system prompt vs. LLM with no grounding)?
Without an answer to this question, the prototype produces an output but not a result.
A working RP session is not a test of the hypothesis.
Minimum viable path: a predefined set of constraint-violation test cases administered manually against prototype output, compared against a no-DSL baseline.
Establishes falsifiability without requiring automated evaluation infrastructure.
Dependencies: OQ-05a (what constraints exist to be violated), OQ-01 (whether the symbolic layer can itself generate violation reports).

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
- [ ] Confirm full citation and URL for [Paper:Peng2025] Codified Profiles (NeurIPS 2025)
- [ ] Confirm full citation and URL for [Paper:GDL2005] Game Description Language
- [ ] Verify current maintenance status of pyDatalog library before it can be considered a viable Option B formalism

---

## RESEARCH PROTOCOLS

### Citation Format

Every factual claim uses inline citation: `[Tag:ShortID]`
Tags (exactly these, no others): `Paper` | `Repo` | `Doc` | `Blog` | `Forum` | `Social` | `Video`
ShortID format: `AuthorYYYY` (e.g., `[Paper:Zhang2024]`)
Full citations are logged in the Research Log with URL and access date.

### Research Log Entry Format

```
[Tag:ShortID] Author(s), "Title," Source/Venue, Year.
URL: [url]
Status: Verified | Partially verified | Needs re-check
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

_Populated as findings are verified.
Empty until first commit._

### Session 1 (March 2026) — Foundational Research

[Paper:Gupta2025] Aakash Gupta, "I Studied 1,500 Academic Papers on Prompt Engineering," Medium/personal, 2025.
URL: https://aakashgupta.medium.com/i-studied-1-500-academic-papers-on-prompt-engineering 
Status: Verified
Notes: Structure > length; role prompting ineffective for correctness; context massively underrated.

[Paper:Chen2025] Chen et al., "When helpfulness backfires," npj Digital Medicine, 2025.
URL: https://www.nature.com/articles/s41746-025-02008-z 
Status: Verified
Notes: Up to 100% compliance with illogical requests in sycophancy study.

[Paper:Sharma2023] Anthropic, "Towards Understanding Sycophancy in Language Models," 2023.
URL: https://www.anthropic.com/research/towards-understanding-sycophancy-in-language-models
Status: Verified
Notes: RLHF mechanism for sycophancy; preference models favor agreement.

[Doc:AnthropicPrompting] Anthropic, "Prompt Engineering Best Practices," 2025.
URL: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering
Status: Verified
Notes: XML tags recommended for mixed-content prompts; rationale-with- instructions improves adherence.

[Paper:Marra2024] Marra et al., "From Statistical Relational to Neurosymbolic AI: A Survey," Artificial Intelligence, 2024.
URL: https://www.sciencedirect.com/science/article/pii/S0004370223002084
Status: Verified
Notes: Hybrid NeSy approach more promising than integrative for general logical reasoning.

[Paper:Chen2025b] M.K.
Chen et al., "A Comparative Study of Neurosymbolic Approaches," NeSy Conference, 2025.
URL: https://www.arxiv.org/pdf/2508.03366
Status: Verified
Notes: Hybrid approach retains LLM capabilities while improving interpretability.

[Paper:Wang2024] Wang et al., "DSPy-ASP Framework," 2024.
URL: cited in neurosymbolic ASP survey
Status: Verified (via secondary source)
Notes: LLM + ASP with iterative solver feedback; up to 50% accuracy improvement.

[Paper:Score2025] SCORE Framework, arXiv, 2025.
URL: https://arxiv.org/html/2503.23512v1
Status: Verified
Notes: RAG-based narrative coherence; 41.8% fewer hallucinations vs. baseline.
Demonstrates RAG as partial mitigation, not solution, for stateful consistency.

### Session 2 (March 2026) — Prototype Scope Research

[S2-E1] OQ-05 decomposition into 05a/05b | Resolved (05b), Open (05a) | [Paper:Story2Game2025] [Paper:ElBoudouri2025] 
[S2-E2] OQ-09 (Evaluation Protocol) added as new open question | Open | None 
[S2-E3] PROJECT GOAL scope text conflict identified and corrected | Resolved | None

[Paper:Story2Game2025] (authors not named in abstract), "Story2Game: Generating (Almost) Everything in an Interactive Fiction Game, "arXiv:2505.03547v1, 2025.
URL: https://arxiv.org/html/2505.03547v1
Status: Verified
Notes: Defines minimal IF world model as locations, objects, NPCs, player agent; demonstrates consistency failures appear even at minimal scale.
Prior sentence identifies failure mode: players able to "fly without prior indication" or "kill characters" outside world logic.

[Paper:ElBoudouri2025] Yassine El Boudouri et al., "RPEval: A Benchmark for Role-Playing LLMs," arXiv:2505.13157v1, 2025.
URL: https://arxiv.org/pdf/2505.13157
Status: Verified
Notes: Frontier models score 5.81–62.24% on in-character consistency against character profiles.
Directionally supports claim that drift is structural, not scale-dependent.
Does NOT directly measure consistency against formal constraint specifications — that gap is noted.
[Inferred] extrapolation to this project's decoherence problem is reasonable but unverified.

### Session 3 (March 2026) — OQ-01 Formalism Research

[S3-E1] Grammars disqualified as constraint mechanism | Resolved | [Verified from EBNF/grammar literature]
[S3-E2] OWL disqualified on open-world assumption grounds | Resolved | [Verified from W3C OWL documentation]
[S3-E3] GDL identified as closest WorldDSL precedent | Verified — citation pending | [Paper:GDL2005]
[S3-E4] Codified Profiles evaluated — partial fit, not complete solution | Resolved | [Paper:Peng2025]
[S3-E5] Closed-world assumption tradeoff for Datalog identified | Open — design decision required | None
[S3-E6] Three viable prototype formalism candidates identified: Hybrid JSON+ASP, Datalog (pyDatalog), Executable Python rules | Open — pending tractability judgment | See OQ-01

[Paper:Peng2025] Libiao Peng et al., "Codified Profiles for Character Role-Playing," NeurIPS 2025 (poster).
URL: [pending — confirm from arXiv or NeurIPS proceedings]
Status: Verified (peer-reviewed, NeurIPS 2025)
Notes: Per-entity behavioral consistency via executable Python scene-parsing functions.
Improves consistency, adaptability, and diversity especially for smaller LLMs.
Does not address inter-entity relational constraints or session state — the check_condition callable is probabilistic (LLM query), not deterministic.

[Paper:GDL2005] Michael Genesereth et al., "General Game Playing: Overview of the AAAI Competition," AI Magazine, 2005.
URL: [pending verification]
Status: Partially verified — needs URL and page confirmation
Notes: Defines Game Description Language as a Datalog variant with static and dynamic facts and state transition functions.
Closest documented precedent to WorldDSL semantics.
Validates that the required formalism is expressible in Datalog.

[Paper:Madabushi2025] Harish Tayyar Madabushi et al., "Neither Stochastic
Parroting nor AGI: LLMs Solve Tasks through Context-Directed Extrapolation
from Training Data Priors," arXiv:2505.23323v1, University of Bath, 2025.
URL: https://arxiv.org/html/2505.23323v1
Status: Verified
Notes: Characterizes LLM behavior as context-directed extrapolation from
training priors, not advanced reasoning. Explicitly recommends augmenting
techniques that do not rely on inherent LLM reasoning. Directly supports
the hybrid NeSy approach and the project's core mechanism clarification.

---

_Document version: 1.0 — March 2026_ _Next review trigger: OQ-01 (DSL Formalism) research complete_