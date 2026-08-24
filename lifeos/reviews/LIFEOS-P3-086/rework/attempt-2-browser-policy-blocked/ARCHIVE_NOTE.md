# P3-086 Attempt 2 Archive Note

本次记录用于保全 2026-08-21 的第二次 P3-086 重跑事实：该会话使用了受 browser-use URL policy 限制的控制表面，未能完成任务卡指定的 Computer Use Chrome 动态预检，形成 29 PASS / 0 FAIL 静态结果与 `Not Implemented=1`。

该会话错误地覆盖了 P3-086 根目录中的初始独立 Evidence，违反了 Rework Evidence 只读保留要求。PM 已在 D-0354 记录此 Evidence 完整性缺口；后续重跑必须写入 `rework/attempt-3/`，不得再覆盖根目录。

初始尝试在覆盖前已由 PM 读取并复跑，原始可核对摘要为：静态 26 PASS / 0 FAIL；独立 runner SHA-256 `3d8a442db4c8c2597b7886dd576ff15436e37a2b01f77f3aa80e9f26daf7c453`；结果 SHA-256 `2343644f52410a6b0d191c1046ef3b94eee7865e52252d754467963d8d088f09`；初始 Manifest SHA-256 `cedc455ade97be009e73a1e8690655696f5defe87d90423593ccb2fcc8cd5cda`。初始结论为动态 Evidence 未完成。

本文件不把第二次结果写成独立 Pass，也不替代完整、隔离的第三次动态复评。
