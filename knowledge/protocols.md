# protocols.md

## Semantics-Driven Worldbuilding DSL Project
Research Protocols — Normative Reference

## RESEARCH PROTOCOLS

### Audit Trigger Protocol

A document audit is triggered when any OQ resolution unblocks at least one downstream OQ.
The audit must be completed before the next research session begins.
Ad hoc audits may be requested at any time but are not required between trigger events.
The AI research partner is the executor of the audit at session start.
The audit is completed before any research question is addressed.

Files are loaded in this order at session start: protocols.md → research-log.md → vision.md.
Loading vision.md last ensures it carries the highest recency weight at the moment of active research.

Audit scope — four steps, executed in order.
No step may be skipped.
No step may be executed out of order.

---

Step 1 — Accuracy pass on the resolved OQ entry.

Read the resolved OQ entry as it currently exists in vision.md.
Check each of the following and correct any that fail:
All "DEPENDS ON" references show [RESOLVED] status.
The "BLOCKS" list correctly names every OQ that is now unblocked.
The mechanism or decision stated in the entry matches the committed session findings exactly.
No language remains that refers to this OQ as open, pending, or requiring investigation.
All citations referenced within the entry exist as full entries in research-log.md.
If any citation is missing from research-log.md, add it before proceeding to Step 2.

HALT CONDITION: If the entry cannot be made accurate without re-opening the OQ —
for example, because the resolution was based on a finding later caught as a citation error,
or because the stated decision contradicts a committed finding —
halt the audit, flag the condition to the human operator, and do not proceed to Step 2.
Migration of an incorrectly resolved OQ is worse than leaving it in place.
The OQ-reopening protocol applies in this case (see below).

Step 1 produces a clean, accurate source entry.
Step 3 migrates it.
Migration before accuracy verification is not permitted.

---

Step 2 — Dependency sweep across vision.md.

Search the full text of vision.md for every occurrence of this OQ's identifier (e.g., "OQ-08").
For each occurrence, apply the appropriate action:

[Inferred] claim with this OQ as a named dependency:
Update the claim to reflect what was found.
Replace "depends on OQ-XX" or "requires OQ-XX resolution" language with a statement of the actual finding or its delegation.
If the claim depends on multiple OQs and only one is now resolved, update only the resolved dependency pointer.
Leave remaining dependency language intact and accurate for the still-open OQs.

"BLOCKS" or "DEPENDS ON" reference in another OQ entry:
Verify the status is now correctly stated as [RESOLVED].
If the referenced OQ entry is itself still open, confirm the dependency accurately reflects current state.

Scope condition or open pointer in WHAT IS VERIFIED:
Close it with the finding.
Remove any "must be investigated in OQ-XX" language.

Cross-reference line (after Step 3 is complete):
Leave it. It is correct by construction.

After Step 2, no occurrence of this OQ's identifier in vision.md may point to it as open, pending,
or unresolved — except the cross-reference line that Step 3 will create.

---

Step 3 — Migration of the resolved OQ entry to research-log.md.

Execute in this exact order. Do not reorder sub-steps.

3a. Confirm Step 1 is complete.
The entry being migrated must be accurate before it is archived.
Migration of an inaccurate entry is not permitted.

3b. Append the full resolved OQ entry — as corrected by Step 1 — to research-log.md
under a new subsection header in this format:

### OQ-XX — [Name] [RESOLVED — SNN]

The session number SNN is the session in which the OQ was resolved.
Use the heading itself as the stable link anchor.
The format ### OQ-XX produces anchor #oq-xx on GitHub — stable, short, and predictably case-folded.
Do not use deprecated HTML <a name=""> anchors.

3c. In vision.md, delete the full OQ entry body.
Replace it with a single cross-reference line in this exact format:

**OQ-XX — [Name]** [RESOLVED — SNN] — [one-sentence decision summary]. → [research-log.md](research-log.md#oq-xx)

The one-sentence summary must be accurate and self-contained.
A reader who only reads vision.md must understand what was decided without opening research-log.md.

3d. Read the cross-reference line back against the archived entry in research-log.md.
Confirm: OQ identifier matches, session number matches, decision summary accurately reflects the archived entry.
Any discrepancy is a Step 3 error; correct it in both files before proceeding.

3e. Confirm no body text from the migrated entry remains anywhere in vision.md
other than the cross-reference line.

---

Step 4 — Integrity verification.

After Steps 1–3, perform the following checks in order.
Each must pass before the audit is closed.

4a. Orphan scan.
Search vision.md for any remaining occurrence of this OQ's identifier not accounted for
by Steps 1–2 or the Step 3 cross-reference line.
Each remaining occurrence is either a Step 2 error (fix it) or evidence that Step 2 was incomplete (fix it).
After fixing, re-run 4a before proceeding to 4b.

4b. Citation integrity.
Confirm every citation ShortID referenced anywhere in the active content of vision.md
has a full entry in research-log.md.
Migration must not create citation orphans.
A cross-reference line that mentions a citation is still an active reference.

4c. [Inferred] claim completeness.
List every [Inferred] claim in vision.md that mentioned this OQ as a dependency.
Confirm each was found and updated in Step 2.
If any were missed, fix them and re-run 4a before proceeding to 4d.

4d. Cross-reference accuracy.
Read the cross-reference line in vision.md against the archived full entry in research-log.md.
Confirm they agree on: OQ identifier, session number, decision summary.
Any discrepancy is a Step 3d error; correct it in both files.

4e. Downstream OQ readiness.
For each OQ that this resolution unblocks, open its entry in vision.md and confirm:
"DEPENDS ON: OQ-XX [RESOLVED]" is correctly stated.
No language remains that treats this dependency as open.
The entry is now ready to be the target of a research session.

4f. Epistemic promotion check.
Review [Inferred] claims in vision.md that now have direct supporting evidence
from this OQ's findings.
If any [Inferred] claim is now fully supported by [Verified] findings, update its marker
to [Verified] with citation.
This step is mandatory, not optional.
A stale [Inferred] marker on a now-verified claim is an epistemic error of the same class
as a stale open-pointer — it misrepresents the evidentiary state of the document.

---

Audit closed when: all four steps complete with no outstanding failures.
Append one Audit Log entry to research-log.md per the Audit Log Format.
Commit all changes to vision.md and research-log.md in a single commit:

git commit -m "audit: OQ-XX resolved — [one-phrase description of what migrated]"

---

OQ Re-Opening Protocol

If a research session produces evidence that directly contradicts a resolved OQ decision:

In vision.md: update the cross-reference line to read:
**OQ-XX — [Name]** [REOPENED — SNN] — [one sentence on what was contradicted]. → [research-log.md](research-log.md#oq-xx)
Then write a new full OQ entry in vision.md from current understanding.
Do not copy back content from research-log.md.

In research-log.md: update the archived entry header to read:
### OQ-XX — [Name] [RESOLVED — SNN] [SUPERSEDED — SNN]
Add one line below the header: Superseded by [Session SNN] — [one sentence on the contradiction].
The archived entry body is not deleted or edited further.

The archive is write-once.
No content flows from research-log.md back to vision.md.
The new vision.md entry is written fresh from current understanding.

Add a session log entry in research-log.md documenting the contradiction and the re-opening.

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

Files are loaded at session start in this order: protocols.md → research-log.md → vision.md.
Loading vision.md last ensures it carries the highest recency weight at the moment of active research.
If a document audit is triggered, the AI research partner completes it before addressing any research question.

```

### Snapshot Trigger

When a research session produces a COMMIT-READY finding, update this document manually.
Add the finding to the appropriate section with its epistemic status.
Session log entry required for every update.

### Audit Log Format

Each audit produces one entry appended to the Audit Log in research-log.md.
Use this exact format:

[AUDIT-SNN-OQ-XX] OQ-XX resolved | [Date] | Steps completed: [1, 2, 3, 4]
Issues found:
  - [Issue description] → [Resolution applied] → Methodology patch recommended: [yes/no]
Methodology patches flagged: [yes/no]
If yes: identify the protocol step affected and the proposed fix in plain language.
Audit closed: [yes/no]
If no: state the blocking condition explicitly.

If no issues were found, the "Issues found" field reads: none.
The Audit Log is append-only.
Entries are never edited after the audit closes.
If a methodology patch is recommended, the patch is applied to protocols.md (or the Research Protocols section of vision-and-protocols.md prior to the file split) in the same commit as the audit.

### Rival Hypothesis Discipline

When evaluating any mechanism or design decision, explicitly state the strongest plausible alternative explanation and assess what evidence would favor it over the proposed approach.
This applies at session level, not only at audit level.
When a research session proposes a mechanism as the solution to an open question, the session log must record: (1) what the strongest competing mechanism was, and (2) why it was rejected or deferred.
Absence of a stated rival is a quality flag, not a neutral finding.

For OQ-09 specifically, the research session must specify before any prototype session counts as a test:
(1) The measurable outcome that would constitute falsification of the per-turn injection sufficiency claim.
(2) Baseline conditions — at minimum: (a) raw LLM with no DSL grounding, and (b) system-prompt-only injection without per-turn re-injection.
Baseline (b) is required to isolate the specific contribution of per-turn injection from symbolic grounding generally.
(3) The improvement threshold that would count as meaningful — "better than baseline" is not a sufficient criterion.

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