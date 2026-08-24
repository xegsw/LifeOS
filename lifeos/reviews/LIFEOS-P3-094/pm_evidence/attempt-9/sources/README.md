# LIFEOS-P3-094

有限 Stage 3 的单进程、离线、task-local SQLite 闭环。只保存调用者明确输入的文本；唯一数据库文件是已存在 task-local 目录中的 `capture.sqlite`，唯一内部页面是同目录 `today.html`。

```bash
mkdir -p /private/tmp/lifeos-p3-094-runtime
python3 -B scripts/operator_cli.py --db /private/tmp/lifeos-p3-094-runtime/capture.sqlite capture --text '用户主动输入' --key first
python3 -B scripts/operator_cli.py --db /private/tmp/lifeos-p3-094-runtime/capture.sqlite render
python3 -B scripts/operator_cli.py --db /private/tmp/lifeos-p3-094-runtime/capture.sqlite clear --confirmation DELETE
```

五个公开入口与 CLI 共用同一条 path gate：保留调用方的词法路径，要求绝对、规范化后严格等价、固定 basename；从 `/` 开始用 `openat`/`O_NOFOLLOW` 打开每级父目录；数据库与页面只接受普通单链接文件。父目录必须预先存在，capture 不创建祖先目录。调用方页面参数、链接、硬链接、目录、FIFO、socket、sidecar 及无法确认的对象均 fail closed。页面失效、临时文件和原子替换只使用稳定 parent fd 与固定 basename。

当前未变更的 `SCHEMA` 会在内存 SQLite 中生成唯一 canonical contract。全部既有 DB 操作先以严格只读模式核对 `quick_check`、对象类型、规范化 SQL、列顺序／类型／非空／默认值／主键、AUTOINCREMENT、唯一 autoindex 与额外对象关闭态，再一次性验证完整 captures/audit 结果集。记录 UUID、带时区时间、SQLite 类型、非空值、逐行 `source=local_capture`、唯一身份，以及 `capture_saved`／repeat／clear 审计链任何一项不可信时，不返回或展示部分记录。

生命周期合同：新 DB 通过同目录独占临时库完成 Schema 与首写后原子发布；既有 DB capture 在写前验证，失败回滚并恢复旧页面，成功新增记录使旧页面失效；重复幂等只追加预期 repeat audit。list/snapshot 严格只读且永不创建 DB。render 先全量验证，再以同目录临时普通文件、flush/fsync、原子 replace 发布；无可信 DB 时先使安全旧页面失效。clear 要求精确 `DELETE`，预检后先使页面失效，再以单事务清空 captures 并追加审计；事务失败回滚 DB，页面保持失效并明确披露。

不支持并发恶意路径替换、多进程并发写、崩溃/WAL 恢复、网络文件系统或外部进程篡改；发现 sidecar 或关键对象身份变化时不报告成功。不得指向既有个人文件或数据库；不得联网、导出、使用 Tauri/IPC、Vault、云、同步、第三方服务或外部用户。
