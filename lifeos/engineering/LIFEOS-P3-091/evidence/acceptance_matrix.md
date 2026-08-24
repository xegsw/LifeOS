# 验收标准 → 测试 → Evidence

| 任务卡验收标准 | 测试 | Evidence |
|---|---|---|
| 三页身份／边界清楚一致可访问 | static 97 checks；Chrome AX | `static_results.json`，`dynamic_results.json` D-01/D-11/D-12 |
| 不伪称真实能力 | 禁止能力静态扫描；失败披露动态核对 | `static_results.json`，D-06/D-15，`03-failure-cleared.jpeg` |
| 生命周期与关闭态不回退 | confirm／grant／CONFIRM／repeat／revoke／failure／refresh | D-02 至 D-07，`02-confirmed-recovery.jpeg`，`03-failure-cleared.jpeg` |
| 暂无建议与权限受限边界 | 三页导航及动态状态核对 | D-08 至 D-10，`04-restricted-offline.jpeg` |
| 键盘、焦点、宽窄屏、reduced-motion | AX 控件路径与 CSS check；Chrome 视觉 | D-11 至 D-14，`01-preflight-default.jpeg`，`05-narrow-responsive.jpeg` |
| 首次／重复／关闭重开与真实边界 | 干净副本静态／Chrome reload；页面内存设计 | `static_results.json`，D-03/D-04/D-07/D-15，`operation_log.md` |
