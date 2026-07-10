# Meridian

面向数据分析师、商业分析师和 AI Agent 的工具与方法论集合。目标是让日常分析工作（SQL 取数、指标计算、趋势归因、研报撰写）和专业商业决策分析更严谨、更可追溯、更可复用。

## 内容

### analysis-workbench — 数据分析一致性工作台

解决多轮 AI 辅助分析中的三个核心问题：

- **指标口径漂移** — 对话推进中指标定义被遗忘或篡改
- **结论前后矛盾** — 新结论与早期结论冲突且无法自查
- **过程不可追溯** — 分析路径冗长，决策链路丢失

通过"分析契约"（Analysis Contract）机制，将指标定义、取数约束、业务规则结构化存储在外部状态文件中，Agent 每步操作前强制读取、操作后强制校验，保持分析过程的一致性和可控性。

### cross-border-intelligence — 跨境决策智能引擎

面向企业出海市场机会分析的 Decision Intelligence 项目骨架。

它不重新开发通用 Agent，而是沉淀通用 Agent 之上的专业分析资产：

- Analysis Skill
- Domain Knowledge
- Metrics
- Evaluation
- Report Templates
- Analysis Workspace CLI

第一阶段聚焦：

> 国家 x 产品 x 产业带 出海机会分析

目标是用通用 Agent + Analysis Harness 复制优秀商业分析师的工作方式，并通过公开内容、定制报告和企业反馈逐步形成可商业化的 AI 决策产品。

## 使用方式

本项目包含两类资产：

1. 可直接安装到 AI 工具中的 `SKILL.md` 指令资产。
2. 可作为独立项目运行的分析工作区、schema、模板和 CLI。

### 使用 analysis-workbench

| 工具 | 放置路径 |
|------|---------|
| QoderWork | `~/.qoderwork/skills/<skill-name>/SKILL.md` |
| Cursor | 项目根目录 `.cursor/rules/` |
| Claude Code | 项目根目录 `CLAUDE.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| 通用 | 直接作为 system prompt 或上下文文件提供给 Agent |

### 快速开始

1. 将 `skill/analysis-workbench/` 复制到你的 AI 工具对应的指令目录
2. 开始数据分析对话，Agent 会按照五阶段流程（对齐→取数→分析→报告→验证）执行

### 使用 cross-border-intelligence

```bash
cd projects/cross-border-intelligence
PYTHONPATH=src python3 -m cbi.cli list
PYTHONPATH=src python3 -m cbi.cli validate templates/analysis-task.yaml --kind task
```

创建一份新的跨境分析任务：

```bash
PYTHONPATH=src python3 -m cbi.cli new-task \
  --product "outdoor lighting" \
  --supply-chain "Guangdong" \
  --markets "Saudi Arabia,Poland,Mexico" \
  --title "Outdoor lighting export opportunity scan"
```

### 独立校验脚本

`verify_consistency.py` 可作为独立的一致性校验工具运行：

```bash
pip install pyyaml
python skill/analysis-workbench/scripts/verify_consistency.py .analysis/
```

## 项目结构

```
Meridian/
├── skill/
│   └── analysis-workbench/      # 数据分析一致性工作台
│       ├── SKILL.md             # Agent 指令文档（核心）
│       ├── templates/           # 契约与状态模板
│       └── scripts/             # 一致性校验脚本
├── projects/
│   └── cross-border-intelligence/
│       ├── docs/                # 项目总纲与操作说明
│       ├── projects/            # 单次跨境分析任务
│       ├── knowledge/           # 领域知识资产
│       ├── skills/              # 结构化分析技能
│       ├── metrics/             # 指标定义与评分逻辑
│       ├── evaluation/          # 结果评估与质量门禁
│       ├── templates/           # 任务与报告模板
│       ├── schemas/             # YAML schema
│       └── src/cbi/             # Analysis Workspace CLI
├── LICENSE
└── README.md
```

## License

MIT
