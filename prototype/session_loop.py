"""
VeriForge Phase 3 — Session Loop
prototype/session_loop.py

Implements the four-stage per-turn cycle:
  Stage 1 — Context derivation  : read abox.json → world state string
  Stage 2 — Prompt assembly     : combine context + user message + condition flag
  Stage 3 — LLM call            : Anthropic Messages API → raw response string
  Stage 4 — Post-processing     : parse delta → validate → commit or surface violation

Three OQ-09 ablation conditions are routing flags on this single loop:
  "A" — Raw LLM          : no context injection, no validation
  "B" — Session-start    : context generated ONCE at session start, validation active
  "C" — Full VeriForge   : context generated from CURRENT ABox each turn, validation active

Design decisions recorded in implementation-log.md:
  IMP-I04-D01 — XML-tag structured output (<narrative> / <delta>)
  IMP-I04-D02 — Module at prototype/ level, not inside prototype/tavern/
  IMP-I04-D03 — Constraint descriptions hard-coded in build_context_string()
  IMP-I04-D04 — claude-haiku-4-5-20251001 for Phase 3; swap constant for Phase 4
  IMP-I04-D05 — Condition B context prepended to user message (not system prompt)

Failure and fix recorded in implementation-log.md:
  IMP-I04-F01 — LLM self-censored delta; system prompt did not specify that the delta
                encodes attempted actions, not successful outcomes. Fixed by adding
                explicit instruction: always emit the attempted delta; the rules engine
                decides what commits.
"""

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import anthropic

# ---------------------------------------------------------------------------
# Import path setup
#
# session_loop.py lives at prototype/session_loop.py.
# validator.py lives at prototype/tavern/validator.py.
#
# Inserting prototype/ into sys.path makes `from tavern.validator import ...`
# resolvable when this module is run from the project root.
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))
from tavern.validator import validate_delta


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Phase 3 development model (IMP-I04-D04).
# Change to "claude-sonnet-4-6" for the Phase 4 ablation study.
MODEL = "claude-haiku-4-5-20251001"

# System prompt carries behavioral instructions only — no world state.
# World state goes into the user message so it sits near the generation
# point each turn, exploiting the recency bias documented in Liu2024 (IMP-I04-D05).
#
# The delta instruction specifies ATTEMPTED state, not successful outcome.
# This is the fix for IMP-I04-F01: the LLM's job is to propose what was
# attempted; the rules engine's job is to decide what commits.
# Without this instruction the LLM reads the constraint descriptions, writes
# a narrative where the action fails, and emits {} — bypassing the symbolic
# layer entirely.
SYSTEM_PROMPT = """\
You are the narrator for a tabletop-style interactive roleplay session set in a fantasy tavern.
Respond to each player action with narrative prose, then output a structured state update.

Your response MUST follow this exact format every time — no exceptions:

<narrative>
[Your narrative text — two to four sentences describing what the character ATTEMPTS to do.
 Write the attempt as if it will succeed. The rules engine will decide whether it commits.]
</narrative>
<delta>
[A JSON object representing the state change the character ATTEMPTED this turn.
 Always emit the delta for what was attempted, even if the action might be forbidden.
 The rules engine validates all deltas. If a delta violates a constraint, it will be
 blocked before committing — you do not need to pre-filter it.
 Valid keys:
   "character_locations" — dict mapping character name to attempted new location
   "character_alive"     — dict mapping character name to true or false
 If nothing was attempted, output exactly: {}
 Do not include keys for fields that do not change this turn.]
</delta>

Example — guard moves from main_hall to entrance:
<narrative>
The guard drains the last of his ale and pushes back from the table.
Satisfied that the common room is quiet, he strides toward the front door.
</narrative>
<delta>
{"character_locations": {"guard": "entrance"}}
</delta>
"""


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class TurnResult:
    """
    Complete record of one session loop turn.

    Every field is populated regardless of condition or outcome, so the demo
    script and future test harness can inspect any aspect of the turn without
    branching on condition type.
    """
    condition: str          # "A", "B", or "C"
    narrative: str          # Surface text extracted from <narrative> tag
    proposed_delta: dict    # Dict extracted from <delta> tag (may be {})
    clean: bool             # True if validation passed or was skipped (Condition A)
    violations: list        # Named violation atom strings; empty if clean
    committed: bool         # True if delta was written to abox.json
    context_injected: str   # The context string sent to the LLM; "" for Condition A
    raw_response: str       # Full unmodified LLM response, for diagnostics


# ---------------------------------------------------------------------------
# Stage 1 — Context derivation
# ---------------------------------------------------------------------------

def build_context_string(abox_path: str) -> str:
    """
    Reads the current abox.json and returns a human-readable authoritative
    world state string for injection into the LLM prompt.

    The output has two parts:

      1. Dynamic state — character locations and alive status, read live from
         abox.json. This part changes as the session progresses and is why
         Condition C rebuilds this string every turn.

      2. Static constraint descriptions — hard-coded for the tavern world
         (IMP-I04-D03). These match the four constraints in tavern_rules.lp
         exactly and do not change during play.

    Location names and adjacency pairs are taken directly from tavern_rules.lp:
      entrance  ↔ main_hall
      main_hall ↔ cellar     (innkeeper only — constraint A1)
      main_hall ↔ back_room
    """
    with open(abox_path) as f:
        abox = json.load(f)

    # Navigate the nested abox.json schema.
    # abox["state"]["located_at"] is a dict: { character: location }
    # abox["state"]["alive"] is a list of living character names.
    state = abox.get("state", {})
    locations: dict = state.get("located_at", {})
    alive_list: list = state.get("alive", [])

    lines = [
        "=== CURRENT WORLD STATE (AUTHORITATIVE — DO NOT CONTRADICT) ===",
        "",
        "Character locations:",
    ]

    for char, loc in sorted(locations.items()):
        # Characters absent from alive_list are dead under the closed-world
        # assumption. The [DEAD] marker makes this explicit to the LLM.
        alive_marker = "" if char in alive_list else " [DEAD]"
        lines.append(f"  {char}{alive_marker} → {loc}")

    lines.append("")
    lines.append(
        "Living characters: "
        + (", ".join(sorted(alive_list)) if alive_list else "(none)")
    )

    # Static constraint descriptions (IMP-I04-D03).
    # These match the four constraints in tavern_rules.lp:
    #   A1 — violation(unauthorized_in_cellar(X))
    #   A2 — violation(dead_character_located(X))
    #   A3 — violation(character_at_multiple_locations(X))
    #   B1 — violation(non_adjacent_move(X, OldLoc, NewLoc))
    lines.append("""
Hard constraints — the rules engine enforces these; emit your delta for what was attempted:
  [A1] CELLAR ACCESS: Only the innkeeper may enter the cellar.
       guard and patron may NOT move to or be in the cellar.
       Valid locations for guard and patron: entrance, main_hall, back_room
  [A2] DEAD CHARACTERS: A dead character cannot have a location.
       If a character dies this turn, set character_alive to false in your delta.
  [A3] UNIQUE LOCATION: A character can only be in one location at a time.
  [B1] ADJACENCY: A character can only move to a directly adjacent location.
       Adjacency map (all connections are bidirectional):
         entrance  ↔ main_hall
         main_hall ↔ cellar     (innkeeper only — see A1)
         main_hall ↔ back_room""")

    lines.append("")
    lines.append("=== END WORLD STATE ===")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Stage 2 — Prompt assembly
# ---------------------------------------------------------------------------

def assemble_prompt(
    user_message: str,
    condition: str,
    session_context: str,
    current_context: str,
) -> tuple:
    """
    Returns (system_string, user_content_string) for the API call.

    The system prompt is identical across all three conditions.
    The difference is entirely in the user message:

      Condition A — user message only; no world state anywhere.
      Condition B — session_context prepended to user message.
                    session_context was built once at session start.
      Condition C — current_context prepended to user message.
                    current_context was built from the live ABox this turn.
    """
    if condition == "A":
        return SYSTEM_PROMPT, user_message

    elif condition == "B":
        if not session_context:
            raise ValueError(
                "Condition B requires session_context. "
                "Call build_context_string() once at session start and pass "
                "the result through every run_turn() call."
            )
        return SYSTEM_PROMPT, f"{session_context}\n{user_message}"

    elif condition == "C":
        if not current_context:
            raise ValueError(
                "Condition C: current_context is empty. "
                "This is a bug in run_turn() — build_context_string() should "
                "have been called before assemble_prompt()."
            )
        return SYSTEM_PROMPT, f"{current_context}\n{user_message}"

    else:
        raise ValueError(f"Unknown condition: {condition!r}. Must be 'A', 'B', or 'C'.")


# ---------------------------------------------------------------------------
# Stage 3 — LLM call
# ---------------------------------------------------------------------------

def call_llm(system: str, user_content: str) -> str:
    """
    Calls the Anthropic Messages API and returns the raw response text.

    anthropic.Anthropic() reads ANTHROPIC_API_KEY from the environment.
    Set it in WSL: export ANTHROPIC_API_KEY="sk-ant-..."

    message.content[0] is a TextBlock for standard (non-tool-use) responses.
    .text is its string content.
    """
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user_content}],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# Stage 4a — Parse structured response
# ---------------------------------------------------------------------------

def parse_response(raw_response: str) -> tuple:
    """
    Extracts narrative and proposed delta from the LLM's XML-tagged response.

    Returns (narrative_text: str, delta_dict: dict).

    re.DOTALL allows the dot metacharacter to match newline characters,
    which is required because tag contents span multiple lines.

    Failure modes are handled conservatively so the session never crashes:
      Missing <narrative> tag  → full raw response becomes the narrative.
      Missing <delta> tag      → empty dict (no-op delta; nothing committed).
      Malformed JSON in <delta> → same as missing tag; proposed_delta={}.
    """
    narrative_match = re.search(r"<narrative>(.*?)</narrative>", raw_response, re.DOTALL)
    delta_match = re.search(r"<delta>(.*?)</delta>", raw_response, re.DOTALL)

    narrative = narrative_match.group(1).strip() if narrative_match else raw_response

    if delta_match:
        try:
            delta = json.loads(delta_match.group(1).strip())
            if not isinstance(delta, dict):
                delta = {}
        except json.JSONDecodeError:
            delta = {}
    else:
        delta = {}

    return narrative, delta


# ---------------------------------------------------------------------------
# Stage 4b — Commit delta to abox.json
# ---------------------------------------------------------------------------

def commit_to_abox(abox_path: str, delta: dict) -> None:
    """
    Applies a validated delta to abox.json in place.

    Only ever called after validate_delta() returns clean=True.
    The ABox is the single authoritative state record (OQ-02a, OQ-02b).

    The delta uses the normalized flat schema from Phase 2 (IMP-I03-D03):
      "character_locations" → updates state.located_at (dict)
      "character_alive"     → updates state.alive (list of living names)

    Death is represented by character_alive[char] = False, which removes the
    character from the alive list. Absence from alive is the closed-world
    representation of death (IMP-I01-F02).
    """
    with open(abox_path) as f:
        abox = json.load(f)

    state = abox.setdefault("state", {})

    if "character_locations" in delta:
        state.setdefault("located_at", {}).update(delta["character_locations"])

    if "character_alive" in delta:
        alive_set = set(state.get("alive", []))
        for char, is_alive in delta["character_alive"].items():
            if is_alive:
                alive_set.add(char)
            else:
                alive_set.discard(char)
        state["alive"] = sorted(alive_set)

    with open(abox_path, "w") as f:
        json.dump(abox, f, indent=2)


# ---------------------------------------------------------------------------
# Entry point — run_turn()
# ---------------------------------------------------------------------------

def run_turn(
    abox_path: str,
    rules_file: str,
    user_prompt: str,
    condition: str,
    session_context: str = "",
) -> TurnResult:
    """
    Executes one complete session loop turn and returns a TurnResult.

    Parameters
    ----------
    abox_path       : Path to abox.json. Read every turn; written only on a
                      clean validated delta (Conditions B and C only).
    rules_file      : Path to tavern_rules.lp. Passed as a path string to
                      validate_delta(), which opens and loads the file itself.
    user_prompt     : The player's action or scripted prompt for this turn.
    condition       : "A", "B", or "C".
    session_context : Pre-generated context string for Condition B only.
                      Build once with build_context_string() at session start
                      and pass through all subsequent run_turn() calls.
                      Ignored for Conditions A and C.

    Side effects
    ------------
    Conditions B and C only: if validate_delta() returns clean=True,
    abox.json is updated in place by commit_to_abox().
    """

    # ── Stage 1: Context derivation ────────────────────────────────────────
    # Condition C reads the live ABox and rebuilds the context string this turn.
    # Conditions A and B leave current_context as an empty string here;
    # Condition B uses the pre-built session_context from the caller instead.
    current_context = build_context_string(abox_path) if condition == "C" else ""

    # Record what was actually sent to the LLM for the TurnResult diagnostic.
    context_injected = current_context if condition == "C" else session_context

    # ── Stage 2: Prompt assembly ────────────────────────────────────────────
    system, user_content = assemble_prompt(
        user_message=user_prompt,
        condition=condition,
        session_context=session_context,
        current_context=current_context,
    )

    # ── Stage 3: LLM call ───────────────────────────────────────────────────
    raw_response = call_llm(system, user_content)

    # ── Stage 4a: Parse structured output ──────────────────────────────────
    narrative, proposed_delta = parse_response(raw_response)

    # ── Stage 4b: Validate and commit ──────────────────────────────────────
    # Condition A bypasses the symbolic layer entirely.
    if condition == "A":
        return TurnResult(
            condition=condition,
            narrative=narrative,
            proposed_delta=proposed_delta,
            clean=True,      # "clean" is meaningless for Condition A; True by convention
            violations=[],
            committed=False,  # Condition A never writes to abox.json
            context_injected="",
            raw_response=raw_response,
        )

    # Conditions B and C: pass both paths to validate_delta().
    # IMPORTANT: validate_delta() reads abox.json itself via the abox_path
    # argument. Do not pre-load the dict and pass it here — the function
    # signature is validate_delta(rules_file, abox_path, proposed_delta).
    result = validate_delta(
        rules_file=rules_file,
        abox_path=abox_path,
        proposed_delta=proposed_delta,
    )

    if result.clean:
        commit_to_abox(abox_path, proposed_delta)

    return TurnResult(
        condition=condition,
        narrative=narrative,
        proposed_delta=proposed_delta,
        clean=result.clean,
        violations=result.violations,
        committed=result.clean,
        context_injected=context_injected,
        raw_response=raw_response,
    )