# PM-P3-106-R1-CE-01｜禁止旧临时文件内容被读取

## 结论

- 严重级别：P0。
- 映射：L1-7 Evidence 诚实、L1-9 授权不漂移；ABF-I-02、I-12、I-13；ABF-M-016、M-018。
- 结果：`LIFEOS-P3-106 resume-1` 不能 Pass，进入正式 Rework 1/2。

## 冻结依据

`ABF-P3-106-v1` 第 60 行明确规定：

- `/private/tmp/lifeos-p3-104-rework-static-results.json` 不得读取；
- 当前既有文件只允许做路径 metadata 的只读前后核对；
- 不得读取内容。

## 事实证据

`evidence/resume-1/tools/run_cleanup_resume.py` 第 22 行对该路径执行：

```text
hashlib.sha256(legacy.read_bytes()).hexdigest()
```

这会实际打开并读取文件内容。生成的 `cleanup_results.json` 第 99–102 行记录了 `legacy_forbidden_metadata_after.sha256`，证明该分支实际执行。

`evidence/resume-1/tools/finalize_resume.py` 第 9–11 行不检查该授权违反，直接把 M016–M018 改写为 PASS；第 24–29 行只检查残留、历史布尔值和自报状态。因此 `final_verifier_results.json` 的全零 PASS 与冻结授权事实冲突。

PM 没有读取或复算该旧文件内容，也没有执行提交的 cleanup runner，避免重复越界。

## 窄整改闭环

1. `resume-1` 全部资产只读保全，新建 `evidence/rework-1/`。
2. 删除 runner 中对禁止旧文件的 `read_bytes`、hash、open/read；只保留 `lstat` 的存在、类型、size、mtime_ns、ctime_ns 等 ABF 允许字段。
3. final verifier 必须检查 runner 源码不存在禁止内容读取表达式，并核对 before/after metadata 相等；不得无条件写 PASS。
4. 使用新的空 Evidence 完整重跑 M001–M018，不得修改或重生成 resume-1。

以上不改变 ABF、runtime、路径正则、数据、IPC、依赖、视觉权威输入或产品结果，符合原任务同范围 Rework 条件。
