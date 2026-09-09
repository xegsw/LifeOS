# P3-148 独立 Delta 1 / 同任务 Closure 验收依据

原ABF v1及S01不改；本增量固定修复后的输入和补测范围。用户既有完整任务与继续授权覆盖；不是新产品任务或真实能力批准。

只读候选包仍 `/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-148/`，FINAL_MANIFEST SHA256 `be74734597b67b7726062df3bd0d0b449ea99a6524572d2d6bbf79191ec1e9cb`，387项。候选聚合摘要 `e898107cc07883a81c6ac575ad29851d9771040ad497edba14911b847a7e86cd`。PM已运行只读verifier匹配，非独立结论。

原独立评审者继续（未参与工程），输出新子目录 `/Users/xxe/.codex/worktrees/5ed8/No.2/lifeos/reviews/LIFEOS-P3-148/independent-review/closure-1/`。原REPORT、MATRIX、runner、Manifest不修改；可只读复用自有runner并在新子目录修正GUI夹具，独立数据须新造。候选接触前先写Delta自有test_design/allowlist/seal，记录旧评审不是本轮预接触，禁止假称全新从未接触原版本。

唯一运行根仍 `/private/tmp/lifeos-p3-148-independent-review-v1`；前轮已记录精确清理，允许在确认absent后重新创建全新0700根及既有profile0600 marker。若存在不复用/覆盖/清理，交PM。此为同任务同字面根的新合成生命周期，不改候选profile、不用工程root/DB/PID/缓存二进制。使用independent-review从新根离线构建。

必须闭合四P1：001 cancel/stale/consumed prepare回放当前状态；002 feedbackIds跨重启与会话/turn隔离；003 epoch及全部来源绑定、响应持久化有效性；004本进程Transport接收线性化和协调器保护、晚撤权持久stale。自有普通有界合成测试，非真实竞态/网络攻击，S01排除继续有效。

同时补前轮评审自身U的fresh完整GUI提问→预览→确认→答案→重启链，NI-001至004的合同内有限断言；前轮P2晚checkpoint作为历史保留，本轮按阶段及时checkpoint。不要求无限组合或复制工程全部测试；未变化且可复核的原独立结果可明确列为继承，当前候选受影响路径需实际验证，不复用旧GUI冒充新二进制。

评审不得修候选或执行被平台拒绝的测试；发现候选P1及时报PM并可继续互不依赖的合规检查，发现污染/禁止接触立即停止。环境中断Paused — Resumable，不机械重开任务。真实数据/DB/Keychain/网络/旧工程运行根禁止，风险/Stage不变。终局新REPORT/MATRIX/Manifest标明原问题关闭依据及未关闭项，Pass仍仅独立合成范围。根清理遵循原marker/自有PID规则。
