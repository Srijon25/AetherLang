---
title: "AetherLang: An AI-native, agent-first DSL for GPT-powered agents with persistent memory and time-based scheduling."
tags:
  - programming languages
  - domain-specific languages
  - AI agents
  - persistent memory
  - LLM integration
  - scheduling
  - Python
authors:
  - name: Srijon Kumar Shill
    orcid: 0009-0001-6647-2743
    affiliation: 1
affiliations:
  - name: Independent Researcher, Bangladesh
    index: 1
date: 2025-12-16
bibliography: paper.bib
---

# Summary

AetherLang is a small, AI-native domain-specific language (DSL) for defining **agents** that combine (1) persistent key–value memory, (2) declarative goals, and (3) GPT-powered behaviors in a single, readable source file. Programs are written as `agent { ... }` blocks with an optional `memory:` section, a `goal:` string, event handlers (`on event "..." ... respond using GPT: "..."`), and periodic behaviors (`every N s: recall "key"`).

The reference implementation is written in Python and includes both a terminal REPL and an optional PyQt5 GUI [@PyQt5] for interactive testing of agents. The runtime integrates with the OpenAI API [@OpenAIAPI] to execute prompts produced from the agent definition and its current memory snapshot, enabling rapid iteration on agent designs while keeping the “agent contract” (memory + goal + triggers) explicit and inspectable.

# Statement of need

Many LLM-driven assistants begin as ad-hoc scripts: prompt strings embedded in code, memory stored in scattered variables, and “agent logic” spread across callbacks and UI code. This makes it difficult to (a) reproduce an agent’s state across runs, (b) understand what inputs the agent is designed to handle, and (c) evolve behaviors without rewriting glue code.

AetherLang addresses these problems by providing a compact language and interpreter where:

- **Memory is explicit and persistent.** Agent state is stored as JSON under `memory/<agent>.json` and is loaded at startup, enabling continuity across sessions.
- **Behaviors are declarative.** Event-triggered responses and scheduled recalls are specified in the source, not hidden in application code.
- **LLM interaction is structured.** “think” and “reflect” prompts are represented as first-class blocks, encouraging separation between *state* (memory, goal) and *inference* (LLM calls).

This design supports teaching demonstrations of agent loops, persistence, and scheduling, and it provides a practical foundation for small agent-driven tools and experiments.

# Design and implementation

AetherLang follows a Parse → Transform → Run pipeline. Source files are parsed with Lark [@Lark] into a syntax tree that is transformed into a Python data model (agent dictionaries: name, memory, goal, event map, schedules). At runtime the interpreter:

1. loads persisted memory (if present),
2. starts background scheduler threads for `every N s: recall "key"`,
3. enters an interactive loop (CLI or GUI) that accepts events and management commands.

When an event is triggered, the runtime performs template substitution from memory (e.g., `{name}`), constructs a prompt that includes a JSON memory snapshot and the event-specific template, and calls the OpenAI API [@OpenAIAPI] to produce the response. Persistence is handled conservatively: explicit `remember "k" = "v"` and `forget "k"` commands update memory immediately on disk; optional memory updates suggested by the LLM are only applied when they parse as JSON objects.

# Use cases and reuse

AetherLang is intended for small, inspectable prototypes rather than production deployment. Typical uses include classroom demos of persistence and scheduling, rapid iteration on agent behavior templates without changing Python code, and reproducible experiments where the exact agent state is stored on disk. The implementation is intentionally compact and can be extended by adding new statement types (e.g., richer schedules, tool calls, or memory schemas) while preserving the core agent abstraction.

# Availability

AetherLang is released under the MIT License and is available at:
`https://github.com/Srijon25/AetherLang`

# Acknowledgements

AetherLang builds on the Python ecosystem, including Lark for parsing [@Lark], PyQt5 for the optional GUI [@PyQt5], and the OpenAI API for GPT-backed behaviors [@OpenAIAPI].

# References
