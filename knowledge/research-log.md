# research-log.md

## Semantics-Driven Worldbuilding DSL Project
Research Log — Append-Only Historical Record

---

## RESOLVED OQ ARCHIVE

_Resolved OQ entries are migrated here during audits._
_Populated as OQs are resolved and migrated during audits._

### OQ-01 — DSL Formalism [RESOLVED — S04]

Selected formalism: Hybrid JSON + ASP (Clingo).
Decisive factors:
(1) LLM→ASP translation precedent exists — LLMASP, DSPy-ASP, [Paper:Hite2025], [Paper:PJWang2024] future work.
(2) ASP is documented in applied narrative constraint enforcement and LLM narrative plan verification — [Paper:PJWang2024], [Paper:YiWang2025].
(3) ASP is tractable for solo non-professional developers — see OQ-06.

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

### OQ-02 — Stateful Session Layer [RESOLVED — S05]

Decomposed into four sub-questions.
All resolved or decided.

**OQ-02a — Storage** [DECIDED — prototype scope]
JSON file.
Human-readable, diff-able, trivially editable for manual corrections.
No research question at prototype scope.

**OQ-02b — State Transitions** [RESOLVED — S05]
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

### OQ-05b — Scale Threshold [RESOLVED — S02]

The hypothesis is testable at minimal scale — 2–5 entities, one location cluster, a handful of constraints.
A single tavern with 3–4 characters and 2–3 hard constraints would be sufficient to test the pipeline end-to-end.
Scaling up adds breadth of coverage but does not add testability of the core hypothesis.
[Paper:Zhou2025] [Paper:ElBoudouri2025]

Note: Initially marked [PROVISIONALLY RESOLVED] at S02.
Promoted to [RESOLVED] at S09 audit — no contradicting evidence found in Sessions 3–8; WHAT IS VERIFIED carries the same claim as [Verified] with the same sources.

### OQ-05a — Representational Scope [RESOLVED — S06]

DEPENDS ON: OQ-01 [RESOLVED] — categories must be expressed in the chosen formalism; cannot be designed without knowing the formalism.
DEPENDS ON: OQ-02b [RESOLVED] — mutable state category cannot be finalized without knowing how state transitions work.
BLOCKS: OQ-09 [UNBLOCKED — S06]

The WorldDSL requires four functional categories:
(1) Entity registry — what named entities exist; encoded as ground ASP facts.
(2) Static properties — facts that never change during play, including spatial topology; encoded as ground ASP facts without transition rules.
(3) Mutable state — facts that change via committed ABox deltas, including character location and inventory; encoded as ABox JSON loaded as ground ASP facts at session start.
(4) Integrity constraints — rules encoding both state consistency ("dead cannot act") and transition validity ("can only move to adjacent room"); encoded as ASP integrity constraints (:- body form).
[Doc:WikipediaGDL] [Doc:ThielschemGDLII] [Paper:Zhou2025]

All four map to documented ASP/Clingo constructs.
Epistemic state, full temporal logic, and goal/terminal encoding are confirmed out-of-scope for prototype.
The ABox-snapshot validation pattern (not fluent-with-time-steps) is appropriate for this project's validation-not-planning use case.
[Verified] — by GDL mapping —
[Inferred] — for RP application —

### OQ-06 — Developer Toolset Fit [RESOLVED — S04]

ASP/Clingo is tractable for a solo non-professional developer.
Evidence: Potassco Getting Started guide (genuinely novice-oriented, pip install clingo, no JVM required) [Doc:PotasscoStart]; CMU CSC 791 course notes on ASP for game design (Martens, 2017), using dungeon generation as motivating example [Doc:CMUMartens2017]; solo hobbyist project modeling social deduction game rules as Clingo constraints with sat/unsat test suite [Repo:botcasp].
IDP-Z3 has no equivalent hobbyist community, game design adoption, or solo project precedent.
[Verified]

### OQ-08 — LLM Output Enforcement Mechanism [RESOLVED — S08]

DEPENDS ON: OQ-01 [RESOLVED]
DEPENDS ON: OQ-05a [RESOLVED]
BLOCKS: OQ-09 [UNBLOCKED — S08]

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

What remained [Unverified] at S08: whether per-turn injection is sufficient to keep LLM extrapolation within constraint boundaries at interactive RP pace.
This was the load-bearing empirical claim of Step 4 of the core hypothesis, delegated to OQ-09.
Confirmed [Verified] at prototype scope — OQ-09 [RESOLVED — S13]: CVR_A=1.000 → CVR_C=0.000.
See empirical closure note below.
Empirical closure: S13. CVR_A=1.000 → CVR_C=0.000; NQS threshold met; directionality floor result documented.
→ [S13 — OQ-09 Empirical Result](research-log.md#s13--oq-09-empirical-result)


### OQ-09 — Prototype Evaluation Protocol [RESOLVED — S10 (protocol) / RESOLVED — S13 (empirical)]

DEPENDS ON: OQ-05a [RESOLVED] — four constraint categories confirmed; test cases can now be specified.
DEPENDS ON: OQ-08 [RESOLVED] — enforcement mechanism specified as per-turn symbolic state injection plus reactive ASP validation; evaluation must test whether this mechanism is sufficient.
DEPENDS ON: OQ-01 [RESOLVED] — ASP generates named UNSAT violation reports; this capability is the primary evaluation oracle.

The claim under test:
Per-turn symbolic state injection plus reactive ASP validation is sufficient to keep LLM extrapolation within constraint boundaries at interactive RP pace.

---

Evaluation design: three-condition ablation study.

Condition A — Raw LLM.
No DSL, no system prompt, no world state injection.
LLM generates narrative from a brief scenario description only.
Purpose: establishes natural violation rate; characterizes the problem VeriForge addresses.

Condition B — System-prompt-only injection.
Full WorldDSL state injected once at session start in the system prompt.
No per-turn re-injection.
Reactive ASP validation still runs (ABox delta checking).
Purpose: isolates the specific contribution of per-turn re-injection from symbolic grounding generally.
This condition is required by protocols.md Rival Hypothesis Discipline to avoid conflating "symbolic grounding helps" with "per-turn re-injection specifically helps."

Condition C — VeriForge.
Per-turn symbolic state injection (ASP-derived constraints and current ABox prepended to each generation call) plus reactive ASP validation.
The full OQ-08 mechanism.

---

Primary metric: Constraint Violation Rate (CVR).
CVR = (human-detected constraint violations in surface text) / (total turns) × 100.
Adapted from Consistency Error Density [Paper:Li2026] — CED normalizes errors by document length; CVR uses session turns as the denominator for interactive RP applicability.

Secondary metric: Violation Detection Rate (VDR).
VDR = (violations caught by ASP before committing) / (total violations detected in surface text) × 100.
Measures the surface-text leak gap: whether the ASP gate catches violations that appear in narrative prose without triggering an ABox delta.
[Unverified] — pre-registered design decision; no literature precedent for this metric in interactive NeSy RP evaluation.

Tertiary metric: False Positive Rate.
Frequency of ASP flagging SAT deltas incorrectly.
A tractability concern, not a correctness concern — relevant to interactive pace.

Evaluator: human review is primary for surface-text violations.
ASP solver is primary for ABox delta violations.
LLM-as-judge is acceptable as a secondary cross-check on human review only.
Rationale: violations targeted by VeriForge are formal constraint violations derivable from the WorldDSL specification; the ASP solver is unambiguously more reliable for these than a judge LLM. [Inferred] — methodological analog from [Paper:Mu2023] programmatic evaluation functions.

---

Falsification criteria (all must hold for the claim to be supported):

(1) Condition C CVR ≤ 25% of Condition A CVR (≥75% reduction from ungrounded baseline)
    [Unverified] — pre-registered design decision; no literature precedent for this threshold in interactive NeSy RP evaluation.

(2) Condition C CVR is statistically lower than Condition B CVR (per-turn re-injection specifically contributes beyond session-start injection)

(3) VDR ≥ 80%
    [Unverified] — pre-registered design decision; no literature precedent for this threshold in interactive NeSy RP evaluation.

The claim is falsified if any one of the three fails.

Additional interpretive condition:
If (2) holds but (3) fails — Condition C significantly outperforms both baselines, but VDR is below 80% — the correct interpretation is: the per-turn injection mechanism is working, but the architecture has a structural surface-text leak.
The symbolic layer correctly validates deltas but does not prevent constraint violations from appearing in narrative prose before a delta is proposed.
This would constitute a partial validation with a known architectural gap, not a clean falsification.

---

Test battery:

Minimum 12 test cases. [Inferred] — judgment call; no published precedent for this number in interactive NeSy RP evaluation.
4 cases targeting Type A integrity constraints (state consistency: "a dead entity cannot act").
4 cases targeting Type B integrity constraints (transition validity: "can only move to an adjacent room").
4 cases targeting compound constraints spanning both types.
Each test case is a scripted 5–10 turn prompt sequence designed to elicit the constraint violation if the mechanism fails.
Test cases must be pre-registered and fixed before running any condition.
Minimum 3 runs per condition per test case; CVR averaged across runs to reduce LLM non-determinism. [Inferred] — from standard evaluation practice.
LLM fixed across all conditions; frontier model (Claude 3.5+ or GPT-4o-class) appropriate for target deployment scenario.

---

Rival hypothesis:
Condition B (session-start injection) is sufficient; per-turn re-injection adds no measurable benefit over a 5–10 turn RP session at prototype scope.
This is structurally what the evaluation design tests.
If Conditions B and C produce indistinguishable CVRs, the correct interpretation is that session-start injection is sufficient at prototype scope — a valid finding, not a failure.
The rival hypothesis was pre-rejected in OQ-08 based on Li2024 drift evidence within 8 turns, but that evidence was measured on older models.
OQ-09 is partly a test of whether that concern is empirically significant at the scale and with the models actually used.

---

Remaining gaps (not blocking resolution; relevant to implementation):

Gap 1 — Surface-text leak (see CLAIMS in vision.md):
Reactive ASP validation of ABox deltas may not catch constraint violations that appear in LLM surface narrative without triggering a delta.
VDR metric is designed to measure this; the vulnerability is [Inferred] pending empirical test.

Gap 2 — OQ-08-T2 (two-step action declaration):
Prospective enforcement requires the LLM to declare actions as structured output before narrating.
Not required at prototype scope; reactive enforcement is the tested mechanism.
Hold for post-prototype.

Sources:
[Paper:Mu2023] — programmatic evaluation function pattern; ASP-as-oracle validation.
[Paper:Qi2025] — three-paradigm constraint evaluation; code-verification tier precedent.
[Paper:Li2026] — CED metric; confirms measurement gap for formal symbolic constraint evaluation in interactive RP.
[Paper:Li2024] — attention decay evidence motivating per-turn over session-start injection.
[Paper:Laban2025] — multi-turn degradation baseline confirming Condition A expected behavior.

---

## AUDIT LOG

_Audit records are appended here after each audit closes._
_Populated as audits are completed._

[AUDIT-S09-OQ-01] OQ-01 resolved | March 9, 2026 | Steps completed: 1, 2, 3, 4
Issues found:
  - [Paper:Wang2024] secondary-source flag unresolved → noted as independent outstanding item → Methodology patch recommended: no
Methodology patches flagged: no
Audit closed: yes

[AUDIT-S09-OQ-02] OQ-02 resolved | March 9, 2026 | Steps completed: 1, 2, 3, 4
Issues found: none
Methodology patches flagged: no
Audit closed: yes

[AUDIT-S09-OQ-05b] OQ-05b resolved | March 9, 2026 | Steps completed: 1, 2, 3, 4
Issues found:
  - Status [PROVISIONALLY RESOLVED] promoted to [RESOLVED — S02] — WHAT IS VERIFIED carries same claim as [Verified]; no contradicting evidence in S03–S08 → corrected before migration → Methodology patch recommended: no
Methodology patches flagged: no
Audit closed: yes

[AUDIT-S09-OQ-05a] OQ-05a resolved | March 9, 2026 | Steps completed: 1, 2, 3, 4
Issues found:
  - Status token [RESOLVED — Session 6] corrected to [RESOLVED — S06] → applied before migration → Methodology patch recommended: no
  - Inline citations missing from OQ-05a body → [Doc:WikipediaGDL] [Doc:ThielschemGDLII] [Paper:Zhou2025] added before migration → Methodology patch recommended: no
  - OQ-05 parent preamble stale ("different resolution status") → updated to "both resolved" in Step 3c → Methodology patch recommended: no
Methodology patches flagged: no
Audit closed: yes

[AUDIT-S09-OQ-06] OQ-06 resolved | March 9, 2026 | Steps completed: 1, 2, 3, 4
Issues found:
  - Status token [RESOLVED] missing session number → corrected to [RESOLVED — S04] before migration → Methodology patch recommended: no
Methodology patches flagged: no
Audit closed: yes

[AUDIT-S09-OQ-08] OQ-08 resolved | March 9, 2026 | Steps completed: 1, 2, 3, 4
Issues found:
  - Status token [RESOLVED — Session 8] corrected to [RESOLVED — S08] → applied before migration → Methodology patch recommended: no
  - DEPENDS ON two dependencies on one line → split to one per line → applied before migration → Methodology patch recommended: no
  - BLOCKS language [NOW UNBLOCKED] → corrected to [UNBLOCKED — S08] → applied before migration → Methodology patch recommended: no
Methodology patches flagged: no
Audit closed: yes

[NOTE-S10-OQ-09] OQ-09 resolved — no audit triggered; OQ-09 unblocks no downstream OQs; research phase complete as of S10.

[AUDIT-ANKYRA-03] Prototype milestone audit | March 2026 | Steps completed: 1, 2, 3, 4, 5, 6
Issues found:
  - [research-log.md] OQ-09-T1 section header stale → appended [RESOLVED — S12] to header → Methodology patch recommended: no
  - [vision.md] OQ-09-T1 status token [OPEN] → updated to [RESOLVED — S12] with disposition summary → Methodology patch recommended: no
  - [implementation-log.md] I05 section header [IN PROGRESS] → corrected to [RESOLVED] → Methodology patch recommended: no
  - [implementation-log.md] IMP-I05-T01 [THREAD] missing Resolution field → added in-place → Methodology patch recommended: no
  - [implementation-log.md] I05 missing required [CLEAN] entry → added → Methodology patch recommended: no
  - [vision.md] OQ-09 body not migrated — no audit trigger fired at S10 or S13 because OQ-09 blocked no downstream OQs; Step 3c migration skipped by design → migrated to cross-reference line per Step 3c → Methodology patch recommended: yes — see below
  - [vision.md] NQS Protocol Addendum orphaned after OQ-09 migration → deleted → Methodology patch recommended: no
  - [vision.md] CORE HYPOTHESIS epistemic block: three stale elements — "not validated against a working prototype"; [Unverified] on Step 4 claim; forward pointer to OQ-09 as open → epistemic markers promoted per Step 4f; stale language removed → Methodology patch recommended: no
  - [vision.md] WHAT IS SYNTHESIZED: three [Inferred] claims with stale OQ-09 forward pointers; two requiring Step 4f epistemic promotion → markers updated; stale phrases removed → Methodology patch recommended: no
  - [vision.md] OQ-08 cross-reference trailing clause forward-pointed to OQ-09 as open → updated to reflect empirical confirmation → Methodology patch recommended: no
  - [vision.md] OQ-03 BLOCKS pointer referenced OQ-09 → updated to reference Phase 5 scope → Methodology patch recommended: no
  - [vision.md] EVALUATION METHODOLOGY NOTE: conditional "if falsification criteria are met" stale → updated to past tense with OQ-09 resolution citation → Methodology patch recommended: no
  - [vision.md] CLAIMS VDR item marked [Inferred] / not yet tested → partially closed with S13 VDR=1.000 finding and role boundary scope qualification → Methodology patch recommended: no
  - [vision.md] CLAIMS two items with stale Influences: OQ-09 → updated to Phase 5 / post-prototype scope → Methodology patch recommended: no
Methodology patches flagged: yes
  Migration gap: Step 3c migration is currently gated on the Audit Trigger Protocol, which fires only when an OQ resolution unblocks a downstream OQ.
  An OQ that resolves without unblocking anything — as OQ-09 did at both S10 and S13 — never triggers the audit and therefore never triggers Step 3c migration, leaving the resolved body in vision.md indefinitely.
  Proposed fix: Ankyra Chats execute a standing migration check at load time — scan vision.md for any resolved OQ whose body has not yet been migrated to a cross-reference line, and execute Step 3c for each before any other work. Patch applied to protocols.md in this commit.
Audit closed: yes

---

## CLOSED VERIFICATION ITEMS

Items migrated from CLAIMS REQUIRING TARGETED VERIFICATION in vision.md upon resolution.
Format: origin session, resolution finding, OQs influenced.

[CVI-01] Confirm full citation and URL for [Paper:Peng2025] Codified Profiles (NeurIPS 2025)
Status: CLOSED — S03 | 20260306
Resolution: Confirmed — Letian Peng and Jingbo Shang, NeurIPS 2025, https://arxiv.org/abs/2505.07705
Influences: OQ-01, OQ-05a

[CVI-02] Confirm full citation and URL for [Paper:GDL2005] Game Description Language
Status: CLOSED — S03 | 20260306
Resolution: Confirmed — Genesereth, Love et al., AAAI 2005, https://www.semanticscholar.org/paper/General-Game-Playing:-Overview-of-the-AAAI-Genesereth-Love/c89c71dbe5617bea44383585b58cd0cbc37bf79a
Influences: OQ-01, OQ-05a

[CVI-03] Verify current maintenance status of pyDatalog library
Status: CLOSED — S03 | 20260306
Resolution: Disqualified — unmaintained since November 2022; maintainer redirects to IDP-Z3
Influences: OQ-01

[CVI-04] Is the flag-then-commit state mechanism implemented in any published system?
Status: CLOSED — S05 (absence finding)
Resolution: NOT FOUND [Verified] — search across RPGBench, CFSM, Story2Game literature; no published system implements human-gated state commit in interactive narrative; all published systems use fully automated state updates
Influences: OQ-02

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

### S09 — OQ Migration Audit & Document Hygiene

[S9-E1] OQ-01 migration audit — formatting corrections; [Paper:Wang2024] secondary-source flag noted as outstanding item | Resolved | None
[S9-E2] OQ-02 migration audit — no issues found | Resolved | None
[S9-E3] OQ-05b migration audit — status promoted from [PROVISIONALLY RESOLVED] to [RESOLVED — S02] | Resolved | None
[S9-E4] OQ-05a migration audit — session token corrected; inline citations added; OQ-05 parent preamble updated | Resolved | None
[S9-E5] OQ-06 migration audit — session token corrected from [RESOLVED] to [RESOLVED — S04] | Resolved | None
[S9-E6] OQ-08 migration audit — session token corrected; DEPENDS ON split to one-per-line; BLOCKS language corrected | Resolved | None
[S9-E7] Document hygiene pass — version bumped to v0.9; CLAIMS section restructured with provenance tags; four OQ cross-reference links added to WHAT IS VERIFIED/SYNTHESIZED; stale OQ-08 pointer corrected; flag-then-commit absence finding closed | Resolved | None
[S9-E8] Context management methodology reviewed (compaction, context hygiene, claudelog.com); research partner named Ankyra | Note | None

### S10 — OQ-09 — Evaluation Protocol

[S10-E1] OQ-09 resolved — three-condition ablation protocol designed; CVR/VDR metrics specified; falsification criteria pre-registered | Resolved | [Paper:Mu2023] [Paper:Qi2025] [Paper:Li2026]
[S10-E2] Surface-text leak gap identified as [Inferred] architectural vulnerability; added to CLAIMS for empirical testing | New CLAIMS entry | None
[S10-E3] Three citation corrections applied per QA pass: VDR threshold epistemic flag, CED denominator distinction, surface-text leak reclassified as architectural finding | Resolved | None

[Paper:Mu2023] Norman Mu, Sarah Chen, Zifan Wang, Sizhe Chen, David Karamardian, Lulwa Aljeraisy, Basel Alomair, Dan Hendrycks, David Wagner, "Can LLMs Follow Simple Rules?" arXiv:2311.04235v3, UC Berkeley / Center for AI Safety, 2023.
URL: https://arxiv.org/abs/2311.04235
Status: [Verified]
Notes: Proposes RuLES — programmatic evaluation functions per scenario to determine rule violations without manual review or unreliable heuristics.
Directly validates the use of the ASP solver as a deterministic evaluation oracle for OQ-09 CVR measurement.

[Paper:Qi2025] Yunjia Qi, Hao Peng, Xiaozhi Wang, Amy Xin, Youfeng Liu, Bin Xu, Lei Hou, Juanzi Li, "AGENTIF: Benchmarking Instruction Following of Large Language Models in Agentic Scenarios," Tsinghua University / Zhipu AI, arXiv:2505.16944v1, 2025.
URL: https://arxiv.org/abs/2505.16944
Status: [Verified]
Notes: Three-paradigm constraint evaluation: code verification (Python), LLM verification (judge model), hybrid.
Code verification preferred for structural constraints; LLM verification reserved for constraints requiring semantic understanding.
Provides methodological precedent for OQ-09 two-tier evaluation design (ASP as code-verification tier; human/LLM judge for surface-text violations).

[Paper:Li2026] Junjie Li, Xinrui Guo, Yuhao Wu, Roy Ka-Wei Lee, Hongzhi Li, Yutao Xie, "Lost in Stories: Consistency Bugs in Long Story Generation by LLMs," Microsoft / Singapore University of Technology and Design, arXiv:2603.05890v1, 2026.
URL: https://arxiv.org/abs/2603.05890
Status: [Verified]
Notes: Introduces ConStory-Bench — 2,000 prompts, five-dimension error taxonomy, 19 fine-grained subtypes, ConStory-Checker automated pipeline.
Standardized metrics: Consistency Error Density (CED, errors per document length) and Group Relative Rank (GRR).
Targets long-form autonomous generation, not interactive RP with formal constraints; CED normalizes by document length, not session turns — VeriForge CVR adapts the principle with session turns as the denominator.
Confirms the measurement gap: no published framework measures constraint-specification violation rates against formal symbolic constraints in interactive RP.

---

### Ankyra-00 — RAG Rival Hypothesis Research (pre-S11)

### OQ-09-T1 — RAG Baseline as Untested Rival [OPEN — Ankyra-00] [RESOLVED — S12]

[AnkyraNote-00-T1] OQ-09-T1 — RAG baseline as untested rival identified and formalized | Ankyra-00 review | [Paper:RoleRAG2025] [Paper:IDRAG2025] [Paper:TRPGRAG2025] [Paper:GSW2025]

RAG is a credible rival for persona/fact-recall consistency but not for hard closed-world relational constraint enforcement (Type A / Type B integrity constraints).
The OQ-09 ablation does not include a RAG baseline condition.
OQ-09-T1 captures this as a named open thread requiring disposition before prototype evaluation begins.

NQS addendum: A secondary human-evaluated Narrative Quality Score metric has been added to the OQ-09 protocol to guard against the CVR=0/unusable output failure mode.
This does not reopen OQ-09.

[Paper:RoleRAG2025] Yongjie Wang, Jonathan Leung, Zhiqi Shen, "RoleRAG: Enhancing LLM Role-Playing via Graph Guided Retrieval," Nanyang Technological University, arXiv:2505.18541, May 2025.
URL: https://arxiv.org/abs/2505.18541
Status: [Verified]
Notes: Graph-guided RAG for character-aligned RP; uses entity disambiguation and boundary-aware retrieval from structured knowledge graph; addresses persona/fact-recall consistency, not hard relational constraint enforcement.
Cited as evidence that RAG is a credible rival in OQ-09-T1.

[Paper:IDRAG2025] Daniel Platnick, Mohamed E. Bengueddache, Marjan Alirezaie, Dava J. Newman, Alex Pentland, Hossein Rahnama, "ID-RAG: Identity Retrieval-Augmented Generation for Long-Horizon Persona Coherence in Generative Agents," arXiv:2509.25299, September 2025.
URL: https://arxiv.org/abs/2509.25299
Status: [Verified]
Notes: Identity knowledge-graph grounding for long-horizon persona coherence; outperforms baselines on identity recall in social simulation; targets persona consistency, not closed-world relational inference.
Cited as evidence that RAG is a credible rival in OQ-09-T1.

[Paper:TRPGRAG2025] Gabriel Rudan Sales Matos, José Wellington Franco da Silva, Artur de Oliveira da Rocha Franco, José Gilvan Rodrigues Maia, José Antônio Fernandes de Macêdo, "Creating Tabletop RPG Dialogues via Retrieval-Augmented Generation," SBGames 2025 (XXIV Brazilian Symposium on Games and Digital Entertainment), Universidade Federal do Ceará, 2025.
URL: https://sol.sbc.org.br/index.php/sbgames/article/download/37366/37148/
Status: [Verified] — precision metric figures confirmed against primary source; N=11 participants; evidentiary weight limited by small sample —
Notes: RAG outperforms standard LLM baselines on human-rated coherence, cohesion, creativity, and engagement in TTRPG dialogue generation (N=11).
Nearest published precedent for RAG in tabletop RP context.
Does not test hard relational constraint enforcement.
Cited as domain-adjacent precedent in OQ-09-T1; small sample limits weight of numeric claims.

[Paper:GSW2025] Shreyas Rajesh, Pavan Holur, Chenda Duan, David Chong, Vwani Roychowdhury, "Beyond Fact Retrieval: Episodic Memory for RAG with Generative Semantic Workspaces," arXiv:2511.07587, November 2025.
URL: https://arxiv.org/abs/2511.07587
Status: [Verified]
Notes: Neuro-inspired generative memory framework (GSW) for spatiotemporal entity tracking; explicitly notes that current RAG solutions fail to build space-time-anchored narrative representations for tracking entities through episodic events; outperforms structured RAG baselines on episodic memory benchmark. 
Cited as evidence of RAG's epistemic limitations in OQ-09-T1.

### S12 — OQ-09-T1 Formal Disposition

[S12-E1] OQ-09-T1 formal disposition: Condition D EXCLUDED — three-part justification completed and implementation infeasibility confirmed | Resolved | [Paper:RoleRAG2025] [Paper:IDRAG2025] [Paper:TRPGRAG2025] [Paper:GSW2025]

**OQ-09-T1 — RAG Baseline as Untested Rival [RESOLVED — S12]**

Disposition: CONDITION D EXCLUDED.

(1) Which failure modes in the test battery RAG could plausibly address.
The test battery targets Type A (state consistency) and Type B (transition validity) constraint pairs.
RAG could plausibly address attention-dilution failures on single-fact recall — forgetting that a character is dead because the state change has been displaced from active context.
However, this failure mode is already addressed by Condition C (per-turn full ABox re-injection), making a separate RAG condition redundant on its strongest ground.
Deeper Type A violations — where the LLM fails to apply the relational entailments of a known fact — require inference over the closed-world ABox, which retrieval alone cannot provide.
[Verified] — [Paper:RoleRAG2025], [Paper:IDRAG2025]

(2) Why symbolic inference is the correct comparison class for Type A and Type B constraints.
Type A constraints are ASP integrity constraints evaluated over the ABox as a whole; they are violated when any combination of committed state facts produces an inconsistency.
Retrieval of individual facts leaves relational entailment to the LLM, which is probabilistic — re-instantiating the problem the symbolic layer is designed to solve.
Type B constraints are transition precondition checks: computational operations over the state graph, not retrievable facts.
A RAG system routing the same inference problem through the LLM is a degraded version of Condition B, not a distinct experimental condition. It does not isolate symbolic inference as the operative variable.
[Verified] — structural, from OQ-05a; [Paper:GSW2025] confirms RAG fails to build space-time-anchored narrative representations needed for episodic entity tracking.

(3) Empirical conditions for overturning the exclusion.
A skeptic must demonstrate that a RAG system operating on the same corpus (ABox + WorldDSL) achieves CVR comparable to Condition C specifically on pre-registered Type A and Type B constraint pairs.
Human-rated coherence, engagement, or persona consistency measures are not sufficient — the bar is formal constraint satisfaction rate on structural constraints.
No published paper meets this bar as of March 2026.
[Verified — confirmed by absence finding across four RAG papers and S12 search pass]

Implementation path infeasibility (secondary, independently sufficient ground):
At prototype scope (single tavern, 3–4 characters, 2–3 hard constraints), the ABox fits entirely within context.
A RAG baseline would retrieve the full corpus on virtually every query, collapsing into an injection indistinguishable from Condition C.
Condition D cannot be implemented as a distinct experimental condition without artificially degrading RAG, which would test a straw-man rather than its best case.
The retrieval-vs.-full-context distinction is experimentally meaningful only at scale, which is explicitly out of prototype scope per OQ-05b [RESOLVED — S02].
[Inferred] — structural consequence of prototype scope constraints.

Epistemic status of exclusion: [Inferred] — the structural argument is logically sound and consistent with all four verified RAG papers, but the specific claim that RAG cannot match Condition C CVR on Type A/B constraints has not been directly tested.
The exclusion holds until a skeptic demonstrates otherwise under the stated empirical bar.

Phase 4 unblocked. Audit trigger does not fire (no downstream OQ unblocked).

### S13 — OQ-09 Empirical Closure

[S13-E1] IMP-I05-T01 disposed — tc-a03 stale-context drift characterized as (a) additional evidence for VeriForge hypothesis (per-turn injection prevents silent ABox divergence) and (b) scope qualifier on CVR directionality result (Condition B CVR=0 achieved via inaccurate world model, not correct state evolution); cross-modal corroboration from GPT-5.4 inter-rater tc-m04-C score | Resolved | run_20260318_150753_summary.json, interrater_summary.json

[S13-E2] OQ-09 formally closed — primary threshold met (100% CVR reduction A→C); NQS threshold met (C ≥ B marginally); directionality check not met (floor result — adversarial sufficiency limit named); VDR_A gap explained; tc-m04 non-finding recorded; inter-rater rubric comprehension gap named; constraint narration artifact named as post-prototype open thread (OQ-10); attempt-vs.-success rubric ambiguity noted | Resolved | run_20260318_150753_summary.json, nqs_ratings.json, interrater_summary.json, interrater_report.md

---

### S13 — OQ-09 Empirical Result

**OQ-09 — Prototype Evaluation Protocol [RESOLVED — S13]**
Note: OQ-09 was resolved twice — protocol design in S10, empirical closure in S13.
This entry records the empirical result. Protocol design rationale is in the S10 entry above.

Run: `20260318_150753` | Model: `claude-sonnet-4-6` | Date: 2026-03-18
Battery: 12 pre-registered cases (Type A + Type B), 23 total turns, 12 violation-designed turns.

**Primary threshold — MET.**
CVR_A = 1.000 → CVR_C = 0.000.
Reduction: 100%.
Threshold ≥75%: met at maximum margin.
Elicitation rate 1.000 across all conditions.
[Verified] — run_20260318_150753_summary.json, primary source.

**Directionality check — NOT MET (floor result).**
CVR_B = CVR_C = 0.000.
Both conditions suppressed all violations.
Not evidence of mechanistic equivalence: IMP-I05-T01 (disposed S13) documents silent stale-context drift under Condition B producing incorrect ABox evolution on tc-a03 turn 3 — Condition B CVR=0 reflects "all turns blocked," not "all turns blocked from an accurate world model."
Named limitation: test battery adversarial sufficiency insufficient to expose this fragility at the CVR level.
Pre-registered battery cannot be retroactively redesigned. Does not affect the primary threshold.
[Verified] — structural, from IMP-I05-T01 characterization.

**VDR_A = 0.667 — structural, not a harness error.**
4 undetected turns are all Type B cases. Under Condition A (no ABox commits), baseline world state renders all Type B moves topologically valid; oracle correctly finds no violations.
VDR_B = VDR_C = 1.000.
[Verified] — structural, from test design documentation and summary JSON.

**NQS threshold — MET.**
Human rater only (sole primary metric per pre-registration).
Condition B mean: 3.67 | Condition C mean: 3.83. Direction correct; C ≥ B.
n=12 per condition; directional, not statistically powered.
tc-m04 non-finding: accumulated multi-turn drift case produced identical scores and notes (B=4, C=4). 
Drift real and symbolic-layer-detectable (IMP-I05-T01) but not perceptible as prose degradation at 3-turn session length.
[Verified] — nqs_ratings.json, primary source.
Qualitative signal [Inferred] — single rater, n=12 per condition.

**Inter-rater analysis.**
Two corrected-rubric LLM models run as secondary raters:
claude-sonnet-4-6: Pearson r=0.081 (p=0.708), 6 divergent cases 
gpt-5.4: Pearson r=0.123 (p=0.567), 6 divergent cases
Both near zero, non-significant. 
Not evidence of unreliable human ratings.
Evidence of rubric comprehension gap: raters evaluated whether narrative respects world rules; rubric intended to evaluate prose quality of attempt descriptions.
Finding about evaluation design requirements, not a reliability failure.
Note: interrater_report.md Critical Methodological Finding section contains stale "all four LLM raters" language; current evidence base is two corrected-rubric models only. Data treated as correct; framing noted as inaccurate.
Residual rubric ambiguity (attempt-vs.-success boundary): both models retained hard cap on cases where narrative describes a forbidden action as narratively succeeding. Whether an attempt can be described as succeeding in the narrative while ABox is blocked is unresolved — noted here; does not affect primary metric.
tc-b03 genuine evaluative disagreement: both LLM models scored tc-b03 as 2 (innkeeper pronoun switch she→he = hard coherence failure); human rater scored 4 (uncertainty noted). Genuine ambiguity about pronoun inconsistency as rubric-level coherence failure; not attributable to role-boundary gap.
tc-m04-C cross-modal corroboration of IMP-I05-T01: GPT-5.4 scored tc-m04-C as 3 (human: 4), detecting guard state inconsistencies across turns — independently identifying ABox divergence traceable to stale-context drift.
Confirms that world-model accuracy and prose surface quality are separable dimensions under VeriForge evaluation.
[Verified] — interrater_summary.json, interrater_report.md, primary sources.

**Qualitative NQS observations (n=1 human rater; observational weight only):**
Condition C spatial/character advantage (tc-a01, tc-a02, tc-a03): per-turn injection enables richer spatial grounding and character interaction. [Inferred]
"Constraint narration artifact" on Type B blockings: per-turn context string produces awkward spatial language ("hidden corridor," "direct route...natural") when proposed action violates adjacency. 
Perceptible in prose; does not affect CVR.
Routed to OQ-10 as post-prototype investigation thread.
Baseline LLM prose failure modes ("closed-world sentences," "arbitrary open-endedness") visible across both conditions — scope boundary for VeriForge.

**IMP-I05-T01 — incorporated and disposed.**
tc-a03 turn 3: Condition B fired B1+A1; Condition C fired A1 only.
Both blocked.
Condition B's world model was incorrect (guard at entrance, not main_hall).
Stale-context drift is silent, structurally fragile, and supports OQ-08 claim.
Cross-modal corroboration from GPT-5.4 tc-m04-C score.

**Epistemic status:**
[Verified] at prototype scope (claude-sonnet-4-6, single tavern, 3–4 characters, 2–3 constraints, max 3 turns per case): per-turn symbolic injection achieves CVR=0 on tested Type A+B pairs without NQS degradation.
[Inferred] beyond prototype scope: CVR divergence between B and C at longer sessions; constraint narration artifact persistence; Condition C quality advantage under larger evaluation; generalization across LLM architectures.

**Scope boundaries:** single tavern, 3–4 characters, 2–3 hard constraints, max 3 turns per case, single LLM, 12 cases.
Post-prototype questions: session length, scale, model variation, constraint complexity, constraint narration artifact, attempt-vs.-success rubric boundary.

**Pre-registration deviation note.**
The S10 pre-registration specified (1) test cases as "5–10 turn prompt sequences" and (2) "minimum 3 runs per condition per test case; CVR averaged across runs to reduce LLM non-determinism."
The executed battery used max 3 turns per case and 1 run per condition (single harness execution run_20260318_150753).
Both deviations reduce adversarial pressure on the test relative to the pre-registered design.
Justification: (1) cases were scoped to 3-turn maximum during Phase 4 design (IMP-I05-D02) to keep the pre-registered battery tractable at solo prototype scope; the reduction is structurally conservative rather than liberal. (2) CVR results are floor (0.000) and ceiling (1.000) values; averaging across additional runs cannot change the binary outcome, and the primary threshold is met at maximum margin. The directionality check is the finding most sensitive to LLM non-determinism — CVR_B = CVR_C = 0.000 may not hold under additional runs or longer sessions; this is already named as the battery adversarial sufficiency limitation.
[Noted — Ankyra-03]

---

### S13 — OQ-10 Thread

**OQ-10 — Constraint Narration Artifact** [OPEN — S13]
Observation: under Condition C, per-turn context injection produces awkward spatial language on Type B blocking turns — narrative describes characters moving "as if there were a hidden corridor" or taking "a direct route...perfectly natural" — language the human rater identified as nonsensical and inconsistent with immersive RP prose.
The per-turn context string, when injecting world state from which a proposed action violates adjacency, appears to shape LLM spatial language in ways that expose the constraint mechanism in the surface text.
Does not affect CVR.
Perceptible in NQS ratings (tc-b01, tc-b02, tc-b04 Condition C scored equal or lower than Condition B by human rater specifically on these cases).
Status: post-prototype investigation thread.
No hard dependencies identified. 
Routes to: future Session Chat if VeriForge development continues beyond prototype scope. 
Investigation question: is the artifact addressable by prompt engineering of the per-turn context string format, or is it structural to the architecture?
Evidence from prototype evaluation: n=1 human rater, 3 Type B cases.
Insufficient to characterize fully — named for forward reference.

---

### S13 — Attempt-vs.-Success Rubric Ambiguity (Note)

**NQS Rubric Ambiguity — Attempt vs. Success Boundary** [NOTED — S13]
The NQS rubric instructs evaluators that describing a violation attempt is correct VeriForge behavior and should not be treated as a coherence failure.
Both corrected-rubric LLM inter-rater models retained a hard cap on cases where the narrative describes a forbidden action as narratively succeeding (e.g., guard fully descends into the cellar) rather than merely initiating.
The rubric does not specify whether an attempt may be described as succeeding in the narrative while the ABox delta is blocked by the symbolic layer.
Implication for future evaluation design: any NQS rubric used in post-prototype evaluation should explicitly address this boundary.
The pre-registered rubric for this study is closed and cannot be retroactively patched.
This note is for forward reference only. No action required at prototype scope.
