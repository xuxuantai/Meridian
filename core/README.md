# Meridian Core

`core/` contains the reusable analysis harness shared by all Meridian adapters
and domain packs.

It defines the durable part of Meridian:

- lifecycle protocol
- artifact contract
- evaluation gates
- domain pack protocol
- reusable run templates
- verification utilities

Prompts and agent-specific instructions should depend on this layer instead of
redefining their own workflow.

## Contents

- `protocols/`: machine-readable protocol notes for lifecycle, artifacts,
  evaluation gates, and domain pack structure.
- `templates/`: starter files for `.analysis/` run artifacts.
- `evaluation/`: local verification scripts.

## Design Rule

If a concept must survive across agents, domains, and repeated analysis runs, it
belongs in `core/`. If it only teaches a specific agent how to behave, it belongs
in `adapters/`.
