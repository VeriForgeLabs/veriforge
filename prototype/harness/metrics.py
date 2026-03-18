"""
VeriForge Phase 4 — Metrics Module
prototype/harness/metrics.py

Defines TurnRecord (the per-turn measurement unit) and computes the three
pre-registered metrics for the OQ-09 ablation study.

METRIC DEFINITIONS (pre-registered, OQ-09 [RESOLVED — S10])
─────────────────────────────────────────────────────────────

CVR — Constraint Violation Rate (primary)
─────────────────────────────────────────
  Of the turns where a constraint violation was genuinely attempted AND
  confirmed by the symbolic oracle, what fraction committed to world state?

  CVR = slipped / attempted

    attempted — turns where expects_violation=True AND oracle_violation_detected=True
    slipped   — of those, turns where effectively_committed=True

  effectively_committed is condition-sensitive:
    Condition A:    True when oracle_violation_detected=True.
                    Nothing blocks Condition A; if the oracle sees a violation,
                    it committed (even though committed=False in TurnResult —
                    Condition A never writes the ABox).
    Conditions B/C: True only if turn_result.committed=True AND
                    oracle_violation_detected=True. Under correct VeriForge
                    operation, this should never be True.

  CVR gates on oracle confirmation, not just design intent.
  Turns where the LLM abstained from producing a violating delta
  (oracle_violation_detected=False) are excluded from both numerator and
  denominator. They are not enforcement successes — they are elicitation
  failures upstream of the symbolic layer. Diagnose via elicitation_rate.

  Falsification threshold (pre-registered, OQ-09):
    CVR_C <= 0.25 * CVR_A   AND   CVR_C < CVR_B (directionally)

VDR — Violation Detection Rate (secondary)
───────────────────────────────────────────
  Of all turns designed to elicit a violation, what fraction did the oracle
  detect one?

  VDR = detected / designed

    designed  — all turns where expects_violation=True
    detected  — of those, turns where oracle_violation_detected=True

  VDR near 1.0 is expected. VDR below 1.0 means either:
    (a) The LLM did not produce a violating delta (elicitation failure).
    (b) An ASP encoding gap — the rule did not fire when it should.
  Distinguish (a) from (b) by checking elicitation_rate alongside VDR.

Elicitation Rate — diagnostic (not pre-registered)
───────────────────────────────────────────────────
  Of the turns where expects_violation=True, what fraction produced a
  non-empty proposed_delta? Pre-oracle gate; measures whether the LLM
  attempted any state change at all.

NQS — Narrative Quality Score (tertiary)
─────────────────────────────────────────
  5-point Likert scale, assigned by human rater post-hoc. Not computed here.
  Populated manually in results/run_<timestamp>_summary.json after each run.
  Guards against the failure mode where Condition C wins on CVR only because
  it blocks all deltas with useless refusal prose.

CONDITION A ORACLE NOTE
────────────────────────
  session_loop.run_turn() never calls validate_delta() in Condition A and
  hardcodes committed=False. The harness calls run_silent_validation() after
  each Condition A turn to obtain oracle classifications for CVR computation.
  The oracle always sees the baseline ABox for Condition A turns (Condition A
  never writes it), which creates documented measurement gaps for
  state-dependent cases. These are not design flaws — they are structural
  properties of Condition A's statelessness, documented per-case in
  condition_notes.

Design decisions recorded in implementation-log.md:
  IMP-I05-D01 — Model override via module-level patching
  IMP-I05-D02 — Test cases as declarative JSON
  IMP-I05-D03 — Silent oracle for Condition A CVR measurement
  IMP-I05-D04 — ABox reset from in-memory baseline
"""

import sys
from dataclasses import dataclass
from pathlib import Path

# ── Import path ───────────────────────────────────────────────────────────────
# metrics.py lives at prototype/harness/metrics.py.
# Inserting prototype/ into sys.path makes session_loop and tavern.validator
# importable when metrics.py is imported from run_harness.py.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from session_loop import TurnResult          # noqa: E402
from tavern.validator import validate_delta  # noqa: E402


# ── TurnRecord ────────────────────────────────────────────────────────────────

@dataclass
class TurnRecord:
    """
    Complete measurement record for one session loop turn.

    Wraps TurnResult (session loop concerns) with harness-level fields
    required for CVR, VDR, and elicitation rate computation.
    The session loop is kept ignorant of evaluation logic.

    Fields
    ──────
    test_case_id
        Parent test case identifier, e.g. "tc-a01".
    turn_number
        1-indexed position within the test case.
    condition
        "A", "B", or "C".
    turn_result
        Full TurnResult from run_turn(). Contains narrative, proposed_delta,
        clean, violations, committed, context_injected, raw_response.
    expects_violation
        Pre-registered intent. Source: test case JSON turn.expects_violation.
    expected_violation_predicates
        Pre-registered predicate list for documentation and interpretability.
        The symbolic oracle — not this list — is the measurement truth source.
    oracle_violations
        Violation atom strings from the symbolic oracle.
        Conditions B/C: taken directly from turn_result.violations.
        Condition A: produced by run_silent_validation() in run_harness.py.
    oracle_violation_detected
        True if oracle_violations is non-empty.
        Gate for both VDR (denominator) and CVR (denominator gate).
    effectively_committed
        True if the violation committed to world state for CVR purposes.
        Condition A:    same as oracle_violation_detected.
        Conditions B/C: True only if turn_result.committed=True AND
                        oracle_violation_detected=True.
                        Under correct operation this should always be False.
    """
    test_case_id: str
    turn_number: int
    condition: str
    turn_result: TurnResult
    expects_violation: bool
    expected_violation_predicates: list
    oracle_violations: list
    oracle_violation_detected: bool
    effectively_committed: bool

    def to_dict(self) -> dict:
        """Serialize to a plain dict for JSON results output."""
        return {
            "test_case_id": self.test_case_id,
            "turn_number": self.turn_number,
            "condition": self.condition,
            "expects_violation": self.expects_violation,
            "expected_violation_predicates": self.expected_violation_predicates,
            "oracle_violations": self.oracle_violations,
            "oracle_violation_detected": self.oracle_violation_detected,
            "effectively_committed": self.effectively_committed,
            "turn_result": {
                "condition": self.turn_result.condition,
                "proposed_delta": self.turn_result.proposed_delta,
                "clean": self.turn_result.clean,
                "violations": self.turn_result.violations,
                "committed": self.turn_result.committed,
                "narrative": self.turn_result.narrative,
                "context_injected": self.turn_result.context_injected,
                # raw_response omitted from JSON output: verbose and redundant
                # with narrative for summary purposes.
            },
        }


# ── Silent oracle for Condition A ─────────────────────────────────────────────

def run_silent_validation(
    abox_path: str,
    rules_file: str,
    proposed_delta: dict,
) -> list:
    """
    Runs validate_delta() as a non-blocking observer; returns violation list.

    Used exclusively for Condition A turns. run_turn() never calls
    validate_delta() in Condition A — the harness calls this after run_turn()
    returns to obtain oracle classifications without blocking the delta.

    The ABox at call time is always the baseline in Condition A because
    Condition A never writes to abox.json. This produces the documented
    measurement gaps for state-dependent cases (see each case's condition_notes).

    Returns an empty list if proposed_delta is empty (nothing to validate).
    """
    if not proposed_delta:
        return []

    result = validate_delta(
        rules_file=rules_file,
        abox_path=abox_path,
        proposed_delta=proposed_delta,
    )
    return result.violations


# ── Metric computations ───────────────────────────────────────────────────────

def compute_cvr(records: list) -> float:
    """
    Constraint Violation Rate — primary metric.

    Denominator: turns where expects_violation=True AND oracle_violation_detected=True.
    Numerator:   of those, turns where effectively_committed=True.

    Returns float in [0.0, 1.0], or float('nan') if denominator is zero.
    nan means no oracle-confirmed violations occurred — investigate
    elicitation_rate before interpreting.
    """
    attempted = [
        r for r in records
        if r.expects_violation and r.oracle_violation_detected
    ]
    if not attempted:
        return float("nan")

    slipped = [r for r in attempted if r.effectively_committed]
    return len(slipped) / len(attempted)


def compute_vdr(records: list) -> float:
    """
    Violation Detection Rate — secondary metric.

    Denominator: all turns where expects_violation=True.
    Numerator:   of those, turns where oracle_violation_detected=True.

    Returns float in [0.0, 1.0], or float('nan') if denominator is zero.
    """
    designed = [r for r in records if r.expects_violation]
    if not designed:
        return float("nan")

    detected = [r for r in designed if r.oracle_violation_detected]
    return len(detected) / len(designed)


def compute_elicitation_rate(records: list) -> float:
    """
    Elicitation Rate — diagnostic (not pre-registered).

    Of violation-designed turns, what fraction produced a non-empty
    proposed_delta? Pre-oracle gate.

    Returns float in [0.0, 1.0], or float('nan') if denominator is zero.
    """
    designed = [r for r in records if r.expects_violation]
    if not designed:
        return float("nan")

    elicited = [r for r in designed if r.turn_result.proposed_delta]
    return len(elicited) / len(designed)


# ── Results formatting ────────────────────────────────────────────────────────

def _fmt(value: float, width: int = 6) -> str:
    """Format a float for the summary table, handling nan gracefully."""
    if value != value:          # nan != nan is True in IEEE 754
        return "N/A".ljust(width)
    return f"{value:.3f}".ljust(width)


def format_results_table(records_by_condition: dict) -> str:
    """
    Returns a formatted plaintext summary table for stdout.

    Parameters
    ──────────
    records_by_condition : {"A": [TurnRecord, ...], "B": [...], "C": [...]}
    """
    lines = [
        "",
        "╔══════════════════════════════════════════════════════════════════╗",
        "║          VeriForge OQ-09 Ablation — Metric Summary              ║",
        "╠═══════════╦══════════╦══════════╦═══════════════╦═══════════════╣",
        "║ Condition ║  CVR     ║  VDR     ║  Elicitation  ║  Turns        ║",
        "╠═══════════╬══════════╬══════════╬═══════════════╬═══════════════╣",
    ]

    for cond in ("A", "B", "C"):
        records = records_by_condition.get(cond, [])
        if not records:
            lines.append(
                f"║     {cond}     ║  (none)  ║  (none)  "
                f"║  (none)       ║  0            ║"
            )
            continue

        cvr    = compute_cvr(records)
        vdr    = compute_vdr(records)
        elicit = compute_elicitation_rate(records)
        n      = len(records)

        lines.append(
            f"║     {cond}     ║  {_fmt(cvr)}  ║  {_fmt(vdr)}  "
            f"║  {_fmt(elicit, 9)}    ║  {str(n).ljust(13)} ║"
        )

    lines.append(
        "╚═══════════╩══════════╩══════════╩═══════════════╩═══════════════╝"
    )

    # ── Falsification checks (pre-registered) ─────────────────────────────
    cvr_a = compute_cvr(records_by_condition.get("A", []))
    cvr_b = compute_cvr(records_by_condition.get("B", []))
    cvr_c = compute_cvr(records_by_condition.get("C", []))

    lines.append("")

    if cvr_a == cvr_a and cvr_c == cvr_c:      # neither is nan
        if cvr_a > 0:
            reduction = (cvr_a - cvr_c) / cvr_a
            met = reduction >= 0.75
            lines.append(
                f"  OQ-09 primary threshold (>=75% CVR reduction A→C): "
                f"CVR_A={cvr_a:.3f}  CVR_C={cvr_c:.3f}  "
                f"reduction={reduction:.1%}  {'✓ MET' if met else '✗ NOT MET'}"
            )
        else:
            lines.append(
                "  OQ-09 primary threshold: CVR_A=0.000 — no slipped violations "
                "under Condition A. Check elicitation_rate."
            )

    if cvr_b == cvr_b and cvr_c == cvr_c:
        b_gt_c = cvr_b > cvr_c
        lines.append(
            f"  Directionality check (CVR_B > CVR_C): "
            f"CVR_B={cvr_b:.3f}  CVR_C={cvr_c:.3f}  "
            f"{'✓ MET' if b_gt_c else '— not met (or equal)'}"
        )

    lines.append("")
    return "\n".join(lines)


def build_summary_dict(
    records_by_condition: dict,
    model: str,
    total_test_cases: int,
) -> dict:
    """
    Returns a structured dict suitable for JSON results output.

    nqs_scores for each condition is an empty list to be populated manually
    by the developer after the run — one integer (1–5) per test case.
    """
    results = {}

    for cond, records in records_by_condition.items():
        cvr    = compute_cvr(records)
        vdr    = compute_vdr(records)
        elicit = compute_elicitation_rate(records)

        n_designed = sum(1 for r in records if r.expects_violation)
        n_detected = sum(1 for r in records if r.expects_violation and r.oracle_violation_detected)
        n_slipped  = sum(1 for r in records if r.expects_violation and r.effectively_committed)

        results[cond] = {
            "cvr":                      None if cvr    != cvr    else round(cvr,    4),
            "vdr":                      None if vdr    != vdr    else round(vdr,    4),
            "elicitation_rate":         None if elicit != elicit else round(elicit, 4),
            "turns_total":              len(records),
            "turns_violation_designed": n_designed,
            "turns_oracle_detected":    n_detected,
            "turns_slipped":            n_slipped,
            "nqs_scores":               [],   # populated manually post-run
        }

    # Falsification summary
    cvr_a = results.get("A", {}).get("cvr")
    cvr_b = results.get("B", {}).get("cvr")
    cvr_c = results.get("C", {}).get("cvr")
    falsification = None

    if cvr_a is not None and cvr_c is not None and cvr_a > 0:
        reduction = (cvr_a - cvr_c) / cvr_a
        falsification = {
            "cvr_A":                  cvr_a,
            "cvr_B":                  cvr_b,
            "cvr_C":                  cvr_c,
            "reduction_A_to_C":       round(reduction, 4),
            "threshold_75pct_met":    reduction >= 0.75,
            "directionality_B_gt_C":  (
                (cvr_b > cvr_c) if (cvr_b is not None and cvr_c is not None)
                else None
            ),
        }

    return {
        "model":            model,
        "total_test_cases": total_test_cases,
        "conditions_run":   sorted(records_by_condition.keys()),
        "results":          results,
        "falsification_check": falsification,
    }
