# Cross-border Domain Pack

AI-assisted decision intelligence domain pack for cross-border market opportunity analysis.

This domain pack runs on top of the Meridian Analysis Harness. It is not a
general agent implementation. It is the vertical asset layer that turns a
general-purpose coding or research agent into a repeatable cross-border business
analysis workspace.

## Product Thesis

General agents can search, read files, run code, analyze data, and generate
reports. The scarce asset is the decision intelligence layer:

- repeatable analysis skills
- domain knowledge
- metric definitions
- evaluation rules
- historical cases
- human feedback loops

The first validation domain is cross-border market opportunity analysis:

> country x product x industry cluster export opportunity analysis

## Domain Pack Layout

```text
domains/cross-border/
  docs/                  Project brief and operating notes
  projects/              One folder per analysis engagement
  knowledge/             Domain knowledge, taxonomy, HS code maps, cases
  skills/                Structured analysis workflows
  metrics/               Metric definitions and scoring logic
  evaluation/            Review checklists and quality gates
  templates/             Task and report templates
  schemas/               YAML schemas for core assets
  src/cbi/               Analysis Workspace CLI
  tests/                 Lightweight CLI tests
```

## V0 Workflow

```text
User thesis
  -> research planning
  -> data collection
  -> data analysis
  -> hypothesis generation
  -> validation
  -> report generation
  -> human review
  -> asset extraction
  -> knowledge update
```

## CLI Quick Start

From the Meridian repository root:

```bash
cd domains/cross-border
```

Then run:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
cbi --help
```

Without installation:

```bash
PYTHONPATH=src python3 -m cbi.cli --help
```

Create a new analysis task:

```bash
PYTHONPATH=src python3 -m cbi.cli new-task \
  --product "outdoor lighting" \
  --supply-chain "Guangdong" \
  --markets "Saudi Arabia,Poland,Mexico" \
  --title "Outdoor lighting export opportunity scan"
```

Validate an asset:

```bash
PYTHONPATH=src python3 -m cbi.cli validate templates/analysis-task.yaml --kind task
PYTHONPATH=src python3 -m cbi.cli validate skills/market-opportunity-analysis.yaml --kind skill
PYTHONPATH=src python3 -m cbi.cli validate metrics/market-opportunity-score.yaml --kind metric
PYTHONPATH=src python3 -m cbi.cli validate evaluation/source-and-logic-review.yaml --kind evaluation
```

## First 90 Days

- Weeks 1-2: set up repository, workspace, schemas, templates, and basic tools.
- Weeks 3-4: produce one manually reviewed benchmark report.
- Weeks 5-8: produce five agent-assisted reports and extract reusable assets.
- Weeks 9-12: publish, interview users, and validate paid demand.

## Design Principle

Do not commercialize prompts, plugins, or agent wrappers as the product. Treat
them as internal execution infrastructure. The product is decision intelligence:
the structured ability to move a user from "I do not know where to enter" to
"I know what market and product test to run next."
