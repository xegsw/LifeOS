# P3-155 Task ABF Locked v1 工程矩阵

| ABF | 正向与反例证据 | 当前状态 |
|---|---|---|
| 01 | baseline.json 165文件；166候选；invariants 14 IPC/Settings/Flow；208组合回归 | 工程通过 |
| 02 | update lifecycle 无变/metadata变/内容变/缺失/返回；fingerprint mutation；source_restoration 来源原件变化与引用失效 | 工程通过 |
| 03 | fixed_health_target_append_rollback_locks_and_schema；combined XML/ZIP/重复/损坏保留；status缺表拒绝；开始状态保存失败不显示running | 工程通过 |
| 04 | source_recovery 6项纯渲染/隔离/迟到，独立进程1项；数量来自现有事务与source job字段 | 行为通过；纯视觉属性待PM裁定 |
| 05 | source_process_recovery 独立PID/同ID重放/暂停重启/手动继续/清旧错误；生命周期旧worker；epoch mutation；154 Flow 8项保留 | 工程通过 |
| 06 | combined刷新/断开/暂停/取消后预览拒绝、身份mutation/send fence；时效6项；确认token/state-expiry mutation | 工程通过 |
| 07 | 14 IPC不变；设置/凭据核心文件字节保持；完整Rust+组合+设置保存/重启/旧根/密文反例 | 工程通过 |
| 08 | real+synthetic-driver编译拒绝；固定目标schema/锁/缺库/边界；Key泄漏/旧account/missing-root mutation；Agent真实访问0 | 工程通过；未执行真实阶段 |
| 09 | real-build-delivery.log、real-bundle.json、checkpoint；旧包保留 | 完整包已构建，实际切换未执行 |
| 10 | 必须用户最少刷新/重复ZIP/恢复/有效资料对话声明 | 待执行，不用合成替代 |

207与208之前的阶段复跑不累加；最终delivery-regression为208单次回归。13个有效mutation中8 Rust、2诊断、2 Flow、1来源错误隔离。独立评审暂停，不是Independent Pass。未运行托管CI，不写CI全绿。首次不完备夹具与对应mutation整轮排除；历史只读保全，不删除失败记录。
