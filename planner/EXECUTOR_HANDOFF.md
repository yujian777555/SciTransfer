# SciTransfer Executor handoff — Round 005: D1 CPU MEASUREMENT MVP ONLY

Planner 已审查 Round004 commit `304d6a49254c6dded165dfc3f8eb2267d02382a0`。结论：**设计阶段 CONDITIONAL ACCEPTED**，但三学科独立性、评分器公平、策略学习与创新性都还没被实测。现在只允许 **Round005 D1（生物信息学差异表达）CPU 最小原型**，不允许 Phase1、D2/D3 大规模实现、付费 API 或 GPU/模型训练。

先 git pull --ff-only，读：
1. `status.json`
2. `planner/reviews/review_004.md`
3. `planner/latest_plan.md`
4. `planner/PROJECT_CHARTER.md`
5. `research/phase0d_method_proposal.md`

R5 Step 0：**先写清楚 NB DGP、批次/处理设计可识别性、动作-观测-结果和 raw FDP/power/cost 评分定义，必须先单独 commit 冻结规范。**
R5 Step 1：才实现 D1 engine + trusted isolated evaluator + real candidate loader (not fake canary), 最多 2 机制，无外部数据。
R5 Step 2：无 LLM，>=4 DEV instances 和 2 个同预算盲参考规则策略，检测评分是否非地板、策略 ID 是否不影响分数，真实证据改变下一动作。
R5 Step 3：assert-based security/scoring/replay tests、准确 pytest logs、schema 合规结果 `results/result_round_005.json`、分开的 safe DEV traces，状态更新、push main。

不得把手写规则叫 source-learned scientific strategy，也不得称模拟评分等于真实科研 Benchmark。不得改旧实验、不得自动进入 Phase1，任何硬条件失败必须 BLOCKED/NO-GO。
