# P3-154 Closure-1：真实失败定位与固定诊断

**Partial / 等待固定阶段和错误码；业务故障尚未关闭，ABF-10未通过。** Codex单Agent，L3，同任务授权内增量。独立评审继续暂停。未读取用户截图、问题、DB或真实日志，也未重发网络。

## 已确认的事实

用户看到的两条固定文案只证明ControlledFlow进入failed，不能区分prepare还是confirm。原health_ui.errorText将多种未映射code统一显示“操作未完成，草稿已保留。”，failed统一给出“重新准备披露”。已通过原始候选代码复现六类code完全不可区分，见closure-1/evidence/reproduction.json。不能把该提示认定为网络失败。

新增实际合成旧库/真实策略检查：

- 合成旧健康库缺states表：Host返回store_operation_failed，读取前后文件不变，不执行迁移。
- 合成旧健康库存在journal：返回readonly_sidecar_required，来源字节不变，未生成回答。
- 生产本地提交策略配合合成旧152 owner/旧question ID：回答、幂等及重启通过；已回答旧问题保持原basisTurn。
- 同一真实策略拒绝任意离线模型回答，返回real_answer_requires_model_port，保留草稿。

这些是不同底层分支的合成反例，不是用户实际根因证明。缺少真实固定code时无法诚实在这些分支中选一个。

## 最小修正

状态栏显示固定“阶段＋错误码”，覆盖草稿、上下文、澄清提交、披露和确认发送。仅白名单常量可见；原始error.message、HTTP正文、未知code和任意stage不展示、不记录。澄清/重试/网络/凭据/存储权限和失败关闭行为不变；没有调整设置、布局或CSS。

私有commit_with_policy从原commit提取，生产入口仍只传编译模式，IPC/Schema未变，不添加生产路径或时钟覆盖。这样可在合成依赖下完整执行生产本地回复分支，避免只重复synthetic false路径。

## 验证

95项受影响检查通过：Host39、披露23、集成14、连续性8、时效6、固定诊断5。2个mutation（隐藏code、泄露raw error）被检出。完整真实版构建成功。未重复无关设置/来源/导入套件，继承依据为生产文件与样式未改变。

首次旧Schema测试预期database_unavailable，实际Host错误转换为store_operation_failed；该失败日志保留，修正预期后新日志通过。诊断mutation首次工具默认reporter不含TAP关键字导致检查脚本失败，改为显式TAP后真实断言失败得到确认；不把编译/工具失败当mutation通过。

原270项Manifest文件及原交付报告逐项保持只读。增量目录：`lifeos/engineering/LIFEOS-P3-154/closure-1/`，含完整165文件candidate（新增诊断TS/JS两个文件，无删除）、分支矩阵、Evidence、checkpoint及Manifest。

## 诊断版切换与当前关卡

App：`/private/tmp/lifeos-p3-154-real-continuity-v1/LifeOS P3-154 C1 Diagnostic.app`。

Binary SHA256：`b11d86af5510470a211283247e6b20b0a69412a538133a73ea888c37ea732c7d`。

已按原合同核对旧154身份并正常退出PID66104，保留旧bundle；C1单次启动PID66855，固定controlled_conversation_started并激活。未重置凭据、迁移/清理/导入、抓取真实内容或代点发送。

已请用户只重新准备保留草稿，暂不确认发送：失败只反馈阶段＋code；若进入披露页只反馈“已到披露页”。该动作不要求网络重放。真正业务根因与修复仍待该固定信息，不能把本诊断增量称为用户问题已修好。

当前执行侧待核对计数：P0=0 / P1=1（真实用户闭环失败尚未关闭）/ P2=0 / Unknown=1（实际底层分支）/ Not Implemented=0。独立评审暂停单列；最终计数由PM裁定。无需新增权限或Key，需PM继续保持ABF-10未通过。

复跑：从b3f6执行`python3 lifeos/engineering/LIFEOS-P3-154/closure-1/tools/rerun.py --affected`；校验`python3 lifeos/engineering/LIFEOS-P3-154/closure-1/tools/verify.py`。checkpoint.resume_from=fixed_stage_and_code。没有后台Agent继续读取或发送，真实App保留供用户操作。
