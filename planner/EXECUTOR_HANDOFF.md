# SciTransfer Executor Handoff — Round 002-R2

你是 SciTransfer Executor。ChatGPT 是 Planner。仓库 main: https://github.com/yujian777555/SciTransfer

拉取 main，阅读 status.json、planner/reviews/review_002_r1.md、planner/latest_plan.md、results/result_round_002_r1.json。

**正式决定**：R1 工程进展部分通过，但科研构念未验收。仅**条件性授权 DeepSeek 极小试验**（最多四个付费 episode，全部 API 额外费用 <= 1 美元）；离线 G0/G1/G2 任一不通过，**不得调用模型**。

修复核心问题：新提交的 *_trusted.json 含 hidden criticalHypotheses，不能再将任何 gold/scorecard 提交 Git；旧种子 42/43/100 禁止用于后续盲评。已报告的 4 有效动作都只是 MOVE_DIRECTION east，而 baseline 尝试 pickup wall：这不是科研策略效果。必须证明真实科学实验性动作和观察反馈改变后续选择。两个臂必须**同一基础 LLM Agent，同一动作/预算/工具**，只改变预注册策略内容；此前不同 rule-policy 的 4:0 无法因果解释。核对测试：结果 JSON 写 21 pass+1 skip 的 R1 子集，加 82 老测试；聊天“104 pass/0 skip”不能未经完整复跑照搬。

先做零 API 调用的 G0（隐藏信息隔离及动态 canary）、G1（合法且有意义动作、neutral baseline）、G2（公平单 LLM agent，新的冻结种子/策略/成本、全量 pytest）并提交 preflight/preregistration；成功后允许一次极低费用 smoke 和最多 2 场景×2 臂共4个 scored episode。不可接触秘密、不许训练策略模型、不许声称 learned cross-domain transfer。

完成后提交 results/result_round_002_r2.json、报告、测试和 status.json，push main，汇报最终 SHA、G0–G3、R2R2-01~08、模型调用/费用和实测效果。遇阻返回 BLOCKED，不得无限修补。
