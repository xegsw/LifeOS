# LIFEOS-P3-073｜基础导出授权沙盒能力包全新隔离独立复评

## 授权与安全语境

LifeOS 为用户本人拥有并授权维护的本地项目。本任务仅在本地工作区、P3-072 授权复跑只读资产和合成测试数据内进行防御性代码审查与回归验证；不涉及外部目标、未授权访问、真实凭据、网络扫描、真实攻击、持久化、数据获取或安全控制规避。相关术语仅用于本项目内部缺陷验证，不扩大范围。

## 范围与模型

- 状态：Evidence Rework Authorized（D-0306）。新建隔离 Codex 独立评审会话，`gpt-5.6-terra` + `xhigh`；不得降级。后备仅 `gpt-5.5` + `xhigh`，须 PM 明确记录不可用原因；路径／写入／原子性／授权链用例禁止降级。
- 最小启动包加 P3-072 任务卡、授权复跑交付物、PM Review、R-0040 与相关 Gate 2/3/4；只读 `lifeos/engineering/LIFEOS-P3-072/authorized_rerun/`、P3-072 旧提交及 PM Evidence。
- 新写独立 runner，只在临时副本运行；不得导入、调用或复制授权复跑测试，不得生成临时导出文件。核验 D-0302 授权链、旧资产保留、当前 hash、默认不写、精确确认／token／状态变化阻断、来源／版本／冲突／撤回／tombstone／未知、单次语义、路径逃逸／覆盖、原子失败清理、审计与关闭态。D-0306 Evidence Rework 必须将 runner 源码、逐项结构化结果、hash 与可复跑说明保留在 `lifeos/reviews/LIFEOS-P3-073/evidence/authorized_rerun/`；旧 P3-073 Evidence 只读保留。

## 不可越界与交付

不得写真实文件或路径、Vault、Tauri/IPC、真实 DB、云、同步、多设备、L3 或外部用户；不关闭 R-0040、不冻结、不恢复基线、不进入 Stage 4。输出独立 Review、Evidence Manifest、结构化结果与交付物。Pass 仅作 P3-072 合成沙盒能力包的 PM／用户输入。
