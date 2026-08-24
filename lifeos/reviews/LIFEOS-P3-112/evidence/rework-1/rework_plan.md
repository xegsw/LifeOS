# LIFEOS-P3-112 Rework 1/2 执行设计

- 创建时间：2026-08-24T17:18:45+0800
- 授权依据：P3-112 PM Review 与 D-0455；同一任务、同一 `ABF-P3-112-v1`，只整改 P3-112 自有 runner／Evidence／Review／交付物。
- 触发问题：初次 runner 只依赖裸 `cargo`，将 PATH 缺失误判为工具不可用；并且未将 `TMPDIR` 收束到唯一临时根。映射 L1-7、L1-9、L1-10 与 ABF-I-05、M-005～M-013。

## 保全与禁止

- 初次 P3-112 Evidence、初次 Review／交付物和 P3-111 全部资产均只读保留。
- 不读取或接触 Pilot-2；不启动真实 app；不联网；不修改 P3-111 candidate、账本、ABF、风险、冻结或阶段。
- 复跑前 `/private/tmp/lifeos-p3-112-review-v1` 必须不存在；所有 Cargo target、TMPDIR、candidate copy、fixtures、control 和 mutation 仅位于该根。

## 独立复跑

1. 验证 ABF／12 个固定输入／72-file candidate identity 和初次 P3-112 历史 hash。
2. 优先解析 PATH 的 `cargo`；为空时仅使用 PM 指定的预存 `/Users/xxe/.cargo/bin/cargo` 与同目录 `rustc`，检查常规可执行文件和版本，不安装、不联网。
3. 以正向 candidate copy 执行 `cargo test --locked --offline` 和 `cargo build --locked --offline`；同时设置根内 `CARGO_TARGET_DIR`、`TMPDIR` 和 `RUSTC`，记录 8 tests、网络关闭和 test fixture 归属。
4. 由本轮新 runner 独立完成静态扫描、动态／隐私审计、initial 37／rework 38 payload 重算、祖先 `/disposable/noop` unchanged control、六类真实 mutation 与提交 verifier 只读 cross-check。
5. 生成逐行 M-001～M-015 closure matrix、非自指 Manifest 和精确 cleanup Evidence；只在全零条件成立时更新为 Pass。
