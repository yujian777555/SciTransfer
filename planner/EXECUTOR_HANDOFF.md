# SciTransfer Executor handoff — USER APPROVED B, ROUND 004 DESIGN ONLY

已获用户明确批准换到 **受控跨领域科学研究过程测量方法（B 路线）**。ChatGPT = Planner；Kimi/MiMo = Executor。仓库 main：https://github.com/yujian777555/SciTransfer 。

这次**不是再次修 SciAgentGYM**，也不是允许马上建大规模 simulator。新的 Round 004 (Phase 0-D) 只产出论文级研究设计与技术可行性审计。

git pull --ff-only 后完整阅读：
- status.json
- planner/PROJECT_CHARTER.md
- planner/latest_plan.md
- research/phase0d_method_proposal.md
- research/phase0d_related_work_novelty_audit.md
- research/phase0d_experiment_protocol.md

必须围绕：Bioinformatics 批次与重复验证、Chemistry 有噪声实验优化、GIS 空间抽样及地理阻塞验证；这三类必须具有真实不同的统计/物理失败机制，不是同个bandit换名。设计隐藏真值的独立评分器和相同 agent/工具/预算的 paired A/B/placebo，源领域轨迹学习策略、目标领域留出测试、负迁移与校准拒绝。明确 **synthetic scientific workflow**, 不准表述为真实湿实验提升。

特别注意已撞车文献：SciAgentGym(ICML26)已经研究科学工具迁移，Memory Transfer Learning(2026)讨论抽象迁移和负迁移，MCMA已研究分层记忆。创新只能严谨评估 outcome-calibrated selection / mechanistic transfer limits，不得宣称 first / SOTA。

交付 method、novelty matrix、experiment matrix、engineering spec、research decision、result_round_004_design.json 和 status.json；每个文件普通 Git 可读。**零付费 API，零 GPU，零模型训练，零 scored target tests，不能进入 Phase1**。完成后 push main 并交 Planner 正式验收，再决定是否批准 CPU MVP。
