# Meridian

面向数据分析师的工具与方法论集合。目标是让日常分析工作（SQL 取数、指标计算、趋势归因、研报撰写）更严谨、更可追溯。

## 内容

### analysis-workbench — 数据分析一致性工作台

解决多轮 AI 辅助分析中的三个核心问题：

- **指标口径漂移** — 对话推进中指标定义被遗忘或篡改
- **结论前后矛盾** — 新结论与早期结论冲突且无法自查
- **过程不可追溯** — 分析路径冗长，决策链路丢失

通过"分析契约"（Analysis Contract）机制，将指标定义、取数约束、业务规则结构化存储在外部状态文件中，Agent 每步操作前强制读取、操作后强制校验，保持分析过程的一致性和可控性。

详见 [docs/analysis-workbench-design.md](docs/analysis-workbench-design.md)

## 使用方式

### 作为 QoderWork Skill 使用

1. 将 `analysis-workbench/` 目录复制到 `~/.qoderwork/skills/analysis-workbench/`
2. 在 QoderWork 中开始新的分析对话，Skill 会自动触发

### 独立使用

`analysis-workbench/scripts/verify_consistency.py` 可作为独立的一致性校验脚本运行：

```bash
pip install pyyaml
python analysis-workbench/scripts/verify_consistency.py .analysis/
```

## 项目结构

```
Meridian/
├── analysis-workbench/          # 数据分析一致性工作台
│   ├── SKILL.md                 # Skill 核心流程指令
│   ├── templates/               # 契约与状态模板
│   └── scripts/                 # 一致性校验脚本
├── docs/                        # 设计文档
├── LICENSE
└── README.md
```

## License

MIT
