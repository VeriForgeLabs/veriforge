#!/usr/bin/env python3
"""
generate_llm_rating_prompts.py

Reads the full harness results JSON and produces one self-contained prompt
file per case-condition pair (24 total) for LLM inter-rater NQS scoring.

Each prompt is blind to the other condition for the same case.
ABox state is tracked turn-by-turn from committed deltas so the rater
has the correct world state at each turn.

Usage (from repo root, venv active):
  python generate_llm_rating_prompts.py results/run_20260318_150753_full.json

Output: results/llm_rating_prompts/
  tc-a01_B.txt, tc-a01_C.txt, tc-a02_B.txt, ... (24 files)
  _batch_all.txt  — all 24 prompts concatenated with separators (for API use)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from copy import deepcopy


# ── World knowledge (encoded once, embedded in every prompt) ──────────────────

WORLD_RULES = """
WORLD RULES
===========
The tavern world has three characters, four locations, and three hard rules.

Characters:
  - innkeeper  — has cellar access
  - guard      — does NOT have cellar access
  - patron     — does NOT have cellar access

Locations and adjacency (movement is only permitted between adjacent locations):
  - entrance   ↔ main_hall
  - main_hall  ↔ cellar
  - main_hall  ↔ back_room
  (back_room and cellar are NOT adjacent — the only path between them runs through main_hall)

The three hard rules:
  Rule A1 — Cellar access: only the innkeeper may be in the cellar.
             Any other character in the cellar is a violation.
  Rule A2 — Dead characters stay put: a dead character cannot have a location.
             Death is represented by absence from the alive list.
             If a dead character appears at any location, this rule is violated.
  Rule B1 — No teleporting: a character may only move between adjacent locations.
             A move between non-adjacent locations is a violation regardless of intent.
""".strip()

RUBRIC = """
RATING RUBRIC
=============
Rate on a 1–5 integer scale. Three dimensions contribute to the score.
A serious failure on any single dimension caps the score at 3 or below.

Dimension 1 — Spatial and causal coherence (weight: 40%)
  Does the narrative correctly reflect the world state?
  Characters should be where the ABox places them at each turn.
  Movements should respect the adjacency topology.
  A narrative that places a character in the wrong room, or ignores a death,
  fails this dimension regardless of prose quality.

Dimension 2 — Constraint handling naturalness (weight: 35%)
  Applies only to violation-designed turns. On clean turns, mark N/A.
  When an action is blocked, does the narrative handle the attempt as a
  natural story beat rather than a robotic refusal or invisible wall?
  "The guard reaches for a bolted door" scores higher than "the guard cannot enter."
  A self-censored empty output or a narrative that pre-emptively describes
  failure without attempting the action scores 1 on this dimension.

Dimension 3 — Engagement and narrative momentum (weight: 25%)
  Does the prose sustain interest across all turns?
  Look for: environmental detail, secondary characters, sensory texture,
  multiple action beats per turn, scene advancement.
  Tunnel-vision prose that ignores the tavern environment scores lower.

Scale anchors:
  5 — Fully grounded; blocking reads as a natural story beat; vivid detail;
      would sustain a real roleplay session.
  4 — Grounded with minor ambiguity; blocking readable if unremarkable;
      competent prose with some texture.
  3 — One coherence issue OR mechanical blocking OR flat/formulaic prose.
      Functional but would not sustain engagement over time.
  2 — Significant coherence failure OR refusal-style blocking OR
      repetitive tunnel-vision prose with no environmental awareness.
  1 — Incoherent world state, wrong characters, empty output, or refusal prose.
      Unusable as roleplay output.

Hard cap rule:
  A single serious coherence failure (wrong character position, dead character
  with location, non-adjacent move described as successful) cannot score above 3
  regardless of engagement quality.

IMPORTANT INSTRUCTIONS
======================
- Score the output AS-IS. Do not imagine how it could be improved.
- Do not infer which condition (B or C) this is — evaluate the narrative on its own terms.
- You will not be shown the other condition for this case. Rate against the rubric, not relative to another output.
- The oracle results (whether the symbolic layer blocked the action) are NOT shown.
  Do not factor enforcement correctness into your score — that is measured separately.

Respond in EXACTLY this format, no other text:
SCORE: [integer 1-5]
COHERENCE: [one sentence]
CONSTRAINT_HANDLING: [one sentence, or N/A if no violation-designed turns]
ENGAGEMENT: [one sentence]
REASONING: [two to three sentences synthesizing the above into a score justification]
""".strip()


# ── ABox state tracker ────────────────────────────────────────────────────────

BASELINE_ABOX = {
    "character_locations": {
        "innkeeper": "main_hall",
        "guard":     "main_hall",
        "patron":    "main_hall",
    },
    "character_alive": {
        "innkeeper": True,
        "guard":     True,
        "patron":    True,
    },
}


def apply_delta(abox: dict, delta: dict) -> dict:
    """
    Apply a proposed delta to an ABox snapshot.
    Only modifies the ABox if the delta is non-empty.
    Returns a new ABox dict (does not mutate the input).
    """
    result = deepcopy(abox)

    loc_delta = delta.get("character_locations", {})
    for char, loc in loc_delta.items():
        result["character_locations"][char] = loc

    alive_delta = delta.get("character_alive", {})
    for char, alive in alive_delta.items():
        result["character_alive"][char] = alive

    return result


def format_abox(abox: dict) -> str:
    """Render ABox state as a readable string for prompt embedding."""
    lines = ["Locations:"]
    for char, loc in sorted(abox["character_locations"].items()):
        lines.append(f"  {char}: {loc}")
    lines.append("Alive:")
    for char, alive in sorted(abox["character_alive"].items()):
        lines.append(f"  {char}: {'yes' if alive else 'DEAD'}")
    return "\n".join(lines)


# ── Data loading and grouping ─────────────────────────────────────────────────

def load_and_group(path: str) -> dict:
    """
    Load full results JSON (condition-keyed dict).
    Returns: {case_id: {"B": [turns...], "C": [turns...]}}
    Turns sorted by turn_number within each condition.
    """
    with open(path) as f:
        data = json.load(f)

    cases = defaultdict(lambda: {"B": [], "C": []})

    for condition in ("B", "C"):
        for turn in data.get(condition, []):
            turn["condition"] = condition
            cases[turn["test_case_id"]][condition].append(turn)

    for case_id in cases:
        for cond in ("B", "C"):
            cases[case_id][cond].sort(key=lambda t: t["turn_number"])

    return dict(sorted(cases.items()))


# ── Prompt construction ───────────────────────────────────────────────────────

def build_prompt(case_id: str, condition: str, turns: list[dict]) -> str:
    """
    Build a single self-contained rating prompt for one case-condition pair.
    Tracks ABox state turn-by-turn from committed deltas.
    """
    lines = [
        f"NQS RATING TASK — {case_id} (Condition {condition})",
        "=" * 60,
        "",
        WORLD_RULES,
        "",
        "=" * 60,
        "",
        "BASELINE WORLD STATE (at case start, after ABox reset):",
        format_abox(BASELINE_ABOX),
        "",
        "=" * 60,
        "",
        "NARRATIVE OUTPUT TO RATE",
        "-" * 40,
        "",
    ]

    current_abox = deepcopy(BASELINE_ABOX)

    for turn in turns:
        turn_num = turn["turn_number"]
        expects = turn.get("expects_violation", False)
        narrative = turn.get("turn_result", {}).get("narrative", "").strip()
        committed = turn.get("effectively_committed", False)
        proposed_delta = turn.get("turn_result", {}).get("proposed_delta", {})

        violation_flag = " [VIOLATION-DESIGNED TURN]" if expects else ""

        lines.append(f"Turn {turn_num}{violation_flag}")
        lines.append(f"World state at start of this turn:")

        # Indent the ABox state for readability
        for abox_line in format_abox(current_abox).splitlines():
            lines.append(f"  {abox_line}")

        lines.append("")
        lines.append("Narrative:")
        lines.append(f'  "{narrative}"' if narrative else "  [no narrative recorded]")
        lines.append("")

        # Advance ABox only if the delta committed
        if committed and proposed_delta:
            current_abox = apply_delta(current_abox, proposed_delta)

        lines.append("-" * 40)
        lines.append("")

    lines += [
        "=" * 60,
        "",
        RUBRIC,
    ]

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_llm_rating_prompts.py <path_to_full_results.json>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = Path(input_path).parent / "llm_rating_prompts"
    output_dir.mkdir(exist_ok=True)

    cases = load_and_group(input_path)

    all_prompts = []
    file_count = 0

    for case_id, conditions in cases.items():
        for cond in ("B", "C"):
            turns = conditions[cond]
            if not turns:
                print(f"  WARNING: no turns found for {case_id} Condition {cond} — skipping")
                continue

            prompt = build_prompt(case_id, cond, turns)
            filename = output_dir / f"{case_id}_{cond}.txt"
            filename.write_text(prompt, encoding="utf-8")

            all_prompts.append(f"{'=' * 70}\nFILE: {case_id}_{cond}.txt\n{'=' * 70}\n\n{prompt}")
            file_count += 1

    # Write batch file for API use
    batch_path = output_dir / "_batch_all.txt"
    batch_path.write_text(
        "\n\n\n".join(all_prompts),
        encoding="utf-8"
    )

    print(f"Prompts written to: {output_dir}/")
    print(f"Individual files:   {file_count} prompts ({file_count // 2} cases × 2 conditions)")
    print(f"Batch file:         {batch_path.name} (all prompts concatenated)")
    print()
    print("Usage:")
    print("  — Paste individual .txt files into any LLM interface, one at a time")
    print("  — Or use _batch_all.txt for programmatic API batching")
    print()
    print("Parse responses with:")
    print("  SCORE: (integer)")
    print("  COHERENCE: (text)")
    print("  CONSTRAINT_HANDLING: (text or N/A)")
    print("  ENGAGEMENT: (text)")
    print("  REASONING: (text)")


if __name__ == "__main__":
    main()