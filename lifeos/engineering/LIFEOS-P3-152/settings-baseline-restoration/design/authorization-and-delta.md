# P3-152 集中设置恢复授权与DTO兼容方案

PM转达用户精确允许：恢复保存Key→手动测试并读取模型→选择模型→显式启用，固定掩码有限尾号、取消自动启用；只允许用户手动DeepSeek /models，无后台发现/重试/回退/重定向，无个人Context。纠正早期禁止test/models；chat/completions仍逐次披露。Agent不操作真实Key/测试/启用/发送，不读真实正文/AX，不关闭当前App。独立复评暂停。

实施：14公开命令不变，在save_ai_provider_settings version5恢复test_models及set_enabled，收紧select_model DTO。生命周期操作带requestId、expectedCredentialRevision、expectedProfileRevision、expectedCatalogRevision、expectedSettingsRevision；选择/启用另带testReceiptId以及modelId或enabled。全部拒绝未知字段、旧无receipt选择、过期版本。保存凭据DTO不变，不自动选择/启用。

不需要SQL Schema迁移。使用现有sources表新增私有保留ID _provider_lifecycle（authorized=false、非个人来源），保存版本化测试回执/目录/选择/启用元数据；requests表保留单次测试的pending/final结果。网络前持久化未知状态、禁用旧目录，崩溃或重复请求不自动重试。测试结果绑定现有profile/credential/catalog revision。未测、receipt不匹配、旧状态或配置改变时public设置与发送守卫均视为禁用/待重测；旧provider密文和旧手填元数据不删除、不迁移成成功测试。旧状态的安全失效由读取覆盖实现，不在启动执行删除/重写。新用户设置动作才持久化新生命周期记录。

catalog modelLabel允许空以支持先保存再测试，所选可调用模型只来自新生命周期测试目录；catalog中的旧手填label不作调用权威。任何catalog版本变化使测试失效（包含mode/provider/endpoint/模型草稿/高级参数），相同配置重存也安全要求重测。首次测试后选择保持disabled；已选模型切换先要求重新测试。Key更新通过revision自动失效。无Key TTL，无明文显示器。

真实transport沿已有固定DeepSeek adapter恢复精确GET /models、body=None；模型目录有界/去重/标识符格式验证与Key回显拒绝。合成只使用固定虚构目录。测试不带个人Context，仅请求授权头。后续真实切换另外安排，不继承上次关闭许可。
