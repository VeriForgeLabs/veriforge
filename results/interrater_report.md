# NQS Inter-Rater Analysis Report

Generated for S13 — OQ-09 resolution session.

## Critical Methodological Finding

All four LLM raters systematically misapplied the rubric's coherence dimension.
They applied the hard-cap rule to narratives describing a character successfully
entering a forbidden location — scoring them 2 — because they evaluated the
narrative against whether the *committed world state* respected the rules.

However, VeriForge's architecture requires the LLM to describe the *attempt*,
not the committed outcome. The symbolic layer (ASP solver) blocks the delta;
the LLM's job is to write a vivid, plausible attempt. 'The guard descends into
the cellar' is the correct narrative output for a violation-designed turn —
the guard attempted it, the solver blocked the commit, the ABox did not update.

The LLM raters evaluated: 'does this narrative respect the world rules?'
The rubric intended: 'is this narrative a plausible, engaging RP output?'
These are different questions under VeriForge's role-boundary architecture.

Consequence: LLM inter-rater scores are not comparable to human scores on the
same dimension. The low correlations below reflect rubric comprehension failure,
not unreliable human ratings. This finding should be stated explicitly in the
OQ-09 resolution write-up.

---

## Per-Model Statistics

### claude-sonnet-4-6

- Ratings collected: 24 / 24
- Human mean NQS: 3.792
- LLM mean NQS:   3.208
- Pearson r:      0.081 (p=0.708)
- Divergent cases (gap ≥ 2): 6

  | Case | Cond | Human | LLM | Gap |
  |------|------|-------|-----|-----|
  | tc-a02 | C | 5 | 3 | 2 |
  | tc-b01 | B | 4 | 2 | 2 |
  | tc-b03 | B | 4 | 2 | 2 |
  | tc-b03 | C | 4 | 2 | 2 |
  | tc-m02 | C | 5 | 3 | 2 |
  | tc-m04 | C | 4 | 2 | 2 |

### gpt-5.4

- Ratings collected: 24 / 24
- Human mean NQS: 3.792
- LLM mean NQS:   2.917
- Pearson r:      0.123 (p=0.567)
- Divergent cases (gap ≥ 2): 6

  | Case | Cond | Human | LLM | Gap |
  |------|------|-------|-----|-----|
  | tc-a02 | B | 4 | 2 | 2 |
  | tc-a02 | C | 5 | 2 | 3 |
  | tc-a03 | C | 5 | 3 | 2 |
  | tc-b03 | B | 4 | 2 | 2 |
  | tc-b03 | C | 4 | 2 | 2 |
  | tc-m02 | C | 5 | 3 | 2 |

---

## Score Distribution Comparison

| Case | Cond | Human | claude-sonnet-4-6 | gpt-5.4 |
|------|------|-------|--------|--------|
| tc-a01 | B | 4 | 4 | 5 |
| tc-a01 | C | 5 | 4 | 4 |
| tc-a02 | B | 4 | 4 | 2 |
| tc-a02 | C | 5 | 3 | 2 |
| tc-a03 | B | 3 | 4 | 3 |
| tc-a03 | C | 5 | 4 | 3 |
| tc-a04 | B | 3 | 4 | 4 |
| tc-a04 | C | 4 | 4 | 3 |
| tc-b01 | B | 4 | 2 | 3 |
| tc-b01 | C | 3 | 3 | 3 |
| tc-b02 | B | 4 | 4 | 3 |
| tc-b02 | C | 3 | 3 | 3 |
| tc-b03 | B | 4 | 2 | 2 |
| tc-b03 | C | 4 | 2 | 2 |
| tc-b04 | B | 3 | 3 | 2 |
| tc-b04 | C | 3 | 2 | 2 |
| tc-m01 | B | 4 | 3 | 3 |
| tc-m01 | C | 3 | 3 | 3 |
| tc-m02 | B | 4 | 3 | 3 |
| tc-m02 | C | 5 | 3 | 3 |
| tc-m03 | B | 3 | 4 | 3 |
| tc-m03 | C | 3 | 3 | 2 |
| tc-m04 | B | 4 | 4 | 4 |
| tc-m04 | C | 4 | 2 | 3 |

---

## Summary for S13

The inter-rater analysis should be presented to S13 as follows:

1. Two LLM models were used as secondary raters with the corrected rubric:
   claude-sonnet-4-6 and gpt-5.4. Four additional models (grok-4.20-reasoning,
   grok-4.20-non-reasoning, gpt-5.3, gpt-5.4-thinking) were run with the
   original misapplied rubric and are documented separately.

2. Both corrected-rubric models showed residual hard-cap application on
   violation-designed cases as 2 regardless of prose quality, because
   they interpreted 'coherence failure' as 'narrative describes a
   rule-violating action as succeeding' — which is the intended behavior
   under VeriForge's role-boundary architecture.

3. The low inter-rater correlations are not evidence of unreliable human
   ratings. They are evidence of a rubric comprehension gap specific to
   VeriForge's unusual architectural property: the narrative intentionally
   describes attempts, not outcomes.

4. The LLM inter-rater pass is therefore not usable as a reliability check
   on the human NQS scores. It is usable as evidence that the role-boundary
   concept requires explicit explanation to any external evaluator — human
   or LLM — before they can apply the NQS rubric correctly.

5. The human NQS ratings stand as the sole primary metric per the
   pre-registered protocol.