#!/usr/bin/env python3
"""
run_llm_interrater.py

Automated inter-rater NQS scoring pass against the Anthropic and OpenAI APIs.
Sends all 24 rating prompts with the corrected rubric (including the VeriForge
role-boundary architectural note) and collects structured responses.

Usage (from repo root, venv active):
  python run_llm_interrater.py --anthropic          # Claude only
  python run_llm_interrater.py --openai             # GPT only
  python run_llm_interrater.py --anthropic --openai # Both

Requirements:
  pip install anthropic openai --break-system-packages
  ANTHROPIC_API_KEY set in environment (already configured for session loop)
  OPENAI_API_KEY set in environment (new — add to .env or export before running)

Output:
  results/llm_ratings_claude-sonnet-4-6.json
  results/llm_ratings_gpt-5.4.json
"""

import argparse
import json
import os
import re
import time
from pathlib import Path as _Path
_env = _Path(".env")
if _env.exists():
    for _line in _env.read_text().splitlines():
        if "=" in _line and not _line.startswith("#"):
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())


# ── Model configuration ───────────────────────────────────────────────────────

ANTHROPIC_MODEL = "claude-sonnet-4-6"
OPENAI_MODEL    = "gpt-5.4"          # update if exact version string differs

PROMPTS_DIR  = _Path("results/llm_rating_prompts")
OUTPUT_DIR   = _Path("results")

# Delay between API calls (seconds) — avoids rate limit errors
CALL_DELAY = 1.5


# ── Corrected inter-rater instructions ───────────────────────────────────────
# This replaces the original instructions with the architectural note added.

CORRECTED_INSTRUCTIONS = """
INTER-RATER NQS SCORING — INSTRUCTIONS FOR EVALUATOR

You are acting as a blind inter-rater for a narrative quality evaluation study.
You will receive one rating task at a time.

YOUR ROLE
=========
You are evaluating the quality of AI-generated narrative text produced during
a roleplay system prototype test. Each task gives you one case — a scripted
multi-turn narrative sequence — and asks you to rate its quality on a 1–5
scale using a provided rubric.

You are NOT:
  — Evaluating whether the system made correct enforcement decisions.
    The oracle results are intentionally withheld. Do not speculate about them.
  — Comparing this output to the other condition for the same case.
    You will see each condition separately. Rate against the rubric only.
  — Suggesting improvements or rewriting the narrative.
    Score what is there, not what could be there.

YOU ARE:
  — Reading the narrative output as a participant in a tabletop or text-based
    roleplay session would read it.
  — Asking: would this output sustain engagement in a real session?
  — Applying the rubric consistently across all tasks.

==========================================================================
CRITICAL ARCHITECTURAL NOTE — READ THIS BEFORE APPLYING THE RUBRIC
==========================================================================
This system uses a two-layer architecture: a generative LLM layer and a
symbolic enforcement layer. The LLM's job is to describe what was ATTEMPTED.
The symbolic layer decides what actually COMMITS to the world state.

This means: a narrative saying "the guard descends into the cellar" on a
violation-designed turn is CORRECT behavior. The guard attempted it. The
symbolic layer blocked the commit. The ABox did not update.

YOU ARE NOT evaluating whether the narrative respects the world rules.
YOU ARE evaluating whether the narrative is a plausible, engaging RP output
given that it describes an attempt that may or may not succeed.

COHERENCE FAILURE means: the narrative places a character in a location that
contradicts their COMMITTED ABox position at the START of that turn — i.e.,
states they are somewhere they have not been moved to by a prior committed delta.
It does NOT mean the narrative describes a rule-violating attempt.

Example of a REAL coherence failure:
  The ABox at turn start shows the guard at main_hall. The narrative opens
  by describing him as already in the back_room with no prior committed move.
  That is a coherence failure — the narrative misrepresents actual world state.

Example of CORRECT behavior on a violation-designed turn:
  The guard attempts to enter the cellar. The narrative describes the attempt
  vividly. This is NOT a coherence failure. Rate it purely on prose quality,
  constraint handling naturalness, and engagement.
==========================================================================

RATING RUBRIC
=============
Rate on a 1–5 integer scale. Three dimensions contribute to the score.
A serious failure on any single dimension caps the score at 3 or below.

Dimension 1 — Spatial and causal coherence (weight: 40%)
  Does the narrative correctly reflect where characters ARE at the start of
  each turn per the provided world state? Characters should be described as
  starting from their committed ABox position. A narrative that starts the
  guard from a room he has not been moved to yet is a coherence failure.
  NOTE: describing a character ATTEMPTING to move to a forbidden location
  is NOT a coherence failure — see architectural note above.

Dimension 2 — Constraint handling naturalness (weight: 35%)
  Applies only to violation-designed turns. On clean turns, mark N/A.
  When an action is blocked by the system, does the narrative handle the attempt
  as a natural story beat — a vivid, plausible attempt that a player would find
  satisfying to read — rather than a robotic refusal, an invisible wall, or a
  self-censored empty output?
  "The guard reaches for the bolted cellar door, finds it immovable" scores
  higher than "the guard cannot enter." A narrative that writes a confident,
  vivid attempt scores HIGHER than one that pre-emptively avoids the action.

Dimension 3 — Engagement and narrative momentum (weight: 25%)
  Does the prose sustain interest across all turns?
  Look for: environmental detail, secondary characters, sensory texture,
  multiple action beats per turn, scene advancement.
  Tunnel-vision prose that ignores the tavern environment scores lower.

Scale anchors:
  5 — Fully grounded per ABox; attempt described vividly as a natural story beat;
      environmental detail, multiple beats; would sustain a real roleplay session.
  4 — Grounded with minor ambiguity; attempt readable if unremarkable;
      competent prose with some texture.
  3 — One coherence issue (wrong starting position) OR mechanical attempt
      description OR flat/formulaic prose.
  2 — Significant coherence failure (wrong starting position, dead character
      with stated location) OR self-censored empty output OR refusal prose.
  1 — Incoherent world state, wrong characters throughout, empty output,
      or pure refusal. Unusable as roleplay output.

Hard cap rule:
  A serious coherence failure — character described as starting from the WRONG
  location per the ABox, or a dead character described as present at a location
  — caps the score at 3 or below regardless of prose quality.
  Describing a violation attempt vividly does NOT trigger the hard cap.

RESPONSE FORMAT
===============
Respond in EXACTLY this format. No preamble, no commentary outside these fields:

SCORE: [integer 1-5]
COHERENCE: [one sentence]
CONSTRAINT_HANDLING: [one sentence, or N/A if no violation-designed turns]
ENGAGEMENT: [one sentence]
REASONING: [two to three sentences synthesizing the above into a score justification]
""".strip()


# ── Response parsing ──────────────────────────────────────────────────────────

def parse_response(text: str, case_id: str, condition: str) -> dict | None:
    """
    Parse a structured model response into a rating dict.
    Returns None if parsing fails.
    """
    score_match = re.search(r"SCORE:\s*(\d)", text)
    if not score_match:
        return None

    coherence_match      = re.search(r"COHERENCE:\s*(.+?)(?=\nCONSTRAINT_HANDLING:|\Z)",
                                     text, re.DOTALL)
    constraint_match     = re.search(r"CONSTRAINT_HANDLING:\s*(.+?)(?=\nENGAGEMENT:|\Z)",
                                     text, re.DOTALL)
    engagement_match     = re.search(r"ENGAGEMENT:\s*(.+?)(?=\nREASONING:|\Z)",
                                     text, re.DOTALL)
    reasoning_match      = re.search(r"REASONING:\s*(.+?)$",
                                     text, re.DOTALL)

    return {
        "case_id":            case_id,
        "condition":          condition,
        "nqs":                int(score_match.group(1)),
        "coherence":          coherence_match.group(1).strip()  if coherence_match  else "",
        "constraint_handling":constraint_match.group(1).strip() if constraint_match else "",
        "engagement":         engagement_match.group(1).strip() if engagement_match else "",
        "notes":              reasoning_match.group(1).strip()  if reasoning_match  else "",
    }


# ── Prompt loading ────────────────────────────────────────────────────────────

def load_prompts() -> list[tuple[str, str, str]]:
    """
    Load all 24 prompt files from PROMPTS_DIR.
    Returns list of (case_id, condition, prompt_text) tuples, sorted by case_id.
    Skips the _batch_all.txt file.
    """
    prompts = []
    for path in sorted(PROMPTS_DIR.glob("tc-*.txt")):
        stem = path.stem  # e.g. tc-a01_B
        m = re.match(r"^(.+)_([BC])$", stem)
        if not m:
            print(f"  SKIP: could not parse {path.name}")
            continue
        case_id   = m.group(1)
        condition = m.group(2)
        # Replace the original instructions block with the corrected one
        # The original instructions end just before the first "NQS RATING TASK" line
        raw = path.read_text(encoding="utf-8")
        # Prepend corrected instructions — the prompt files already contain the
        # world rules and rubric, but we prepend the corrected instructions as
        # a system-level framing that overrides the embedded rubric where they conflict
        full_prompt = CORRECTED_INSTRUCTIONS + "\n\n" + "=" * 70 + "\n\n" + raw
        prompts.append((case_id, condition, full_prompt))
    return prompts


# ── API callers ───────────────────────────────────────────────────────────────

def call_anthropic(prompt: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=512,
        temperature=0,
        system="You are a precise evaluator. Output ONLY the structured response format requested. No preamble, no reasoning prose, no markdown. Begin your response with SCORE:",
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def call_openai(prompt: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0,
        max_completion_tokens=512,
        messages=[
            {"role": "system", "content": "You are a precise evaluator. Output ONLY the structured response format requested. No preamble, no reasoning prose, no markdown. Begin your response with SCORE:"},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


# ── Main runner ───────────────────────────────────────────────────────────────

def run_pass(model_name: str, caller, prompts: list) -> None:
    """Run a full 24-prompt pass for one model and save results."""
    output_path = OUTPUT_DIR / f"llm_ratings_{model_name}.json"

    # Resume from partial run if output already exists
    if output_path.exists():
        with open(output_path) as f:
            existing = json.load(f)
        done = {(r["case_id"], r["condition"]) for r in existing}
        print(f"  Resuming — {len(done)} ratings already present")
    else:
        existing = []
        done = set()

    results   = list(existing)
    failed    = []

    for i, (case_id, condition, prompt) in enumerate(prompts):
        key = (case_id, condition)
        if key in done:
            continue

        print(f"  [{i+1:2d}/24] {case_id} Condition {condition} ... ", end="", flush=True)

        try:
            raw = caller(prompt)
            rating = parse_response(raw, case_id, condition)

            if rating:
                results.append(rating)
                done.add(key)
                print(f"SCORE={rating['nqs']}")
            else:
                print("PARSE FAILED — saving raw response")
                failed.append({
                    "case_id":   case_id,
                    "condition": condition,
                    "raw":       raw,
                })

        except Exception as e:
            print(f"API ERROR: {e}")
            failed.append({
                "case_id":   case_id,
                "condition": condition,
                "error":     str(e),
            })

        # Save after every successful rating — safe to interrupt and resume
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        time.sleep(CALL_DELAY)

    print(f"\n  Complete: {len(results)} rated, {len(failed)} failed")
    print(f"  Results: {output_path}")

    if failed:
        fail_path = OUTPUT_DIR / f"llm_ratings_{model_name}_failed.json"
        with open(fail_path, "w") as f:
            json.dump(failed, f, indent=2)
        print(f"  Failed:  {fail_path} — review and re-run manually if needed")


def main():
    parser = argparse.ArgumentParser(description="Automated LLM inter-rater NQS pass")
    parser.add_argument("--anthropic", action="store_true", help="Run Claude pass")
    parser.add_argument("--openai",    action="store_true", help="Run GPT pass")
    args = parser.parse_args()

    if not args.anthropic and not args.openai:
        parser.print_help()
        return

    OUTPUT_DIR.mkdir(exist_ok=True)

    if not PROMPTS_DIR.exists():
        print(f"ERROR: {PROMPTS_DIR} not found.")
        print("       Run generate_llm_rating_prompts.py first.")
        return

    prompts = load_prompts()
    print(f"Loaded {len(prompts)} prompt files from {PROMPTS_DIR}")

    if len(prompts) != 24:
        print(f"WARNING: expected 24 prompts, found {len(prompts)}")

    if args.anthropic:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("ERROR: ANTHROPIC_API_KEY not set in environment")
        else:
            print(f"\n── Anthropic pass ({ANTHROPIC_MODEL}) ──")
            run_pass(ANTHROPIC_MODEL, call_anthropic, prompts)

    if args.openai:
        if not os.environ.get("OPENAI_API_KEY"):
            print("ERROR: OPENAI_API_KEY not set in environment")
            print("       export OPENAI_API_KEY=your_key_here")
        else:
            print(f"\n── OpenAI pass ({OPENAI_MODEL}) ──")
            run_pass(OPENAI_MODEL, call_openai, prompts)

    print("\nDone. Run process_llm_ratings.py to compute inter-rater statistics.")


if __name__ == "__main__":
    main()
