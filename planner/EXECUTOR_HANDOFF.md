# SciTransfer Executor handoff — ACTIVE Round 003-R1

用户已同意按 Planner 推荐的 A 路线再进行**一次** SciAgentGYM 本地可执行验证；不是授权无期限安装或自动切换科研方向。

仓库：https://github.com/yujian777555/SciTransfer ，main。
上游 SciAgentGYM：https://github.com/CMarsRover/SciAgentGYM
**固定版本：`e9dbbea4369d67694e38bf8be67bedbcaf9e9300`**；其根 LICENSE 已确认 Apache-2.0（仍需查第三方内容授权）。

`git pull --ff-only origin main` 后读 `status.json`, `planner/latest_plan.md`, `planner/reviews/review_003.md`。本轮任务是 `Round 003-R1`，不是 Phase1。

严格限制：**零付费 API、零训练、最长 2 小时、最多两个有界源码获取路径**。检查本地缓存、合法 archive/HTTPS checkout，实际验证 SHA。网络若仍阻塞，直接给 BLOCKED_SOURCE_ACCESS 及命令日志，不要无限重试。

若能取得源码，先轻量安装，实际运行科学工具 A→观察→依赖证据选择工具 B，再从另一真正学科验证一个小例子；禁止虚构工具结果。对比官方评分器：它在某些 mismatch 时会进入 secondary_verification_with_llm，必须以禁止外联的测试夹具检查，不得冒充纯离线官方评估。严格隔离 `answer`、`golden_answer`、`solution_steps`、`tool_expected`，动态 canary 验证候选输入及 Git 导出没有任何 gold。不得把上游完整数据库/答案提交 SciTransfer。

交付：`results/round_003_r1_preflight.md`、`benchmarks/round_003_r1_sciagentgym_runtime.md`、`results/round_003_r1_scorer_integrity.md`、`results/result_round_003_r1.json`、`status.json`，测试后 commit push main。报告 R3R1-01~08、真实 SHA/运行/成本以及 GO/CONDITIONAL/NO-GO。

**如果仍不能运行，停下来交 Planner 和用户决定是否改为受控实验环境，不可擅自开始 B 路线。**
