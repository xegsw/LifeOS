# P3-148 存储映射与无旧库 DDL 方案

状态：设计提案，未访问真实DB，未创建任何运行根。固定代码与行号均相对5c26431的P3-147 candidate。

## 已核对事实

`src/repository.rs:12–22,146–150`已有records、memories、states、drafts、questions、packets、derivations、feedback、sources，均为`id PRIMARY KEY, body JSON TEXT`。requests存operation/payload/result，audit存事件/引用/时间，meta单调revision；records有source_version及turn_identity唯一索引。`open:93–164`不是只读打开：会建表、建索引、插入fixture sources。不能直接用于“无迁移打开既有真实库”。

`save:387–520`只有record/answer/remember三种intent、200字符限制、每领域最多3条活跃conversation记录；它还计算原文SHA256，并可能自动解析为state。这些不是来源对话的合适隐含语义。`draft:697–727`不走完整txn，同revision异文可覆盖。`txn:338–371`把完整payload和result复制进requests，不能用于Secret。`snapshot:188–205`仅过滤sourceFile记录，其他表全量返回，不能承载新内部请求和凭据。以上均为源码事实，不是针对真实库的缺陷复现。

`source_store.rs:19–31,229–233,536–581`已有来源/段落/版本/权限表及依赖失效；搜索是有界词项匹配（中文双字、英文词），不是FTS5或语义搜索。旧设计中“FTS查询”不能作为当前实现证明。`application/core.ts:39–50`的旧resolver会自动加入确认memory和state；来源对话不能沿用它扩大披露。

## 推荐：同一业务库，零新增对话表，零旧库DDL

| 对象 | 复用位置 | P3-148新增JSON语义 / 事务 |
|---|---|---|
| 问题原文 | records | schemaVersion:3, kind:source_ai_question, intent:question，conversationId/turnId唯一；text原样、version=1、createdAt服务端、sourceId=conversation、status=active。不计算contentHash，不推断state，不套三条活跃状态上限；历史旧记录不改写 |
| 草稿 | drafts | kind:source_ai_draft，text/revision/turnId/conversationId/status；CAS，同revision异文拒绝；save_question原子消费绑定draft，records+draft committed+receipt+revision一起提交 |
| 预览/发送尝试 | packets | kind:source_ai_preview；questionRef及版本、源段inputRefs、纠正引用、精确bodyJson、预算、profile/credential revision、过期时间、随机token；status保留active/stale用于旧失效路径，独立deliveryState记录ready/cancelled/dispatching等，不因stale抹掉已发送事实 |
| 回答 | derivations | kind:source_ai_answer；answerId、dispatchId、conversationId/turnId、provider/model、text、inputRefs、validated citations、usage可缺、时间、confirmed=false、status=candidate/stale、revision；回答不是用户records，也不自动写memory/state |
| 反馈 | feedback | kind:source_ai_feedback；targetId、decision、createdAt、expectedAnswerRevision、affectedCitationIds、correctionRecordId?；helpful不是事实确认 |
| 纠正原文 | records | kind:source_ai_correction，intent:correction，sourceId=conversation，独立turnId，correctsAnswerId、affectedInputRefs；不覆盖来源或原问题；与feedback、受影响derivation/preview失效、revision同事务 |
| 幂等/恢复 | requests | command/version/operation纳入规范operation；question/draft普通请求可存本地正文但不导出；send只存previewId/token对应不透明ID及dispatchId，不复制正文；回放状态查询当前packets，不能回放陈旧“成功”覆盖当前stale |
| 审计 | audit / meta | 仅固定事件、随机引用与时间；不记问题/答案/Key/路径/原文hash；meta在所有新写事务递增 |

每个新JSON对象带schemaVersion=3，旧对象缺版本按旧读取器处理。旧v2写入器不能消费/覆盖v3 kind；148通用snapshot以显式类型投影过滤内部packets、provider、Secret和新对话正文，专用分页读才返回当前会话。旧147文件不改；保留老分支的合成回归，明确记录148新投影差异。JSON语义改变仍是存储合同改变，不因没有ALTER TABLE而免审批。

使用typed Repository Port（ConversationRepository、PreviewRepository、FeedbackRepository），由Application界定跨对象事务；表名/SQL只留Adapter。现有内部通用put不是新Application公共接口。禁止复制成第二memory库、把所有来源加载进snapshot或把模型建议写成确认事实。

### 真实库的拟打开方式

唯一已有业务库字面值 `/Users/xxe/Documents/LifeOS-Source-Pilot-1/capture.sqlite`，包括其SQLite必要`-journal/-wal/-shm`副文件；当前仅写在方案，不探测。用户批准148本地读写范围并在App点击“打开已有本地会话”后，单独`open_existing_for_conversation`验证既有147所有权marker及FD边界，使用READ_WRITE|NOFOLLOW且**无CREATE**，不调用repository::open、source_store::init、source_api::resume或worker。检查上述必要表、索引、JSON兼容性/版本元信息；缺库/合同不符返回source_database_missing/store_contract_mismatch，无DDL、无备份复制、无marker补造。检查结果只呈现固定非内容码。

确认单还须批准复用147输出根所有权的显式委托：接受准确147 marker，不能修改它或将目录冒充148新根。实现148编译profile绑定该委托，运行时root/env覆盖继续拒绝。建议`p3-148-session.lock`只防遵守该锁的多个148实例同时运行；旧147不遵守此锁，不能据此证明跨版本互斥或自动阻止147重开。用户先关闭147、在148使用期间不重开147是操作前提，仍是未自动强制的限制，不保证跨版本并发安全。锁/副文件名纳入真实接线合同，不接受任意路径；不为此修改147或扩大进程探测，现阶段不读取进程或锁。

来源查询只读取已导入source_segments/records/source_files/connectors/grants；不访问Obsidian源目录、缓存原件或触发刷新。引用打开复用已有分段详情API，不打开外部编辑器/文件。来源有效性按**本地已知版本**判断；未重新扫描无法保证磁盘原文没有改变，必须显示“已导入版本”。外部文件变化发现属于后续明确授权，不伪称实时同步。

148真实模式的v1 source读分支也必须改由`open_existing_for_conversation`接线，跳过source_api::dispatch当前238–240行的初始化DDL；详情分页cursor可写已有cursor表，但缺任何所需表只报合同不符。暂停/取消/断开仍由既有事务语义处理且不得启动worker。保留API签名不意味着可以复用会隐式初始化/扫描的整个dispatch函数。

同turn跨request重放：若question已存在且与绑定已committed草稿的会话、turn、revision、原文完全一致，返回同questionId；若任一不同返回turn_conflict。不依赖SQLite唯一键错误伪装成通用数据库错误，也不把新requestId当作另一次保存。旧v2三条活跃状态计数须排除新question/correction kind；这是148适配器显式兼容性差异，旧147实现不改。

### 凭据确需独立受限存储，但不是第二对话库

推荐唯一新文件（待批准）`/Users/xxe/Documents/LifeOS-Source-Pilot-1/p3-148-provider.sqlite`及其SQLite副文件。理由：避免凭据落入drafts通用snapshot、requests正文回执或业务库导出路径；不迁移旧库，也不读144/145凭据表。业务库无新表；新provider库新增2表，只有固定profile：

```sql
CREATE TABLE provider_profile (
  id TEXT PRIMARY KEY CHECK(id='deepseek-default'),
  revision INTEGER NOT NULL CHECK(revision>=1),
  credential_revision INTEGER NOT NULL CHECK(credential_revision>=0),
  config_json TEXT NOT NULL CHECK(json_valid(config_json)),
  envelope_json TEXT CHECK(envelope_json IS NULL OR json_valid(envelope_json))
);
CREATE TABLE provider_operations (
  id TEXT PRIMARY KEY,
  operation TEXT NOT NULL,
  state TEXT NOT NULL,
  metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json))
);
```

config_json封闭字段：schemaVersion=1、enabled、modelId?、testReceiptId?、testedCredentialRevision?、models数组、updatedAt。envelope_json封闭字段：algorithm、version、ciphertext/nonce/tag（base64且解码长度校验）、keyReference、maskedTail（末4字符）、aadVersion=1。operation.metadata仅profileId、expected/new revision、newReference?、oldReference?、testReceiptId?、模型列表、固定结果码与时间；**不得存apiKey、Secret hash或请求原文**。operation枚举replace/delete/test/select/enable，状态prepared/committed/cleanup_pending/failed/outcome_unknown，由typed Adapter校验。

新库文件0600、目录维持0700、相对FD排他创建，未知已存文件不接管。数据库和OS Keychain不具备分布式原子事务，使用03的显式操作日志恢复。问题/片段/答案仍是未加密业务SQLite中的用户数据，只有API Key为AES-GCM密文，不能宣传整库加密。

provider_operations.operation补充拟`recover`，metadata增加可选`recoveryOperationIds:ID[]`（仅本库待恢复操作ID，无秘密或外部引用输入）；与01的recover_credentials一同批准。启动不运行OS恢复，用户激活本地存储后的读取也只展示待处理元数据；OS恢复仅由03所列用户明确恢复/保存/删除动作触发。

## 未知与决策

真实库是否具备固定代码预期结构、marker是否匹配、是否有旧App写入、真实来源量/质量均Unknown；本轮不能验证。推荐先用合成生成的“147结构库”证明无DDL打开与恢复，禁止复制真实DB做夹具。若真实接线后结构不符，停在同任务门禁，PM展示必要变化，不自动迁移/备份。新provider库2表、v3 JSON语义、147根委托和锁文件须一起批准。
