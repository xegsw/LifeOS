# LIFEOS-P3-072｜基础导出受控沙盒能力包

## 授权与安全语境

LifeOS 为用户本人拥有并授权维护的本地项目。本任务仅限本卡指定的隔离工程目录、临时沙盒路径和合成测试数据，用于防御性软件工程、缺陷修复与本地回归验证；不涉及外部目标、未授权访问、真实凭据、网络扫描、真实攻击、持久化、数据获取或安全控制规避。“绕过／攻击／权限边界”等术语仅用于本项目内部防御性缺陷验证，不扩大任何范围。

## 状态、模型与范围

- 状态：Execution Authorized（D-0302）；本卡原先未授权提交及其 PM Evidence 必须只读保留，不得作为本次可采纳结果。授权复跑只能写入 `lifeos/engineering/LIFEOS-P3-072/authorized_rerun/`、对应新 Evidence 与授权复跑交付物，且必须在全新隔离 Codex 工程会话完成。
- 推荐：Codex，`gpt-5.6-terra` + `xhigh`；理由：文件边界、原子失败与反例矩阵需要工程级核验。允许降级模型：无；禁止降级：任何路径／写入／授权／原子性用例；必须升级条件：发现 P0/P1、Evidence 冲突或边界扩展；后备：`gpt-5.5` + `xhigh`，仅在 PM 明确记录原因后使用。
- 直接输入：`lifeos/CURRENT_STATUS.md`、P3-070/P3-071 交付物、Review、Evidence 与 R-0040；定向读取 `PM_OPERATING_MODEL.md` 的受控能力包／验收／任务下发规则、`ROLE_MATRIX.md`、`STAGE_GATES.md` 相关 Gate 2/3/4。
- 可写：仅 `lifeos/engineering/LIFEOS-P3-072/authorized_rerun/`、其新 Evidence 与授权复跑交付物；P3-070/P3-071、P3-072 原先未授权提交及其 PM Evidence 均只读。只可在每次运行新建的系统临时目录内生成合成导出文件，运行结束须保留所需 Evidence、不得触达用户路径、Vault 或现有文件。

## 能力包完成定义

在同一隔离目录内完成合成记录的预览→精确确认→一次性临时沙盒文件输出→内容／来源／身份 hash 回执；实现、回归、必要反例、Evidence 与文案可包内完成。默认不写；目标仅能是新建临时沙盒；来源／版本／范围／确认／冲突／撤回／tombstone／未知、越界路径、重名／覆盖、写入失败与半成品均须 fail-closed、审计且不留可见输出。必须显式证明网络、Tauri/IPC、Vault、真实 DB、云、同步、多设备、L3、外部用户与任何非临时路径均关闭。

## 不可混入与停止

不得连接或操作真实数据、真实用户路径、Vault、Tauri/IPC、云或第三方服务；不得关闭 R-0040、冻结资产、恢复工程基线或进入 Stage 4。任何 P0/P1、Unknown／Not Implemented、Evidence/hash 冲突、路径逃逸、非原子写入或范围扩展立即停止并回报 PM。完成后须一次 PM 验收、一次全新隔离独立复评和一次用户采纳；风险关闭、真实能力启用或阶段决定另立任务。

## 交付

输出 `lifeos/deliverables/LIFEOS-P3-072_basic_export_controlled_sandbox_capability_package_authorized_rerun.md`、授权复跑工程 Evidence／Manifest、本地预检（不可用则记录）及会话简报；不得更新 PM 账本或创建后续任务。
