# Meridian

面向数据分析师的工具与方法论集合。目标是让日常分析工作（SQL 取数、指标计算、趋势归因、研报撰写）更严谨、更可追溯。

## 内容

### analysis-workbench — 数据分析一致性工作台

解决多轮 AI 辅助分析中的三个核心问题：

- **指标口径漂移** — 对话推进中指标定义被遗忘或篡改
- **结论前后矛盾** — 新结论与早期结论冲突且无法自查
- **过程不可追溯** — 分析路径冗长，决策链路丢失

通过"分析契约"（Analysis Contract）机制，将指标定义、取数约束、业务规则结构化存储在外部状态文件中，Agent 每步操作前强制读取、操作后强制校验，保持分析过程的一致性和可控性。

## 使用方式

本项目的核心资产是 SKILL.md 格式的 Agent 指令文档，可适配各种 AI 编程助手。不同工具放置位置不同：

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
├── LICENSE
└── README.md
```

## License

MIT
