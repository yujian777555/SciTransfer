# SciTransfer — Kimi Executor Handoff (copy/paste)

你是 SciTransfer 项目的 **Executor（执行者）**；ChatGPT 是唯一的 **Planner（规划者）**。
仓库：https://github.com/yujian777555/SciTransfer
唯一事实来源是 GitHub `main` 分支内真实代码、记录、状态和实验数据，而不是聊天总结。

**请直接开始 Round 001，不要创建新项目，也不要重写科研目标：**

1. 克隆或拉取 `main`，检查 HEAD、`git status`。
2. 完整读取：`status.json`、`planner/PROJECT_CHARTER.md`、`planner/latest_plan.md`、`planner/STATUS_PROTOCOL.md`、`schemas/result_round.schema.json`。
3. 严格按最新计划执行：**真实 ScienceAgentBench verified 环境的核实、最小 Python 接口、No-Strategy vs Fixed-Strategy 配对运行器、三个领域官方评估、真实轨迹与成本记录**。
4. 遵守硬验收 AC-01 至 AC-06。优先验证真实 benchmark 环境，避免先写大量抽象架构。
5. 所有 mock/synthetic 结果只能作为 infra test，绝不能充作真实科学结果。
6. 如果官方基准无法运行、选定学科不可用、预算不足或需要用户提供凭证，清楚记录 BLOCKED 和最小解阻步骤；不要伪造成功。
7. 全部实现、测试、结果及 `status.json` 提交并 push；`state` 只能设置 `AWAITING_PLANNER_REVIEW`、`PARTIAL` 或 `BLOCKED`，不得自行验收为 ACCEPTED。
8. 最后回报 HEAD SHA、三领域的真实任务 ID、真实 A/B 配对次数、官方评分原始路径、测试通过/失败/跳过数量、未达标 AC 和后续预计成本。

**严禁**绕过官方 evaluator、读取泄漏的隐藏答案、引入虚构结果、私自扩大高成本实验、擅自改变研究方向、把“做了几个 Agent”作为创新性主张。

如计划与当前仓库状态冲突，暂停并反馈实际差异，由 Planner 决策。
