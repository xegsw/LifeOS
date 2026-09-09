# P3-152 模型设置产品基线审计与集中修复 Delta

状态：审计完成；集中修复待 PM 纠正冲突合同后实施。不是设置功能 Pass、Independent Pass 或任务 Complete。当前真实修复版保持运行，未关闭、读取 AX/截图、真实 DB/Keychain、执行网络或真实设置动作。主责 Codex 工程审计；PM 负责合同及真实能力授权，独立评审继续暂停。

## 核心结论

用户确认的 D-0621 产品基线不允许把成功测试返回的模型选择退化成手填模型，不允许选择即启用，不允许取消固定掩码/有限尾号显示。当前152三项均存在回退。118项上一轮保存修复测试只证明局部实现行为及相应回归，不能证明完整设置产品基线通过；其中“无需测试的本地模型选择”本身沿用了冲突合同。本轮不以新增局部Pass覆盖问题。

## 原规则 → 当前行为 → 引入点 → 最小修复

|项目|原规则与既有实现|当前152行为|可确认引入点|最小修复|
|---|---|---|---|---|
|模型目录|产品基线45–48行；143 runtime.rs 1128–1153：用户测试成功发布目录，清空选择且不启用；148 provider_store.rs 490–543仍保留测试目录/receipt与选择分离|输入框+datalist，任意合法模型ID被加入models；public Host test操作拒绝|152初始candidate/application/health_ui.ts:13、provider_store.rs:470起已出现，早于本轮保存修复；design/ipc-delta-proposal.md写了不调用test/models|恢复手动“测试并读取模型”、仅测试目录下拉、显式确认选择；不接受手填ID冒充已测试目录|
|显式启用|基线14、48行；143选择设置enabled=false，另一步set_enabled；148选择也保持false|select_model有密文即enabled=true；replace_credential若存在modelId继续enabled；UI无显式启用动作，Host不暴露set_enabled|152初始provider_store已经自动启用；ui-restoration/controlled_conversation.ts:44、46又将保存配置/Key串接selectModel，本轮credential-save-fix保留了该接线|保存、测试、选择、启用四步分离；去掉保存后的自动select；Host发送前检查当前配置版本的成功测试+显式选择+显式启用；所有旧入口也必须严格守卫|
|Key显示|基线39行固定掩码+有限尾号；143 runtime.rs:669生成四点+后四位，ui/app.js:104展示credentialMask|后端仍返回maskedTail，UI只显示“API Key 已保存，不显示原文”，完全未显示固定掩码/尾号|152初始health_ui没有消费maskedTail，ui-restoration继续遗漏，本轮只修复存储状态真假而未恢复掩码|只用已有元数据渲染固定四点+最多4尾号；不读取明文、不为显示解密，不增加显示全文按钮；Local不出现Key输入|
|Key寿命|基线37–38行：SQLite加密、跨重启保留，无仅本会话选项|provider envelope仍持久化，read读取存储状态；未发现凭据TTL/自动过期删除逻辑|没有代码证据表明本地Key改成限时；不能把用户用词理解成已确认过期缺陷|保留持久化；在纯合成中补保存→关开App→掩码状态和解密可用的完整回归，不增加TTL；真实服务端Key有效性仍未知|

143交付报告55–74行还记录测试意外选择的实际整改：测试后选项必须为空，用户另点确认选择，再单独显式启用。它不是可省略的视觉文案。

## “限时”需要区分的现象

- 凭据寿命：当前本地代码未发现到期字段或定时删除；不能因此保证真实Provider密钥永远有效，未查询真实服务。
- 输入临时清空：旧152在保存前及重绘时清空输入是已定位缺陷。本轮修复仅在Host确认成功后清空对应输入，并保留同页重绘节点；离开页面不缓存输入。空输入框不代表已保存密文失效。
- 明文显示超时：143与当前UI均password输入，已保存值只应掩码显示；未找到“显示完整Key若干秒”的已确认能力，不新增明文revealer。
- 请求timeout：deepseek.rs:135–138是连接15秒/整次60秒，属于发送请求期限，不是Key寿命；设置advanced.timeoutSeconds目前只是偏好，实际发送固定60秒。
- 披露有效期：controlled.rs:39为preview创建后120000ms，过期须重新准备披露，同样不删除Key。

已向用户询问“限时”对应显示、输入消失、已保存Key失效还是请求超时，尚未收到答复，不自行猜定。

## 纯合成复现

运行 tools/reproduce.mjs 使用现有 synthetic-driver（先断言snapshot.mode=synthetic），只建立新driver fixture，不操作当前real App。6项断言确认：①后端尾号存在、UI遗漏；②模型手填且测试禁用；③任意未测试模型选择即启用；④更换Key无需重测仍保持启用；⑤公共测试操作返回operation_rejected；⑥新前端Flow能读取保存状态。第⑥仅前端重建，不冒充App/OS重启。输出只记录真假和固定错误码。未发测试/models网络，未读真实Key。

## 集中修复方案与需要 PM 决定的冲突

1. 产品规则继续以MODEL_SETTINGS_BASELINE_V1为准；PM需正式纠正152 ipc-delta-proposal的“不调用test/models”和real-stage R04/R06“仅chat/completions”，不能把笼统合同确认视为用户同意能力降级。当前审计未自行实现或触发/models。
2. 恢复已有Provider测试生命周期：测试结果绑定profile/credential/config revision及明确receipt，成功只发布目录并保持未选择/未启用；失败/取消/变更后旧目录不可作为可选来源；配置、Key、已启用模型或关键参数变更必须失效旧测试和启用态。首次从新测试目录确认选择与随后显式启用分离。重启不得自动测试、选择、启用或重发。
3. 后端优先复用148已有测试目录/receipt/选择分离代码，保留152真实根和凭据端口，不复用148真实根/凭据；现有两个Provider表是否足够经定向设计确认。公开IPC补测试及启用严格DTO，收紧旧select_model避免绕过；这属于合同差异，不仅加一个按钮。最小真实网络delta限定用户本人点击固定DeepSeek /models、不得带个人Context、不得后台调用/重定向/fallback/自动重试，收据不含Key/模型列表正文。待PM集中明确此授权。
4. 旧152手填模型列表不能迁移成已测试目录；拟在获准切换后由App将其保留为非可用历史/草稿并标待测试、禁用，凭据密文与对话保持。该非敏感状态兼容变更须纳入修复合同，当前审计不修改真实存储。
5. UI恢复掩码尾号、测试/选择/启用与明确状态提示，保留已修复的输入失败保留和固定码。保存主按钮可以保存用户填写的配置/凭据，但绝不顺带测试、选择或启用。
6. 同一增量一次覆盖：未测禁止选择/启用/发送；测试失败/未知/重复；旧receipt/Key变更/CAS；目录外ID；选择但未启用；显式启用；重启；掩码不泄漏完整值/前缀/长度；Cloud/Local切换；对话/来源/健康既有回归及合成actual-Tauri。独立复评与真实用户验证由PM安排，不再只交保存按钮局部Pass。

当前仅提案与审计，没有修改任何候选、历史包、真实App或数据，没有启动新/models授权。任务保持未Complete，后续安全切换需要另有已明确授权，不继承上一次关闭许可。
