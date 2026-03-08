# VeriForge

## Hypothesis

A natural language (NL) to Domain Specific Language (DSL) pipeline can be constructed such that:
1. A human provides NL worldbuilding input via a meta-questionnaire.
2. This is translated into a WorldDSL artifact (machine-readable, deterministic).
3. The WorldDSL artifact is used to generate structured outputs (prompts, guardrails, context injections) targeting LLM RP systems.
4. These outputs enforce world-specific rules deterministically by providing authoritative context that directs LLM extrapolation — the LLM does not reason from the DSL, it extrapolates fluently from it, producing inference-level behavior without genuine reasoning.
5. Creative latitude is preserved because the symbolic layer enforces only what it explicitly governs; everything outside that scope remains probabilistic and generative.
6. The result is significantly reduced narrative drift, decoherence, and hallucination across long and multi-session RP — not because the LLM has been made more consistent, but because inference has been delegated to a layer that is deterministic by design.

Current status: hypothesis-stage research. 
All architectural claims are unverified propositions under active investigation.
See: knowledge/vision-and-protocols.md for up-to-date research.
