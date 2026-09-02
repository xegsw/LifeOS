# P3-144 Phase B 独立评审测试设计

## 身份、时序与冻结范围

- 评审角色：全新隔离独立评审；不参与候选工程实现，不修改候选、工程 Evidence、PM 账本、风险、冻结或 Stage。
- 冻结任务：`LIFEOS-P3-144`，冻结验收依据：`ABF-P3-144-v1`。
- 被评审候选 Git commit：`f6c03b083efe4525005887dd1dd4dad423ca6d10`。
- 评审阶段：仅 Phase B 合成／离线。不得进入 Phase C，不得连接真实 DeepSeek、使用真实凭据或读取真实内容。
- 本文件与同目录的 allowlist、禁止路径声明及 seal 已在接触候选、P3-144 工程 Evidence、交付物或任何 P3-144 Manifest 前自写并封存。

## 独立验证策略

1. 复算任务卡、ABF、Freeze Manifest、固定输入、候选 commit/blob 与工程 Manifest 的完整性；所有候选与历史资产只读。
2. 仅在 `/private/tmp/lifeos-p3-144-independent-review-v1` 创建全新 0700 合成运行根、SQLite DB、marker 与 review-owned 测试；不得调用、复制或执行候选测试／verifier 作为正证据。
3. 用 review-owned 测试覆盖 ABF-M-003 至 M-019：Work／非医疗 Health 语义、每类三条和 200 字符界限、空值／未知字段／错误类型写前拒绝、最小 Context、失效／撤销／跨域排除、预算、披露移除、每次重新确认、取消／未确认零发送、DeepSeek-only authority、凭据失败关闭、AI 派生身份、五种反馈、纠正失效与重启。
4. 对每项关键失败关闭执行全新可抛弃 mutation：过量／超长输入、旧确认重放、披露集合变更、非 DeepSeek provider、坏 authority／redirect、凭据缺失或篡改、医疗诊断语义、过期或已纠正条目。任一 mutation 未在写入／网络前失败即为 P0，停止正向验证。
5. 精确验证 20 IPC 注册项、Cloud 8／Local 4、防回退及无隐藏 send IPC；记录不含内容的计数、对象类型和稳定错误码。
6. 自行启动候选构建出的 offline actual-Tauri App，绑定 launch 直接返回的新 PID，再以 exact title 的 AXWindow、AXWebArea／AXWebView 和 target-only screenshot／几何分别取得默认、compact、narrow 三档 Evidence。候选工程截图或 verifier 不得替代此证据。
7. 用仅合成 canary 做泄漏守卫；不对真实 Pilot-7 正文、DB 或凭据执行任何扫描或读取。
8. 先停止所有 writer/PID，再以精确普通 marker 内容、类型和权限验证后清理唯一临时根；错误、缺失或 symlink marker 必须拒绝清理。生成非自指 Manifest 与独立 verifier，最后复核五类计数和历史未修改。

## 预期结论阈值

- `Pass` 仅在 ABF-I-01 至 I-15、ABF-M-001 至 M-024 均完成并通过，P0/P1/Unknown/Not Implemented 为 0，且 Phase A 工程 Gate 已被独立复算通过时成立。
- GUI／AX／截图能力暂不可用时写入 `checkpoint.json` 并报告 `Paused — Resumable`；不得以旧截图、bundle selector 或前台窗口替代 direct-PID 证据。
- 任何禁止路径接触、真实网络／凭据／内容接触、候选或历史写入、或 precontact 顺序破坏均为 `Irrecoverable Invalidation`；停止而不归因候选缺陷。

## 非结论边界

本评审即使通过，也只表示 Phase B 合成／离线独立关卡通过，供 PM 决定是否进入 Phase C；不构成 PM Pass、风险关闭、产品冻结、真实能力启用或 Stage 4 准入。
