# LIFEOS-P3-094 attempt-4 PM Validation

## 范围

- 仅使用固定非敏感文本和 `/private/tmp` 新建隔离目录。
- 未读取既有个人文件／DB，未覆盖工程 Evidence。
- PM 临时目录在命令退出时精确删除，复核后不存在。

## 执行侧 Evidence 复核

- attempt-4 runner 以独立 PM Evidence 输出目录复跑：`13 PASS / 0 FAIL`，退出码 0。
- attempt-4 Manifest：14 个非自指文件 SHA-256 全部一致。
- `historical_read_only_hashes.json`：56 个历史只读文件当前 SHA-256 全部一致。

## PM 删除边界反例

PM 在隔离临时目录创建：

1. `authorized-runtime/capture.sqlite`，只含固定非敏感记录；
2. DB 父目录之外的 `outside-runtime/unrelated-fixed-sentinel.txt`，只含固定非敏感哨兵文本。

随后分别通过运行时 API 与公开 CLI，把 DB 外哨兵文件作为 `output_path` / `clear --output` 参数传入。两条路径均返回 `cleared`，数据库记录数变为 0，哨兵文件被删除。

结构化事实：

```json
{
  "db_count_after": 0,
  "operation_status": "cleared",
  "victim_existed_before": true,
  "victim_exists_after": false,
  "victim_outside_db_parent": true
}
```

CLI 复核同样得到：`CLI_OUT_OF_SCOPE_FILE_DELETED=true`，随后 `today` 返回 0 条记录。

## PM 判断

- P0=1：`delete_all()` 与 `clear --output` 没有把删除目标限制为同一 task-local DB 父目录下的精确 `today.html`，可删除调用者指定的其他可写本地文件，违反任务卡的目录授权和删除边界。
- P1=0；P2=0；Unknown=0；Not Implemented=0。
- 执行侧 13 项 PASS 与 hash 证据真实有效，但自检没有覆盖“DB 外路径必须拒绝且文件、DB 均保持不变”的负向用例，不能抵消该 P0。
- 结论：`Accepted / PM Adjusted to Rework / Awaiting User Confirmation`。
