# P3-108 Evidence Manifest（非自指）

本 Manifest 不包含自身；以下列出的均为本轮 P3-108 自身 Evidence。哈希计算于精确清理后，复跑命令与结果语义见 `dynamic_closure.md`、`matrix-results.json` 和 `final-verifier.json`。

| 文件 | SHA-256 |
|---|---|
| `build-results.json` | `b64dcc1b8d9b01635329713ee958d51e5e0640c9c76c9ca496843be37b615206` |
| `build/cargo-build.log` | `ea743f1a25f8e77a616f27e53b147a66663f62ba68474fec9fda69c92da21c14` |
| `build/cargo-tauri-build.log` | `3e58c79925ba61910735974355f27a743ab25facb03dc5c24db7f0001cf1c953` |
| `build/cargo-test.log` | `23901783daaeb4e8b59be59c470fbb1fc4bbdf07079aae2eccc112cf4c6c5c49` |
| `cleanup.json` | `763338bf34001b4d531a69f080c15ef564489fba98328104db1642a7374f716f` |
| `copy-inventory.json` | `554b5717c620b6a9b0b54b3bca6dde8416875a2d053e5bb8f1df768860e92443` |
| `dynamic/P3108-D01-default.jpeg` | `f770e31d3890fdaae33246a6e597c06e6c261fb6cbe3c1e10ed1bf1fbee7b487` |
| `dynamic/P3108-D02-no-suggestion.jpeg` | `de3272279b8d67158391e86d95ee62bf6be1bd4e0b461a1572795e3ae5f32faf` |
| `dynamic/P3108-D03-restricted.jpeg` | `b6d5c85ef75d5d061fada7191f664cd072813725670a3e3704b5fb0d50813dc1` |
| `dynamic/P3108-D04-first-capture.jpeg` | `f2e111fb9746ed70fe11c316f38dce92b3e44f90cfe61b2431914efffe7a0765` |
| `dynamic/P3108-D05-repeat.jpeg` | `469edf94849506b1bcb6f452aa8fdf2be56c8c865cb6c4a93cf82fb5786a3744` |
| `dynamic/P3108-D06-conflict.jpeg` | `fc190abb2df62b32e6c9d068963fc462562bb10a0e2fe99f7125f6edda4da323` |
| `dynamic/P3108-D07-failure.jpeg` | `b1a8afa367cf3d85b8352160488c47bc2848cdcffa4567321e0da479a787ef46` |
| `dynamic/P3108-D08-refresh.jpeg` | `fd703de87127410ae604d0d9691a5e1164aaa3c09c98737230e3d23992191191` |
| `dynamic/P3108-D10-reopen.jpeg` | `172549bffda6a6f9084f3efc6f3862664d34ca45b47c498d830f41b2f92404b1` |
| `dynamic/P3108-D12-unknown-ipc.jpeg` | `5e5003769bbbeee6f10824a48e6cb25f760adcf00f78d6202a68ae0f204190f4` |
| `dynamic/P3108-D13-extra-fields.jpeg` | `7055260a47f0426a1ba9c6367abcc6a246fab0f4fa61d4c4eda91280124933f9` |
| `dynamic/P3108-D16-700x760.jpeg` | `a08fccd597949c90e24b17ba84ab66b87cce3d862363b3f1f6fa38b8f247a348` |
| `dynamic/P3108-D17-tab-focus.jpeg` | `da3e731a417cf25ac7d474897e590fb0eac11df8bf8cda10a3ed68fdb98b4423` |
| `dynamic/P3108-D18-enter-skip.jpeg` | `7dac58f69a37ad5390342063b21aa2f79966a818536df82ddd0fc4ca97ad041e` |
| `dynamic/P3108-D20-content-tamper.jpeg` | `1265528e6eae4060178f92d9fce17c6d561ee0f3a946323313ab32cd1344dc1b` |
| `dynamic_closure.md` | `4915dc0788f447995e3ff28a11cad5f663a408e8e5f62578074c48a7e10b0007` |
| `final-verifier.json` | `eb16da1038b8c7d052358fb5aa6b6597326843dc13a9aa8aacb29fe63e125e3a` |
| `final_verifier.py` | `f1f68cdcef9431bd319c7b46f10f6c789025e82a8a2d9c54509d11870963ba6a` |
| `independent_runner.py` | `e5ce64cf51e8f7d28602e2c4f8cf89b572f10c455fb1fdea3497a8d09b727500` |
| `manifest-verification.json` | `cacacf4b45936ab7472fe53d633c0c7e0d9dacee2631487d956364d4ed8eea89` |
| `matrix-results.json` | `3db422fcaf7acb631b82bfff88c539c76fdc9669544c9a194d9cc850b97edb2c` |
| `runner-error.json` | `16ab027d49fc0989db65b4257b23e541cea253c9f3f0db4d0bf05695efdfd101` |
| `snapshot.json` | `fe42782634c5f325382a8fe90c14e8a66e084776e2854ad7402583d20cdc7b52` |
| `static-results.json` | `dcb1ba8f6a68bb7d9daca71fd2f810b62d7ba65329eba27406b9f52eb16de094` |
| `test_design.md` | `390d67e69695275ba274edb226838c6b88300ef61246febc0f67b19b4e6b37f2` |

`runner-error.json` 保留首次独立 runner 未显式定位既有 Cargo 可执行路径的透明历史；随后 runner 仅将 PATH 指向既有 `~/.cargo/bin`，没有安装、下载或修改工具链，最终 M-005 已独立通过。
