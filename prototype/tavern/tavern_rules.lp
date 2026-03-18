% ============================================================
% VeriForge Tavern World — Rules File
% Phase 1 artifact | implementation-log.md: I02
% ============================================================
%
% Encodes WorldDSL Categories 1, 2, and 4.
% Category 3 (mutable state) is NEVER hardcoded here.
% It is injected at runtime via ctl.add() (Phase 2+)
% or via hand-crafted test .lp files (Phase 1 CLI testing).
%
% See: IMP-I01-F02 — hardcoding Category 3 here causes
% silent dual-assertion failures.
%
% Violation pattern: derivation-only (always SAT).
% Violations are readable as atoms in the stable model.
% See: IMP-I01-D05.
% ============================================================


% ---- Category 1: Entity Registry -------------------------
% Declares every named entity the world knows about.
% These are the ground truth definitions — not assertions
% about current state.

character(innkeeper).
character(guard).
character(patron).

location(tavern_main).
location(cellar).
location(street).


% ---- Category 2: Static Properties -----------------------
% Facts that never change during play.
% Spatial topology and access-control designations are static.
% Adjacent(A, B) is stated in both directions — the solver
% does not derive the reverse automatically.

restricted(cellar).

adjacent(tavern_main, cellar).
adjacent(cellar, tavern_main).
adjacent(tavern_main, street).
adjacent(street, tavern_main).


% ---- Category 4: Integrity Constraints -------------------
% Named-violation pattern (IMP-I01-D05):
%   - Each constraint derives a violation/1 atom when triggered.
%   - No paired :- violation(X) constraint — program stays SAT.
%   - Enforcement loop checks for violation(...) atoms in the
%     yielded stable model, not result.satisfiable.
%
% Violation atoms use compound arguments to name the offending
% entity: violation(unauthorized_in_cellar(guard)) is more
% actionable than violation(unauthorized_in_cellar).
% Both are valid atoms in ASP; the argument is a compound term.


% Constraint 1 — Type A (State Consistency):
% The cellar is a restricted area. Only the innkeeper may be there.
%
% X != innkeeper uses inequality over constants.
% This generalises correctly if new characters are added to
% Category 1 — they are automatically covered.

violation(unauthorized_in_cellar(X)) :-
    character(X),
    located_at(X, cellar),
    X != innkeeper.


% Constraint 2 — Type A (State Consistency):
% A dead character cannot occupy any location.
%
% "not alive(X)" is negation-as-failure under the closed-world
% assumption: if alive(X) is absent from the stable model,
% the solver treats it as false.
% The ABox must assert alive(X) for every living character.
% Omitting it is equivalent to declaring the character dead.

violation(dead_character_located(X)) :-
    character(X),
    located_at(X, _),
    not alive(X).


% Constraint 3 — Type A (State Consistency):
% A character cannot occupy two locations simultaneously.
%
% This guards against the ABox management error where both old
% and new locations persist after a move (IMP-I01-F02 failure mode).
% L1 != L2 prevents the rule from firing on (L, L) — a character
% being at the same location twice, which cannot occur with ground
% facts but is excluded explicitly for correctness.

violation(character_at_multiple_locations(X)) :-
    character(X),
    located_at(X, L1),
    located_at(X, L2),
    L1 != L2.
