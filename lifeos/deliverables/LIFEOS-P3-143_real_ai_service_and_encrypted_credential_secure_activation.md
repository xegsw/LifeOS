# LIFEOS-P3-143 工程进展交付物

## 结论

**Phase A 合成／离线工程 Gate：Pass；Phase B 用户操作的单一 DeepSeek Real Gate：Pass for Phase C handoff。** 任务整体尚未完成，当前已完成真实 Gate 与凭据删除，准备进入 **Phase C — 全新隔离独立评审**。Agent 未接触、读取、记录或传输 API Key、模型标识、prompt 或 response 正文。

本轮按 PM 定向校正复核了冻结合同：此前将 Desktop 强行要求为 1280×1024 是执行侧增加的条件，不是 AC-01／AC-06／AC-16 或 ABF-I-01 的冻结要求。P3-142 的正式 PM Pass 已接受“requested 1280×1024、实际 target-only Desktop 1036×768”的同类证据。P3-143 现有 Desktop 证据满足真正合同：直启 PID → 精确 AXWindow → AXWebArea、完整可读的目标窗口、正常 scroll-area 可达性与零凭据泄漏。

## 范围与边界

- 本轮 Closure 仅修改 P3-143 candidate 的 build-time root authority、离线测试与同任务 Evidence／Manifest／交付物；P3-142、首次独立评审与全部历史输入只读。
- 本轮 Closure 保持合成／离线；Phase B 的两次 `https://api.deepseek.com` 用户请求仅以既有非内容收据保全。未接触 Pilot、个人 DB／文本、Context、Memory、Health 或其他 Provider。
- 未作独立评审、PM 验收、风险关闭、产品冻结或 Stage 变更结论。

## Phase A 已完成事实

1. AES-256-GCM 凭据密文与独立 P3-143 Keychain 随机密钥材料的生命周期、篡改、替换、删除与失败关闭覆盖通过；SQLite 不含明文凭据。
2. DeepSeek adapter 仅允许精确 `https://api.deepseek.com`，并在真实模式具备 HTTPS、无 redirect、无代理继承、无后台／重试边界；UI 无直连网络 API。
3. Cloud 8、Local 4、Cloud/Local 分离及恰好 20 IPC 均保留。除 DeepSeek 外均未验证、未连接。
4. 离线检查通过：format、13 项串行 Rust 测试、18 项静态合同、marker wrong／symlink／traversal 负例矩阵。
5. Compact（PID 68596）与 Narrow（PID 68686）均取得精确窗口几何、AXWebArea 和可读 target-only 原生截图。
6. Desktop（PID 68490）取得 1280×949 logical AXWindow、AXWebArea 与 1036×768 可读 target-only 截图。依据 P3-142 的已通过先例和正式合同，该证据通过；276×322 缩略图已删除并仅保留排除记录。
7. 非自指 Phase A Final Manifest 已生成并复算：113 entries、0 errors；包含 candidate、acceptance freeze manifest、10 项 freeze 固定输入、P3-142 history 和本任务 Evidence。

## Phase B 用户手工操作步骤

PM 需在获授权的 Real-Gate 运行时打开 P3-143 App。随后只能由用户完成：

1. 在 App 的 DeepSeek 安全输入框手工输入 Key，并点击保存。
2. 用户点击“测试并读取模型”，从返回的模型中选择一个，再显式启用。
3. 用户发送唯一冻结的无个人含义 canary；响应仅在 App 内瞬时显示。
4. 用户点击删除凭据；后续验证只记录非内容元数据，并证明调用失败关闭与精确清理。

Agent 不得索取、观察、复制、记录或接收 Key，且不得代替用户点击上述真实动作。

## Evidence 与交付路径

- [Phase A 最终 Gate](/Users/xxe/.codex/worktrees/de3f/No.2/lifeos/engineering/LIFEOS-P3-143/evidence/phase_a_final_gate.json)
- [逐行 AC 矩阵](/Users/xxe/.codex/worktrees/de3f/No.2/lifeos/engineering/LIFEOS-P3-143/evidence/phase_a_ac_matrix.json)
- [Desktop 合同复核／治理校正](/Users/xxe/.codex/worktrees/de3f/No.2/lifeos/engineering/LIFEOS-P3-143/evidence/phase_a_desktop_visual_contract_review.json)
- [三档原生窗口 Evidence](/Users/xxe/.codex/worktrees/de3f/No.2/lifeos/engineering/LIFEOS-P3-143/evidence/native_window_evidence.json)
- [Phase A Final Manifest](/Users/xxe/.codex/worktrees/de3f/No.2/lifeos/engineering/LIFEOS-P3-143/FINAL_MANIFEST.json) 与 [verifier](/Users/xxe/.codex/worktrees/de3f/No.2/lifeos/engineering/LIFEOS-P3-143/evidence/manifest_verification.json)
- [checkpoint](/Users/xxe/.codex/worktrees/de3f/No.2/lifeos/engineering/LIFEOS-P3-143/evidence/checkpoint.json)

## 角色与关卡

- 主责：Codex 工程执行。
- L3 Phase A：Pass。
- Phase B 用户 Real Gate：Pass for Phase C handoff；App 已停止，临时根保留给独立评审。
- Phase C 独立评审、PM 验收、风险关闭、产品冻结与 Stage 4：均未开始。

## Phase B 状态机 Closure 更新

- 用户手工保存凭据后，只以非敏感结构核对确认密文记录和精确 P3-143 Keychain 服务存在；Agent 未读取 Key、reference 或安全输入框。
- 用户手工“测试并读取模型”产生唯一 non-content `GET` 收据：精确 `https://api.deepseek.com`、`2xx`、请求/响应均为 `1KiB_or_less`。未读取模型标识、响应或错误正文。
- 非敏感状态发现模型选择态已出现而服务未启用。PM 判定这违反测试／选择分离，已停止 App 且没有重试或重放该真实请求。
- 窄修正使测试强制清空 `selected_model` 与 `enabled`；UI 下拉只保存本地 `pendingModel`，用户必须另点“确认选择模型”才会写入选择。纯状态 mutation 单元测试、静态合同、format 与离线实际 Tauri 构建均通过。
- 当前仅清空了非敏感 `selectedModel`／`enabled`；密文、Keychain 项、已测试模型目录和唯一 GET 收据均保留。修正候选 digest 为 `a63af432…d81e6d`，当前 Manifest/verifier 为 119 entries／0 errors。
- 修正 App 已重开。下一步只能由用户本人选择一个已测试模型并点击“确认选择模型”；不得启用或发送 canary。

相关 Evidence：[Closure](/Users/xxe/.codex/worktrees/de3f/No.2/lifeos/engineering/LIFEOS-P3-143/evidence/phase_b_state_separation_closure.json)、[测试收据](/Users/xxe/.codex/worktrees/de3f/No.2/lifeos/engineering/LIFEOS-P3-143/evidence/phase_b_test_models_receipt.json)、[Phase B checkpoint](/Users/xxe/.codex/worktrees/de3f/No.2/lifeos/engineering/LIFEOS-P3-143/evidence/phase_b_checkpoint.json)。

## Phase B 用户已确认模型选择

- 用户已在重开后的 App 内自行完成选择及“确认选择模型”；Agent 未读取模型标识、Key、安全输入框或任何响应内容。
- 只读非敏感检查通过：已选择、仍未启用，测试模型目录非空；唯一 non-content 网络收据仍是原先的 `test_models` GET，数量保持 1，未重放测试。
- Agent 未发起网络动作；本步不触发 fallback、其他 Provider 或 canary。App 继续前台运行，下一步只允许用户本人点击“显式启用所选模型”；尚不得发送 canary。

相关 Evidence：[模型选择收据](/Users/xxe/.codex/worktrees/de3f/No.2/lifeos/engineering/LIFEOS-P3-143/evidence/phase_b_model_selection_receipt.json)。

## Phase B 用户已显式启用服务

- 用户已自行点击“显式启用所选模型”；Agent 只核对已选择、已启用和测试目录非空，未读取模型标识、Key、安全输入框或正文。
- 唯一 non-content 网络收据数量仍为 1，仍是此前的 `test_models` GET；启用未产生 Agent 网络动作、测试重放、fallback、后台或其他 Provider 请求。
- App 保持运行。下一步仅允许用户本人发送冻结的无个人含义合成 canary，唯一可用 authority 为 `https://api.deepseek.com`。

相关 Evidence：[启用收据](/Users/xxe/.codex/worktrees/de3f/No.2/lifeos/engineering/LIFEOS-P3-143/evidence/phase_b_enablement_receipt.json)。

## Phase B 固定合成 canary 已完成

- non-content 网络序列恰好两次：此前 `test_models` GET 与本次 `send_fixed_canary` POST；两次均为精确 `https://api.deepseek.com`、`2xx`，请求／响应仅记录 `1KiB_or_less` bucket。
- 未读取、记录或输出 Key、prompt、模型标识、响应或错误正文；Agent 未代点、重发或重放 canary。未观察到 retry、redirect、proxy、fallback、后台或其他 Provider 收据。
- 用户报告钥匙串弹窗已消失。当前 Closure 后的 ad-hoc、无 Team ID 开发构建身份变更可触发 macOS 钥匙串再次授权提示；此为受控交互事实，不推断为凭据泄漏，也未读取弹窗内容。
- App 保持运行；下一步仅允许用户本人在 App 内删除凭据，之后再做失败关闭和精确清理核对。

相关 Evidence：[canary 收据](/Users/xxe/.codex/worktrees/de3f/No.2/lifeos/engineering/LIFEOS-P3-143/evidence/phase_b_canary_receipt.json)。

## Phase B 凭据删除与 fresh restart 失败关闭

- 用户已在 App 内删除凭据。只读非内容核对确认：`encrypted_credential` 行数为 0；credential reference、mask、selected model 均为空；服务禁用且模型目录清空。
- 仅查询精确 P3-143 Keychain service 后确认专用项不存在；未枚举或读取其他钥匙串项及任何秘密。
- 修正 App 已以 fresh direct PID 72791 重启并绑定精确 AXWindow → HTML WebView。界面显示尚未保存凭据，删除、测试与全局发送按钮均禁用。
- 删除与 fresh restart 后网络收据仍恰好为历史两条，未产生第三次请求；由此证明无凭据状态在网络前失败关闭。
- fresh App 已停止。Phase B 工程 Gate 已完成，下一步仅允许全新隔离、候选与工程 Evidence 只读的 Phase C 独立评审。
- 唯一临时根及其 marker、候选与非内容 Evidence 均保留给 Phase C；尚未执行 marker-gated 清理，避免丢失评审输入。
- 当前非自指 Final Manifest 已重建并复核：124 entries、0 errors。

**Phase B 工程结论：Pass for Phase C handoff。** 这不是独立评审、PM 验收、风险关闭、产品冻结或 Stage 变更结论。

相关 Evidence：[删除与 fresh restart 收据](/Users/xxe/.codex/worktrees/de3f/No.2/lifeos/engineering/LIFEOS-P3-143/evidence/phase_b_credential_delete_receipt.json)、[交叉核对](/Users/xxe/.codex/worktrees/de3f/No.2/lifeos/engineering/LIFEOS-P3-143/evidence/phase_b_deletion_and_fresh_restart_deny_receipt.json)。

## IR-P0-001 root authority Closure

- 首次独立评审的 `IR-P0-001` 已只读保全；本工程 Closure 仅修正候选的 root authority，不改动 Provider 目录、20 IPC、凭据／Keychain、网络语义或 Phase B 历史。
- `build.rs` 现在只编译两种 profile：精确工程根，或以严格 8–48 位安全 run-id 组合出的 `/private/tmp/lifeos-p3-143-independent-review-<run-id>`。运行时只读取编译进候选的 authority，并再次核对 root/runtime 0700、marker 0600 非 symlink 且内容精确、DB 为 root 直接子项。
- 离线验证通过：17 项串行 Rust 测试、20 项静态合同；两个不同合法 review run-id 独立构建成功；traversal／短 run-id／未知 profile／engineering profile 混入 review run-id 均在 build-time 拒绝。任意运行时路径环境变量未改变编译 authority。
- 全程只使用新的合成 review test root／DB；未访问或修改已保留工程 Phase-B 根、真实 Provider、凭据或网络。
- 候选现有 85 个文件，root authority Closure 后 digest 为 `06ffa277be1dd42c946d7f7372d8a7f66619784a78aef351ceedc8068b1951c1`；此前 `a63af432…d81e6d` 仅作为 Phase B 历史保留。

**工程 Closure 结论：Ready for 全新隔离 independent re-review。** 不得在本会话自行评审、重新真实调用或清理既有历史。

相关 Evidence：[root authority Closure](/Users/xxe/.codex/worktrees/de3f/No.2/lifeos/engineering/LIFEOS-P3-143/evidence/root_authority_closure.json)。
