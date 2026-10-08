# SciTransfer — Executor handoff (Round 001-R2)

你是 Executor，ChatGPT 是 Planner。仓库 https://github.com/yujian777555/SciTransfer ，分支 main。

1. 拉取最新 main，检查 HEAD、git status、status.json。
2. 阅读 planner/reviews/review_001_r1.md 与 planner/latest_plan.md；当前是 Round 001-R2，不是 Round 002。
3. 只修复 ZIP 下载安全性与真实官方评分链路，不生成新代码，不训练模型，不扩展研究范围。
4. ZIP 下载必须单进程、HTTP Range 精确校验、不可覆盖有效 partial；有 ChildProcess.kill 时检查真实 PID/字节数而不是认为后台已经启动。
5. 如工具不允许访问 XiaomiMiMoProjects 目录，请使用授权工作目录或征询授权，禁止绕过。
6. 优先 WSL2/Linux + Docker + verified split + pinned dataset 完整序列一致性；原生 Windows shim 不能冒充官方原版验证。
7. OpenAI/Azure 凭证必须属实，不能用 DashScope key 假装 OpenAI key。需要时告知用户在本地配置，勿把密钥发送至聊天/仓库。
8. 校验旧六份程序 SHA256 后先评分 Task85 A，成功后继续其余五份；写入 R2 新结果，不修改历史 001/R1 文件。
9. 执行单元+集成测试，记录原始日志，完整上报 R2-01..08。
10. 不能完成则报告 BLOCKED 与明确的用户操作，不反复试错或伪造评分。最后 commit+push 并交 Planner 审查，不得自行 ACCEPTED。
