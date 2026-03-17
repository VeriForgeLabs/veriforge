% =============================================================
% VeriForge Toy Example — Pattern 2: Integrity Constraints
% Adds a hard rule: imprisoned characters cannot leave the cell.
% Test with located_at(prisoner, cell) for SAT,
% change to located_at(prisoner, corridor) for UNSAT.
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

% --- Mutable state (ABox) ---
% Change prisoner's location to corridor to trigger UNSAT.
located_at(guard, corridor).
located_at(prisoner, cell).
located_at(merchant, corridor).

% --- Category 4: Integrity constraint ---
% An imprisoned character must not be located outside the cell.
:- character(X), imprisoned(X), located_at(X, L), L != cell.
