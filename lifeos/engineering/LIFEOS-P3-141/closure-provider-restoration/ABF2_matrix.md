# ABF-P3-141-v2 工程矩阵

本矩阵只说明本次 Provider Restoration Closure 的工程事实；它不恢复已撤回的旧 Phase-B Pass，也不构成独立评审、PM 验收或 Phase C 授权。

| ABF2 | 工程状态 | 可复核 Evidence | 结论 |
|---|---|---|---|
| M-001 | PASS | `evidence/source_semantic_diff.md`、`evidence/source_lineage.json`、候选 79 文件 tree | 从 P3-140 继承五类 profile 的语义：OpenAI、Anthropic、Ollama、LM Studio、Custom OpenAI-compatible。DeepSeek/Kimi 仍属于 Custom。 |
| M-002 | PASS | `evidence/source_semantic_diff.md`、`evidence/cargo_test.log`、`evidence/non_provider_regression.json` | 只有 `runtime.rs` 的 Adapter/profile mapping 与 `runtime-adapter.js` 的 Settings 标签发生 Provider delta；20 IPC 和非 Provider 50 项离线回归保持通过。 |
| M-003 | PASS | `evidence/provider_state_machine.json`、`evidence/cargo_test.log` | 显式 save→test→enable；首次 loopback send 后锁定 profile；切换被 `provider_locked_after_first_send` 拒绝；没有 fallback 或后台重发。 |
| M-004 | PASS | `evidence/provider_protocol_dynamic.json`、`evidence/cargo_test.log` | 这是本地合成 loopback 的真实 socket 协议测试，而非字符串扫描：五类 Adapter 正例以及 mode、顺序、错误 envelope、错误 response 的负例均通过。 |
| M-005 | PASS | `evidence/actual_tauri_provider_viewports.json`、三份 `*_native_ax.json`、三份 startup receipt、`evidence/screenshots/` | 每档均从本次直接 PID 找到唯一精确标题 AXWindow 与原生 AXWebArea；截图显示 P3-141 标题及恢复后的云端／本地兼容服务设置。实际可用区域使 desktop outer height 为 949，收据与同 PID AX 尺寸一致并诚实保留 requested 1280×1024。 |
| M-006 | PASS | `precontact_seal.json`、`evidence/prohibited_target_attestation.json`、`evidence/cleanup_receipt.json` | 测试输入、runtime、bundle、PID 收据和清理均只在指定临时根；无真实 Provider、网络、凭据、真实内容或受禁止目标操作。 |
| M-007 | PASS | `evidence/history_lineage.json`、`evidence/failure_history/` | 旧 Phase-B Pass 的撤回与之前错误尝试只读保留；本轮前台抓图、辅助程序编译和日志包装的失败也作为失败历史保留。 |
| M-008 | PENDING_SEPARATE_INDEPENDENT_REVIEW | `evidence/FINAL_MANIFEST.json`、本矩阵、工程报告 | 本工程包已固定为可独立复评输入；独立评审尚未启动，不能由工程会话自行给出 Pass。 |
| M-009 | PASS | `tools/cleanup_temp.sh`、`evidence/cleanup_receipt.json` | marker-gated 精确临时根清理已完成；receipt 明确记录 `REMOVED_EXACT_TASK_ROOT` 与 `root_exists_after=false`。 |

工程计数（本矩阵形成时）：P0=0，P1=0，P2=0，Unknown=0，Not Implemented=0。独立评审、PM 验收以及 Phase C/D/E 是后续治理状态，均非本 Closure 的已完成能力。
