# tests/test_validator.py
"""
pytest tests for prototype/tavern/validator.py.
Phase 2 resolution criterion requires at least one Type A and one Type B test.
All five tests are included for full coverage of the established constraints.
"""

import json
from pathlib import Path

import pytest

from prototype.tavern.validator import validate_delta, ValidationResult

# ─── Paths ───────────────────────────────────────────────────────────────────

# These paths are relative to the project root, where pytest is invoked.
RULES_FILE = Path("prototype/tavern/tavern_rules.lp")
ABOX_PATH  = Path("prototype/tavern/abox.json")


# ─── Fixtures ─────────────────────────────────────────────────────────────────

def _write_abox(tmp_path: Path, located_at: dict, alive: list) -> Path:
    """Write a minimal ABox to a temporary file using the real Phase 1 schema.

    Accepts located_at as a dict and alive as a list — matching the structure
    of the committed abox.json — so tests exercise the same code path as
    production use. The _doc and _asp_mapping fields are omitted since the
    validator only reads the "state" key.
    """
    abox = {
        "state": {
            "located_at": located_at,
            "alive": alive,
        }
    }
    abox_file = tmp_path / "abox.json"
    abox_file.write_text(json.dumps(abox))
    return abox_file


# ─── Baseline ─────────────────────────────────────────────────────────────────

def test_clean_delta_returns_clean_true():
    """A move that violates no constraint returns clean=True.

    Guard moves from main_hall to main_hall (no change) — the simplest
    possible clean case. Verifies the committed_delta is echoed back.
    """
    delta = {"character_locations": {"guard": "main_hall"}}
    result = validate_delta(RULES_FILE, ABOX_PATH, delta)

    assert result.clean is True
    assert result.violations == []
    assert result.committed_delta == delta


# ─── Type A — State Consistency ───────────────────────────────────────────────

def test_type_a_unauthorized_in_cellar():
    """Guard moves to cellar: violates Constraint A1 (no cellar access).

    Expected: clean=False, violation atom contains 'unauthorized_in_cellar'.
    """
    delta = {"character_locations": {"guard": "cellar"}}
    result = validate_delta(RULES_FILE, ABOX_PATH, delta)

    assert result.clean is False
    assert result.committed_delta is None
    assert any("unauthorized_in_cellar" in v for v in result.violations), (
        f"Expected 'unauthorized_in_cellar' in violations; got: {result.violations}"
    )


def test_type_a_dead_character_located():
    """Patron dies but remains at a location: violates Constraint A2.

    The delta sets alive=False for the patron while keeping their location.
    Expected: clean=False, violation atom contains 'dead_character_located'.
    """
    delta = {"character_alive": {"patron": False}}
    result = validate_delta(RULES_FILE, ABOX_PATH, delta)

    assert result.clean is False
    assert any("dead_character_located" in v for v in result.violations), (
        f"Expected 'dead_character_located' in violations; got: {result.violations}"
    )


# ─── Type B — Transition Validity ─────────────────────────────────────────────

def test_type_b_adjacent_move_is_clean(tmp_path):
    """Guard moves from entrance to main_hall — adjacent, no violation.

    Sets up a custom ABox with guard starting at entrance, then proposes
    a move to main_hall. The adjacent/2 fact covers this pair.
    Expected: clean=True.
    """
    abox_file = _write_abox(
        tmp_path,
        located_at={"innkeeper": "main_hall", "guard": "entrance", "patron": "main_hall"},
        alive=["innkeeper", "guard", "patron"],
    )

    delta = {"character_locations": {"guard": "main_hall"}}
    result = validate_delta(RULES_FILE, abox_file, delta)

    assert result.clean is True
    assert result.violations == []


def test_type_b_non_adjacent_move_violation(tmp_path):
    """Guard jumps from entrance directly to cellar — not adjacent.

    entrance is adjacent to main_hall only.
    cellar is adjacent to main_hall only.
    entrance → cellar skips main_hall — no adjacent/2 fact covers this pair.
    Expected: clean=False, violation atom names 'non_adjacent_move'.
    """
    abox_file = _write_abox(
        tmp_path,
        located_at={"innkeeper": "main_hall", "guard": "entrance", "patron": "main_hall"},
        alive=["innkeeper", "guard", "patron"],
    )

    delta = {"character_locations": {"guard": "cellar"}}
    result = validate_delta(RULES_FILE, abox_file, delta)

    assert result.clean is False
    assert result.committed_delta is None
    assert any("non_adjacent_move" in v for v in result.violations), (
        f"Expected 'non_adjacent_move' in violations; got: {result.violations}"
    )
    