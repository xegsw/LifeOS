# LIFEOS-P3-073 Evidence Rework Manifest

本 Manifest 仅登记 D-0306 后新建的可复查独立 Evidence。被评审资产保持只读；旧 P3-073 Evidence 继续原样保留。

- `independent_runner.py`: `39c3beafe5a025687a4f3e7367200e70fe1b535917982959b8ef63b8fb2abafe`
- `independent_results.json`: `a9d49e6fc9194b01801b65e41a557d4e271f5eedcda30b79dbaa905c9d98ae32`
- `README.md`: `74d4af4e5e11f78e05df6e4b1cc08f2d7e5ff234b06be48e707311c45da13215`

## 被评审授权复跑资产核验

runner 已逐项重算 `lifeos/engineering/LIFEOS-P3-072/authorized_rerun/evidence/MANIFEST.md` 所列六项 hash，结果为 `AR-01 PASS`。主体 `src/sandbox_export.py` SHA-256 为 `76997bded53f6aa1c943deb8705fb725ba03385bb423d05f5916ea3862c070fb`。

runner 也逐项重算 P3-072 原先未授权目录所列六项 hash，结果为 `AR-02 PASS`；这些资产仅验证保留，不作为可采纳结果。

## 结果与复跑

`independent_results.json` 为 18 PASS / 0 FAIL。复跑：

```bash
python3 lifeos/reviews/LIFEOS-P3-073/evidence/authorized_rerun/independent_runner.py
shasum -a 256 lifeos/reviews/LIFEOS-P3-073/evidence/authorized_rerun/independent_runner.py lifeos/reviews/LIFEOS-P3-073/evidence/authorized_rerun/independent_results.json lifeos/reviews/LIFEOS-P3-073/evidence/authorized_rerun/README.md
```

首次命令会重写 results，随后哈希应与本 Manifest 一致。运行仅使用一次性系统临时副本，不创建临时导出文件。
