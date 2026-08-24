# LIFEOS-P3-094 Rework attempt-8

本轮只修复 render 的 DB 缺失旧页面生命周期和严格只读读取：DB 缺失时先失效安全 task-local 旧页面且不创建 DB；零字节、无必需 Schema、部分 Schema 或查询失败时不初始化、不补写、不创建 SQLite 副文件，并保持 DB bytes／大小／hash／对象清单不变。

```bash
python3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-8/scripts/run_attempt_8.py
```

runner 仅在 `/private/tmp` 创建固定非敏感夹具，使用 `-B` 和内置 `compile()`，不写用户缓存目录。提交 Evidence 位于本目录 `evidence/`；PM 复跑须使用外置 `/private/tmp` Evidence 路径，避免覆盖提交 Evidence。
