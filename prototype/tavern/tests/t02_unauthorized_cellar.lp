% ============================================================
% Test 02 — Constraint 1 Violation: Unauthorized Character in Cellar
% Phase 1 CLI test | implementation-log.md: I02
% ============================================================
%
% Usage:
%   clingo prototype/tavern/tavern_rules.lp prototype/tavern/tests/t02_unauthorized_cellar.lp
%
% Scenario: The guard has entered the cellar. The cellar is restricted
%   to the innkeeper only (Constraint 1).
%
% Expected result: SATISFIABLE.
%   Stable model contains: violation(unauthorized_in_cellar(guard))
% ============================================================

located_at(innkeeper, tavern_main).
located_at(guard,     cellar).       % guard in restricted area — triggers Constraint 1
located_at(patron,    tavern_main).

alive(innkeeper).
alive(guard).
alive(patron).
