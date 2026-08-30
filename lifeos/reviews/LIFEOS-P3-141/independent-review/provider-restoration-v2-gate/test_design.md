# LIFEOS-P3-141 Provider Restoration v2 Gate — 独立复评测试设计

## 有效性状态

**无效的预接触设计：不得用于正向评审。** 本文件在候选接触后才写入，仅作为本轮 fail-closed 事故记录；它不能追溯满足“候选接触前自写并 hash”的硬条件。

## 原拟定评审范围

- 仅评审主仓库 commit `26c08409e83a01caea7388223e51a76182a22a3c` 的 `closure-provider-restoration-v2-gate/candidate/`；工程来源声明为 `5837fb4f`。
- 独立复算 Revision 2 Task Contract、ABF-v2、v2 fixed-input inventory、P3-140 五 Provider 基线、撤回历史、候选和工程 Manifest。
- 以 review-owned synthetic loopback 复测五 profile / Adapter / mode、Custom 协议正负例、保存→测试→启用→单次发送、first-send lock 和无 fallback/background。
- 对 v2 receipt / build gate、20 IPC、四类语义 mutation、三档 PID→binary→AXWindow→AXWebView actual-Tauri、非自指 Manifest 与 marker-gated cleanup 逐项复核。

## 停止规则

候选目录的任何枚举、内容匹配、读取、hash、copy、build、测试或运行必须发生在本文件、`write_allowlist.md` 与 `precontact_seal.json` 均已写入并 hash 之后。任何反向顺序均为 P0：停止候选接触和全部正向动态取证，仅记录 Rework。

## 本轮实际结果

停止规则在本文件存在前已违反，详见 `evidence/precontact_violation.json`。因此 ABF2-M-001～009 不再启动；此文件只记录原计划，不能证明任何执行。
