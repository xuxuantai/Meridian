## Analysis Workbench — 嵌入 Qoder 的数据分析一致性工作台

### 一、问题回顾

在使用通用 AI Agent 做业务数据研报时，多轮交互会导致三类关键信息丢失或被篡改：

1. **指标口径漂移** — 对话推进过程中，之前确认的指标定义（如"活跃用户"的精确含义）被上下文压缩丢弃，后续分析不知不觉用了不同口径。
2. **结论前后矛盾** — 分析做了十几步后，新结论与早期结论冲突，但 Agent 没有能力自查，用户也难以人工排查。
3. **过程不可追溯** — 分析路径冗长，做到后面忘了前面做了什么，无法回溯决策链路。

Analysis Workbench 通过一套轻量外部机制解决这三个问题，不改造底层 Agent，而是给 Agent 配一个"外挂的记忆体和质量控制系统"。

---

### 二、整体架构

```
┌──────────────────────────────────────────────────────┐
│                    Qoder IDE                          │
│                                                      │
│  ┌────────────┐    ┌──────────────────────────────┐  │
│  │  Agent     │    │  Analysis Workbench Skill     │  │
│  │  (LLM)    │◄──►│                              │  │
│  │           │    │  ┌──────────┐ ┌────────────┐  │  │
│  │           │    │  │ Contract │ │   State    │  │  │
│  │           │    │  │ Manager  │ │  Tracker   │  │  │
│  │           │    │  └──────────┘ └────────────┘  │  │
│  │           │    │  ┌──────────┐ ┌────────────┐  │  │
│  │           │    │  │ Context  │ │ Consistency│  │  │
│  │           │    │  │ Injector │ │  Watchdog  │  │  │
│  └────────────┘    │  └──────────┘ └────────────┘  │  │
│                    └──────────────────────────────┘  │
│                              │                       │
│                    ┌─────────▼─────────┐             │
│                    │  项目文件系统       │             │
│                    │                   │             │
│                    │  .analysis/       │             │
│                    │  ├── contract.yaml│             │
│                    │  ├── state.yaml   │             │
│                    │  ├── changelog.md │             │
│                    │  └── report/      │             │
│                    └───────────────────┘             │
└──────────────────────────────────────────────────────┘
```

核心设计原则：**文件即状态**。所有分析状态以结构化文件形式存在于项目目录中，Agent 通过读写这些文件来维护一致性。这使得：

- 状态对用户完全透明（随时可以查看和修改）
- 天然支持 Git 版本管理（可追溯、可回滚）
- 不依赖任何外部服务（纯文件系统，零部署成本）
- 跨会话可恢复（关掉 Qoder 再打开，分析状态不丢失）

---

### 三、分析契约（Analysis Contract）

分析契约是整个系统的核心数据结构。它以 YAML 格式存储在 `.analysis/contract.yaml` 中，记录了一次分析任务中所有"不可违背"的约束。

#### 3.1 完整 Schema

```yaml
# .analysis/contract.yaml
meta:
  id: "analysis-2026-06-27-001"
  title: "2026Q2 用户增长归因分析"
  created: "2026-06-27T10:00:00+08:00"
  updated: "2026-06-27T10:00:00+08:00"
  phase: "contract"           # contract | retrieve | analysis | report | completed
  locked: false               # 全局锁定（report 阶段确认后设为 true）

# 指标定义 — 每个指标的精确定义，是整个分析的"度量衡"
metrics:
  - id: "active_user"
    name: "活跃用户"
    definition: "当日有至少一次核心行为（发帖、评论、点赞）的去重用户数"
    formula: "COUNT(DISTINCT user_id) WHERE action IN ('post','comment','like') AND date = target_date"
    unit: "人"
    exclusions:
      - "排除内部测试账号（user_tag = 'internal'）"
      - "排除注册未满24小时的账号"
    locked: false             # 锁定后不可在未确认情况下修改
    source: "用户确认"        # 来源标记：谁定义的、从哪来的
    version: 1

  - id: "new_user_7d_retention"
    name: "新用户7日留存率"
    definition: "注册后第7日（含）仍有至少一次登录行为的新用户占比"
    formula: "COUNT(DISTINCT CASE WHEN login_date = register_date + 7 THEN user_id END) / COUNT(DISTINCT register_user_id)"
    unit: "%"
    exclusions:
      - "排除通过内部邀请链接注册的账号"
    locked: false
    source: "产品需求文档 v3.2"
    version: 1

# 取数约束 — 数据源、时间范围、过滤条件
data_constraints:
  - id: "dc_time_range"
    description: "分析时间范围"
    rule: "2026-04-01 至 2026-06-26"
    locked: true

  - id: "dc_source"
    description: "数据源"
    rule: "使用 analytics_dw 数仓的 ods 层原始表"
    locked: false

  - id: "dc_test_accounts"
    description: "排除测试账号"
    rule: "WHERE user_tag != 'internal' AND user_tag != 'test'"
    locked: true

# 业务规则 — 分析过程中必须遵守的业务逻辑约束
business_rules:
  - id: "br_revenue"
    description: "营收口径"
    rule: "以财务系统确认的已回款金额为准，不含应收账款"
    locked: true

  - id: "br_cohort"
    description: "队列划分"
    rule: "按用户首次注册日所在自然周划分队列"
    locked: false

# 已锁定的结论 — 分析过程中确认的关键结论，不可被后续分析推翻
conclusions: []
  # 分析过程中逐步填入，格式见下方 state.yaml 中的 conclusions
```

#### 3.2 设计要点

**锁定机制（Lock）**：每个条目都有 `locked` 字段。一旦锁定，Agent 在后续分析中不可自行修改该条目——如果分析过程中发现需要修改已锁定的条目，必须显式向用户确认并记录修改原因。这直接解决了"口径漂移"问题。

**版本字段（Version）**：每个指标定义有版本号。如果经过用户确认后修改了已锁定的定义，版本号递增，并在 changelog 中记录变更原因。这使得口径变更完全可追溯。

**来源标记（Source）**：记录每个定义是从哪里来的——是用户口述的、产品文档定义的、还是 Agent 推断后用户确认的。不同来源的可信度不同，后续校验时的权重也不同。

---

### 四、分析状态（Analysis State）

状态文件 `.analysis/state.yaml` 记录分析的实时进展，是分析的"工作记忆"。

```yaml
# .analysis/state.yaml
current_phase: "analysis"     # 当前阶段
current_step: 3               # 当前步骤编号
started: "2026-06-27T10:00:00+08:00"

# 已确认的结论
conclusions:
  - id: "c1"
    statement: "Q2 新用户7日留存率整体为 34.2%，较 Q1 下降 3.1pp"
    evidence: "基于 analytics_dw.user_retention_7d 表计算，排除测试账号"
    depends_on: []            # 依赖的前置结论
    metrics_used: ["new_user_7d_retention"]
    locked: true
    confirmed_at: "2026-06-27T11:30:00+08:00"

  - id: "c2"
    statement: "留存下降主要由 5月注册渠道质量变化驱动"
    evidence: "分渠道对比显示，信息流渠道留存从 38% 降至 29%"
    depends_on: ["c1"]        # 依赖 c1 的结论
    metrics_used: ["new_user_7d_retention", "active_user"]
    locked: true
    confirmed_at: "2026-06-27T14:00:00+08:00"

# 决策日志 — 分析过程中的关键决策
decisions:
  - step: 2
    decision: "选择按周而非按天做队列分析，因为日粒度噪声过大"
    rationale: "对比了日粒度和周粒度的趋势图，日粒度波动超过 ±15%"
    timestamp: "2026-06-27T10:45:00+08:00"

# 数据快照 — 关键中间结果，供后续引用
snapshots:
  - id: "s1"
    description: "Q2 各周留存率明细"
    data_summary: "W14: 36.1%, W15: 35.0%, W16: 33.8%, ..."
    file_ref: ".analysis/report/retention_weekly.csv"
    created: "2026-06-27T11:00:00+08:00"
```

#### 4.1 设计要点

**结论依赖链**：每个结论通过 `depends_on` 字段声明依赖关系，形成一个有向无环图（DAG）。当某个基础结论被修改时，所有依赖它的下游结论自动标记为"需重新验证"。这解决了"结论前后矛盾"的问题——不是靠 Agent 的记忆，而是靠显式的依赖关系图。

**决策日志**：记录分析过程中的关键决策及其理由。当 Agent 在后续步骤中"忘记"为什么选择了某个分析方法时，可以回溯决策日志。这解决了"过程不可追溯"的问题。

**数据快照**：保存关键中间结果的摘要和文件引用。避免 Agent 在后续步骤中需要重新执行查询来获取已知结果，同时也提供了审计线索。

---

### 五、工作流设计

整个分析过程分为 5 个阶段，每个阶段有明确的输入、输出和"阶段门禁"（Phase Gate）。

```
  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
  │  1.对齐  │───►│  2.取数  │───►│  3.分析  │───►│  4.报告  │───►│  5.验证  │
  │ Contract │    │ Retrieve │    │ Analysis │    │  Report  │    │  Verify  │
  └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
       │               │               │               │               │
       ▼               ▼               ▼               ▼               ▼
   contract.yaml   SQL + 数据      结论逐步锁定     报告草稿      一致性校验报告
   初稿完成        准备就绪        conclusions[]    report.md     通过/不通过
```

#### Phase 1: 对齐（Contract）

**目标**：与用户确认分析主题、核心指标定义、取数约束。

Agent 行为：
1. 询问用户本次分析的主题和目标
2. 根据主题，引导用户定义核心指标（如果用户提供了指标文档，从中提取）
3. 将提取的指标定义、约束条件写入 `contract.yaml`
4. 逐一向用户确认每个定义是否正确
5. 用户确认后，将关键条目锁定

**阶段门禁**：用户明确确认"契约没问题，开始取数"后，进入下一阶段。

**再注入点**：无（这是起点）。

#### Phase 2: 取数（Retrieve）

**目标**：根据契约编写取数逻辑，获取数据。

Agent 行为：
1. **再注入**：读取 `contract.yaml` 中的 metrics 和 data_constraints，将其作为取数的约束条件注入当前思考
2. 编写 SQL 或取数脚本
3. 执行取数，验证数据基本质量（行数、空值、异常值）
4. 将取数逻辑记录到 `state.yaml` 的 decisions 中

**阶段门禁**：数据获取成功，基本质量检查通过。

**关键约束**：Agent 编写 SQL 时，必须逐条核对 contract 中的 exclusions 和 data_constraints，不得遗漏。

#### Phase 3: 分析（Analysis）— 核心阶段

**目标**：执行分析，逐步产出并锁定结论。

Agent 行为（每个分析步骤）：
1. **再注入**：读取 `contract.yaml` 中与当前步骤相关的指标定义 + 已锁定结论
2. 执行当前分析步骤
3. **一致性校验**：检查当前步骤的输出是否与已锁定的指标定义和结论一致
4. 如果产生新结论：写入 `state.yaml` 的 conclusions，询问用户是否锁定
5. 如果修改了指标定义：更新 `contract.yaml`，递增 version，记录到 changelog

**阶段门禁**：所有分析步骤完成，核心结论均已锁定。

**这是再注入和校验最密集的阶段**：每一步都要"先读契约、再做分析、后校验一致性"，形成一个闭环。

#### Phase 4: 报告（Report）

**目标**：汇总分析结论，生成结构化研报。

Agent 行为：
1. **全量再注入**：读取完整的 `contract.yaml` 和 `state.yaml`
2. 基于已锁定的结论撰写报告
3. **引用校验**：报告中每个数据点和结论都必须能追溯到 `state.yaml` 中的某条 conclusion 或 snapshot
4. 生成报告文件

**阶段门禁**：报告生成完成，用户确认报告内容。

#### Phase 5: 验证（Verify）

**目标**：对报告进行最终一致性校验。

校验清单：
- [ ] 报告中每个指标的使用是否与 contract 定义一致
- [ ] 报告中每个结论是否与 state 中的锁定结论一致
- [ ] 报告中的数据引用是否与 snapshots 匹配
- [ ] 是否存在未记录在 contract 中的隐式假设
- [ ] 结论依赖链是否完整（每个结论的 evidence 是否充分）

输出：校验报告，标注通过/不通过及具体问题。

---

### 六、核心机制详解

#### 6.1 再注入机制（Context Re-injection）

再注入是本系统最核心的机制。其原理是：在 Agent 执行每个分析步骤之前，从外部状态文件中提取相关信息，注入到当前对话的上下文中，确保 Agent "不会忘记"关键约束。

**注入策略**：

| 阶段 | 注入内容 | 注入时机 |
|------|---------|---------|
| Contract | 无 | — |
| Retrieve | 全部 metrics 定义 + data_constraints | 写 SQL 前 |
| Analysis | 当前步骤相关的 metrics + 全部已锁定 conclusions | 每步分析前 |
| Report | 完整 contract + 完整 state | 写报告前 |
| Verify | 完整 contract + 完整 state + 报告 | 校验前 |

**注入方式**：通过 Skill 指令引导 Agent 在每个步骤开始时主动读取相关文件。在 Qoder 的 Skill 框架中，这通过 SKILL.md 中的流程指令实现——Agent 被指示在每步开始前"先读取 contract.yaml 中的相关定义"。

**动态筛选**：在 Analysis 阶段，全量注入可能浪费上下文。更优的做法是根据当前分析涉及的指标 ID，只注入相关的 metric 定义。这通过在 Skill 中指导 Agent "只读取与当前分析步骤相关的指标定义"来实现。

#### 6.2 一致性校验（Consistency Watchdog）

校验发生在两个层面：

**步骤级校验**（Analysis 阶段每步执行后）：
1. 提取当前输出中涉及的所有指标名称
2. 与 contract.yaml 中对应指标的定义对比
3. 检查当前输出的数值计算是否与定义中的 formula 和 exclusions 一致
4. 检查当前结论是否与已有 locked conclusions 矛盾

**报告级校验**（Verify 阶段）：
1. 扫描报告中所有定量陈述
2. 逐条与 state.yaml 中的 conclusions 和 snapshots 交叉验证
3. 检查报告中是否有未追溯到 state 的"无源结论"
4. 输出校验结果报告

**校验结果处理**：
- 通过：正常继续
- 警告：标注潜在问题，让用户决定
- 失败：阻断流程，要求用户确认后才能继续

#### 6.3 变更日志（Changelog）

`.analysis/changelog.md` 记录所有对契约和状态的修改：

```markdown
## 2026-06-27 10:30 — 指标定义更新
- 指标: active_user
- 变更: 新增排除条件"排除注册未满24小时的账号"
- 原因: 用户指出注册当天行为不代表真实活跃
- 版本: v1 → v2
- 影响结论: 无（尚未开始计算该指标）

## 2026-06-27 14:15 — 结论修正
- 结论 ID: c2
- 变更: 留存下降归因从"渠道质量"细化为"信息流渠道占比提升"
- 原因: 进一步分析发现渠道留存率本身未变，是渠道结构变化导致
- 影响结论: c3（需重新验证）
```

---

### 七、文件结构

一个使用 Analysis Workbench 的项目，目录结构如下：

```
my-analysis-project/
├── .analysis/                    # Workbench 工作目录
│   ├── contract.yaml             # 分析契约（核心）
│   ├── state.yaml                # 分析状态
│   ├── changelog.md              # 变更日志
│   └── report/                   # 分析产出物
│       ├── retention_weekly.csv
│       ├── channel_breakdown.csv
│       └── final_report.md
├── queries/                      # 取数脚本
│   ├── 01_user_retention.sql
│   └── 02_channel_analysis.sql
├── AGENTS.md                     # 项目级 Agent 指令（可选）
└── README.md                     # 分析项目说明
```

---

### 八、与 Qoder 的集成方式

Analysis Workbench 以一个 Qoder Skill 的形式交付。用户安装 Skill 后，在 Qoder 中触发分析工作流时，Skill 会自动引导 Agent 按照上述流程执行。

#### 8.1 Skill 结构

```
analysis-workbench/
├── SKILL.md                      # 核心 Skill 文件（流程指令）
├── templates/
│   ├── contract_template.yaml    # 契约模板
│   └── state_template.yaml       # 状态模板
└── scripts/
    └── verify_consistency.py     # 一致性校验脚本（辅助）
```

#### 8.2 触发方式

- **显式触发**：用户说"开始一个分析任务"或"帮我做 XX 分析"时，Agent 识别并调用 Skill
- **隐式触发**：当用户的工作涉及 SQL 取数、指标计算、趋势分析等关键词时，Agent 自动建议启用 Workbench 模式

#### 8.3 与 Qoder 特性的结合

- **Git 集成**：`.analysis/` 目录天然支持 Git 管理，每次阶段转换建议用户 commit
- **文件预览**：contract.yaml 和 state.yaml 可以随时在 Qoder 中打开查看
- **终端集成**：取数和分析步骤可以直接在 Qoder 终端中执行
- **跨会话恢复**：由于状态全部持久化到文件，关掉 Qoder 再打开后，Agent 读取 `.analysis/state.yaml` 即可恢复到上次中断的地方

---

### 九、典型交互流程示例

```
用户: 帮我做一个 Q2 用户留存分析报告

Agent: [触发 Analysis Workbench Skill]
       好的，我来启动分析工作台。首先进入对齐阶段——
       请告诉我：
       1. 本次分析的核心问题是什么？
       2. 需要关注哪些关键指标？
       3. 有没有现成的指标定义文档可以参考？

用户: 主要看新用户7日留存率的趋势和下降原因。
      指标定义参考这个文档：[附件]

Agent: [提取指标定义，生成 contract.yaml 初稿]
       我从文档中提取了以下指标定义，请确认：
       
       ■ 新用户7日留存率：注册后第7日有登录行为的新用户占比
         - 排除内部邀请注册
         - 排除注册未满7天的用户
       
       ■ 活跃用户：当日有核心行为的去重用户
         - 核心行为：发帖、评论、点赞
         - 排除测试账号
       
       这些定义是否准确？有没有需要补充的约束条件？

用户: 活跃用户还需要排除注册未满24小时的

Agent: [更新 contract.yaml，记录变更]
       已更新。活跃用户新增排除条件：注册未满24小时。
       契约确认完毕，进入取数阶段。
       [读取 contract.yaml 中的 data_constraints]
       [编写 SQL，执行取数...]
       
       ...（分析过程）...

Agent: [步骤级校验]
       ⚠ 注意：当前步骤计算的留存率为 38.5%，但按照契约定义
       （排除注册未满7天的用户），这里是否包含了注册第1-6天的用户？
       建议检查 SQL 中的日期过滤条件。

用户: 你说得对，我改下 SQL

       ...（继续分析）...

Agent: [产出结论]
       结论 C1：Q2 新用户7日留存率整体 34.2%，较 Q1 下降 3.1pp。
       是否锁定此结论？

用户: 确认锁定

Agent: [写入 state.yaml，标记 locked: true]
       结论已锁定。继续下一步分析...
```

---

### 十、边界与演进

#### 当前方案的边界

1. **上下文窗口硬约束**：当分析涉及 20+ 指标、50+ 结论时，即使按需注入也可能占据大量上下文。此时需要拆分子任务。
2. **校验覆盖率**：一致性校验基于指标定义的文本匹配和数值比对，无法捕捉深层的分析逻辑错误（如因果推断错误）。
3. **用户配合成本**：锁定确认、定义校验等步骤会增加交互轮数，对于快速探索性分析可能过于"重"。

#### 演进方向

1. **轻模式 / 重模式切换**：探索性分析使用轻模式（简化契约、减少校验），正式报告使用重模式（完整契约、严格校验）。
2. **指标库沉淀**：跨分析任务复用已验证的指标定义，形成组织级的"指标知识库"。
3. **自动化校验脚本**：将一致性校验从 Agent 的"自校验"升级为独立的 Python 脚本执行，提高校验的可靠性。
4. **与 BI 工具联动**：将 contract.yaml 中的指标定义自动同步到 BI 工具的指标管理层，确保分析与看板口径一致。
