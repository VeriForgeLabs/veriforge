% =============================================================
% VeriForge Toy Example — Pattern 4: Enforcement Loop
% Rules and static structure only.
% All ABox state injected at runtime via ctl.add().
% =============================================================

% --- Entity registry ---
character(guard).
character(prisoner).
character(merchant).

location(cell).
location(corridor).

% --- Static properties ---
has_bars(cell).
imprisoned(prisoner).

% --- Named-violation auxiliary predicates ---
% One predicate per hard constraint.
% No paired :- violation(X) — enforcement loop reads atoms directly.
violation(prisoner_not_in_cell) :-
    imprisoned(X),
    located_at(X, L),
    L != cell.
