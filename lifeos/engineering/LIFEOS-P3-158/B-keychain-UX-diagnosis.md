# P3-158 B 钥匙串重复提示：只读诊断与待批准方案

状态：Paused — Resumable；仅诊断，未实施缓存、签名、信任或 ACL 变更。不是 B Pass 或安全边界批准。

## 已证实

- 每个新确认请求在 `operations.rs::operation_consume` 中调用一次 `provider_store::credential`；随后才持久化许可消费并调用 ModelPort。重复请求由幂等记录恢复，不走第二次模型发送。
- `credential → decode → secure_credentials::decrypt → MacosCredentialPort::find_generic_password` 使用进程内 `security_framework` 原生 API；没有通过外部 `security` 进程读取密码。
- `reference_lineage` 只接受 `p3-152-key-` 加 32 位小写十六进制 account；映射固定 service `com.lifeos.p3-152.aead-key.v1`。未枚举实际 account、ACL 或钥匙串项内容。
- 每次解密重新加载 32 字节 AEAD 密钥，解密后清零；返回的 API Key 在请求计划中用 `Zeroizing` 管理。没有跨请求凭据缓存。因此加密凭据持久保存不等于系统允许后续访问免提示。
- 当前 bundle 是 linker-signed ad-hoc 签名：TeamIdentifier 未设置、Info.plist 未绑定、没有资源封装；designated requirement 直接绑定 cdhash。当前与两个留存构建的 cdhash 不同。相同显示名称和路径并不能提供跨构建稳定的签名身份。
- 最新条件表达请求已经 `succeeded / none / businessChanged=false`；没有持久 dispatching 预览。预算开发 14/24、未见 0/16、总 14/40。诊断未生成新预览或网络请求。

## 假设与未确认

每次重新查询，加上临时签名身份变化，与反复要求系统授权一致；重建尤其可能使先前基于代码身份的信任不再匹配。但没有读取 ACL，无法判断当前项是否要求逐次确认、是否存在一次性允许，或稳定签名后是否仍会提示。不能据此声称钥匙串损坏，也不能要求用户用“始终允许”掩盖问题。

当前请求已完成，不能把用户先前截图当作此刻仍有在途密码等待的证据；本轮没有抓取弹窗或屏幕。

## 最小修复顺序（需 PM/用户明确安全差异，尚未执行）

1. **先解决构建身份**：冻结唯一 bundle identifier 和完整打包流程，使用经用户明确指定、可持续使用的合法签名身份签署完整 bundle。仅固定 ad-hoc identifier 不能证明信任稳定。不得自行枚举签名私钥、修改钥匙串 ACL 或扩大信任；无获准签名身份时暂停该路线。测试“同一签名身份的重启及同范围重建”，而不是再让用户重复输入密码。稳定签名可能减少因重建造成的提示，不保证改变项本身的逐次交互策略。
2. **补等待后的失败关闭验证**：当前 `operation_valid` 在可能阻塞的凭据查询前执行；查询返回后至 ModelPort 前没有再次调用它。应在用户等待结束后、许可落盘及网络开始前重新核对预览 TTL、配置/凭据修订、启用状态、目标及授权。保持原五分钟发送 TTL；过期或撤凭据零新增发送。此项是代码风险点，不代表已观测到越界发送。
3. **仅在稳定身份仍不足、且获单独批准时考虑解锁租约**：建议范围限 B、单一既有 profile/account、单进程不可序列化的 AEAD 密钥，不缓存第二份 API Key；首次用户主动解锁后绝对上限 15 分钟、闲置上限 5 分钟，以较早者结束；系统锁屏/会话失活/暂停/退出/切换 profile/修订改变/撤凭据立即清零。每次发送仍先重新只读核对凭据存在、修订、启用及预览授权，不能仅凭缓存发送。拒绝/取消不填缓存。退出重启不恢复租约，不设置绕过系统交互的 ACL。

租约是新增内存密钥生命周期，不属于当前诊断授权。跨进程撤凭据还需要可证明的发送前失效屏障及竞态测试；若不能保证撤销后阻断新发送，不采用缓存路线。不得承诺尚未实现的跨进程即时清零；已发出的网络请求本来就不能保证撤回。

## 验证与保全要求

先做纯合成 CredentialPort 的查询次数、租约过期/锁屏/拒绝/撤销/竞态、等待期间预览过期测试；真实验证仍限获准身份且由用户完成系统交互。不得采集密码弹窗、Key、ACL 或原始传输日志。旧英文回执、失败及调用计数只读保留。当前不要求用户再次输入密码或批准新发送，旧 P3-157 App 和 C 数据不操作。

证据：`evidence/B-keychain-diagnosis.json`、`evidence/B-signing-identity-metadata.json`、`evidence/B-keychain-pause-state.json`。PM 需裁定稳定签名条件、等待后复核的实施范围，以及是否确有必要另行批准解锁租约；工程侧不自行选择安全权限方案。
