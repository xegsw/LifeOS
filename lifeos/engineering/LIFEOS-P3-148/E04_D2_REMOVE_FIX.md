# IR-D2-002 移除控制同包修复

2026-09-08；Codex工程。修复/定向验证完成，等待独立复核，不是独立Pass或PM Pass。读取的评审REPORT精确路径/hash见evidence/E04-D2-remove-lineage.json；IR-D2-001已由该评审36/36关闭，原GUI/几何/底层有效结果继承。

根因：UI从公开preview取得内部turnId，但preview_public有意删除此字段。旧正常点击静默无操作，仍可确认旧包。

修复：Flow在准备成功时保存调用者已经确定的turn及累计排除列表，与当前preview绑定；UI的移除入口只调用flow.remove(id)。移除立即清空旧确认和上下文，等待旧包取消后，用受控turn及累计排除列表重组。移除ID须属于当前来源片段。取消失败、重组失败、缺失/错误上下文均显示错误并保持无可确认包；重组中编辑会拒绝晚到包。发送/取消/失效同时清理内部上下文。后端公开DTO及权限判断零改动。

相对494包仅4/87候选文件变化：application/conversation_flow.ts、source_ui.ts及对应两个ui生成JS；其他83项（含全部Rust、CSS、Provider设置）不变。

回归：tools/test_e04_remove.mjs新增6项：不含turnId的真实公开形状、直接prepare/已保存turn路径、累计排除、取消/重组失败、无效segment/上下文、编辑竞态；加5项草稿重试与9项原flow，共20/20通过。日志evidence/E04-D2-remove-tests.log。离线locked构建通过，未重跑无关底层测试。

实际GUI：新binary直启PID84329，精确标题LifeOS P3-148 - Synthetic Offline、AXWindow→WebArea、700×760窗口取证。正常输入合成问题→发送准备→展开→点击第一段“本次移除”。before/after packets证明旧ready→cancelled、新previewId/确认token、指定segment被排除；笔记3→2、纠正1保留。新body不含被移除片段文字。derivations保持13，没有本次模型发送。截图app-e04removebefore1/after1及E04-remove-packets-before/after.json、E04-remove-body-check.json。图片已查看，App已停止。此轮仅验证移除，整体布局/键盘几何继承未修改UI部分的已有效评审。

原494项、报告及Manifest在history/pre-E04-D2-remove-package.zip逐项保全。新候选SHA256：030445c127678fc8197d89154dcda583245ed64b16de97916c184f4cf625e114；binary：9fcbd3acbfba8bcf3016c09e16e801ed0714e07e894d85182ca1b5c7b3064d0b。谱系含最小差异before/after。新的FINAL_MANIFEST覆盖全部新旧产物。

未改评审包、未接触评审root或真实根/DB/正文/凭据/网络；没有视觉重设计、Provider配置变更、push/merge或PM账本修改。下一步请PM交独立定向验证IR-D2-002，保持当前新包只读。
