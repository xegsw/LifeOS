# P3-148 独立合成安全评审合同 / ABF v1

## 启动材料补录 S01（不改变候选和验收）

PM补足遗漏的定向读取清单，基准目录均为 `/Users/xxe/.codex/worktrees/b3f6/No.2/`：

- `lifeos/CURRENT_STATUS.md` 全文（旧144指针只作历史索引，当前分派以本卡及PM工程接收记录为准）。
- `lifeos/PM_OPERATING_MODEL.md` 第80–156行（授权与隔离/复用）、449–482行（角色与独立评审）、601–612行（分级）、633–692行（状态与可恢复执行）。
- `lifeos/ROLE_MATRIX.md` 第5–73行（角色和PM）、91–143行（数据/AI安全/技术）、188–EOF（分派/交付）。
- `lifeos/STAGE_GATES.md` 第5–35行（独立要求）、60–130行（数据/权限/技术Gate）、245–EOF（Stage4限制及任务/例外）；不据此开展Stage准入。
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`、`lifeos/templates/EXECUTION_CHECKPOINT_TEMPLATE.json` 全文；原卡列INDEPENDENT_REVIEW_TEMPLATE亦全文。

上述均是治理/模板，不是候选接触；允许读取。原seal及test_design保持原样，新增S01补录与hash，记录候选接触仍为0后继续同次评审，不重做原seal或开新评审。

平台限制范围：已知历史对象为P3-147独立Delta复评（IR-P0-147-001之后的安全复评），涉及源文件/附件路径逃逸、symlink/TOCTOU替换与外链目标安全测试。PM没有平台内部逐测试判定ID，不能虚构精确名单。保守排除全部P3-147旧runner、其迁移/改名版、文件/目录链接逃逸与竞态替换、SSRF/重定向/外链攻击，以及live WebView负面注入。本次仅按本卡自写P3-148普通合成接口/内存Port/事务状态/预算/重启测试，禁止把排除项重包装。排除不意味着风险解决；涉及断言用源码及明确合规证据评估，确实无法满足就列限制/Unknown，不冒充Pass。不存在“必须先得到平台内部名单才能读取普通候选代码”的新增门禁。

PM 2026-09-08 固定本次评审依据；仅验收依据固定，不是产品/架构冻结。用户已批准完整P3-148及继续评审，L3新增存储/凭据/网络边界触发独立检查。不是新产品任务。

## 输入与身份

候选及工程包唯一只读根 `/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-148/`。其FINAL_MANIFEST.json SHA256为 `3a4ee14faf9521664d64c0eb01437300c2481a9752766fe0b16ab188bc300bb2`，363文件；候选声明摘要 `22123533bb92bde530b01b54be9065a113d1dbd7f73a580799dde0db3c8dac56`。PM已运行清单校验，不是独立证据。只读主报告 `/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/deliverables/LIFEOS-P3-148_source_backed_ai_conversation.md`。

验收权威：包内contract-inputs/01至05设计、E01/E02/E03-task-card.md的增量（后增量优先），其hash通过固定Manifest校验。T01–T25原有限断言不得降低；CONTRACT_ASSERTION_MAP、E02_IMPLEMENTATION、E03_IMPLEMENTATION只作工程声明，独立判断不得以Covered替代验证。

## 独立性与写范围

全新评审执行上下文，不参与工程；先读取本卡及治理，自己写test_design.md、allowlist、禁止目标声明和precontact seal并hash，再接触候选或工程资产（包括枚举）。输出唯一 `/Users/xxe/.codex/worktrees/5ed8/No.2/lifeos/reviews/LIFEOS-P3-148/independent-review/`；全新合成运行根唯一 `/private/tmp/lifeos-p3-148-independent-review-v1`。不接触任何旧运行根，不复用工程PID/DB/二进制/测试runner作独立证据。若唯一新根已存在不覆盖不清理，报告冲突。

预接触前可读b3f6根AGENTS.md、ACCEPTANCE_GOVERNANCE及CI_CD_GOVERNANCE相关授权/独立性/恢复规则和INDEPENDENT_REVIEW_TEMPLATE；只读模板不算候选接触。预接触后按profile规定创建0700新根与0600准确marker，复制固定候选至该根；使用independent-review编译profile、已有工具链离线构建，target/TMP均在新根，不下载依赖。不得修改候选；自写验证和可丢弃合成反例与正候选分开。

## 必须验证的有限矩阵

R01 固定清单/来源一致及预接触独立性；R02 严格DTO/Raw入口与Json旁路拒绝（原语测试和live正常调用分开，不强制未授权live负面注入）；R03 草稿幂等/失败/重启/分页隔离；R04 相关检索、权限/版本/预算及预览发送绑定；R05 重复发送/并发、超时unknown、撤权前后、无后台重发；R06 引用/纠正/反馈依赖与重启；R07 模拟CredentialPort生命周期、密文持久化、Secret无日志/回执、显式恢复；R08 无旧库DDL/seed/扫描及新provider库有限创建；R09 两合成模式拒绝真实Transport/OS能力，真实接线只读静态核对；R10 独立actual Tauri正常对话/Settings、700×760与桌面请求1280×1024（受工作区限制实际尺寸单列），精确launch PID→窗口→WebArea→截图几何；R11 历史/当前证据分离与终局完整性。

逐项映射T01–T25，使用自有纯虚构fixture、正负路径与必要有界进程内mutation，不复制工程测试作为独立runner。只检测用户自有代码；禁止执行或重新包装此前平台拒绝的测试，不更换执行方绕过平台。某断言无合规方式验证，明确Not Implemented/Unknown及原因，不编造Pass。无需穷举无限线程/机器指令组合。

## 禁止与恢复

禁止真实profile启动、真实DB/来源/凭据/OS Keychain/Provider/网络的任何访问、探测、hash；禁止Vault、所有Pilot和工程旧临时根；不修改工程、PM账本或冻结/风险/Stage，不push/merge，不转派。读取候选内真实路径常量仅作源码核对，不触达目标。无系统锁屏/显示设置修改。

锁屏/AX暂不可用写checkpoint并Paused — Resumable，候选和合同不变从受影响阶段恢复；错误截图保全排除再补取，不重做无关阶段。候选缺陷回报PM在原工程Closure修复；只读输入污染/禁止接触立即停止如实记录。清理仅本次新根且准确marker/无symlink/已停所有自有写入者；不可验证则保留，禁止广泛删除。

## 交付与结论

独立报告、review-owned runner及结果、逐行矩阵、checkpoint、非自指FINAL_MANIFEST和复核说明。五类计数逐项给理由；Pass需所有本评审要求有证据，无P0/P1/Unknown/Not Implemented未解项。仅合成离线安全结论，不是实际OS安全验证、真实调用成功、PM最终Accepted、风险关闭或Stage准入。不要把“不接真实系统”的范围限定计作失败，也不得把它写成真实通过。
