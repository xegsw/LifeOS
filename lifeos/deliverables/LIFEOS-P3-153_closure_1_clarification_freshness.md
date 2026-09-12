# P3-153 Closure-1：澄清依据的时效与授权

**工程修正完成，提交 PM 复验。** Codex 单 Agent；L2 synthetic/offline；2026-09-09。沿用原任务和 D-0652，不新增权限、Schema、IPC、请求字段或真实操作。

## 先行复现与修正

PM指出的问题已在修改生产逻辑前复现：昨天回答20分钟，合成时钟前进一天后，关联状态过期且无有效的替代可用时间依据；今天主动请求安排仍被 `clarification_suppressed` 拒绝。旧测试确实把这种永久抑制当成正确行为。

同类检查发现第二处：状态在 prepare 时尚有效、提交前已过期，但 packet 自身仍在5分钟有效期内，原验证仅比较状态内容未变化，会接受已过期的状态引用。两项复现见 `evidence/reproduction.log/json`；其中“2通过”是缺陷复现断言，不是修复验收。

修正如下：

- `answered` 保留为历史事实，不再直接抑制新问题。当前仍有有效状态或获准来源可回答时不问；这些依据到期、撤权或成为墓碑后，新的主动请求可触发一个必要追问。新问题采用新实例ID，旧 answered 行原样保留。
- Application 只使用经过当前授权和时效过滤、实际进入上下文的状态判断缺口，不使用未过滤 snapshot 状态。
- Host 在 commit、披露确认及结果完成时重验状态有效期。发送前过期则拒绝，模型调用为0；调用过程中才过期，晚到结果标为 stale，不自动再发。
- `reject` 仍持续至显式 `reopen`，不因过期而解除。暂缓保留既定时间条件，用户可以主动提前回答；忽略仅对本次有效。读取与时间推进不生成新问题，不改状态/历史，不触发定时联网。

## 同类路径一次覆盖

| 场景 | 结果 |
|---|---|
| 昨日20分钟过期，今日主动安排，无替代时长依据 | 允许一个新追问，旧 answered 原样保留 |
| 有效替代30分钟状态或获准来源 | 不重复问 |
| 替代来源到期/撤权/墓碑，状态撤权/墓碑 | 不使用失效依据，允许新缺口；不复活旧状态 |
| prepare后状态或来源跨有效期 | 拒绝旧packet |
| prepare后来源版本/授权generation变化 | 失败关闭 |
| 披露确认前状态过期 | 0次模型调用 |
| 模型返回时状态刚过期 | 历史回答stale，重复确认不重发 |
| 明确拒绝跨多日、仅打开/读取 | 拒绝仍有效，DB内容无变化 |
| 独立进程关闭→夹具状态过期→重新打开 | 新请求产生新问题，旧回答和问题保留 |

最后一项使用本任务新建 `p153-c1-*` 合成数据库，在其进程关闭后仅调整该夹具的状态时效，不暴露新的运行时IPC/时钟参数。两个实际PID为 `[58045, 58049]`，见 freshness.json。Rust使用 `cfg(test)` 线程局部时钟，生产构建不含时钟覆写。

## 验证与计数

| 本轮实际执行 | 结果 |
|---|---|
| 完整累计候选离线构建 | Pass |
| Host语义 | 35/35 |
| 披露/确认/返回 | 23/23 |
| Application/Host集成 | 14/14 |
| 原连续性 | 8/8 |
| 新时效/授权/独立重启 | 6/6 |
| 受影响测试合计 | **86/86** |
| 来源过期时钟跨越定向复跑 | 1/1，不重复计入86 |

未重复运行原快照中未受影响的81项，也未重做原生GUI；原151项记录保持只读，复用范围见 impact-map.md。不能把本轮结果写成“全部167项重新执行”。chat renderer、CSS及Settings文件hash未变，原6份GUI仍覆盖相同布局和动作；新增条件由Application/Host行为验证。

范围内 **P0=0、P1=0、P2=0、Unknown=0、Not Implemented=0**。独立评审仍按用户要求暂停，不是 Independent Pass；真实能力未启用。

## 历史保全与交付

- 原终局231项Manifest及原报告逐项保持不变，见 parent-snapshot.json。原151项快照没有重写。
- Closure-1完整候选仍为163文件，与父候选差异5文件：Host、health_context及生成JS、两个Rust测试文件；无候选文件删除。
- 生产文件与已构建副本一致；最后仅加强来源过期测试的时钟跨越方式，最终测试源码已编译并通过。
- 差异及候选摘要见 difference-manifest.json；摘要 `6e4e2be788d1af9d3f0c4bfffcab2dfebe68647f479066eb2a637193fb0a6a61`。
- 工程：`lifeos/engineering/LIFEOS-P3-153/closure-1/`，包括 candidate、tests、tools、evidence、impact-map、checkpoint、FINAL_MANIFEST。
- 未重开GUI、未替换原合成App；未触达真实App/数据/凭据/网络；没有提交推送或修改账本/冻结/风险/Stage。

复跑（从b3f6仓库根）：

```sh
python3 lifeos/engineering/LIFEOS-P3-153/closure-1/tools/rerun.py --affected
python3 lifeos/engineering/LIFEOS-P3-153/closure-1/tools/verify.py
```

复跑在唯一授权合成根下新建副本，源码和交付Evidence保持只读。托管CI未运行，不声称CI全绿。

需 PM：复验并裁决本次同任务Closure-1。没有新的授权或协议问题待决。
