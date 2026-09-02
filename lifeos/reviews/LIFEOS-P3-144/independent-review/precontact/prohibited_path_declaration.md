# P3-144 Phase B 独立评审禁止路径与能力声明

## 绝对禁止路径

`/Users/xxe/Documents/LifeOS-Self-Use-Pilot-7`

`/Users/xxe/Documents/LifeOS-Self-Use-Pilot-7/capture.sqlite`

对上述路径及其任何子项，Phase B 中禁止一切 `exists`、`stat`、`lstat`、`access`、`probe`、枚举、glob、hash、读取、复制、创建、写入、删除、清理、SQLite 连接、进程参数引用或间接脚本访问。不得以父目录／模糊扫描／清理校验方式触及。

## 绝对禁止的数据与网络能力

- 真实个人内容、真实 DB、真实凭据、OS Credential Store 中的真实条目。
- `https://api.deepseek.com` 的真实请求以及所有其他 Provider、网络 endpoint、代理、重定向、后台发送、自动重试和并行发送。
- 真实 Health／医疗数据、医疗诊断／治疗／药物／紧急判断。

## 历史与治理禁止

- 不修改 P3-143 candidate、工程 Evidence、交付物、Review、Manifest 或其历史；不修改 P3-144 engineering、deliverable、PM 账本、风险、冻结、Stage 或任务卡／ABF。
- 不关闭 R-0055／R-0056，不冻结产品，不进入 Stage 4，不开始 Phase C／D，不创建后继任务。

## 失效处理

如发生上述任一接触、真实内容泄漏、真实网络／凭据操作、候选或历史写入，立即停止，记录 `Irrecoverable Invalidation`；不得以清理追溯修复独立性或正证据。
