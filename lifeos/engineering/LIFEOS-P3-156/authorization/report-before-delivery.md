# P3-156 自然对话中的安排与进展闭环

2026-09-10，Partial / Paused — Resumable；Codex工程专项，L2，复用已结束155工程写入的会话。D-0659及任务卡授权合同内执行；关键协议差异待PM明确批准。不是工程完成、PM Pass或Independent Pass。独立评审依既有决定继续暂停。

## 已完成事实

核对任务指定155父FINAL_MANIFEST的315文件及real-switch增量14文件，所有文件和两份报告摘要匹配；166个candidate文件逐项核对、文件集合无遗漏，再原样复制到156/candidate。父Manifest SHA256为22954f3f3ab1bb5b5bd880ec742c7f1ebc26252ee35ba2a64988ab8df6cefb49，切换增量Manifest为614c003d44bd3f3e3a9ce9d11a4b0a1f98fa6ed4a616f76f2579df7d4ed43225。历史状态字样不替代155最终PM Review。

独占创建/private/tmp/lifeos-p3-156-next-action-v1，根与synthetic目录0700，精确.owner.json为0600。未创建数据库、未运行候选、未构建或启动App。复制源码仍含155路径，因此批准前不得直接执行继承runner。

能力映射确认可复用现有草稿、幂等事务、来源引用/授权检查、上下文与失败恢复；当前实际v4/v5没有Action稳定身份/版本/操作DTO。架构已有Action领域方向，不能据此冒称运行时已接线，也不把Apple导入命令Action误认作产品Action。

整理34个合成交互设计用例，涵盖创建/调整/完成/取消、唯一指代与歧义、引用/假设/否定/沉默、重复/迟到/失败/恢复、来源失效及模型切换。这些是待实现的预期合同，行为通过数为0，不能把用例数量当测试通过。可复跑tools/verify_baseline.py仅验证历史、owner及用例ID唯一性；evidence/preflight.json保存实际结果。

## 具体待批差异

工程根minimal-protocol-proposal.md给出完整有限差异：保留14公共命令及v4/v5，在同一库现有records/feedback/questions中增加明确版本kind，接线TS Action领域/Repository/Application及合成限定v6 prepare/commit/snapshot。不新增第二任务库，不执行外部行动，不自动长期化，不自动重开完成/取消事项，不迁移真实库。不把物理表未改当成语义协议未改。

提案已直接交PM。任务卡要求“新增关键实体、Schema/API/公共IPC/权限必须先明确差异并获批准”，故仅依赖该批准的实现暂停；未再次索取任务启动口令。当前未收到明确批准。若PM认为需要用户确认，由PM展示此具体差异收口。

## 交付与恢复

工程根：/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-156/。

- candidate/：166文件基线原样副本，未修改，未执行。
- baseline-snapshot.json：两份父Manifest身份和166文件摘要。
- capability-map.md：复用/缺口与影响面。
- minimal-protocol-proposal.md：待批接口与持久化语义。
- tests/interaction-corpus.json：34条设计用例。
- tools/verify_baseline.py、evidence/preflight.json：基线核验入口及结果。
- checkpoint.json：resume_from=protocol_approval，safe_to_resume=false；明确批准后先按差异定向更新合同摘要、再做task-local配置和实现。

工程身份/历史保全关卡已过；新增行为、完整回归、合成App源码绑定和受影响视觉尚未实施/验证。未发现候选P0/P1/P2缺陷，但这不是无缺陷验收；Action运行时尚未实现。真实App/DB/来源/ZIP/凭据/Provider/网络接触为0；不操作PM账本，不关闭风险，不冻结、不切Stage，不提交推送或自动合并，不启动后继。
