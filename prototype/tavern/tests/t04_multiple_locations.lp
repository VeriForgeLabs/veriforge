% ============================================================
% Test 04 — Constraint 3 Violation: Character at Two Locations
% Phase 1 CLI test | implementation-log.md: I02
% ============================================================
%
% Usage:
%   clingo prototype/tavern/tavern_rules.lp prototype/tavern/tests/t04_multiple_locations.lp
%
% Scenario: The innkeeper appears at both tavern_main and cellar.
%   This reproduces the exact failure mode from IMP-I01-F02: an ABox
%   delta that asserts a new location without retracting the old one.
%   ASP accumulates facts — it does not override them.
%   Both located_at atoms become simultaneously true.
%   Constraint 3 catches the inconsistency.
%
% Note: innkeeper IS allowed in the cellar (Constraint 1 applies only
%   to non-innkeeper characters), so this test isolates Constraint 3
%   without triggering Constraint 1.
%
% Expected result: SATISFIABLE.
%   Stable model contains: violation(character_at_multiple_locations(innkeeper))
% ============================================================

located_at(innkeeper, tavern_main).
located_at(innkeeper, cellar).       % duplicate location — triggers Constraint 3
located_at(guard,     tavern_main).
located_at(patron,    tavern_main).

alive(innkeeper).
alive(guard).
alive(patron).
