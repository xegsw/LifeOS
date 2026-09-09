## IR-P0-147-001 artifact安全Closure

原固定提交 `640ebb6fe8d87398a05940b30f1263dad157dfa0` 的target artifact子目录链接可被字符串路径create/chmod跟随，导致哨兵0750变0700并写入，仍报fetched。这是有效候选P0，不是环境或Key问题。原566项工程文件逐Git blob归档在 `history/pre-artifact-closure/snapshot.tar.gz`，附旧Manifest、旧报告、lineage及原review/runner/results；旧历史不改写。

新增 `artifact_io.rs` 持有从根逐组件打开的目录FD链；mkdirat/openat相对FD创建，O_NOFOLLOW、O_EXCL、0700/0600及inode/owner/mode检查，不chmod既有目录。Web与local target、worker staging、parser stdin/stdout和缓存读取、最终发布与recovery均使用持有FD；发布从staging FD复制到排他新文件，sync及验证后才提交数据库，不按路径重开staging。恢复使用两个目录FD间排他renameatx_np，不覆盖既有文件。

确定性TOCTOU测试在生产检查与操作之间替换祖先/文件：FD操作至多作用于原持有inode，随后边界拒绝，不跟随替换链接或修改哨兵。10项Web/local控制、目录链接、最终文件链接、staging链接、DB回执故障覆盖内容和权限不变、失败无fetched；7项Rust新增覆盖祖先替换、parser、发布与隔离。原review反例2项仅适配到工程自有根执行，不能作为Independent Pass。

失败发布或DB失败可保留无数据库引用的孤儿文件，待已有recovery处理；不声称文件系统与SQLite间有对任意同UID并发进程的全局原子事务。测试哨兵和所有写入仅在工程自有合成根；实际review根及真实根未访问。UI、25IPC、Schema、Provider和root配置未变。详细修正与限制见 `design/artifact-safety-closure.md`。

## 文件责任与复核入口

artifact_io.rs负责目录链与文件FD生命期；source_file.rs将输入复制到持有输出FD；source_worker.rs负责staging/parser/发布/recovery接线；source_targets.rs共用Web/local发布；runtime_root.rs仅增加编译marker访问器；main.rs注册内部模块；repository.rs仅移除未用import。测试runner新增target_boundaries阶段。没有新增运行时IPC测试后门。

自动结果：65当前+29历史；原review反例2例另计。完整差异见evidence/artifact-closure-diff.json，正负日志见AC_MATRIX。原历史Rework与候选修正分开，风险是否关闭由独立复评和PM判断。
