# SciTransfer — Executor Handoff: Round 002 (Phase 0-B)

你是 SciTransfer Executor（Kimi/MiMo），ChatGPT 是科研 Planner。仓库 main 为唯一事实来源：https://github.com/yujian777555/SciTransfer

**Planner 已关闭 Round 001：PARTIAL / INCONCLUSIVE，未验收其跨领域策略迁移结果。现在开始 Round 002（Phase 0-B）：Benchmark 适用性与多步科研决策可执行性评估。**

开始前执行 git pull --ff-only，读取 status.json、planner/reviews/review_001_r3.md、planner/latest_plan.md。

1. 保留过去 001/R1/R2/R3 原始记录不改，增加 results/round_001_r3_erratum.md 说明 R3 300s vs hardcoded 601.3s、R3 CSV 与 JSON 行数不匹配、Task85 exception->SUCCESS/0、Task16 空结果、Task21 未评分，以及候选程序能访问 gold junction 的风险。不能编造追溯时间。
2. **不要再无期限重跑 Task21，也不需要继续修 Docker 十几轮。**
3. 按新计划验证至少两个候选环境（推荐 DiscoveryWorld 与现有 ScienceAgentBench 或 SciAgentGym），必须实测可安装、可 reset、真正有科研 action/observation/score。明确区分不同主题与真正跨学科目标。
4. 仅为一个最合适环境实现最小多步决策 runner：observe→decide→act→evidence→decide again；每臂可用工具相同，不允许候选程序读取隐藏 gold。
5. 做极小规模、有上限的真实校准试验（建议总共 6-10 episodes，API 花费上限 1 USD，超出先问用户），报告真实 scorer、轨迹、成本及 floor/ceiling 情况。此处手写策略仅为 feasibility，**不能号称已学会迁移**。
6. 给出 GO/CONDITIONAL/NO-GO 的研究决策。记录 accepted/blocked 项、具体原始日志、版本及 hashes。
7. 写入 results/result_round_002.json，更新 status.json，测试后 commit/push main；最后汇报最终 SHA、任务/领域覆盖、多步轨迹、真实评分和是否达到 R2B-01～08。

**禁止**重新生成 Round001 六份代码，擅自开始 Phase1 训练，捏造跨领域效果，自行宣布 Planner 验收。
