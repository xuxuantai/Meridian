# Meridian Architecture

Meridian is an analysis harness, not a prompt library.

The distinction matters:

- A prompt tells an agent what to do in the current conversation.
- A harness defines the persistent protocol that keeps analysis reliable across
  tools, tasks, domains, and repeated runs.

## Layers

### 1. Agent Runtime

The runtime is replaceable:

- Codex
- Claude Code
- OpenCode
- OpenHands
- future local or enterprise agents

Meridian should not depend on one runtime.

### 2. Adapter Layer

Adapters translate Meridian into something a runtime can follow:

- `SKILL.md`
- system prompts
- project rules
- MCP servers
- local CLI wrappers
- future hosted workbench integrations

Prompts live here. They are important, but they are not the durable asset.

### 3. Core Harness

Core defines the reusable protocol:

- lifecycle phases
- required artifacts
- state files
- claim and evidence tracking
- quality gates
- extraction loop

This layer should stay domain-neutral.

### 4. Domain Pack

A domain pack specializes the harness for one field:

- decision questions
- analysis methods
- metrics
- knowledge structure
- data source expectations
- report templates
- evaluation rules
- reusable case library

Cross-border market opportunity analysis is the first domain pack.

### 5. Analysis Run

An analysis run is a concrete engagement or research task. It should produce:

- contract
- plan
- source log
- evidence table
- claim ledger
- report
- review result
- extracted reusable assets

## Artifact Flow

```text
Input question
  -> contract
  -> plan
  -> sources
  -> evidence
  -> claims
  -> synthesis
  -> evaluation
  -> report
  -> extraction
```

The important idea is that the report is not the only output. Every run should
improve the harness by extracting better metrics, methods, templates, knowledge,
and evaluation checks.

## What Should Remain Stable

- File-based state.
- Explicit contracts.
- Locked metric definitions.
- Claim-to-evidence traceability.
- Quality gates before publication.
- Human review as a source of improved domain assets.

## What Can Change

- Agent runtime.
- Prompt format.
- Domain pack structure.
- CLI implementation.
- UI or workbench surface.
- Data connectors.

This is why Meridian should optimize for protocol clarity before interface
polish.
