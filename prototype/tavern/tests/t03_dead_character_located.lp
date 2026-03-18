% ============================================================
% Test 03 — Constraint 2 Violation: Dead Character Has a Location
% Phase 1 CLI test | implementation-log.md: I02
% ============================================================
%
% Usage:
%   clingo prototype/tavern/tavern_rules.lp prototype/tavern/tests/t03_dead_character_located.lp
%
% Scenario: The patron has died, but their located_at fact was not
%   removed from the ABox. alive(patron) is absent — the closed-world
%   assumption treats this as false. Constraint 2 fires.
%
% This simulates the silent ABox management error where a character
%   death is narrated but the state update is incomplete: the ABox
%   delta removes alive(patron) but fails to also remove located_at(patron, ...).
%
% Expected result: SATISFIABLE.
%   Stable model contains: violation(dead_character_located(patron))
% ============================================================

located_at(innkeeper, tavern_main).
located_at(guard,     tavern_main).
located_at(patron,    tavern_main).  % patron has a location but is dead — triggers Constraint 2

alive(innkeeper).
alive(guard).
% alive(patron) is intentionally absent.
% Closed-world assumption: absent fact = false.
% The solver treats patron as dead.
