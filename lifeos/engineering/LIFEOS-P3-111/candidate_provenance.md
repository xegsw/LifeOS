# P3-111 候选来源与正向白名单

- 唯一来源：`lifeos/engineering/LIFEOS-P3-106` 的 rework-1 Frozen Manifest，复算 SHA-256：`7a4007791223c55f4ea8541290a2fa60d36df69f0db5ece7b9507ca64da049fe`。
- 复制时不含 `evidence/`、`scripts/`、`tests/`、`target/`、任何既有 runner 或历史产物；这些目录均未进入 P3-111 候选。
- 以下为复制前与复制后相同的源文件 SHA-256（其后发生的 P3-111 改动会由最终 Payload Manifest 单独记录）。

| 白名单源 | SHA-256 |
|---|---|
| `.gitignore` | `c72c9ae2191ce55866638da7ff6f1724ec24c0310019261565ec2fd1b1e9c31c` |
| `Cargo.lock` | `430583c26b3104ff384c7ab539b0ebe79d90509a957701a2fb1ebd3b4c2026f1` |
| `Cargo.toml` | `9fd339d217537af1d7880f1070d0ed9e6c9c14c96e6b9fa32523293fdadb018e` |
| `README.md` | `67231092f2be8b0efddc3fd6fd856d22ed8b23a7dca66b7ce90689b7b7af5725` |
| `build.rs` | `62343b39726897a2c190d7ffe52bfd5ef85236f1f08a9f7d4595ee5993e02c74` |
| `rust-toolchain.toml` | `54231ca6bea6a491dfa45c5c1e12cc7485ae94c16a374e52933ee1a7cb48248f` |
| `tauri.conf.json` | `d44e1e03ade7ecc5dc75f5431295de78735ccf0596a421eae0f553411294e0f0` |
| `capabilities/main.json` | `ce407aaef4f37c9387727179aff9897f7957defdaebd42274021b8016d59050b` |
| `src/main.rs` | `4d7a1e4a1eebe08ffec78a4c0cd0e7cdeabf6b92e68c003b02e3515a035e042c` |
| `src/runtime.rs` | `0ca8dbc53faf1c5b9b6c021711ebe16e4fe5102851948e5fac1c589c13ce3529` |
| `ui/app.js` | `62d6685c8911efb5ccaabadde350e267cb0ce58b829abbeca0580ff7025a6507` |
| `ui/default-recovery.html` | `4a6464236b03ad5ffee1d50268169558320ca90484fe646933ff19c2497a5d56` |
| `ui/no-reliable-suggestion.html` | `1fdd0129ffa056fd64a08e0c6227cdf84b90cc8e964ff811dde2efabfaa85ce2` |
| `ui/restricted-offline.html` | `fa918f044fa9cbb4f3eafcb117af97bc039c5bbeb075ada2e91f9da34eecd27d` |
| `ui/styles.css` | `5b93977e863bd33a6f505e585080cdf85a547c08cee1bca9c7fa05008d26d50d` |

还复制了构建必需的正向资产：`icons/`（53 个文件；`icon.icns`=`e6e7eae0a6060cb21ace32751adb2bd9da6b2527374a4daae79c9aad505d11ed`，`icon.png`=`1e17993555bbe3d3984f113044221455fb0aa20bde281bfdc41c02a77c816293`）以及 `gen/schemas/`（4 个文件；`desktop-schema.json`=`f68a9c570ecff07ac6826145d33b966d6fc02f7d680967f44437268b08a6ba78`、`capabilities.json`=`f4a72eb313b4f56b9b231adebbe8906d5b5bbf3432ec82f6fce155dc3fb1716a`）。
