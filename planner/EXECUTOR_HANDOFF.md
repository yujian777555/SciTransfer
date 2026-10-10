# SciTransfer Executor handoff — Round005-R1 D1 scientific measurement FIX, LAST D1 GATE

Planner 审查 Round005 `c9b0d7030eb53339479174c26046487b2981a81d` 的源文件和8条DEV成绩后发现：独立规范先提交确实成功；但是 D1 engine 中分配重复/QC/加对照/拟合动作均不改变数据；反馈策略按 step 决定动作且计算高方差量后从未用于决策；Action.cost 可由调用者伪造/写负数；空报告 utility=0.4（8条 DEV 中高于6条）；同进程 engine.truth 直接可访问，所谓独立评分没有 OS 边界；M1 应常数 phi 代码却始终随机；重复提交 gene IDs 扭曲 FDP；结果 JSON 不满足 schemas/result_round.schema.json。

**R5-01 PASS，R5-02/04/06 PARTIAL，R5-03/05 FAIL。测量有效性没有验收。**

只允许一次 CPU/$0 Round005-R1 核心修复。拉取 main 并读 `planner/reviews/review_005.md`、`planner/latest_plan.md` 和 `status.json`。

1. 新规范 `research/round_005_r1_d1_corrective_spec.md` + 独立评审，**先单独 commit**，旧结果原封不动。
2. 真正实现有后果的重复测量、QC信息与预算，删除或实现其他无作用动作，独立 OS/文件权限可信评分，真正候选加载路径 canary。绝不能自制奖励“迁移策略好”。
3. 服务端定价、唯一合法 gene IDs、空报告中立、公平随机/批次调整；验证 M1/M2 φ 数学一致性。
4. 断言式测试，同一决策状态下改变合法 QC 观察，下一动作实际不同；≥4DEV task×2参考规则，说明分数和成本的真实来源。没有源域策略训练。
5. 完整测试原始命令+退出码；结果 `results/result_round_005_r1.json` 用旧 schema **AC-01..06** 合规（DEV runs=[]），门报告另写。最终更新 status+push。
6. 若真实动作/可信隔离/评分任一硬门失败，直接 `NO_GO_D1_MVP` 停止，不允许无限维修、D2/D3、Phase1、模型/付费API。

请按 R5R1-01～06 汇报证据、SHA 和费用，由 Planner 复核。
