# SciTransfer — Executor handoff (Round 001-R1, active)

你现在是 SciTransfer Executor（Kimi / MiMo，实际执行的 Agent 名称如实记录），ChatGPT 作为 Planner 审查每一轮。

仓库：https://github.com/yujian777555/SciTransfer ，主分支 `main`。**已发布 001-R1 补救计划，不能跳到 Round 002。**

首先：`git pull --ff-only`、核对 HEAD 与 `status.json`，完整读取：
- `planner/reviews/review_001.md`（Planner 已审查的具体缺陷）
- `planner/latest_plan.md`（当轮正式工作与 R1-01~09 硬验收）
- `planner/PROJECT_CHARTER.md` / `planner/STATUS_PROTOCOL.md`
- `results/result_round_001.json`（旧结果保持只读）

**优先级：** P0 官方 evaluator 的 `--split verified`、正确按实例提取 JSONL、所有路径绝对化、score 缺失 fail-closed；然后非破坏式 ZIP 续传、WSL/Linux/Docker 与 OpenAI/Azure 合法凭证检查；先评分六份已有程序，不要再次花 API 费用生成新程序。

重要：官方 harness 默认 `validation`，输出日志是整数据集逐行结果，且入口无条件检查 OpenAI/Azure 凭证；仅选非视觉任务不代表一定能无凭证启动。原生 Windows import `resource` 会失败。当前 `scripts/start_download.ps1` 会删除部分 ZIP，暂停使用，先修复。用户的 `Access denied ... outside allowed directories` 要在授权范围内移动/重建工作目录，不得绕过。 `ChildProcess.kill` 不等于确认下载仍在后台。

006 个原始 agent 生成记录和 `results/round_001_runs/` 不得改写。不要补写/回填 “preregistered” 时间。新结果 `results/round_001_r1_runs/`，验收 `results/result_round_001_r1.json` 和明确 R1-01～09。

至少拿到三领域每个一对 **官方真实 A/B 评分** 才有可能通过 R1；否则报告 PARTIAL/BLOCKED 及证据，不允许伪造结果或自我验收。记录所有测试的真实 pass/fail/skip、具体阻塞命令和文件下载状态。最后 commit + push，告诉 Planner commit SHA 和结果路径。

严格遵循最新正式计划，不自行扩大研究范围或跳到训练阶段。
