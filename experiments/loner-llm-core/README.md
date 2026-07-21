# Loner 3e LLM Core Rules Experiment

This directory contains the generic, rules-light Loner 3e adaptation for LLM-driven interactive fiction.

## Goal

Create the smallest practical core package that constrains an LLM with:

- Loner 3e scene and Oracle procedures
- tool-generated, auditable dice rolls
- binding `Yes/No, and/but` outcome contracts
- minimal state tracking
- forward-pressure rules
- player-agency and continuity guardrails

The LLM remains the interpreter, adjudicator, and narrator. This is not a standalone game engine, application, or deterministic simulation.

## Scope

The core package is setting-agnostic. Setting-specific material, such as Warhammer 40,000 or cyberpunk guidance, belongs in separate addenda and is outside the initial scope.

## Initial deliverables

- `CORE_RULES.md`
- `PROJECT_INSTRUCTIONS.md`
- `STATE_LEDGER.md`
- `START_GAME_TEMPLATE.md`

## Working rule

Prefer the smallest intervention that produces a meaningful improvement in narrative discipline, adjudication consistency, and state continuity. Do not add infrastructure until observed play failures justify it.
