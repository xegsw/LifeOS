# LIFEOS-P3-116 Rework 1｜受污染 AX Evidence 精确删除记录

- 日期：2026-08-25
- 用户授权：采纳 Rework 1/2；授权同一 P3-116 Evidence／隐私窄整改；授权精确删除 `D-000.ax.txt` 至 `D-045.ax.txt` 共 46 个受污染文件。
- 删除原因：46 个 AX raw logs 含任务 synthetic 原型范围外的 ambient 浏览器元数据，违反 task-local synthetic-only Evidence 边界。
- 删除范围：仅下表 46 个普通文件；不删除候选原型、截图、结构化结果、runner、Manifest 或其他初次 Evidence。
- 恢复性：工作区文件已精确删除；其删除前 SHA-256 与历史判断保留如下。不得从包含受污染内容的副本恢复为活动 Evidence。

| 精确路径 | 删除前 SHA-256 |
|---|---|
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-000.ax.txt` | `1715746a03a80e264cf38be1cfae4af3c5839ffc0a2b3749166b6231c365172a` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-001.ax.txt` | `36dea8b95281a43b24dae2817fca1cadab4e82a2a11b882faa03d3fc0c5aea8b` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-002.ax.txt` | `9b33cd8fb80c69dbce7e167e6eebbbb6257901b0c5fa4b0f1707d0ed06cc9fe6` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-003.ax.txt` | `500fa12913e9dd32885017af210ed9fcdd50a431f9a88a4edaf1aa153e52f0d4` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-004.ax.txt` | `1715746a03a80e264cf38be1cfae4af3c5839ffc0a2b3749166b6231c365172a` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-005.ax.txt` | `82d683b740428c891f96550caf158391fefa9118c49452a66ab601c4c164f6d4` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-006.ax.txt` | `82d683b740428c891f96550caf158391fefa9118c49452a66ab601c4c164f6d4` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-007.ax.txt` | `68f8f25458cd2ea679b363c19728aba1b110e0d95a9d68d851cbae485702cb4f` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-008.ax.txt` | `4e7f0239f1e3731c6bd041c1c6540e6cf15e1878883ab822099d81d341cac64c` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-009.ax.txt` | `d88dec16d122b68221d9ec951d8231450adf280d2c7717989ca5bc22b1bfb2a5` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-010.ax.txt` | `76b4e2cd2509d0e2bb2f0aacfdcf0f12bdbdec9b17378c0acbac58462172ed45` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-011.ax.txt` | `5e6e48fb3376ddfe9163d4c142a5d683c825e09470a499af709c225b117bba4a` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-012.ax.txt` | `5e6e48fb3376ddfe9163d4c142a5d683c825e09470a499af709c225b117bba4a` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-013.ax.txt` | `5e6e48fb3376ddfe9163d4c142a5d683c825e09470a499af709c225b117bba4a` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-014.ax.txt` | `5e6e48fb3376ddfe9163d4c142a5d683c825e09470a499af709c225b117bba4a` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-015.ax.txt` | `5e6e48fb3376ddfe9163d4c142a5d683c825e09470a499af709c225b117bba4a` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-016.ax.txt` | `5e6e48fb3376ddfe9163d4c142a5d683c825e09470a499af709c225b117bba4a` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-017.ax.txt` | `72a4c60d37796b9df9157c648bf626d81337c70103d5a7a6d609f9c15e82feda` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-018.ax.txt` | `916647d054c9004d23f33c5655230c1603fde5ad0c5c9021eb1fba0fa2b33cc5` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-019.ax.txt` | `c97be53952cd4fb3cadf6d6ca78cf64c157bb8a6e2a0041edb4259914889ff07` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-020.ax.txt` | `981352d5b71475ee1a57aa4754d8dd60f679863a8f289b3cdc510255f5c5902d` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-021.ax.txt` | `ae2a260bae5a0987574fcdaf16bfba0e17f52f141ac99e091cae46ec9216644e` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-022.ax.txt` | `710da405f2effe28657ccb096af1865f37420d7fb4d2055052603d1356791102` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-023.ax.txt` | `9ff675d4daabb87ed97327a4eb23174d2798a6711893cd9386fb0ad383b3a32a` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-024.ax.txt` | `8c934ebc68f9ff54b611c0d28f5c0d06ee8122ae7185d261cf4f796854232a52` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-025.ax.txt` | `ae2a260bae5a0987574fcdaf16bfba0e17f52f141ac99e091cae46ec9216644e` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-026.ax.txt` | `387aa5fb1fd5dc89a8854ed160271f77069c02bacbd56336e8089e045039a0c4` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-027.ax.txt` | `9d0826240c453f60f5287c1c591506c5a36bf615975d194d21d00f29b1c9782d` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-028.ax.txt` | `916647d054c9004d23f33c5655230c1603fde5ad0c5c9021eb1fba0fa2b33cc5` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-029.ax.txt` | `3115df4a56bed9ba28d480ff7fbf7dd3caccba36f741481eb9415ac35234e71c` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-030.ax.txt` | `5d64cef6702a4f0840ef2b8f7b326af74e6ab4fb6c03d050eb7fe7cb60ab3434` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-031.ax.txt` | `a7b9b8a85434aeaad5d1bd64ec4b6a1c208d73a675c53c193d6fd997f839f293` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-032.ax.txt` | `1715746a03a80e264cf38be1cfae4af3c5839ffc0a2b3749166b6231c365172a` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-033.ax.txt` | `0ac67a720d1aa4ef343cd127b5132d7abbf4f6d9d5c24d7080f4be27a3b0523d` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-034.ax.txt` | `23bbfa29635ed7140070fdacbbf2fc2fd0b2dc2f0458f46c987002102ca7c79d` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-035.ax.txt` | `24e80c4792a5423def657cb43ee9719cf49c0b99841f5dc5881cc3e621b072d8` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-036.ax.txt` | `5cfebc4376e1030327381f9f192f5a6b7553b7c7eecd8bee7f8b620de4fa696e` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-037.ax.txt` | `1e8fbc9ac196b841803d086ec17c64d12f9bfc918c43d82c132e54457311f8db` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-038.ax.txt` | `21e9226fb79dd652b023ef8fa49c24ffea16018b22ebfdd781c20c88d4c8c58c` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-039.ax.txt` | `af285d118a86a2285e4974834e7df7616213a52964360811203e748b245042b7` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-040.ax.txt` | `79b803e34ee6a7e42c8987793d7b065dca923a9d93273318e72e76702f5c9635` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-041.ax.txt` | `98f9de0ffd6c819bbbde90509fc21503cd665fd71e16af0daebb643decfa74ee` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-042.ax.txt` | `c57a235f7a7c7bfd881c1bcb1f94e4c521a9bc80ba5e89a6657f4238469df8ab` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-043.ax.txt` | `aa5ca47a599a9b303fc47e80e1b90adafe5be07db90ca4612837a52ce382c847` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-044.ax.txt` | `3f1ec7e958c8cd656accfc2ad69ca5c0a2f6ed10e0b7062b26b5967ea2828f8c` |
| `lifeos/prototypes/LIFEOS-P3-116/evidence/raw/D-045.ax.txt` | `f2e1e7a7c044620a0a8bb05a63031be9423fef1c9e6d50650630677b1ef4b2cd` |

- 删除后核验：PASS。46 个精确路径逐一 `test ! -e` 成立；`raw/` 目录仅保留未获删除授权的 `dynamic_actions.json`，删除后路径清单 SHA-256 为 `53153677c14b7d8478c5333e466a2c12a5b69b08c66aef8111a7739204fe143d`，文件数为 1。
