# P3-152 真实健康来源与 DeepSeek 受控自然对话：合成阶段交付

## 状态与结论

Partial — 合成工程阶段完成，待 PM 验收；真实阶段 Awaiting authorization。风险 L3。执行侧 A01–A09 全部有合成证据，不宣称 Independent Pass、真实闭环、风险关闭或产品冻结。

主责 Codex 工程/包内测试；独立评审依用户及 PM 指示暂停，无协审结论。复用151结束后的同一工程会话，新152根执行；未继承151的真实路径权限。任务合同、合成ABF和IPC授权摘要分别位于工程包 contract-inputs/task.md、synthetic-ABF-v1.md、design/phase-authorization.md。需 PM 决策：验收合成包，并取得此前提出的精确真实存储/凭据目标答复。

## 结果

自然问题经本地有限规则筛选只读合成健康观察、短期状态或确认记忆，Host校验授权/有效期/ref版本及最多3来源+2状态记忆/4096字节，生成包含实际问题和引用内容的披露预览。模型、接收方和完整请求可见，用户无需手工组装上下文。

确认只提交preview ID、revision和一次性token；Host保持不可变body、再次核对草稿/模型/凭据/来源/授权，再原子消费并进入ModelPort。重复和并发不会产生第二次请求；预览过期/篡改拒绝；失败保留草稿，手动重试重新披露和确认。发送中取消只停止等待，不声称远端数据撤回。启动遗留dispatching保守记为未知且不自动重发。

沿用AES-256-GCM加密envelope、AAD/revision、ModelPort及CredentialPort接口。合成KeyPort使用明确不安全的确定性测试材料，只用于虚构值；它不是实际Keychain保护。真实OS CredentialPort没有被调用。模型ID由本地输入/选项选择，不自动读取网络模型列表或测试连接；真实transport在合成模式前置拒绝。

健康来源只读Reader保留日期、UTC偏移、未知、估算和多来源不合并。发现并修正长历史边界：原先按最近128条全体记录寻找失效投影，可能遗漏较旧投影；现在定向读取有限健康投影，超限失败关闭。补测150条无关历史后的失效更新，未改原始表达或源库。

## 验证与证据

- Host最终36/36：evidence/host-tests-final.log。
- TS→真实Rust Host适配集成8/8：evidence/integration-tests-final.json。
- code mutation 3/3被检出：evidence/mutations.json与mutation-*.log；分别移除有效期、确认token及密钥回显守卫。修改仅发生于临时副本，最终候选未受mutation改写。
- 实际Tauri合成窗口：宽1280×949、窄700×762；设置、实际披露、确认回答、失败草稿、重试再披露、发送中取消、重启草稿及加密配置恢复均有GUI证据。界面与AX均限定新合成PID，未捕获真实窗口。
- 最终修正仅Host来源缓存及测试变化，原GUI的UI文件摘要未变，故复用相关呈现/流程证据；最终二进制另取新PID日期筛选检查，见evidence/gui-reuse-impact.json和gui-final-date-filter。
- 历史保全：151 Manifest 178文件+外部报告1复算通过；148/150直接代码输入的精确路径/hash在contract-inputs/code-inputs.json。后者为收口登记，不是启动前封存。
- 离线完整runner实跑通过（Host36/36、集成8/8及两项构建），见evidence/rerun-result.json。
- 完整逐行结论：design/acceptance-matrix.md。非自指FINAL_MANIFEST列出本包文件及本报告，校验脚本独立复算。README与tools/rerun.sh给出仅离线自动复跑入口；GUI和真实用户操作不进无人值守runner。

五类计数：合成阶段 P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0。整体任务 P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=1，唯一未实现项为尚未获精确目标授权的真实运行与用户发送闭环，不属于本次合成包的候选缺陷。

测试覆盖有限合同，不宣称完整历史回归、通用自然语言理解、真实Provider可用性或真实健康结论。API Key回显测试针对完整合成canary，不宣称能检测一切变换编码泄漏。

## 尚待真实授权

真实健康只读目标与逐次DeepSeek接收边界已有原则授权，本阶段仍未访问。新真实会话/配置/凭据目标未明确批准，因此runtime仍固定synthetic，不探测新旧真实根，不调用Keychain，不进行任何网络请求。

精确提案见design/real-target-proposal.md：建议新 /Users/xxe/Documents/LifeOS-Health-Conversation-Pilot-1 及明列会话DB、加密providerDB、marker/必要sidecars和本任务Keychain命名空间；旧配置复用是未获准的可选提案，未执行。PM此前倾向仅新配置，不能以该倾向代替用户答复。

授权和真实阶段验收补充齐备后，仍在本任务内接线；真实Key只由用户App输入，真实发送只由用户逐次点击。Agent不代点、不抓取真实正文/AX/截图/内容hash。未收到真实成功操作确认，不宣称真实闭环完成。

## 恢复、保留与交付

锁屏曾使GUI暂停，解锁后从该阶段恢复，未重做无关测试。checkpoint现指向await_real_target_authorization，已完成阶段和最终候选摘要可核对。

新合成根 /private/tmp/lifeos-p3-152-health-conversation-v1 保留，最终App保持打开；精确PID和二进制摘要见evidence/synthetic-launch.json（进程状态可随关闭而变化）。mutation和复跑副本保留，不清理旧根、真实资产或历史Evidence。

本交付无独立评审、PM账本更新、风险关闭、push/merge或后继任务启动。真实未授权属于待决事项，非用户需要重复批准已确定的健康只读/DeepSeek逐次发送边界。完整Task Contract未变，后续包内修正仍在本任务内处理。
