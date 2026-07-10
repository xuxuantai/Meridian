# Meridian

Meridian is an analysis harness for AI agents doing professional business and
data analysis.

The project is not a collection of prompts. Prompts are only adapters. The core
asset is a reusable analysis protocol: how an agent defines a decision question,
locks metric definitions, records evidence, manages claims, evaluates logic, and
turns each completed analysis into reusable domain knowledge.

## Why Meridian Exists

General-purpose agents can search, read files, run code, and write reports. The
hard part in professional analysis is making the work reliable:

- metric definitions drift during long conversations
- conclusions contradict earlier claims
- evidence is hard to trace
- assumptions disappear into prose
- domain methods are not extracted after each project

Meridian turns those fragile steps into explicit files, lifecycle phases,
quality gates, and domain packs.

## Architecture

```text
Meridian
├── core/                       # Harness protocol, templates, and verification
│   ├── protocols/              # Lifecycle, artifact, evaluation, and pack specs
│   ├── templates/              # Reusable state/contract templates
│   └── evaluation/             # Local verification utilities
├── adapters/                   # Tool-specific prompt or runtime adapters
│   └── agent-skills/
├── domains/                    # Vertical analysis packs
│   └── cross-border/
└── docs/                       # Architecture and roadmap
```

## Mental Model

```text
Agent Runtime
  Codex / Claude Code / OpenCode / OpenHands
        |
Adapter
  SKILL.md, system prompt, tool rule, local runtime wrapper
        |
Meridian Core
  lifecycle + artifacts + state + gates + verification
        |
Domain Pack
  methods + metrics + knowledge + templates + evaluations
        |
Analysis Run
  one concrete business question, traceable from input to recommendation
```

## Core

`core/` defines the generic harness that every domain pack should reuse.

Current core assets:

- `core/protocols/harness-lifecycle.yaml`
- `core/protocols/artifacts.yaml`
- `core/protocols/evaluation-gates.yaml`
- `core/protocols/domain-pack.yaml`
- `core/templates/analysis-contract.yaml`
- `core/templates/analysis-state.yaml`
- `core/evaluation/verify_consistency.py`

The core lifecycle is:

```text
intake
  -> contract
  -> plan
  -> retrieve
  -> analyze
  -> synthesize
  -> evaluate
  -> publish
  -> extract
```

## Adapters

`adapters/` contains prompt and tool-specific wrappers. These are intentionally
not treated as the product itself.

The first adapter is:

- `adapters/agent-skills/meridian-analysis-harness/SKILL.md`

It tells a general-purpose agent how to follow Meridian's lifecycle and state
protocol.

## Domain Packs

`domains/` contains vertical packs that reuse the core harness in a specific
analysis field.

The first pack is:

- `domains/cross-border/`

It focuses on:

> country x product x industry cluster export opportunity analysis

Each domain pack should include a `meridian.domain.yaml` manifest that declares
its decision scope, assets, metrics, evaluation rules, and extraction targets.

## Quick Start

Run the cross-border domain pack:

```bash
cd domains/cross-border
PYTHONPATH=src python3 -m cbi.cli list
PYTHONPATH=src python3 -m cbi.cli validate templates/analysis-task.yaml --kind task
```

Run the generic consistency checker:

```bash
pip install pyyaml
python core/evaluation/verify_consistency.py .analysis/
```

## Roadmap

Meridian should evolve in this order:

1. **Protocol first**: stabilize lifecycle, artifact, and evaluation contracts.
2. **Adapter second**: make Codex, Claude Code, OpenCode, and other agents obey the same protocol.
3. **Domain packs third**: add vertical methods such as cross-border, industry research, investment analysis, and strategy.
4. **Evaluation loop fourth**: compare agent outputs against human review and historical cases.
5. **Workbench last**: build UI only after the protocol and repeated workflows are clear.

See `docs/architecture.md` and `docs/evolution-roadmap.md` for the fuller design.

## License

MIT
