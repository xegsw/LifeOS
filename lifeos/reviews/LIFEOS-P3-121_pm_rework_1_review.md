# LIFEOS-P3-121 PM Rework-1 Review

## 验收信息

- 任务 ID：`LIFEOS-P3-121`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-121_p3_116_design_faithful_p3_120_runtime_combined_closure_acceptance_basis_freeze.md`
- ABF ID／SHA-256：`ABF-P3-121-v1` / `b5d3597a5460983ffda923aa65f9aa23218dc1aa6730a171b0183e5062c53a03`
- ABF 启动前状态：Frozen
- 本次反例映射：L1-6/L1-7/L1-10；ABF-I-03/I-12/I-13；M-009/M-019/M-020
- 正式 Rework 次数／上限：2/2
- 任务验收状态：Rework 2/2 / Awaiting User Adoption
- 资产状态：Not Frozen
- 是否允许下一任务：No
- 是否允许下一阶段：No
- 专项交付物：`lifeos/deliverables/LIFEOS-P3-121_p3_116_design_faithful_p3_120_runtime_combined_closure.md`
- 初次 PM Review：`lifeos/reviews/LIFEOS-P3-121_pm_review.md`（保持只读，作为本轮固定授权输入）
- 本 Review：`lifeos/reviews/LIFEOS-P3-121_pm_rework_1_review.md`
- 更新时间：2026-08-25

## PM 总结

- P3-116 视觉忠实度整改已实质完成：icon-only Rail、尺度、留白、身份色和 Global AI 空间关系恢复；当前 actual-App 不再呈现为工程 Dashboard。
- 1160x768 与 700x760 当前 Tauri actual-App 图尺寸准确、同 DOM 自适应可见；1280x1024 图实际为 1036x768，M-009 仍 Not Implemented。
- PM 复算 Rework Manifest 所列 104 项，104/104 hash 匹配；initial Evidence 和初次 PM Evidence hash 保持。
- 但组合闭环缺 M-020，Rework Manifest 漏列当前交付物、combined closure、mutation 和初次 PM Evidence Manifest；M-019 的完整 lineage 不能成立。
- 最终计数：P0=1、P1=1、P2=0、Unknown=0、Not Implemented=2。结论为 Rework 2/2，等待用户采纳。

## 两层验收治理

- 是否新增无法映射的标准：No
- 是否需要修改 ABF：No
- 是否仍满足同任务 Rework 条件：Yes；用户结果、Tauri 架构、目录、合成数据、三 IPC、Schema/API 和风险边界不变
- 是否达到正式 Rework 上限：Yes；本次为 2/2
- 当前任务是否关闭：No；等待用户是否采纳最后一轮窄整改
- 再次失败的后置状态：不得第三轮同任务 Rework；须关闭为 `Closed — Acceptance Not Met`，如仍需相同结果则新建任务／新 ABF

## 视觉与 Apple 设计检查

`apple-design` 的 simplicity、spatial consistency、flexibility 与 craft 用于辅助核查。它没有添加新验收要求；正式依据仍是 Frozen P3-116 source/contract 和 ABF。当前设计整改通过该辅助检查，视觉 P1 视为关闭。

## Evidence 摘要

- 提交 Rework Manifest：104/104 列示 hash 匹配，Manifest 自身 SHA-256 `0e1722342a88c924e9fa2d5a170f8e9f63229bf60f4b6cdec9ea13da24764cad`
- 视觉尺寸：1036x768（1280x1024 请求）、1160x768、700x760
- Rust locked/offline：执行侧报告 9/9 PASS
- 静态视觉／边界：执行侧报告 10/10 PASS
- Runtime：执行侧 actual-App trace 保留首次、幂等、第二次、刷新和关闭重开；本轮未发现 Runtime 退化反例
- 清理：`/private/tmp/lifeos-p3-121-combined-v1` 不存在；PM 未创建临时根
- 历史：initial Engineering Evidence、初次 PM Review/Evidence 保持只读

## 未通过项

### PM-RW1-001 — P1 / Not Implemented

M-009 要求 exact 1280x1024 actual Tauri App Evidence；实际提交为 1036x768。配置声明、文件名和请求尺寸不能替代可观察实际尺寸。

### PM-RW1-002 — P0 / Not Implemented

`combined-closure.json` 没有 M-020；Rework Manifest 没有覆盖当前交付物、combined closure、mutation result 和初次 PM Evidence Manifest。该缺口违反 final lineage、Evidence 诚实与可复核性，不因整体结果诚实写为 NOT_PASS 而消失。

## Rework 2/2 整改边界

1. 当前视觉实现作为整改基线，不再重设计。
2. 在支持该原生窗口几何的受控测试环境取得 exact 1280x1024 Tauri App Evidence；不调整系统显示缩放，不用静态、缩放、浏览器或配置声明替代。
3. 在 combined closure 中补 M-020，并生成覆盖 current candidate、全部 Rework Evidence、当前交付物、初次 PM Evidence、Frozen/authorization inputs 与 cleanup 的非自指总 Manifest。
4. 对遗漏 current delivery、遗漏 closure/mutation、错误 viewport、额外文件和历史 hash 漂移执行 pristine-control 后的 disposable mutation fail-closed。
5. 新产物写入 P3-121 自有 `rework-2` 子目录；initial 与 rework-1 Evidence 严格只读。

## 边界与风险

- Tauri/WebView 架构保持；仅三 IPC。
- 不访问 Pilot、真实 DB／路径／文本、网络、模型或外部能力。
- 不修改 Frozen ABF、P3-116/P3-120 历史、Schema/API、风险、冻结或阶段。
- R-0051 维持原有限关闭；R-0024/R-0025/R-0040/R-0052 及其他风险状态不变。

## 本地预检

跳过。理由：本轮是关键视觉、Tauri/IPC 与 Evidence lineage 的高风险正式 PM 判断；本地模型不能决定 Rework 或替代直接 hash／尺寸／source 检查。

## 需要用户确认

是否采纳 P3-121 Rework 2/2，并授权原工程会话仅执行上述 exact 1280x1024 Evidence 与 M-020/Final Manifest 最终收口。若本轮再失败，P3-121 必须关闭，不允许第三次 Rework。
