# P3-155 资料更新与日常恢复闭环

**工程实现和合成安全检查完成；Partial / Paused — Resumable，尚未真实切换，任务未Complete。** Codex单专项顺序复用；P3-154已结束且历史只读。风险L3，依据5ed8任务卡及Task ABF Locked v1、D-0656完整授权。独立评审按用户指示暂停，非Independent Pass。需要PM裁定剩余视觉Evidence及接续Gate。

## 本轮结果

完整继承154最终flow-stage的165文件，当前166文件，17项候选文件新增/修改，无删除。保留14 IPC、完整Shell/Settings、Provider选项、保存/测试/选择/启用分离、Key加密持久且无TTL，以及154最终错误归属和只读恢复。未重建刷新/导入/对话系统。

- 来源状态与健康导入状态独立读取、报错、重试；一个失败不短路另一条正常链。迟到状态/动作不覆盖新页面或解锁其他操作。
- 既有来源区域显示真实阶段、已发现/处理/待处理及本轮新增/变化/未变化/缺失数量。新增/变化计数随现有发布事务写入既有counters JSON，不新增表或输入DTO。总量未知不显示百分比。
- 未变identity继续复用；identity变化但fingerprint相同时保留版本与解析成果。缺失原件重新出现时正确恢复有效版本，不沿用missing状态。失败与历史内容保留。
- 进程退出后未完成来源显示待手动继续，不自动扫描；手动继续沿旧epoch/worker和检查点恢复。旧worker错误仅能写回所属epoch，继续时清除先前错误。
- 按155授权恢复原有健康固定ZIP入口；status表从CREATE改为existing-only校验，缺表拒绝、不迁移。开始状态保存失败会显示失败而非假运行中。重复、歧义、事务回滚与固定目标保护均沿已有算法；不泛称任意文件无损去重。

## 实际验证

最终单次回归 **208项通过**：Rust118、UI25、集成14、组合11、连续性8、澄清UI5、安全诊断6、154 Flow8、来源状态/进程恢复7、时效6。日志位于工程根`evidence/delivery-regression/`。前序206/207等阶段不累加。

**13个有效mutation**：8 Rust（内容复用、旧worker错误归属、缺表迁移、确认token、时效、远端Key回显、缺库、旧account）、2诊断、2 Flow、1来源隔离。编译失败不算mutation检出；有效结果要求测试运行并出现失败。

新增旧worker测试最初缺少合成基础表，修正后通过；该首次失败及其所在mutation整轮排除，重新执行有效mutation。预修正来源隔离失败也保留。`evidence/exclusions.json`说明排除项，未删除失败记录。

真实与synthetic-driver同时启用的构建被`real driver forbidden`拒绝。Agent真实正文/DB/Key/日志/AX/截图/内容hash收集为0，真实Provider调用为0。既有源文件写入仅发生于合成反例，不操作用户原件。未运行托管CI，不写CI全绿。

## 视觉Evidence与尚未执行阶段

本轮CSS、主导航、Settings表单未变；DOM仅在既有来源/健康区域增加状态段落、计数及重试按钮。实际编译渲染函数及交互测试覆盖条件显示、转义、固定错误码、忙碌/迟到状态、只读重试，但不能证明像素布局。

合成状态HTML已生成；Browser工具明确拒绝file URL，并禁止替代浏览器或间接绕过。已停止该路径，截图0张，**未声称视觉Pass**。未验证窄窗换行、实际字形/行高、遮挡、滚动及按钮实际可达性。具体影响和现有覆盖见`design/impact-map.md`，由PM按D-0649裁定是否需要进一步已获准验证；不要求用户处理平台问题，不把此问题泛称候选功能失败。

完整真实模式App已离线构建并打包，但**未启动/切换**：
`/private/tmp/lifeos-p3-155-source-update-v1/LifeOS P3-155 Source Update.app`。
Binary SHA-256：`8716005747edc7d0fb21df7a816c0cf10684fb110b9b48e9fad29b984a1eb14c`。
旧154 App及全部真实根保持原样。切换入口有检查点门禁，当前不允许执行；待PM确认工程Gate与视觉处置后继续合同内精确身份正常切换，不要求用户重复授权同一边界。

## 角色、关卡与计数

工程主责Codex，PM负责验收和账本；独立评审暂停。ABF-01/02/03/05/06/07/08工程检查通过；ABF-04行为通过、纯视觉待裁定；ABF-09实际切换未执行；ABF-10用户真实结果未执行。细表见`design/acceptance-matrix.md`。

当前执行侧P0=0、P1=0、P2=0、Unknown=2（纯视觉属性、用户实际结果）、Not Implemented=1（待门禁后执行的真实切换）。待Gate不等同产品能力缺陷，也不允许提前写全任务Pass。

PM当前所需决定：依据明确DOM影响面裁定视觉Evidence处置，随后允许从现有检查点接续工程Gate。之后仅需用户执行既定最少真实刷新、同ZIP重复导入、手动恢复/重启和有效资料对话；实际发送逐次确认，只反馈成功声明或固定码。当前无需用户操作，不索取正文截图。

## 交付与恢复

工程根：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-155/`。
包含完整candidate、existing-capability-map、impact-map、候选差异、固定输入、验收矩阵、baseline、Manifest、checkpoint、真实bundle身份及合成Evidence。

离线复跑：`python3 /Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-155/tools/rerun.py`。只在155独占合成根创建新副本，旧候选/Evidence不改。验包入口同目录`tools/verify.py`；Rust mutation入口`tools/mutations.py`。当前App切换工具不是测试复跑入口。

检查点：工程根`checkpoint.json`；resume_from=`pm_visual_disposition`。已完成构建、208回归、13mutation、历史保全不因视觉工具限制重做；从PM裁定后的最早受影响阶段继续。禁止边界接触为No。无清理、迁移、真实权限扩大、提交推送、自动合并或后继启动。没有新任务建议。
