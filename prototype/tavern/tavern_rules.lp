% ============================================================
% VeriForge Tavern World — Rules File
% Phase 2 artifact | implementation-log.md: I02, I03
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
% These are ground truth definitions, not assertions
% about current state.

character(innkeeper).
character(guard).
character(patron).

location(entrance).
location(main_hall).
location(cellar).
location(back_room).


% ---- Category 2: Static Properties -----------------------
% Facts that never change during play.
% Spatial topology and access-control designations are static.

% Only the innkeeper has authorised access to the cellar.
cellar_access(innkeeper).

% Adjacency is symmetric — each pair stated in both directions.
% The solver does not derive the reverse automatically.
adjacent(entrance, main_hall).
adjacent(main_hall, entrance).
adjacent(main_hall, cellar).
adjacent(cellar, main_hall).
adjacent(main_hall, back_room).
adjacent(back_room, main_hall).


% ---- Category 4: Integrity Constraints -------------------
% Named-violation pattern (IMP-I01-D05):
%   - Each constraint derives a violation/1 atom when triggered.
%   - No paired :- violation(X) constraint — program stays SAT.
%   - Enforcement loop checks for violation(...) atoms in the
%     yielded stable model, not result.satisfiable.
%
% Violation atoms carry the offending entity as a compound
% argument: violation(unauthorized_in_cellar(guard)) is more
% actionable than violation(unauthorized_in_cellar).
% See: IMP-I02-D04.


% Constraint A1 — Type A (State Consistency):
% Only characters with cellar_access may be in the cellar.
%
% "not cellar_access(X)" uses negation-as-failure: if
% cellar_access(X) is absent from the stable model, the
% solver treats it as false. New characters granted access
% via cellar_access(X) facts are automatically exempt
% without modifying this rule.

violation(unauthorized_in_cellar(X)) :-
    character(X),
    located_at(X, cellar),
    not cellar_access(X).


% Constraint A2 — Type A (State Consistency):
% A dead character cannot occupy any location.
%
% "not alive(X)" fires when alive(X) is absent from the
% stable model. The ABox must assert alive(X) for every
% living character. Omitting it is equivalent to declaring
% the character dead (closed-world assumption).

violation(dead_character_located(X)) :-
    character(X),
    located_at(X, _),
    not alive(X).


% Constraint A3 — Type A (State Consistency):
% A character cannot occupy two locations simultaneously.
%
% L1 != L2 prevents the rule from firing when both variables
% unify to the same location — a degenerate case that cannot
% occur with well-formed ABox facts but is excluded for
% correctness.

violation(character_at_multiple_locations(X)) :-
    character(X),
    located_at(X, L1),
    located_at(X, L2),
    L1 != L2.


% Constraint B1 — Type B (Transition Validity):
% A character can only move to an adjacent location.
%
% was_at(X, OldLoc) is injected from the current ABox by
% the Phase 2 Python module — it records where X was before
% this delta was proposed.
%
% located_at(X, NewLoc) is injected from the proposed delta
% — it records where X wants to be after the delta commits.
%
% OldLoc != NewLoc guards against flagging stay-in-place as
% a violation. A character remaining at their current location
% satisfies was_at(X, L) and located_at(X, L) simultaneously.
% Since no location is declared adjacent to itself, the
% "not adjacent" check would fire incorrectly without this guard.

violation(non_adjacent_move(X, OldLoc, NewLoc)) :-
    character(X),
    was_at(X, OldLoc),
    located_at(X, NewLoc),
    OldLoc != NewLoc,
    not adjacent(OldLoc, NewLoc).