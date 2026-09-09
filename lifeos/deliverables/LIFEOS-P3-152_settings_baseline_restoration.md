# P3-152 模型设置基线恢复

状态：工程恢复、合成回归与打包完成；Paused — Resumable，待安全切换和用户真实操作。任务整体不Complete，独立复评继续暂停。主责Codex工程；PM负责合同与最终验收。沿用同任务Closure，不另建微任务。

## 授权与范围

用户已明确允许恢复“保存Key → 手动测试并读取模型列表 → 选择模型 → 显式启用”、固定掩码/有限尾号，取消自动启用，并允许用户本人手动固定DeepSeek /models；纠正早期152禁止test/models的冲突。其他Provider网络未恢复。Agent未操作真实Key、测试、选择、启用、发送、真实DB/Keychain/AX/截图或网络，未关闭当前真实App。完整DTO与兼容方案见 design/authorization-and-delta.md，PM已核对允许继续。

## 结果与baseline lineage

|产品基线|恢复行为与实现|
|---|---|
|14行 保存/测试/选择/显式启用分离|保存配置与Key不再隐式select；test_models成功只发布目录且未选/未启用；确认选择保持disabled；set_enabled独立动作。发送读取同一生命周期守卫。|
|38–39行 持久加密、非仅本会话|沿用已有provider.sqlite密文与Keychain端口，不增加TTL、不删除旧密文。合成Store关闭重开验证凭据解密可用及启用状态保留。|
|41行 固定掩码/有限尾号|只从maskedTail元数据渲染固定四点+4尾号，异常尾号只显示四点；不为展示解密，不显示完整值/前缀/长度。不新增明文显示计时器。|
|44行 Local不索取Key|Local界面无Key输入；Cloud/Local目录状态沿用隔离。未授权的其他Provider不测试。|
|48行 参数变化须重测|测试绑定profile/credential/catalog revision；模式、Provider、模型草稿、关键参数保存都会使旧测试禁用；错误endpoint拒绝。Key变更通过revision使旧目录失效。|
|49行 模型来自用户成功测试|恢复精确/models目录验证，拒绝手填/目录外ID、错误receipt、旧DTO及版本冲突。模型列表上限256项、单ID128字节、编码目录8192字节，不截断冒充完整。|
|50行 显式选择并启用|首次从测试目录选择可直接进入“待显式启用”；更换已选模型会禁用并要求重测，然后可以重新选择和启用，已验证用户可完成链路。|

产品基线和143/148旧实现维持历史只读；没有将早期笼统152合同当成用户同意产品降级。UI继续保留既有Cloud/Local目录项，本恢复只新增获准DeepSeek测试能力。

## 后端与兼容

14公开命令保持不变，version5在save_ai_provider_settings提供test_models/select_model/set_enabled的严格操作DTO。生命周期操作绑定四个expected revision；选择/启用另需testReceiptId。旧不带receipt的选择操作拒绝。保存凭据DTO及加密实现保持；底层旧自动enabled写法同时移除，public设置和实际发送均以新生命周期为唯一权威。

没有SQL Schema迁移。现有sources表私有保留ID _provider_lifecycle保存版本化测试/模型/启用状态，authorized=false，保留ID守卫即使伪造authorized=true也不准作为个人来源。旧手填目录/旧enabled记录只作为历史元数据保留，不转换为成功测试；无有效新绑定时读取与发送一律待重测/禁用，不在启动删除或改写凭据/个人数据。后续用户操作才写新生命周期。

测试在网络前先持久化outcome_unknown并禁用旧目录；请求ID重放/重启不重新调用。回执记录固定GET /models、版本绑定和固定状态，不包含Key或原始HTTP错误。真实transport使用原固定DeepSeek adapter、无个人body、无重定向/代理/fallback/后台发现/自动重试；返回模型有界、去重、格式检查并拒绝Key回显。chat/completions逐次披露流程保留；preview额外绑定settingsRevision，停用/重测/重启或状态变化不会复用旧确认。

已有15秒连接超时、60秒请求超时、120秒披露有效期均不代表Key寿命。

## 验证与限制

- Host 77/77：完整生命周期、旧状态失效、四版本CAS、目录外/错receipt/旧DTO拒绝、测试失败/未知与重复不重发、换模型重测闭环、真实端点注入拒绝、模式/Provider/高级参数变化、合成重启和旧凭据保留、私有metadata伪造不能进入来源/引用/模型body、请求不含Key/原始错误。
- UI单元25/25：8项本次设置测试+17项继承健康/来源测试。
- Host集成14/14、来源/健康/对话组合11/11；合计127项。继承测试的setup已改为显式测试/选择/启用，不再用自动启用作为通过标准。
- 8项隔离浏览器交互观察：使用候选原始UI与synthetic-driver本地桥，完成四步链、换模型重测、刷新后掩码和状态保留；默认1280×720和App最小宽度560×640的页面检查，document宽560，无横向溢出。只截取合成浏览器页面；这不是native Tauri AX证据，也不冒称真实Keychain/Provider验证。
- 1491项历史Manifest文件及所列外部报告校验保持一致；新候选新增1文件、修改14、删除0。变更清单、候选hash、完整日志在evidence。
- 真实binary只构建打包，没有启动。当前真实App未关闭或替换。无commit/push、未冻结产品/关闭风险/改变Stage。

本次无需重做未受影响的历史GUI；真实操作结果仍需用户在安全切换后验证。127项是同范围工程自检，不是Independent Pass、PM Pass或整产品Complete。

## 交付与切换

App：/private/tmp/lifeos-p3-152-health-conversation-v1/LifeOS P3-152 Model Settings Restored.app

Binary SHA256：3a0f72dfca5caa27c013b1ae91a7aa455c45910c282acaff82c69e48df0127c4。

候选、复跑tools/rerun.sh、校验tools/verify_package.py、FINAL_MANIFEST.json均在本增量目录。checkpoint resume_from=authorized_safe_switch_then_user_test_select_enable。

本轮PM明确要求暂不关闭当前版。待用户允许本次安全切换后，实时核对当前Credential Fix.app身份，正常退出、保留数据凭据草稿，不强杀/删锁；确认旧实例退出后只启动一次本恢复版，共享conversation.lock门禁不变。随后用户本人保存/测试/选择/显式启用，Agent只接受固定错误码或用户结果，不代操作真实凭据/网络。PM最终验收与独立复评仍待安排。

增量目录：/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-152/settings-baseline-restoration
