"""
VeriForge Phase 4 — Evaluation Harness Orchestrator
prototype/harness/run_harness.py

Runs the OQ-09 three-condition ablation study.

WHAT THIS DOES
──────────────
For each requested condition (A, B, C):
  For each pre-registered test case (12 total):
    1. Reset abox.json to baseline (in-memory copy from harness startup).
    2. If Condition B: build session_context once from the baseline ABox.
    3. For each turn in the test case: call session_loop.run_turn().
    4. If Condition A: call run_silent_validation() to get oracle
       classifications (validate_delta() is never called inside run_turn()
       for Condition A — see session_loop.py Condition A early return).
    5. Assemble TurnRecord with all measurement fields populated.
  Compute CVR, VDR, elicitation_rate across all TurnRecords for this condition.
Write results files and print summary table with falsification check.

DESIGN DECISIONS
─────────────────
See implementation-log.md IMP-I05-D01 through IMP-I05-D04.

USAGE
─────
Run from the project root (where prototype/ is visible as a package):

  # Full ablation — all three conditions:
  python -m prototype.harness.run_harness

  # Single condition (useful for incremental verification):
  python -m prototype.harness.run_harness --conditions A
  python -m prototype.harness.run_harness --conditions A C

  # Dry run — no LLM API calls, no cost, verifies infrastructure only:
  python -m prototype.harness.run_harness --dry-run --conditions A

  # Override model for a run (default is claude-sonnet-4-6 for Phase 4):
  python -m prototype.harness.run_harness --model claude-haiku-4-5-20251001

OUTPUTS
───────
  results/run_<timestamp>_full.json    — all TurnRecords, one array per condition
  results/run_<timestamp>_summary.json — CVR/VDR table + falsification check
  stdout                               — per-turn progress log + summary table

  After a run completes, open the summary JSON and populate the nqs_scores
  list for each condition with one Likert score (1–5) per test case.

DRY-RUN NOTE
────────────
In dry-run mode, call_llm() is patched with a function that returns a fixed
guard→cellar response. This exercises the full pipeline (parse → validate →
commit gate → TurnRecord → metrics) without API calls. Dry-run CVR and VDR
figures are not meaningful — they exist only to confirm the infrastructure
runs without errors before spending API credits.
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path


# ── Import path setup ──────────────────────────────────────────────────────────
# This file lives at prototype/harness/run_harness.py.
# We need imports from three distinct locations:
#   session_loop           → prototype/session_loop.py
#   tavern.validator       → prototype/tavern/validator.py  (via session_loop)
#   harness.metrics        → prototype/harness/metrics.py
#
# Adding both the project root and prototype/ to sys.path covers all three.

HARNESS_DIR   = Path(__file__).resolve().parent        # prototype/harness/
PROTOTYPE_DIR = HARNESS_DIR.parent                     # prototype/
PROJECT_ROOT  = PROTOTYPE_DIR.parent                   # veriforge/

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROTOTYPE_DIR))

import session_loop                                     # noqa: E402
from session_loop import run_turn, build_context_string # noqa: E402
from harness.metrics import (                           # noqa: E402
    TurnRecord,
    run_silent_validation,
    compute_cvr,
    compute_vdr,
    format_results_table,
    build_summary_dict,
)


# ── Constants ──────────────────────────────────────────────────────────────────

# Phase 4 model (IMP-I05-D01 / IMP-I04-D04).
# Patches session_loop.MODEL at harness startup so all run_turn() calls
# use this model. session_loop defaults to claude-haiku-4-5-20251001
# (Phase 3 development model); the frontier model is required for Phase 4.
PHASE_4_MODEL = "claude-sonnet-4-6"

# All paths relative to PROJECT_ROOT so the harness is runnable from the
# project root regardless of the working directory at invocation.
ABOX_PATH      = PROJECT_ROOT / "prototype" / "tavern" / "abox.json"
RULES_FILE     = PROJECT_ROOT / "prototype" / "tavern" / "tavern_rules.lp"
TEST_CASES_DIR = HARNESS_DIR  / "test_cases"
RESULTS_DIR    = PROJECT_ROOT / "results"


# ── Dry-run mock ───────────────────────────────────────────────────────────────
# The dry-run mock always returns a guard→cellar response (a known A1 violation).
# This exercises every path in the pipeline without API calls:
#   Condition A: oracle detects A1; effectively_committed=True; CVR contribution.
#   Conditions B/C: validator blocks A1; committed=False; CVR contribution zero.

_DRY_RUN_RESPONSE = """\
<narrative>
The guard moves toward the cellar, pushing open the heavy door.
</narrative>
<delta>
{"character_locations": {"guard": "cellar"}}
</delta>
"""


def _mock_call_llm(system: str, user_content: str) -> str:
    """Drop-in replacement for session_loop.call_llm() in dry-run mode."""
    time.sleep(0.05)    # Simulate network latency; makes progress output readable.
    return _DRY_RUN_RESPONSE


# ── ABox management ────────────────────────────────────────────────────────────

def load_baseline_abox(abox_path: Path) -> dict:
    """
    Reads abox.json into memory as the canonical baseline state (IMP-I05-D04).

    Called once at harness startup, before any test case runs.
    All subsequent test case resets write this dict back to disk.
    If you need to modify the world's starting configuration, edit abox.json
    before running the harness — the in-memory baseline is taken from whatever
    abox.json contains at startup.
    """
    with open(abox_path) as f:
        return json.load(f)


def reset_abox(abox_path: Path, baseline: dict) -> None:
    """
    Writes the baseline dict back to abox.json.

    Called before every test case so each case starts from identical world
    state. This is the only place in the harness that writes to abox.json
    directly — commit_to_abox() inside run_turn() is the other write path,
    but that fires only on clean validated deltas in Conditions B and C.
    """
    with open(abox_path, "w") as f:
        json.dump(baseline, f, indent=2)


# ── Test case loading ──────────────────────────────────────────────────────────

def load_test_cases(test_cases_dir: Path) -> list:
    """
    Loads all tc-*.json files from test_cases_dir, sorted by filename.

    Alphabetical sort gives consistent ordering: tc-a01 through tc-m04.
    Returns a list of parsed JSON dicts, one per test case.
    """
    files = sorted(test_cases_dir.glob("tc-*.json"))
    if not files:
        raise FileNotFoundError(
            f"No test case files found in {test_cases_dir}.\n"
            "Run from the project root and verify that "
            "prototype/harness/test_cases/ contains tc-*.json files."
        )
    cases = []
    for f in files:
        with open(f) as fh:
            cases.append(json.load(fh))
    return cases


# ── Core per-turn execution ────────────────────────────────────────────────────

def execute_turn(
    turn_spec: dict,
    test_case_id: str,
    condition: str,
    abox_path: Path,
    rules_file: Path,
    session_context: str,
) -> TurnRecord:
    """
    Executes one turn and returns a fully populated TurnRecord.

    Calls run_turn() from session_loop, then enriches the result with
    oracle classifications (for Condition A) and assembles TurnRecord
    with all CVR/VDR measurement fields.

    Parameters
    ──────────
    turn_spec       : One element from test_case["turns"].
    test_case_id    : Parent test case identifier, e.g. "tc-a01".
    condition       : "A", "B", or "C".
    abox_path       : Current abox.json path.
    rules_file      : tavern_rules.lp path.
    session_context : Pre-built context string for Condition B; empty for A and C.
    """
    turn_number          = turn_spec["turn"]
    prompt               = turn_spec["prompt"]
    expects_violation    = turn_spec["expects_violation"]
    expected_predicates  = turn_spec.get("expected_violation_predicates", [])

    # ── Call the session loop ─────────────────────────────────────────────
    # run_turn() executes all four stages and returns a TurnResult.
    # For Condition A: violations=[], committed=False always (early return
    # before Stage 4b in session_loop.py).
    result = run_turn(
        abox_path=str(abox_path),
        rules_file=str(rules_file),
        user_prompt=prompt,
        condition=condition,
        session_context=session_context,
    )

    # ── Oracle classification ─────────────────────────────────────────────
    # Conditions B/C: validate_delta() ran inside run_turn(); violations
    # are already in result.violations.
    #
    # Condition A: validate_delta() was never called. We call it now as a
    # silent post-hoc observer (IMP-I05-D03). The ABox is still the baseline
    # because Condition A never writes it.
    if condition == "A":
        oracle_violations = run_silent_validation(
            abox_path=str(abox_path),
            rules_file=str(rules_file),
            proposed_delta=result.proposed_delta,
        )
    else:
        oracle_violations = result.violations

    oracle_detected = len(oracle_violations) > 0

    # ── effectively_committed ─────────────────────────────────────────────
    # Condition A: nothing can block a violation — if the oracle detects
    # one, it effectively committed (even though committed=False in the
    # TurnResult, since Condition A never writes the ABox).
    #
    # Conditions B/C: a violation slips through only if the validator
    # missed it (committed=True AND oracle_detected). Under correct
    # VeriForge operation this should never be True.
    if condition == "A":
        effectively_committed = oracle_detected
    else:
        effectively_committed = result.committed and oracle_detected

    return TurnRecord(
        test_case_id=test_case_id,
        turn_number=turn_number,
        condition=condition,
        turn_result=result,
        expects_violation=expects_violation,
        expected_violation_predicates=expected_predicates,
        oracle_violations=oracle_violations,
        oracle_violation_detected=oracle_detected,
        effectively_committed=effectively_committed,
    )


# ── Per-test-case execution ────────────────────────────────────────────────────

def run_test_case(
    test_case: dict,
    condition: str,
    abox_path: Path,
    rules_file: Path,
    baseline_abox: dict,
) -> list:
    """
    Runs all turns of one test case under one condition.

    Resets the ABox to baseline before the first turn.
    Builds session_context for Condition B from the reset (baseline) ABox.
    Returns a list of TurnRecords, one per turn.

    Condition B mechanics
    ─────────────────────
    build_context_string() reads abox.json at call time. Calling it once
    from the baseline state — before any turn commits a delta — is the
    correct Condition B semantics: context is generated once at session
    start from the initial state and never updated thereafter.

    For Condition C, run_turn() calls build_context_string() internally
    on each turn from the live (potentially updated) ABox. session_context
    is passed as an empty string; run_turn() ignores it for Condition C.
    """
    case_id = test_case["id"]

    if test_case.get("reset_abox", True):
        reset_abox(abox_path, baseline_abox)

    session_context = (
        build_context_string(str(abox_path)) if condition == "B" else ""
    )

    records = []

    for turn_spec in test_case["turns"]:
        turn_num  = turn_spec["turn"]
        expects   = turn_spec["expects_violation"]
        viol_marker = "⚠" if expects else " "

        print(
            f"  [{condition}] {case_id} turn {turn_num} {viol_marker}  "
            f"{turn_spec['prompt'][:65]}"
            f"{'…' if len(turn_spec['prompt']) > 65 else ''}",
            end="",
            flush=True,
        )

        record = execute_turn(
            turn_spec=turn_spec,
            test_case_id=case_id,
            condition=condition,
            abox_path=abox_path,
            rules_file=rules_file,
            session_context=session_context,
        )

        # ── Per-turn result line ───────────────────────────────────────────
        if expects:
            if record.oracle_violation_detected:
                if record.effectively_committed:
                    outcome = "  → ✗ SLIPPED"
                else:
                    blocked_by = ", ".join(record.oracle_violations)
                    outcome = f"  → ✓ blocked ({blocked_by})"
            else:
                delta_preview = str(record.turn_result.proposed_delta)[:40]
                outcome = f"  → — no oracle violation (delta: {delta_preview})"
        else:
            if record.oracle_violation_detected:
                # A violation on a clean-designed turn is unexpected.
                # Could be a test case design error or an unintended interaction.
                outcome = f"  → ⚠ UNEXPECTED: {record.oracle_violations}"
            else:
                outcome = "  → ✓ clean"

        print(outcome)
        records.append(record)

    return records


# ── Per-condition execution ────────────────────────────────────────────────────

def run_condition(
    condition: str,
    test_cases: list,
    abox_path: Path,
    rules_file: Path,
    baseline_abox: dict,
) -> list:
    """
    Runs all 12 test cases under one condition.

    Returns a flat list of all TurnRecords for that condition.
    """
    labels = {
        "A": "Raw LLM — no context injection, no validation",
        "B": "Session-start injection — context built once, validation active",
        "C": "Full VeriForge — per-turn injection, validation active",
    }

    print(f"\n{'═' * 70}")
    print(f"  CONDITION {condition}  —  {labels[condition]}")
    print(f"{'═' * 70}\n")

    all_records = []
    for test_case in test_cases:
        records = run_test_case(
            test_case=test_case,
            condition=condition,
            abox_path=abox_path,
            rules_file=rules_file,
            baseline_abox=baseline_abox,
        )
        all_records.extend(records)

    cvr = compute_cvr(all_records)
    vdr = compute_vdr(all_records)
    cvr_str = f"{cvr:.3f}" if cvr == cvr else "N/A"
    vdr_str = f"{vdr:.3f}" if vdr == vdr else "N/A"
    print(f"\n  Condition {condition} complete — CVR: {cvr_str}  VDR: {vdr_str}\n")

    return all_records


# ── Results output ─────────────────────────────────────────────────────────────

def save_results(
    records_by_condition: dict,
    model: str,
    total_test_cases: int,
    timestamp: str,
) -> None:
    """
    Writes two results files to RESULTS_DIR, creating it if needed.

      run_<timestamp>_full.json    — every TurnRecord serialized to JSON
      run_<timestamp>_summary.json — CVR/VDR table and falsification check

    After writing, print the file paths so they are visible in the terminal log.
    """
    RESULTS_DIR.mkdir(exist_ok=True)

    full_path = RESULTS_DIR / f"run_{timestamp}_full.json"
    full_data = {
        cond: [r.to_dict() for r in records]
        for cond, records in records_by_condition.items()
    }
    with open(full_path, "w") as f:
        json.dump(full_data, f, indent=2)

    summary_path = RESULTS_DIR / f"run_{timestamp}_summary.json"
    summary = build_summary_dict(
        records_by_condition=records_by_condition,
        model=model,
        total_test_cases=total_test_cases,
    )
    summary["timestamp"]          = timestamp
    summary["full_results_file"]  = str(full_path.name)
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n  Results written:")
    print(f"    Full:    {full_path}")
    print(f"    Summary: {summary_path}")


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="VeriForge Phase 4 — OQ-09 Ablation Harness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full ablation — all three conditions:
  python -m prototype.harness.run_harness

  # Single condition (cheapest entry point; run A first):
  python -m prototype.harness.run_harness --conditions A

  # Dry run — verifies pipeline without API calls:
  python -m prototype.harness.run_harness --dry-run --conditions A

  # Override model:
  python -m prototype.harness.run_harness --model claude-haiku-4-5-20251001
        """,
    )
    parser.add_argument(
        "--conditions",
        nargs="+",
        choices=["A", "B", "C"],
        default=["A", "B", "C"],
        help="Conditions to run (default: all three).",
    )
    parser.add_argument(
        "--model",
        default=PHASE_4_MODEL,
        help=f"Anthropic model string (default: {PHASE_4_MODEL}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Mock the LLM with a fixed guard→cellar response. "
            "Verifies harness infrastructure without API calls. "
            "CVR/VDR figures are not meaningful in this mode."
        ),
    )
    args = parser.parse_args()

    # ── Model override (IMP-I05-D01) ──────────────────────────────────────
    # Patching the module-level constant before any run_turn() call ensures
    # all turns in this run use the specified model.
    session_loop.MODEL = args.model

    # ── Dry-run mock ──────────────────────────────────────────────────────
    if args.dry_run:
        session_loop.call_llm = _mock_call_llm
        print("\n  ⚠ DRY-RUN MODE — LLM calls mocked; metrics not meaningful.\n")

    # ── Pre-flight checks ─────────────────────────────────────────────────
    for path, label in [
        (ABOX_PATH,      "prototype/tavern/abox.json"),
        (RULES_FILE,     "prototype/tavern/tavern_rules.lp"),
        (TEST_CASES_DIR, "prototype/harness/test_cases/"),
    ]:
        if not path.exists():
            print(f"ERROR: {label} not found at {path}.")
            print("Run this script from the project root.")
            sys.exit(1)

    # ── Load test cases and baseline ABox ─────────────────────────────────
    test_cases    = load_test_cases(TEST_CASES_DIR)
    baseline_abox = load_baseline_abox(ABOX_PATH)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\nVeriForge OQ-09 Ablation Harness")
    print(f"  Model:      {args.model}")
    print(f"  Conditions: {' '.join(args.conditions)}")
    print(f"  Test cases: {len(test_cases)}")
    print(f"  Timestamp:  {timestamp}")
    if args.dry_run:
        print("  Mode:       DRY RUN")

    # ── Run requested conditions ──────────────────────────────────────────
    records_by_condition: dict = {}

    try:
        for condition in args.conditions:
            records_by_condition[condition] = run_condition(
                condition=condition,
                test_cases=test_cases,
                abox_path=ABOX_PATH,
                rules_file=RULES_FILE,
                baseline_abox=baseline_abox,
            )
    except KeyboardInterrupt:
        print("\n\n  Interrupted. Saving partial results…\n")

    # ── Output ────────────────────────────────────────────────────────────
    if records_by_condition:
        print(format_results_table(records_by_condition))
        save_results(
            records_by_condition=records_by_condition,
            model=args.model,
            total_test_cases=len(test_cases),
            timestamp=timestamp,
        )

    # ── Restore ABox to baseline ──────────────────────────────────────────
    # Conditions B and C may have modified abox.json during the run.
    # Restoring to baseline leaves the working tree clean.
    reset_abox(ABOX_PATH, baseline_abox)
    print("\n  abox.json restored to baseline.\n")


if __name__ == "__main__":
    main()
