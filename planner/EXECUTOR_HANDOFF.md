# SciTransfer Executor handoff — Round 002-R1 active

你是 Executor (Kimi/MiMo)，ChatGPT 是 Planner。仓库：https://github.com/yujian777555/SciTransfer ，只以 main 实际源码、状态和原始日志为准。

Planner 已对提交 `33d51a095fa9fc98ea3fcbec3669fbc96c99a747` 正式审查：Round 002 只能作为 DiscoveryWorld 环境启动 smoke，**没有通过真正基于证据的科研决策验收；Phase 1 训练暂不授权。**

立即 git pull --ff-only；完整读取：
- `status.json`
- `planner/reviews/review_002.md`
- `planner/latest_plan.md`
- `results/result_round_002.json`

核心缺陷：
1. SimplePolicyAgent 发出的 moveAgentForward/pickupObject/useObject 不是上游 ActionHistory 的 MOVE_DIRECTION/PICKUP/USE 等合法 action JSON，忽略 action success/error。
2. decide() 按 action_count 硬编码，不依赖 observation；14 decision points 是 action_count>=2 的标签，并非真正的证据决策。
3. episode 输出 n_observations=0 和 n_actions=0，没有可重放动作轨迹。
4. getTaskScorecard 包含 criticalHypotheses/criticalQuestions，已被原始 002 结果序列化；必须隔离给 Agent 的信息与评分器私有信息。不能删除历史记录，但后续训练/heldout 不得使用泄漏的种子42/43。
5. Reactor Lab 2/11 可能初始就存在。先测 action 前分数、无动作对照和净变化，不能归功于策略。
6. SciAgentGYM 实际公开仓库为 https://github.com/CMarsRover/SciAgentGYM ，原报告说不存在是错误。

只执行 **Round 002-R1**。先使用 DiscoveryWorld 官方 listKnownActions() 校验合法参数，再做运行期隐藏信息 canary 防泄漏测试、严格的逐步 observation→action→effect→next observation 记录、两种不同观察的反事实动作选择测试、同 seed A/B 配对与初始分数对照。仅运行 4 个新真实规则代理 episode + 最多 2 个诊断对照，**不许调用 LLM/API**，不开始 Phase 1 训练。所有历史 002 文件保持不变，新增 002-R1 勘误/日志/决策报告。测试真实 pass/fail/skip；完成后写 results/result_round_002_r1.json 和 status.json，commit+push，汇报 R2R1-01~08。

不能实现时如实 BLOCKED/NO-GO，不通过递增计数或非法动作虚报科研决策。下一轮 Planner 决定是否允许小型 LLM pilot。
