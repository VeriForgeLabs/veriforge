% =============================================================
% VeriForge Toy Example — Pattern 3: Named-Violation Predicates
% Rules and static structure only — no mutable state hardcoded.
% ABox state (located_at facts) is always injected via ctl.add().
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

% --- Category 4: Named-violation auxiliary predicate ---
% Derives a named atom when an imprisoned character is outside the cell.
% NO paired :- violation(X) constraint — the enforcement loop reads the atom.
violation(prisoner_not_in_cell) :-
    imprisoned(X),
    located_at(X, L),
    L != cell.
