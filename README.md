# Meridian

Meridian 是一套让 AI Agent 做专业商业/数据分析时更严谨、更可追溯、可复用的 Analysis Harness。

它不是单一分析模板，也不是某个垂直行业工具。Meridian 的核心目标是把专业分析师在多轮分析中的关键能力结构化：

- 指标口径保持一致
- 结论前后不矛盾
- 分析过程可追溯
- 数据、假设、判断和建议可复核
- 领域分析方法可以沉淀为可复用资产

## 架构

```text
Meridian
├── core/                         # 通用分析 Harness
│   ├── templates/                # 分析契约与状态模板
│   └── evaluation/               # 一致性校验工具
├── skills/                       # Agent 指令层
│   └── meridian-analysis-harness/
└── domains/                      # 垂直领域分析包
    └── cross-border/
```

## 核心关系

```text
Meridian = 专业分析 Harness

core = 分析协议、状态管理、校验机制
skills = 让通用 Agent 遵守 Meridian 工作流的指令层
domains = 在具体商业场景中复用 Meridian 的领域资产包
```

## Core Harness

`core/` 是 Meridian 的通用底座，沉淀跨场景复用的分析协议。

当前包括：

- `core/templates/analysis-contract.yaml`
- `core/templates/analysis-state.yaml`
- `core/evaluation/verify_consistency.py`

它解决多轮 AI 辅助分析中的三个核心问题：

- **指标口径漂移**：对话推进中指标定义被遗忘或篡改
- **结论前后矛盾**：新结论与早期结论冲突且无法自查
- **过程不可追溯**：分析路径冗长，决策链路丢失

核心机制是"分析契约"：

```text
分析需求
  -> contract.yaml 锁定指标、约束和业务规则
  -> state.yaml 记录阶段、结论和决策日志
  -> 每一步分析前读取约束
  -> 每一步分析后校验一致性
  -> 最终报告可追溯到锁定结论和数据证据
```

## Agent Skill

`skills/meridian-analysis-harness/` 是 Meridian 的通用 Agent 指令层。

它可以复制到不同 AI 工具的指令目录中：

| 工具 | 放置路径 |
|------|---------|
| QoderWork | `~/.qoderwork/skills/<skill-name>/SKILL.md` |
| Cursor | 项目根目录 `.cursor/rules/` |
| Claude Code | 项目根目录 `CLAUDE.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| 通用 | 直接作为 system prompt 或上下文文件提供给 Agent |

使用方式：

```bash
cp -R skills/meridian-analysis-harness ~/.qoderwork/skills/
```

## Domain Pack: Cross-border

`domains/cross-border/` 是 Meridian 的第一个垂直领域包。

它面向企业出海市场机会分析，聚焦：

> 国家 x 产品 x 产业带 出海机会分析

它不重新开发通用 Agent，而是在 Meridian Harness 之上沉淀专业分析资产：

- Analysis Skill
- Domain Knowledge
- Metrics
- Evaluation
- Report Templates
- Analysis Workspace CLI

使用方式：

```bash
cd domains/cross-border
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

## Consistency Check

`verify_consistency.py` 可作为独立的一致性校验工具运行：

```bash
pip install pyyaml
python core/evaluation/verify_consistency.py .analysis/
```

## Project Structure

```text
Meridian/
├── core/
│   ├── templates/
│   │   ├── analysis-contract.yaml
│   │   └── analysis-state.yaml
│   └── evaluation/
│       └── verify_consistency.py
├── skills/
│   └── meridian-analysis-harness/
│       └── SKILL.md
├── domains/
│   └── cross-border/
│       ├── docs/
│       ├── projects/
│       ├── knowledge/
│       ├── skills/
│       ├── metrics/
│       ├── evaluation/
│       ├── templates/
│       ├── schemas/
│       └── src/cbi/
├── LICENSE
└── README.md
```

## License

MIT
