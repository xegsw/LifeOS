# P3-133 Closure-2 独立复评：预注册测试设计

## 身份、范围与独立性

- 评审轮次：`re-review-1`；对象为 Closure-2 candidate，仅作独立复评，不修改候选或工程 Evidence。
- 设计时间：2026-08-27；本文件在读取候选源码、工程 runner、工程结构化结果、工程 Manifest 和首次失败 Review 前创建。
- 独立方法：本轮将自写验证脚本和结构化结果，不导入、调用、复制或修改工程侧 runner／测试；只把工程资产作为只读 hash 与历史保全对象。
- 允许动态环境：唯一新建的 `/private/tmp/lifeos-p3-133-independent-re-review-v1`，仅存放本轮构建目标、全新合成 SQLite DB、应用运行期文件和无正文的临时观测。
- 禁止对象：任何 Pilot、真实根、真实 DB、真实文本、网络、模型、外部进程、clear/export、未授权 IPC；测试中不得对它们进行 access、stat、hash 或 cleanup。

## 固定合成输入与隐私规则

- 每条正常 Capture 在运行时由长度和 Unicode code point 生成；不会在测试代码、日志、截图、JSON、hash 输入或 Manifest 中保存文本正文。
- 正例使用三条不同的、长度为 200 Unicode 字符的合成字符串；负例使用长度 201 的合成字符串；第四条使用另一条不超过 200 的合成字符串。
- 隐私验证使用只在进程内生成的 taint 值：验证最终证据目录、运行日志、截图 OCR/AX 摘要、JSON 字符串与 hash-input 清单均不含该值或其可识别派生标识；证据只保留布尔结果、长度、计数和错误码。
- 所有截图仅在输入框清空、页面不显示 Capture 正文时采集；若无法排除正文，立即停止该截图路径并判该行未通过。

## 预注册矩阵

| ID | 独立操作 | 预期 | 正证据 | 失败关闭／完整性检查 |
|---|---|---|---|---|
| RR-01 | 复算 Frozen task/ABF/固定输入和 Closure-2 Manifest | hash、普通文件类型、声明数量全部一致 | `fixed-inputs.json` | mismatch/链接/额外候选文件即停止，不启动 app |
| RR-02 | 对 candidate 与历史只读资产作前后 inventory/hash | 本轮外部资产零变化 | `history-before.json`、`history-after.json` | 任一变化即 Rework，不以清理抵消 |
| RR-03 | 静态检查 Capture UI 读取顺序 | textarea 读取发生在 busy/render 前，旧模式不存在 | `source-read-order.json` | 无法证明则不以后台 IPC 测试替代 |
| RR-04 | 全新合成根启动 actual Tauri 并核验 app/PID/window/11 IPC | 真正运行的 bundle；恰好 11 IPC、无扩展能力 | `actual-app-identity.json`、`command-inventory.json` | 无可识别 actual app 或命令数不符即 Not Pass |
| RR-05 | 通过 Capture UI 依次提交三条长度 200 的合成值 | 三次均在 UI 成功，计数 3/3，DB 仅有三 Capture | `capture-success-noncontent.json` | 每次操作后刷新 AX；不得复用 rerender 后的元素索引 |
| RR-06 | 提交长度 201 值，分别在空库与三条已存状态运行 | 均在任何 DB/文件变化前拒绝 | `input-limit.json` | 前后 DB/hash、文件 inventory、哨兵一致 |
| RR-07 | 在三条已存状态提交第四条合法长度值 | 在任何 DB/文件变化前拒绝 | `fourth-record.json` | 前后 DB/hash、文件 inventory、哨兵一致 |
| RR-08 | 对相对、非规范、链接链、非目录、既有 DB、非普通 DB 做独立 mutation | 启动/写入前 fail closed | `root-db-mutations.json` | 原对象、哨兵、DB 与文件清单保持不变 |
| RR-09 | 在未显式确认前查询 Context/Today | 无 Action、无 Today Focus | `unconfirmed-state.json` | Capture 身份和计数不变 |
| RR-10 | 仅对一个 candidate 显式 accept；其余不接受 | 恰好产生一个 open Action 与一个 Today Focus | `confirmed-action.json`、`today-focus.json` | 不得由 Capture/Context 自动创建 Action |
| RR-11 | 刷新、关闭并重开 actual Tauri | 非内容计数、opaque identity、Context/Action/Focus 状态一致，无复制/sidecar | `restart.json` | 前后状态不一致或出现 sidecar 即 Not Pass |
| RR-12 | 在 real mode 调用 Understanding/Feedback UI/IPC 观察固定不可用态 | ModelPort/adapter 调用 0；Understanding=0；noticed=0；无 Feedback | `model-disabled.json` | 不得以合成 adapter 结果替代 |
| RR-13 | 对动态产物与评审输出进行 taint/内容/派生标识扫描 | 结果、截图、日志、JSON、Manifest 无正文或派生标识 | `privacy-taint.json` | 任一可能泄露立即停止并 Rework |
| RR-14 | 复查路径写入台账、文件类型、链接链和无网络/无外部进程面 | 写入只限本轮 review/temp 路径，无禁用面 | `boundary-inventory.json` | 发现合同外写入或访问即 Not Pass |
| RR-15 | 最终仅精确清理本轮临时根，复核 review assets 与历史 | temp root absent；review 证据在授权目录；历史仍不变 | `cleanup.json`、非自指 `FINAL_MANIFEST.json` | 不清理真实根；不使用 glob/find/宽前缀 |

## 判定与停止规则

- Pass 仅在 RR-01 至 RR-15 全部通过、P0/P1/Unknown/Not Implemented 均为 0 时成立。P2 仅可保留不影响唯一用户结果且有明确事实的项。
- actual-Tauri Capture 入口失败、真实输入可能出现在本轮 Evidence、任何合同外访问/写入、Frozen/hash 不一致、无法证明 UI 动态行为或清理不能精确执行，均 fail closed，不由静态或工程 Evidence 补足。
- 本轮结论不会冻结资产、关闭 R-0053、启动真实自用、进入 Stage 4 或替代 PM 最终核对。
