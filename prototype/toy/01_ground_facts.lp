% =============================================================
% VeriForge Toy Example — Pattern 1: Ground Facts
% Encodes entity registry, static properties, and mutable state
% as unconditional ASP facts.
% =============================================================

% --- Category 1: Entity registry ---
% Declares what named entities exist in the world.
character(guard).
character(prisoner).
character(merchant).

location(cell).
location(corridor).

% --- Category 2: Static properties ---
% Facts that never change during play.
% The cell has bars — a permanent physical property.
has_bars(cell).

% --- Category 3: Mutable state ---
% Current positions, loaded from ABox JSON at session start.
% In this toy, we write them directly.
located_at(guard, cell).
located_at(prisoner, cell).
located_at(merchant, corridor).
