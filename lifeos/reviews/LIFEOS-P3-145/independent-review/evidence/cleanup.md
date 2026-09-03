# 临时根精确清理记录

- 清理目标：`/private/tmp/lifeos-p3-145-independent-review-v1`
- 标记文件：`.lifeos_p3_145_review_marker`
- 经验证的根标记 SHA-256：`4b8b4cb1917051be1323a1f10be2fc0eb45c925d882554c001b8087dfda4450c`
- 清理脚本：`cleanup_temp_root.sh`

## 执行过程

1. 首次脚本校验将候选 owner marker 的 hash 错用于根 marker；比较失败后安全停止，未删除任何文件。随后读取根 marker 内容并校正为上述根 marker SHA-256。
2. 第二次尝试中，Git 对只读候选目录输出一次 `failed to delete ... Permission denied` 警告；candidate worktree 登记随即消失，但后续复核发现临时根仍存在。此前命令的 `cleanup_root_absent` 文本来自错误的 shell 控制流，不能作为删除证据，已撤销。
3. 清理脚本现已改为：在同一 exact-root／marker／hash 三重校验后，允许 Git remove 失败、仅恢复该临时只读 candidate 副本的用户写权限、再删除该精确临时根；删除后必须由独立存在性检查确认。

## 最终验证（修正后的重试）

- 重试前根 marker SHA-256 再次匹配 `4b8b4cb1917051be1323a1f10be2fc0eb45c925d882554c001b8087dfda4450c`。
- 清理脚本对已被移除登记的 candidate 输出 `not a working tree`，按脚本的清理分支继续；仅对该临时 candidate 副本恢复用户写权限后删除 exact root。
- 脚本内的 `test ! -e /private/tmp/lifeos-p3-145-independent-review-v1` 通过；脚本外再次执行的同一存在性检查通过。
- `git worktree list --porcelain` 不再包含该 candidate root。

## 结论

- 临时 review root：已不存在。
- 临时 candidate worktree 登记：已不存在。
- 未对发现的另一工作树 App 进程、Pilot-7 或任何真实数据边界执行清理。
- 此删除是本轮合成 review 临时产物，按 marker 校验执行；不可恢复。
