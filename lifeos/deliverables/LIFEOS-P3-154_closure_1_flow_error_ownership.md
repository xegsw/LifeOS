# P3-154 Closure-1：错误归属与本地恢复

状态：Partial / Closure Cycle，等待 PM 复核及用户真实结果。主责 Codex 工程；风险 L3。独立评审按原指示暂停，未宣称 Independent Pass。ABF-10 未通过，不能把合成通过解释为用户此次请求成功。

## 事实与根因

在 confirmation-stage 的完整候选副本上先运行 7 个合成回归，7/7 失败。修正后原 7 项及实际状态渲染检查共 8/8 通过。未读取用户截图、AX、真实 DB、日志或正文，也未联网重发。

| 可复现缺陷 | 代码根因及本轮修正 |
|---|---|
| 恢复先失败后成功仍保留旧错误 | start 成功分支未清 error；成功恢复清除旧错误和提示 |
| 草稿保存失败迟到至成功 prepare | 排队保存 catch 无归属；按序号、turnId 和忙碌阶段约束，成功准备清错 |
| 旧草稿错误挂到新输入 | persist 缺少代际检查；仅更新仍对应的草稿 |
| 回答已保存，刷新失败却允许重新准备 | confirm 的保存与 reload 共用失败分支；拆出 refresh-failed，恢复按钮只调用本地 read |
| 新 prepare 的错误与旧回答混淆 | error 未携带轮次；内部绑定 turnId/draftRevision，当前输入错误明确标识，历史回答不改 |
| 取消的迟到完成结果清空新草稿 | cancel 的 await 后缺少代际检查；过期取消结果不改变新输入 |
| 旧 snapshot 失败覆盖较新恢复 | reload 无请求序号；忽略已被取代的读取结果和错误 |

另修正安全错误码传递：只接受候选中固定的码，支持结构化对象、固定码字符串及最多 2048 字符的 JSON envelope；不输出原 message/body、未知码或任意文本。未知 Host 码与无效 envelope 分别显示固定分类。首次回归发现设置 credential_revision_conflict 被过滤，该失败保留在 first-regression；已补齐累积候选的固定码清单并重新通过设置集成。

**推断边界：**以上证明候选存在可造成类似症状的缺陷，不能证明用户看到的回答属于本次轮次，不能证明其 operation_failed 的唯一底层原因。也不能从“模型没收到资料”推断来源读取损坏。来源选择、授权、领域判断、上下文预算、披露、真实策略及 Host Schema 未改。

## 验证与影响

受影响检查共 139 项通过：Rust Host 39、披露 28、UI 25、集成 14、连续性 8、澄清 UI 5、安全诊断 6、Flow 状态 8、时效 6。新恢复用例核对保存成功后恢复失败及再次恢复全过程，prepare=1、confirm=1，不会因恢复增加发送。4 个 mutation 被检测：旧草稿错误守卫移除、保存后刷新误导重新准备、隐藏固定码、泄漏原错误。前两项另有可复跑入口。Rust 真实策略解析、旧 Schema/密文与确认消费测试本轮再跑通过。

仅修改应用层状态、固定诊断、既有状态区按钮和对应测试/工具；CSS、布局、Host、Provider、来源和授权逻辑不变。按 D-0649 使用实际编译状态渲染函数和行为检查，不新增真实截图/AX，不把静态测试声明成桌面视觉证据。继承 confirmation-stage、初始 Closure-1、原 P3-154 的只读 Manifest 和报告；最终 verifier 逐文件复核。

完整真实模式离线构建通过。已正常退出精确身份的旧 PID 67268，保留旧 bundle，启动新完整 App：`/private/tmp/lifeos-p3-154-real-continuity-v1/LifeOS P3-154 C1 Flow Recovery.app`。新 PID 67899、固定启动状态 controlled_conversation_started，激活请求成功。binary SHA-256：`d40a514e4855a30d17a876dc86a4fd7494598e6005a9757c18e03d770de865cd`。这些是生命周期元数据，不能证明界面内容或业务结果。

## 交付与复跑

工程增量：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-154/closure-1/flow-stage/`。

- `evidence/flow-before.log`：修正前 7 项失败；`evidence/affected/`：最终影响回归；`evidence/first-regression/`：首次回归失败保留。
- `evidence/fixed-error-code-inventory.json`：仅源码固定字面量清单，不含运行期内容。
- `evidence/flow-mutations.json`、`diagnostic-mutations.json`：4 个 mutation；`flow-mutations-replay.json`：Flow mutation 独立复跑。
- `FINAL_MANIFEST.json`、`parent-snapshot.json`、`checkpoint.json`：增量与历史保全。

只读验包：`python3 /Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-154/closure-1/flow-stage/tools/verify.py`。

离线复跑：`python3 /Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-154/closure-1/flow-stage/tools/rerun.py --affected`。在既有 task-owned synthetic 根创建新副本，不修改候选或历史 Evidence。Flow mutation 可执行同目录 `flow_mutations.py`。切换脚本为一次性入口，不作为测试复跑命令。

## 角色、计数与未决结果

工程侧已复现缺陷完成同范围修正；主责 Codex，PM 负责验收。此次专项不自行关闭风险、冻结、推进阶段或提交合并；不启动独立评审。P0=0，P1=1（真实业务结果仍未通过），P2=0，Unknown=1（实际错误唯一归因），Not Implemented=0；该计数不抵消 ABF-10 未通过。

当前不要求用户重复发送，不索取正文、回答或截图。请 PM 复核工程修正，并决定之后一次必要的真实验收；任何实际发送仍须用户逐次确认。checkpoint 的 resume_from 为 pm_review_and_fixed_noncontent_result。已完成阶段不因桌面解锁重复执行；未接触禁止边界。无新增范围或后继任务建议。
