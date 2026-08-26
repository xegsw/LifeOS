# LIFEOS-P3-129 独立评审计划

## 建立时点与独立性

- 建立时点：在读取候选侧 `verifier.py` 前。
- 被评审对象：`lifeos/architecture/LIFEOS-P3-129/` 的最终候选包，以及任务卡指定的只读固定输入。
- 本评审不导入、调用、复制或修改候选侧 runner；独立 runner 仅使用 Python 标准库重新解析候选 JSON 和固定 Markdown 文本。
- 写入边界：仅本目录；候选、canonical V1.0、V0.1 历史和 PM 账本保持只读。

## 独立核对设计

1. 以 `ABF-P3-129-v1` 的固定 hash 及本评审自行定义的路径表复算 V1.0 与七项历史输入，确认候选的 `fixed_inputs.json` 没有遗漏或替换。
2. 直接检查 V1.0 Draft 状态、V0.1 的仍然有效状态，以及 candidate 的 V0→V1 分类、compatibility、freeze scope、runtime transition 与 promotion patch 是否分别覆盖 ABF-M-002 至 M-006 的语义。
3. 自行验证 promotion patch 前后 bytes：除状态／supersession metadata 外，V1.0 正文不得变化；post hash 必须可复算。
4. 直接复算候选历史保全和非自指 Final Manifest；不将 Manifest 自身计入其 inventory。
5. 以独立 runner 在内存 disposable 副本中注入 V1 hash 替换、V0.1 行遗漏、Schema/API 冻结扩大、V1 正文变更四类 mutation；每类必须出现针对性的 fail-closed 原因。
6. Gate 1–4 做基于冻结文本的独立判断；Gate 5 只检查其是否诚实标为不适用，不替代用户价值验证。

## 预设结论规则

- 任一固定输入／历史 hash 漂移、未覆盖的 V0.1 规范、冻结范围扩大、promotion 发生正文变更、独立性不足或提前 Frozen 均为 `Blocked / Not Pass`。
- 所有检查通过时仅可结论为 `Independent Pass / Awaiting PM Gate Review and Final User Freeze Confirmation`；本评审无权 promotion 或更新账本。
