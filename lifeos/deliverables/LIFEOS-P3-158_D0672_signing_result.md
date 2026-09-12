# P3-158 D-0672 签名增量结果

2026-09-10。Codex 工程专项，同一 P3-158 任务。签名工程检查完成，待 PM 核对；整个 P3-158 仍 In Progress，非 Complete / Independent Pass。独立评审按用户例外暂停，真实接口与 C 的 v8 使用仍未开放。

## 合同与身份

执行依据为 5ed8 任务卡 `LIFEOS-P3-158_D0670_approved_addendum.md`、两份固定签名/v8方案及 Revision 1，另由 `LIFEOS-P3-158_D0671_certificate_location_readonly.md`、`LIFEOS-P3-158_D0672_login_identity_signing.md` 精确补充证书位置与使用许可。用户分别确认“允许”。原方案及位置偏差收据只读保留。

D-0671 仅查询公开证书，并在内存中做精确 CN 过滤，登录钥匙串匹配 1 张：

- 名称：LifeOS P3-158 Local Development Signing。
- SHA1：7490dc97208f45420c4dfc9c48ddf6f59113b6f4。
- SHA256：77aeaaa16f719d1394d36442fbb9732f9d6e5ea7903954d292cd445df372357d。
- 有效期：2026-09-10 09:38:52 UTC 至 2027-09-10 09:38:52 UTC；RSA 2048，SHA256withRSA，Code Signing / Digital Signature。

D-0672 允许系统 codesign 使用显式登录钥匙串与以上指纹。用户在系统界面完成“允许”。Agent 未读取或导出私钥、未迁移/删除/复制/重建身份，未查看 Provider 项/ACL，未改变信任或默认钥匙串/搜索列表。原专用钥匙串保留。成功签名证明系统能使用对应身份，不额外推断私钥物理位置、不可导出属性或 Provider 访问权限。

## 已验证结果

| 项目 | 结果与边界 |
|---|---|
| 当前候选 | 181 文件；两次构建 candidateFiles 完全相同，输入为 D-0667 完整 176 文件候选的增量 |
| 两次构建 | online-synthetic，均 cargo --locked --offline；第二次使用全新 online-rebuild target 目录，未联网构建 |
| 完整包 | 先签 helper，再签包含 Info.plist/资源封装的 App；固定主 identifier local.lifeos.p3-158.main-chain |
| 严格验签 | 两包主程序/helper 均 codesign --verify --strict 通过；另以 certificate leaf 精确指纹验证通过 |
| 稳定身份 | 两包主程序 DR 完全相同，helper DR 完全相同；主 DR 为 identifier 与 certificate root 指纹共同约束 |
| 字节差异 | 两次编译输入二进制 SHA256 不同，稳定签名不依赖二进制字节恒等 |
| 首包启动 | 直接启动 PID 14099，Host 返回 synthetic_conversation_started；按精确 App 路径读取标题与 tauri://localhost WebView，保存 AX/截图 |
| 正常重启 | CUA 正常退出 14099，确认 PID 已退出；同一签名二进制直接重启 PID 14156，首页与 WebView 恢复 |
| 重建包启动 | 正常退出 14156；重建包直接启动 PID 15208，首页与 WebView 恢复，保存 AX/截图 |
| GUI 绑定方法 | 直接启动返回 PID、精确可执行文件路径、固定启动状态与 CUA 精确 App 路径选择关联；CUA 不暴露原始 AX PID 属性，不能冒称其输出含原始 AX PID |
| 网络/凭据体验 | 新增模型请求 0；未加载 Provider Key，Provider 免提示体验 Unknown |

当前打开的重建包：`/private/tmp/lifeos-p3-158-main-chain-v1/build/signing-v1/D0672-rebuilt/LifeOS P3-158 Online Test.app`。旧 B 包文件没有覆盖；仅正常退出了本任务旧 B 实例以释放独占锁。P3-157 App/数据未接触。

## 保留并排除的中间结果

首次签名脚本缺少内联 requirements 所需的 `=`，在参数解析阶段失败。按本机 codesign 手册修正后，用新的独占 staging 重试。该失败不是私钥/信任结论。

第二次系统签名和严格验签均成功，但脚本最初错误期待 `Sealed Resources=`，未识别实际 `Sealed Resources version=2`。修正判定后，仅重新核验原已签包并保存收据，没有为此重复签名。原失败日志保留。

首次 GUI 选择超时，随后精确启动状态查明为 `store_busy`：旧 B 实例 PID 7017 持有独占锁。其窗口当时停在首页，没有发送预览。正常退出旧 B 后新包启动成功；前两次启动不计正 GUI Evidence。未删除或绕过锁文件。

## v8 离线状态与剩余工作

既有 17 步完整继承回归保留。最新受影响范围：23 项 v8 Rust、5 项实际 IPC（含首轮/第二轮预览重启）、19 项生产回执校验通过；8/8 编译有效的 mutation 被测试检出，原候选 hash 保持不变。补修内容包括当前状态恢复、撤权后的读取、条件最新版本、查询结果结构/来源/时间窗一致性、查询回执、取消晚到响应、前端成功回执及剩余模型活动预算传入实际 transport。

这些结果不等于 v8 全部合同门槛通过。仍需同任务内补齐：Host 活动阶段独立持久预留/崩溃计量边界（当前短 Host 片段主要在完成时结算）、其他尚未覆盖的合同审查项、v8 完整 App 离线业务 GUI Evidence、增量逐行矩阵与最终差异 Manifest，以及门槛通过后逐次用户确认的 B 开发/PM 未见样本。现阶段不恢复自动或无人确认的模型发送。

预算：旧 B 开发 14/24、未见 0/16、总 14/40；新协调开发/未见实际模型请求均 0。C/真实接口不动。无风险关闭、架构冻结、Stage 切换、主线合并或新任务。

## 可复核入口

- 签名证书元数据：`lifeos/engineering/LIFEOS-P3-158/signing/D0671-login-public-certificate.json`。
- 首包精确验签：`lifeos/engineering/LIFEOS-P3-158/evidence/D0672-signature-verified.json`。
- 两包 DR/证书比较：`lifeos/engineering/LIFEOS-P3-158/evidence/D0672-rebuild-signature-comparison.json`。
- 同包重启与重建包启动：`D0672-same-bundle-restart.json`、`D0672-rebuilt-launch.json`（同 evidence 目录）。
- 构建身份：`D0672-build-identity.json`、`D0672-rebuild-identity.json`（同 evidence 目录）。
- mutation：`evidence/D0670-mutations-9a17b0a8-109b-4516-95a6-6049235bc31c/results.json`，及 `candidate-preservation.json`。
- 默认离线复跑：`python3 lifeos/engineering/LIFEOS-P3-158/tools/run_v8_checks.py`；支持 --steps 与 --rust-filter，仅重跑受影响范围。
- 检查点：`lifeos/engineering/LIFEOS-P3-158/checkpoint.json`。需要 PM 核对签名增量；无需再次申请原范围工程修正授权。
