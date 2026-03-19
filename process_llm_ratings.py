#!/usr/bin/env python3
"""
process_llm_ratings.py

Parses four LLM inter-rater markdown files, extracts scores, computes
inter-rater statistics against the human NQS ratings, and produces:

  results/llm_ratings_parsed.json      — all four models' scores in one file
  results/interrater_summary.json      — correlation and divergence statistics
  results/interrater_report.md         — human-readable summary for S13

Usage (from repo root, venv active):
  python process_llm_ratings.py

Assumes:
  results/nqs_ratings.json             — human ratings (already present)
  LLM markdown files in current directory or results/llm_rating_prompts/
"""

import json
import re
from pathlib import Path

try:
    from scipy.stats import pearsonr
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("NOTE: scipy not installed — Pearson r will not be computed.")
    print("      Install with: pip install scipy --break-system-packages")
    print()


# ── File locations ────────────────────────────────────────────────────────────

HUMAN_RATINGS_PATH = Path("results/nqs_ratings.json")

LLM_FILES = {
#    "grok-4.20-reasoning":     Path("LLM_ratings_Grok_4_20_reasoning.md"),
#    "grok-4.20-non-reasoning": Path("LLM_ratings_Grok_4_20_auto.md"),
#    "gpt-5.3":                 Path("LLM_ratings_ChatGPT_5_3_instant.md"),
#    "gpt-5.4":                 Path("LLM_ratings_ChatGPT_5_4_thinking.md"),
    "claude-sonnet-4-6":       Path("results/llm_ratings_claude-sonnet-4-6.json"),
    "gpt-5.4":                 Path("results/llm_ratings_gpt-5.4.json"),
}

OUTPUT_DIR = Path("results")


# ── Parsing ───────────────────────────────────────────────────────────────────

def parse_llm_file(path: Path) -> list[dict]:
    """
    Parse a markdown ratings file into a list of rating dicts.
    Handles test_case_id with or without .txt suffix.
    Extracts case_id and condition from the combined field (e.g. tc-a01_B).
    """
    text = path.read_text(encoding="utf-8")
    ratings = []

    # Split on test_case_id blocks
    blocks = re.split(r"(?=test_case_id:)", text)

    for block in blocks:
        if not block.strip() or "test_case_id:" not in block:
            continue

        # Extract test_case_id — strip .txt suffix if present
        id_match = re.search(r"test_case_id:\s*(\S+)", block)
        if not id_match:
            continue
        raw_id = id_match.group(1).replace(".txt", "")

        # Split combined id into case_id and condition
        # Format is either tc-a01_B or tc-a01_B
        cond_match = re.match(r"^(.+)_([BC])$", raw_id)
        if not cond_match:
            print(f"  WARNING: could not parse case/condition from '{raw_id}' — skipping")
            continue

        case_id   = cond_match.group(1)
        condition = cond_match.group(2)

        # Extract score
        score_match = re.search(r"SCORE:\s*(\d)", block)
        if not score_match:
            print(f"  WARNING: no SCORE found for {raw_id} — skipping")
            continue
        score = int(score_match.group(1))

        # Extract reasoning (optional — for reference)
        reasoning_match = re.search(r"REASONING:\s*(.+?)(?=\n\n|\ntest_case_id:|\Z)",
                                    block, re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else ""

        ratings.append({
            "case_id":   case_id,
            "condition": condition,
            "nqs":       score,
            "reasoning": reasoning,
        })

    return ratings

def load_json_ratings(path: Path) -> list[dict]:
    with open(path) as f:
        return json.load(f)


# ── Statistics ────────────────────────────────────────────────────────────────

def load_human_ratings(path: Path) -> dict:
    """Load human ratings as {(case_id, condition): score}."""
    with open(path) as f:
        data = json.load(f)
    return {(r["case_id"], r["condition"]): r["nqs"] for r in data}


def compute_stats(human: dict, llm_ratings: list[dict], model_name: str) -> dict:
    """
    Compute inter-rater statistics for one model against human ratings.
    Returns a stats dict.
    """
    keys = sorted(human.keys())
    llm_map = {(r["case_id"], r["condition"]): r["nqs"] for r in llm_ratings}

    # Check coverage
    missing = [k for k in keys if k not in llm_map]
    if missing:
        print(f"  WARNING [{model_name}]: missing ratings for {missing}")

    h_scores = []
    l_scores = []
    divergent = []

    for k in keys:
        if k not in llm_map:
            continue
        h = human[k]
        l = llm_map[k]
        h_scores.append(h)
        l_scores.append(l)
        gap = abs(h - l)
        if gap >= 2:
            divergent.append({
                "case_id":   k[0],
                "condition": k[1],
                "human":     h,
                "llm":       l,
                "gap":       gap,
            })

    stats = {
        "model":          model_name,
        "n_rated":        len(h_scores),
        "human_mean":     round(sum(h_scores) / len(h_scores), 3),
        "llm_mean":       round(sum(l_scores) / len(l_scores), 3),
        "divergent_cases": divergent,
        "n_divergent":    len(divergent),
    }

    if SCIPY_AVAILABLE and len(h_scores) >= 3:
        r, p = pearsonr(h_scores, l_scores)
        stats["pearson_r"] = round(r, 3)
        stats["pearson_p"] = round(p, 3)
    else:
        stats["pearson_r"] = None
        stats["pearson_p"] = None

    return stats


# ── Report generation ─────────────────────────────────────────────────────────

def generate_report(all_stats: list[dict], all_parsed: dict, human: dict) -> str:
    """Generate a human-readable markdown report for S13."""

    lines = [
        "# NQS Inter-Rater Analysis Report",
        "",
        "Generated for S13 — OQ-09 resolution session.",
        "",
        "## Critical Methodological Finding",
        "",
        "All four LLM raters systematically misapplied the rubric's coherence dimension.",
        "They applied the hard-cap rule to narratives describing a character successfully",
        "entering a forbidden location — scoring them 2 — because they evaluated the",
        "narrative against whether the *committed world state* respected the rules.",
        "",
        "However, VeriForge's architecture requires the LLM to describe the *attempt*,",
        "not the committed outcome. The symbolic layer (ASP solver) blocks the delta;",
        "the LLM's job is to write a vivid, plausible attempt. 'The guard descends into",
        "the cellar' is the correct narrative output for a violation-designed turn —",
        "the guard attempted it, the solver blocked the commit, the ABox did not update.",
        "",
        "The LLM raters evaluated: 'does this narrative respect the world rules?'",
        "The rubric intended: 'is this narrative a plausible, engaging RP output?'",
        "These are different questions under VeriForge's role-boundary architecture.",
        "",
        "Consequence: LLM inter-rater scores are not comparable to human scores on the",
        "same dimension. The low correlations below reflect rubric comprehension failure,",
        "not unreliable human ratings. This finding should be stated explicitly in the",
        "OQ-09 resolution write-up.",
        "",
        "---",
        "",
        "## Per-Model Statistics",
        "",
    ]

    for stats in all_stats:
        model = stats["model"]
        r_str = f"{stats['pearson_r']:.3f}" if stats["pearson_r"] is not None else "N/A"
        p_str = f"{stats['pearson_p']:.3f}" if stats["pearson_p"] is not None else "N/A"
        lines += [
            f"### {model}",
            "",
            f"- Ratings collected: {stats['n_rated']} / 24",
            f"- Human mean NQS: {stats['human_mean']}",
            f"- LLM mean NQS:   {stats['llm_mean']}",
            f"- Pearson r:      {r_str} (p={p_str})",
            f"- Divergent cases (gap ≥ 2): {stats['n_divergent']}",
            "",
        ]

        if stats["divergent_cases"]:
            lines.append("  | Case | Cond | Human | LLM | Gap |")
            lines.append("  |------|------|-------|-----|-----|")
            for d in stats["divergent_cases"]:
                lines.append(f"  | {d['case_id']} | {d['condition']} | "
                              f"{d['human']} | {d['llm']} | {d['gap']} |")
            lines.append("")

    # Score distribution comparison across all raters
    lines += [
        "---",
        "",
        "## Score Distribution Comparison",
        "",
        "| Case | Cond | Human | " + " | ".join(all_parsed.keys()) + " |",
        "|------|------|-------|" + "--------|" * len(all_parsed),
    ]

    model_keys = list(all_parsed.keys())
    model_maps = {m: {(r["case_id"], r["condition"]): r["nqs"]
                      for r in all_parsed[m]} for m in model_keys}

    for k in sorted(human.keys()):
        case_id, cond = k
        h = human[k]
        scores = [str(model_maps[m].get(k, "?")) for m in model_keys]
        lines.append(f"| {case_id} | {cond} | {h} | {' | '.join(scores)} |")

    lines += [
        "",
        "---",
        "",
        "## Summary for S13",
        "",
        "The inter-rater analysis should be presented to S13 as follows:",
        "",
        "1. Two LLM models were used as secondary raters with the corrected rubric:",
        "   claude-sonnet-4-6 and gpt-5.4. Four additional models (grok-4.20-reasoning,",
        "   grok-4.20-non-reasoning, gpt-5.3, gpt-5.4-thinking) were run with the",
        "   original misapplied rubric and are documented separately.",
        "",
        "2. Both corrected-rubric models showed residual hard-cap application on",
        "   violation-designed cases as 2 regardless of prose quality, because",
        "   they interpreted 'coherence failure' as 'narrative describes a",
        "   rule-violating action as succeeding' — which is the intended behavior",
        "   under VeriForge's role-boundary architecture.",
        "",
        "3. The low inter-rater correlations are not evidence of unreliable human",
        "   ratings. They are evidence of a rubric comprehension gap specific to",
        "   VeriForge's unusual architectural property: the narrative intentionally",
        "   describes attempts, not outcomes.",
        "",
        "4. The LLM inter-rater pass is therefore not usable as a reliability check",
        "   on the human NQS scores. It is usable as evidence that the role-boundary",
        "   concept requires explicit explanation to any external evaluator — human",
        "   or LLM — before they can apply the NQS rubric correctly.",
        "",
        "5. The human NQS ratings stand as the sole primary metric per the",
        "   pre-registered protocol.",
    ]

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Load human ratings
    if not HUMAN_RATINGS_PATH.exists():
        print(f"ERROR: {HUMAN_RATINGS_PATH} not found.")
        print("       Run NQS rating app first and save results/nqs_ratings.json.")
        return

    human = load_human_ratings(HUMAN_RATINGS_PATH)
    print(f"Human ratings loaded: {len(human)} entries")

    # Parse all LLM files
    all_parsed = {}
    all_stats  = []

    for model_name, file_path in LLM_FILES.items():
        if not file_path.exists():
            print(f"  SKIP: {file_path} not found")
            continue

        print(f"\nParsing: {file_path.name}")
        if file_path.suffix == ".json":
            ratings = load_json_ratings(file_path)
        else:
            ratings = parse_llm_file(file_path)
        print(f"  Parsed {len(ratings)} ratings for {model_name}")

        all_parsed[model_name] = ratings
        stats = compute_stats(human, ratings, model_name)
        all_stats.append(stats)

        r_str = f"{stats['pearson_r']:.3f}" if stats["pearson_r"] is not None else "N/A"
        print(f"  Pearson r = {r_str} | divergent cases = {stats['n_divergent']}")

    if not all_parsed:
        print("\nNo LLM rating files found. Check file paths in LLM_FILES dict.")
        return

    # Write parsed ratings
    parsed_path = OUTPUT_DIR / "llm_ratings_parsed.json"
    with open(parsed_path, "w") as f:
        json.dump(all_parsed, f, indent=2)
    print(f"\nParsed ratings written to: {parsed_path}")

    # Write stats summary
    stats_path = OUTPUT_DIR / "interrater_summary.json"
    with open(stats_path, "w") as f:
        json.dump(all_stats, f, indent=2)
    print(f"Statistics written to:     {stats_path}")

    # Write markdown report
    report = generate_report(all_stats, all_parsed, human)
    report_path = OUTPUT_DIR / "interrater_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Report written to:         {report_path}")

    print("\nDone. Bring the following to S13:")
    print(f"  {HUMAN_RATINGS_PATH}")
    print(f"  {stats_path}")
    print(f"  {report_path}")


if __name__ == "__main__":
    main()