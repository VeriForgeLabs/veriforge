% ============================================================
% Test 01 — Valid Initial State
% Phase 1 CLI test | implementation-log.md: I02
% ============================================================
%
% Usage:
%   clingo prototype/tavern/tavern_rules.lp prototype/tavern/tests/t01_valid_state.lp
%
% Scenario: All three characters are in tavern_main. All are alive.
%   This is the initial ABox state encoded in abox.json.
%
% Expected result: SATISFIABLE. No violation atoms in the stable model.
% ============================================================

% Category 3 — Mutable state (hand-crafted for CLI testing)
% In Phase 2+, the Python module injects these via ctl.add().

located_at(innkeeper, tavern_main).
located_at(guard,     tavern_main).
located_at(patron,    tavern_main).

alive(innkeeper).
alive(guard).
alive(patron).
