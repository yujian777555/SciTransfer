# SciTransfer — Executor Handoff: Round 001-R3

你的角色是 SciTransfer Executor（Kimi/MiMo），ChatGPT 是 Planner。唯一事实来源是 https://github.com/yujian777555/SciTransfer 的 main 分支。

## 立刻操作

1. git pull --ff-only；读取 status.json、planner/reviews/review_001_r2.md、planner/latest_plan.md 和 results/result_round_001_r2.json。
2. Round 001-R2 **未通过 Planner 验收**：虽然 ZIP 已报告完成下载且 55 项测试报告通过，但 scripts/r2_evaluate_all.py 的评分器为手写版本，A/B 共用 pred_results，哈希不匹配也继续执行，失败仍可能读旧文件。R2 的四个 0 分不能直接用于科研结论。
3. 严格执行 **Round 001-R3**。只允许重新执行已有六份程序；不重新生成程序、不调用 LLM、不训练模型、不改变研究题目。
4. 第一优先级是从本地受限 benchmark_verified.zip 中确认三个 Task 的真实官方评分脚本与 SHA；直接调用原始函数，不能用重新实现冒充。受限 gold/原始数据不能推到 GitHub。
5. 第二优先级是创建六个严格独立的 A/B 工作目录，使用完整 SHA256 硬校验，禁止读取 REPO_ROOT/pred_results 旧结果；程序退出码非零/超时就返回 null 分，保存详细证据。
6. 第三优先级是先 Task85 A 最小 smoke，再完整评估 6 个原始程序。Task21 的超时可以进行一次有上限的诊断，不能改写程序或无限重试。
7. 官方原版 Docker 若因网络失败，按计划有限尝试、记录日志即可；使用原始官方 scorer 的本地修改版 runner 必须标记为 DIRECT_ORIGINAL_SCORER_MODIFIED_RUNNER，绝不写 official_evaluation=true。
8. 运行已有 55 项测试及新增的 scorer 一致性/隔离/哈希/超时集成测试。
9. 写 results/result_round_001_r3.json、results/round_001_r3_runs/、status.json，提交并 push main。最后回报 SHA、六臂结果、实际测试总数、R3-01～08 的每项状态及阻碍。

**不得自行接受 Phase 0 或进入 Round 002。** 如无法取得可靠评分，请返回 PARTIAL/BLOCKED 和最小可操作的解阻步骤，而不是制造 0 分或伪造官方成绩。
