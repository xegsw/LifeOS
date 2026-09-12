# P3-155 影响与证据适配

完整基线165文件，新增1个仅synthetic-driver/boundary-tests启用的测试模块，最终166文件。差异逐文件见candidate-difference.json；无删除文件。公共14 IPC注册、输入DTO、既有表结构、真实固定路径/凭据服务及账号格式不变。

| 差异 | 用户行为影响 | 验证 |
|---|---|---|
| SourcesController start并发读取独立状态、独立错误/重试、代际守卫 | 健康异常不遮蔽工作资料，反向亦然；旧动作不清空新页 | source_recovery、sources_ui、combined |
| 既有来源section内新增真实阶段/数量/错误提示；健康section内新增状态只读重试及歧义说明 | 不提供假百分比；已处理/待处理/新增/变化/未变化/缺失有实际字段依据 | 实际sourcesView/AppleImportView输出与事件动作检查；渲染字符串断言 |
| source_worker同内容fingerprint复用、missing返回强制重新恢复 | 未变资料保留版本/解析；缺失恢复不永久停留missing | synthetic_update_lifecycle：无变/元数据变/正文变/缺失/返回、原件fixture修改与版本断言 |
| commit_batch原事务内写既有counters.outcome | 新增/变化计数不会先于记录发布 | 同一事务更新及上述生命周期断言 |
| source_api根据实际worker和未完成任务显示paused；手动resume可接回中断任务；错误写入绑定epoch | 重启不自动采集；旧worker失败不挂新任务；刷新/继续激活仅既有固定SourcePort | 独立进程source_process_recovery、暂停/重放/恢复、late_error检查 |
| lib恢复已有健康入口；status_table只验证既有表 | 用户手动选固定ZIP后沿旧事务导入；缺表不迁移 | 固定目标schema/锁/事务回滚、重复ZIP/部分失败、status缺表负例 |
| 新155合成根/构建模式/标识 | 不写154历史合成根；真实根与Key持久不变 | 基线差异、构建互斥及设置兼容回归 |

## 视觉范围与未验证属性

CSS四个主样式、Shell主导航、Settings页面结构与模型表单不变；没有新增页面/卡片墙。DOM变化限既有来源区域和健康导入区域内的状态段落、计数及重试按钮，文案可能增加换行和高度。实际纯渲染函数测试证明状态与按钮按条件出现，转义、安全码、忙碌及过期动作行为有断言；这些不能证明像素布局。

合成页evidence/synthetic-source-states.html来自最终实际sourcesView与既有CSS，仅有合成状态。Browser工具拒绝该file URL并明确禁止替代浏览器、间接执行或绕过，未继续受阻路径，也未收集任何真实窗口。当前截图0张，**没有视觉Pass**。

仍未验证：窄窗换行、实际字形/行高、长错误段落遮挡、滚动与按钮实际可达性。该Evidence Gap只影响这组视觉属性，不把整个候选标失败。请PM按D-0649基于此明确影响面决定是否仍需直接查看或其他已获准验证；本执行不自行绕过工具限制，也不让用户调试平台。真实App尚未切换。

## 复用边界

154的设置/Key/Provider、单次披露与错误归属在本轮累积测试再次覆盖，不用CSS相同代替行为。未重复154真实用户对话和历史视觉；其Accepted只证明旧阶段，不证明155真实更新。实际Provider发送、健康导入文件选择与刷新必须用户操作；本轮合成行为不得替代ABF-10。独立评审仍暂停。
