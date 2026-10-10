# SciTransfer — Executor Handoff: Phase0E / Round006 REAL-DATA FEASIBILITY DESIGN ONLY

用户已批准对 SciTransfer 采用真实公开科学分析任务、独立结果评分的方向重新规划。**这是科研设计/可行性阶段，不是开始下一轮编码或训练。** 原 D1 模拟器 R5R1 已 NO-GO，禁止继续修补原模拟器，不许自动做新 simulator。

main: https://github.com/yujian777555/SciTransfer
`git pull --ff-only origin main` 后读 `status.json`, `planner/latest_plan.md`, `research/phase0e_real_data_candidate_audit.md`, `research/phase0e_method_real_data.md`, `research/phase0e_novelty_feasibility.md`。

优先真实独立标签：
- ESOL/DeepChem 真实水溶性实验标签 + scaffold holdout；
- NOAA GHCN-Daily 小范围真实气象站标签 + spatial blocked holdout；
- airway/pasilla + DESeq2 仅第三领域候选；没有完备真实 DE gene gold，不准捏造 FDP/Power gold。

必须明确这只是**真实数据的回顾性分析过程**，不是新做实验或发明化学反应。构建可复现的分析动作/公共DEV反馈/隔离TEST评分协议、source-only process strategy 与强统计/ML baselines，严格检查是否仅仅是常识性的 cross-validation checklist 已撞车。保证真实科学任务与策略迁移有论文创新可能性，否则 NO-GO。

本轮 **0 API / 0 GPU / 0 训练 / 0 新增可执行系统 / 0 实验成绩**。只写数据审计、Method、识别协议、撞车分析、可行性决策与 schema 合规设计结果，更新 status 后 push。实际 CPU 下载/软件安装/小规模真实任务 smoke 必须等 Planner 下一轮单独批准。
