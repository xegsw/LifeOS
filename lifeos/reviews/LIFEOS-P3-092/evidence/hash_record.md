# LIFEOS-P3-092｜Hash 核验记录

副本：`/private/tmp/lifeos-p3-092-XpxwaB/app`。对照时间：2026-08-22（Asia/Shanghai）。

## P3-091 当前五项源文件（before / task-local copy / after）

| 文件 | before | 副本 | after | 结论 |
|---|---|---|---|---|
| `default-recovery.html` | `e0a274914e15550b5d16e7ec57267ac7b958ce22e7f2794cf832b2f9b657761b` | `e0a274914e15550b5d16e7ec57267ac7b958ce22e7f2794cf832b2f9b657761b` | `e0a274914e15550b5d16e7ec57267ac7b958ce22e7f2794cf832b2f9b657761b` | PASS |
| `no-reliable-suggestion.html` | `e7a59086357b14811605c2442039f6f15a0462deb2c7d4913828eae13a2d1793` | `e7a59086357b14811605c2442039f6f15a0462deb2c7d4913828eae13a2d1793` | `e7a59086357b14811605c2442039f6f15a0462deb2c7d4913828eae13a2d1793` | PASS |
| `restricted-offline.html` | `b9254076b390eba9a84721d3b68c4fd817f3db6964c6e535b6444e0d9a48078e` | `b9254076b390eba9a84721d3b68c4fd817f3db6964c6e535b6444e0d9a48078e` | `b9254076b390eba9a84721d3b68c4fd817f3db6964c6e535b6444e0d9a48078e` | PASS |
| `styles.css` | `35cab6aedf68b76aad5a54f60a87dd43adb4a2c4e16ac966c51c02c31ec02b91` | `35cab6aedf68b76aad5a54f60a87dd43adb4a2c4e16ac966c51c02c31ec02b91` | `35cab6aedf68b76aad5a54f60a87dd43adb4a2c4e16ac966c51c02c31ec02b91` | PASS |
| `app.js` | `a0dc4b80be80fb4f61519d2c1f19ef52f888a1c1578bc95a60a430481f63bdac` | `a0dc4b80be80fb4f61519d2c1f19ef52f888a1c1578bc95a60a430481f63bdac` | `a0dc4b80be80fb4f61519d2c1f19ef52f888a1c1578bc95a60a430481f63bdac` | PASS |

## 指定历史只读输入

| 文件 | 复算 SHA-256 | 任务输入记录 | 结论 |
|---|---|---|---|
| P3-089 `default-recovery.html` | `c8e6e130bdb26962f6663afc56529fecf2c3501f643633655837daa433ee16b4` | 同值 | PASS |
| P3-089 `no-reliable-suggestion.html` | `c38a3d8fe35bb00d5d13ca1fa1967daa813c1b8af083e75de3fb9cb593d0520d` | 同值 | PASS |
| P3-089 `restricted-offline.html` | `0965726629e105087b94680476f18e5a35f361f046be23ccbc468850ac84085f` | 同值 | PASS |
| P3-089 `styles.css` | `052600b12672a7d9bf255c130edbb4eb5d6d3d3bfee3a64be403e24e74dfe94a` | 同值 | PASS |
| P3-089 `app.js` | `88dc10ffa945d12baf42b771e4c6fddef791a5f1305e9f1d349161977684fe1a` | 同值 | PASS |
| P3-090 attempt-2 Evidence Manifest | `5365fec7762b587bdb02c6e65b7f7eff312139a1a32cfa04c665dbe7c58decf4` | 同值 | PASS |

P3-091 初始及 attempt-2 Evidence Manifest 也已复算，但它们不要求与自身列出的内容 hash 相同：`ae3011ee9a895aef1e88e3b35aedc5862b55d38eef5b42f0cf7b54b700524db7`、`5dd7e82804dd9c60fcc2ad378d7fa80393a1d767586c6aff7673b09c4e6bef6e`。
