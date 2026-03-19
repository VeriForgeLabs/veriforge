# protocols.md

## Semantics-Driven Worldbuilding DSL Project

Research Protocols — Normative Reference

---

## CHAT ARCHITECTURE

Four distinct chat types serve different roles in this project.
Each loads different files, operates under different conduct rules, and has different output responsibilities.

---

### Ankyra Chats (ANN)

Role: Meta layer.
- Reviews Session and Implementation Chat outputs.
- Generates commit blocks and commit instructions.
- Audits project documents.
- Refines methods and protocols.
- Final authorization gate before any content touches the project files.

File load order: protocols.md → research-log.md → vision.md → implementation-log.md → learning-notes.md

Naming: Ankyra-00, Ankyra-01, Ankyra-02, ...
The inaugural Ankyra Chat (covering S09/S10 planning and pre-S11 preparation) is retroactively designated Ankyra-00.

Conduct rules:
- Does not conduct primary research.
- Does not write implementation code.
- Generates commit blocks only after explicit human authorization.
- Maintains awareness of what has and has not been committed to the project files.
- Applies the Closed-Loop Limitation protocol to all architectural review.

Output:
- Commit blocks with explicit file targets and commit messages.
- Opener templates for new Session or Implementation Chats.
- Protocol additions when gaps are identified.

---

### Session Chats (SNN)

Role: Research layer.
- Primary research sessions.
- Generates findings, citations, OQ resolutions.
- Does NOT generate commit blocks.
- Outputs are candidates for Ankyra review.

File load order: protocols.md → research-log.md → vision.md

Naming: Continues from research phase — S11, S12, ...

Conduct rules:
- All research conduct protocols apply (citation format, epistemic tagging, rival hypothesis discipline, blind spot check, mode declaration).
- Outputs flagged COMMIT-READY are candidates only. Ankyra authorizes commits.
- Session log entries are generated but not committed until Ankyra review.

---

### Implementation Chats (INN)

Role: Build layer.
- Environment setup, code, prototype construction.
- Follows implementation-log.md discipline.
- Does NOT conduct research or generate commits.
- Outputs are candidates for Ankyra review.

File load order: protocols.md → implementation-log.md → learning-notes.md (vision.md loaded on request or when architectural questions arise)

Naming: I01, I02, I03, ...

Conduct rules:
- Hello World style teaching implementation: every step enumerated and explained.
- Best practices followed at every layer; no shortcuts without explicit justification.
- [FAIL] entries are mandatory; a clean log with no failures is incomplete.
- [DECISION] entries are required whenever a design choice is made; each must name the alternative not taken and the reason for rejection.
  A log with no [DECISION] entries is as incomplete as one with no [FAIL] entries.
- [THREAD] entries name open items that surface during implementation and require future disposition; each must state an explicit routing destination (Session Chat, protocols.md patch, or named implementation phase) and a named trigger condition for when disposition is required.
- Shell context must be confirmed before any terminal commands are issued.
- Any configuration string, API method name, or package-specific syntax included in a command the user will execute verbatim must be verified against current primary source documentation before being stated; training knowledge is not sufficient.
- The four core project files in knowledge/ — protocols.md, research-log.md, vision.md, and implementation-log.md — are untouched by implementation commits.
  knowledge/learning-notes.md is a fifth file in the same directory with a different function: personal reference capture.
  It is populated directly by the developer from NOTE-READY blocks and is not part of the research integrity boundary.
- When an INN chat produces a conceptual explanation, pattern walkthrough, or "why this works" reasoning worth preserving, flag it ✓ NOTE-READY and include a pre-formatted markdown block targeting a named section in knowledge/learning-notes.md.
  NOTE-READY blocks are added directly by the developer to learning-notes.md — no Ankyra oversight required.
  NOTE-READY is distinct from COMMIT-READY, which requires Ankyra review and explicit authorization.

  Format:
  ```
  ✓ NOTE-READY
  Target: knowledge/learning-notes.md — ## [Section] / ### [Subsection]

  [markdown content]
  ```

- No research questions pursued inline — surface as named threads for Session Chats.

---

### Exploration Chats (ENN)

Role: Ideation layer.
- Loose questions, what-ifs, analogies, half-formed hunches, adjacent ideas.
- No obligation to produce findings.
- No commit pathway of any kind.
- The conversation develops naturally through curiosity and discussion.
- Connection to existing project questions is an emergent property, not a design objective.

File load order: protocols.md → research-log.md → vision.md → implementation-log.md
Full document context is required for silent background awareness.
Loaded files are not surfaced into the conversation unless directly relevant to a question being discussed.

Naming: E01, E02, E03, ...

Conduct rules:
- No epistemic tagging required unless a claim is being seriously entertained for handoff.
- No citation requirement unless precision matters to the question.
- No COMMIT-READY pathway. No commit blocks of any kind.
- No blind spot check or mode declaration required.
- The conversation goes wherever it goes.

Silent awareness:
The ENN chat holds the current OQ and implementation thread state as background context.
It does not actively steer conversation toward existing questions.
It monitors for emergence — ideas that develop naturally into something that crosses one of the following thresholds:

  (a) The idea directly bears on a named open question or open thread.
  (b) The idea would materially change how a resolved question is understood.
  (c) The idea is substantive enough to warrant a new named open question or implementation thread that does not currently exist.

When a threshold is crossed, the ENN chat immediately flags it and prompts the user to initiate a handoff.
It does not initiate the handoff autonomously.
The threshold must be crossed naturally through the development of the conversation — the ENN chat does not push toward or seek a relation to existing OQs.

The only structured output an ENN chat is responsible for is the **✓ HANDOFF-READY** block.
Everything else is conversation.

Handoff protocol:
When a threshold is crossed, the ENN chat produces a ✓ HANDOFF-READY flag and a structured handoff block (template in REFERENCE FORMATS below).
The user decides whether and when to carry it to Ankyra. Ankyra determines the appropriate next step (direct commit, Session Chat, or Implementation Chat) and references the ENN chat as origin in any resulting commit.
ENN chats are not tracked in any project file unless a handoff occurs and Ankyra generates a commit from it.

---

## RESEARCH PROTOCOLS

---

### Audit Trigger Protocol

A document audit is triggered when any OQ resolution unblocks at least one downstream OQ.
The audit must be completed before the next research session begins.
Ad hoc audits may be requested at any time but are not required between trigger events.
The AI research partner is the executor of the audit at session start.
The audit is completed before any research question is addressed.

Standing migration check (Ankyra Chats only):
At each Ankyra Chat, before any other work, scan vision.md for any resolved OQ whose body has not yet been migrated to a cross-reference line.
For each such OQ, execute Step 3c migration before proceeding.
This closes the structural gap in the Audit Trigger Protocol: the trigger fires only when an OQ resolution unblocks a downstream OQ.
An OQ that resolves without unblocking anything — e.g., the terminal OQ in a research phase — never triggers the audit and therefore never triggers migration.
The standing migration check is the corrective for that class of case.
Named threads (e.g., OQ-09-T1) follow the same migration rule as primary OQs — when resolved, replace the body in vision.md with a cross-reference line in Step 3c format.

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

HALT CONDITION: If the entry cannot be made accurate without re-opening the OQ — for example, because the resolution was based on a finding later caught as a citation error, or because the stated decision contradicts a committed finding — halt the audit, flag the condition to the human operator, and do not proceed to Step 2.
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
If the claim depends on multiple OQs and only one is now resolved, update only the resolved dependency pointer. Leave remaining dependency language intact and accurate for still-open OQs.

"BLOCKS" or "DEPENDS ON" reference in another OQ entry:
Verify the status is now correctly stated as [RESOLVED].
If the referenced OQ entry is itself still open, confirm the dependency accurately reflects current state.

Scope condition or open pointer in WHAT IS VERIFIED:
Close it with the finding.
Remove any "must be investigated in OQ-XX" language.

Cross-reference line (after Step 3 is complete):
Leave it. It is correct by construction.

After Step 2, no occurrence of this OQ's identifier in vision.md may point to it as open, pending, or unresolved — except the cross-reference line that Step 3 will create.

---

Step 3 — Migration of the resolved OQ entry to research-log.md.

Execute in this exact order. Do not reorder sub-steps.

3a. Confirm Step 1 is complete.
The entry being migrated must be accurate before it is archived.
Migration of an inaccurate entry is not permitted.

3b. Append the full resolved OQ entry — as corrected by Step 1 — to research-log.md under a new subsection header in this format:

### OQ-XX — [Name] [RESOLVED — SNN]

The session number SNN is the session in which the OQ was resolved.
Use the heading itself as the stable link anchor.
The format ### OQ-XX produces anchor #oq-xx on GitHub — stable, short, and predictably case-folded. Do not use deprecated HTML <a name=""> anchors.

3c. In vision.md, delete the full OQ entry body.
Replace it with a single cross-reference line in this exact format:

**OQ-XX — [Name]** [RESOLVED — SNN] — [one-sentence decision summary]. → [research-log.md](research-log.md#oq-xx)

The one-sentence summary must be accurate and self-contained.
A reader who only reads vision.md must understand what was decided without opening research-log.md.

3d. Read the cross-reference line back against the archived entry in research-log.md.
Confirm: OQ identifier matches, session number matches, decision summary accurately reflects the archived entry.
Any discrepancy is a Step 3 error; correct it in both files before proceeding.

3e. Confirm no body text from the migrated entry remains anywhere in vision.md other than the cross-reference line.

---

Step 4 — Integrity verification.

After Steps 1–3, perform the following checks in order.
Each must pass before the audit is closed.

4a. Orphan scan.
Search vision.md for any remaining occurrence of this OQ's identifier not accounted for by Steps 1–2 or the Step 3 cross-reference line.
Each remaining occurrence is either a Step 2 error (fix it) or evidence that Step 2 was incomplete (fix it). After fixing, re-run 4a before proceeding to 4b.

4b. Citation integrity.
Confirm every citation ShortID referenced anywhere in the active content of vision.md has a full entry in research-log.md. Migration must not create citation orphans.
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
Review [Inferred] claims in vision.md that now have direct supporting evidence from this OQ's findings.
If any [Inferred] claim is now fully supported by [Verified] findings, update its marker to [Verified] with citation.
This step is mandatory, not optional.
A stale [Inferred] marker on a now-verified claim is an epistemic error of the same class as a stale open-pointer — it misrepresents the evidentiary state of the document.

---

Audit closed when: all four steps complete with no outstanding failures.
Append one Audit Log entry to research-log.md per the Audit Log Format.
Commit all changes to vision.md and research-log.md in a single commit:

git commit -m "audit: OQ-XX resolved — [one-phrase description of what migrated]"

---

### OQ Re-Opening Protocol

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

---

### Rival Hypothesis Discipline

When evaluating any mechanism or design decision, explicitly state the strongest plausible alternative explanation and assess what evidence would favor it over the proposed approach.
This applies at session level, not only at audit level.
When a research session proposes a mechanism as the solution to an open question, the session log must record: (1) what the strongest competing mechanism was, and (2) why it was rejected or deferred.
Absence of a stated rival is a quality flag, not a neutral finding.

---

### Session Mode Declaration

Each Session Chat (SNN) opener must declare its operative mode.
Modes are mutually exclusive for any given session segment; a session may shift modes explicitly but not implicitly.

EXPLORE
- Generate hypotheses freely.
- Flag all outputs [Inferred].
- Nothing commits without explicit promotion in a subsequent VERIFY pass.

VERIFY
- Check specific claims against primary sources.
- Nothing commits without a confirmed URL and primary-source access.

COMMIT
- Audit and format outputs for the project files.
- Ankyra Chat role only.
- Session and Implementation Chats do not COMMIT.

---

### Blind Spot Check

Each Session Chat (SNN) opener must include one forced question before research begins.

  "What question would a skeptic say this session focus is implicitly not asking?"

The answer must be stated explicitly and either: (a) acknowledged as out of scope with one sentence justifying that, or (b) folded into the session focus.
An unanswered blind spot check is a quality flag, not a neutral finding.

---

### Closed-Loop Limitation

The adversarial framing preamble reduces sycophancy structurally.
It does not eliminate the closed-loop problem: asking the same model to evaluate outputs it helped generate provides weaker external pressure than an independent check.

For high-stakes design decisions (prototype architecture, evaluation design, falsification criteria), at least one verification pass should use a cold context — a fresh conversation with no prior session history — or a separate model run independently on the same question.

This is a standing protocol requirement for prototype-phase architectural decisions.
It is advisory for research-phase synthesis.

---

### Snapshot Trigger

When a Session Chat (SNN) produces a COMMIT-READY finding, update vision.md manually.
Add the finding to the appropriate section with its epistemic status.
Session log entry required for every update.

---

## IMPLEMENTATION PROTOCOLS

---

### Implementation Log Entry Format

Each implementation chat appends one section block to implementation-log.md.
The section header format is:

### IXX — [Phase Name] | [Date] | [Status]

Where XX is the implementation chat number (e.g., I01, I02).

Four entry types are defined. All are append-only except [THREAD], which may have a Resolution: field added in-place when the thread closes.
```
[DECISION] IMP-IXX-DNN — [Title]
Chosen: [what was selected]
Alternative not taken: [what was rejected]
Reason: [why]

[FAIL] IMP-IXX-FNN — [Title]
Error: [what went wrong]
Cause: [why it happened]
Resolution: [how it was fixed]
Methodology patch recommended: [yes/no]

[THREAD] IMP-IXX-TNN — [Title]
Description: [what the thread is about]
Routes to: [Session Chat | protocols.md | implementation phase]
Disposition trigger: [named condition or event that requires this to be resolved]
Resolution: (added in-place when thread closes — not populated at creation)
```

[CLEAN] IMP-IXX — [One sentence confirming no failures occurred in this phase.]
[Brief explanation linking absence of failures to prior error knowledge if applicable, or a simple statement that the phase ran without recordable errors.]

[RESOLVED] IMP-IXX — [Pre-registered resolution criterion, summarized in one sentence.]
Evidence: [Observed outputs or test results that confirm the exit criterion was met.
List each test case or verification step with its actual result.]

[THREAD] entries are the single exception to the append-only rule.
When a thread is closed, a Resolution: field is added in-place to the original entry.
[DECISION] and [FAIL] entries remain strictly append-only.
[CLEAN] and [RESOLVED] entries are append-only; one of each appears at most once per phase block.

Usage rules:
- [CLEAN] is required when a phase closes with no [FAIL] entries.
  Absence of [CLEAN] when no [FAIL] entries exist is indistinguishable from incomplete recording.
- [RESOLVED] is required as the final entry in every phase block.
  It records the evidence that the pre-registered exit criterion was met.
  A phase block without a [RESOLVED] entry is not closed, regardless of the status token in the phase map.

---

## REFERENCE FORMATS

---

### Opener Templates

#### Ankyra Chat (ANN) Opener
```
Ankyra Chat [NN] | Previous: Ankyra-[NN-1] | Date: [DATE]
Mode: COMMIT
Under review: [SNN output | INN output | protocol discussion | none]

Files loaded: protocols.md → research-log.md → vision.md → implementation-log.md → learning-notes.md

This is an Ankyra Chat.
My role is review and commit generation, not primary research or implementation.
I do not generate commits without explicit human authorization.
I maintain awareness of what has and has not been committed to the project files.

What is committed vs. pending:
[State explicitly what was last committed to each file and what is known to be pending.]

---

[Paste Session or Implementation output here, or describe what needs review]
```

---

#### Session Chat (SNN) Opener
```
Session [N] | Last snapshot: [date or "none"]
Mode: [EXPLORE | VERIFY]
Focus: [one sentence on today's research question]
Open questions being addressed: [OQ-XX, OQ-YY or "none"]
Pending verifications: [list or "none"]

Blind spot check: [What question would a skeptic say this session focus is implicitly not asking? State it and either acknowledge as out of scope (one sentence) or fold in.]

Files are loaded at session start in this order: protocols.md → research-log.md → vision.md.
Loading vision.md last ensures it carries the highest recency weight at the moment of active research.
If a document audit is triggered, complete it before addressing any research question.

---

[Your question]
```

---

#### Implementation Chat (INN) Opener
```
Implementation Chat [IXX] | Date: [DATE]
Phase: [Phase number and name, e.g., Phase 0 — Clingo Fundamentals]
Phase status: [NOT STARTED | IN PROGRESS | BLOCKED]
Shell context: [WSL bash | PowerShell | other — confirm before any terminal commands]

Files loaded: protocols.md → implementation-log.md → learning-notes.md

This is an Implementation Chat.
My role is building, not research or committing.
I do not generate commit blocks.
I flag conceptual explanations worth preserving as ✓ NOTE-READY blocks.
I surface research questions as named [THREAD] entries for Session Chats.

---

[Describe what we are building today and where we left off]
```

---

#### Exploration Chat (ENN) Opener
```
Exploration Chat [ENN] | Date: [DATE]

Files loaded: protocols.md → research-log.md → vision.md → implementation-log.md

This is an Exploration Chat.
The conversation goes wherever it goes.
I hold the current project state as silent background context.
I will flag ✓ HANDOFF-READY if an idea crosses a threshold worth elevating.
I do not generate commit blocks or steer toward existing OQs.

---

[Start the conversation]
```

---

### ENN Handoff Block Template
```
---
✓ HANDOFF-READY

**Origin:** [ENN chat identifier, e.g., E01]
**Emerged from:** [One sentence describing what was being discussed when the threshold was crossed]
**Threshold triggered:** [a | b | c]

**Core claim:**
[The idea stated as precisely as possible. One paragraph maximum.
State it directly so Ankyra can evaluate it.]

**Epistemic status:** [Verified | Inferred | Unverified]
[Brief justification — what is this based on?]

**Citations (if any):**
[Full citation entries in standard project format, or "none"]

**Relationship to existing project:**
[Which OQ, thread, or phase this bears on — or "potential new OQ" if threshold (c) was triggered. One sentence per relationship.]

**Suggested Ankyra next step:**
[Direct commit candidate | Warrants Session Chat | Warrants Implementation Chat | Unclear — needs Ankyra evaluation]

**Full context summary:**
[A summary of the ENN conversation leading to this finding, sufficient for Ankyra to reconstruct the reasoning without reading the original chat.
Include key intermediate steps, analogies, or examples that shaped the claim.]
---
```

---

### Citation Format

Every factual claim uses inline citation: `[Tag:ShortID]`
Tags (exactly these, no others): `Paper` | `Repo` | `Doc` | `Blog` | `Forum` | `Social` | `Video`
ShortID format: `AuthorYYYY` (e.g., `[Paper:Zhang2024]`)
Full citations are logged in the Research Log with URL.
Epistemic markers are always clean tokens: [Verified], [Inferred], [Unverified].
Supporting citations or explanatory notes follow outside the bracket, set off with em-dashes:
[Verified] — Paper:X — Never embed explanatory text inside the bracket itself.

Precision claims — accuracy figures, percentages, named mechanisms — require primary source confirmation before committing.
Abstract-level verification is not sufficient for precision claims.
When a precision claim is cited via a secondary source, the status note must identify the actual primary source and flag it for direct confirmation.

---

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

---

### Session Log Format

Each research session adds entries in this format:
```
[SN-EN] Topic | Status (Open/Resolved/Superseded) | Key sources
```

Where N = session number, EN = entry number within session.

---

### Audit Log Format

Each audit produces one entry appended to the Audit Log in research-log.md.
Use this exact format:

```
First line (use the appropriate identifier for audit type):
[AUDIT-SNN-OQ-XX] OQ-XX resolved | [Date] | Steps completed: [1, 2, 3, 4]
[AUDIT-ANKYRA-NN] Milestone audit | [Date] | Steps completed: [1, 2, 3, 4, 5, 6]

Issues found:
  - [Issue description] → [Resolution applied] → Methodology patch recommended: [yes/no]
Methodology patches flagged: [yes/no]
If yes: identify the protocol step affected and the proposed fix in plain language.
Audit closed: [yes/no]
If no: state the blocking condition explicitly.
```

If no issues were found, the "Issues found" field reads: none.
The Audit Log is append-only.
Entries are never edited after the audit closes.
If a methodology patch is recommended, the patch is applied to protocols.md in the same commit as the audit.
