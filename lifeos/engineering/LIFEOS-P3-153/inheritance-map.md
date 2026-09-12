# P3-153 累积继承映射

输入：P3-152 settings-baseline-restoration/candidate，163 文件逐项 SHA256 验证见 evidence/inherited-candidate.json。原件只读。

| 能力 | 现有接线 | 本轮处理 |
|---|---|---|
| Shell / 设置 | health_ui → settings_view / settings_actions → controlled_conversation → settings_lifecycle | 原有导航、布局、模型目录选择及四步生命周期保留；回归 25 UI 用例 |
| 来源 / 导入 / 健康查看 | sources_view / apple_import → host_gateway → source-engine / health_reader | 只隔离合成根，保留全部命令与来源版本校验 |
| 直接对话 / 必要追问 | ControlledFlow → HealthConversation → health_context → health_conversation_host | 补缺口判断、纠正、生命周期；禁止增加预总结请求 |
| 状态 / 记忆 / 原文 | records / states / memories / derivations | 复用现有 SQLite JSON 表；原文与候选、已确认记忆分离 |
| 披露确认 | controlled_conversation → model_port / provider_store | 保留预算、版本、撤权、确认绑定；只用合成端口 |
| 重启 | Store / SQLite / 文件锁 | 测试专用固定名称 fixture，独立进程顺序打开同一合成库 |

真实实现保留但 P3-153 build.rs 拒绝 controlled-real 构建。未启动、探测或关闭真实 App。
