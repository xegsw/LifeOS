# P3-156 既有能力映射与缺口

2026-09-10，工程阶段事实；非PM验收。映射范围是任务指定的155完整166文件候选及直接架构/IA输入，不代表全仓所有历史版本。

| 能力 | 现有落点 | 本轮复用与缺口 |
|---|---|---|
| Action领域 | 架构V1.0第3/5节已有Action与ActionRepository候选语义；166文件候选未找到产品Action实体/仓储接线 | 不能宣称方向新增，也不能把未接线当已实现；需要明确Action领域DTO与版本历史协议 |
| 草稿与提交 | src/health_conversation_host.rs Draft、Prepare、Commit及draft/prepare/commit | 复用原始表达、draft revision、turnId；现有Commit只接受state/clarification，没有行动操作/目标/expectedVersion |
| 事务与重复 | 同文件tx，requests/meta/audit | 复用请求ID+规范payload幂等事务；同ID不同payload拒绝；还须turn级重复约束 |
| Feedback | 同文件decide；application/core.ts relevantFeedback | 当前实际v4是clarification_decision，不是行动反馈；新增kind属于语义协议变更，不借JSON灵活性隐瞒 |
| Context/依据 | application/health_context.ts；host allowed、prepare与snapshot | 复用source identity/version/authGeneration与失效检查；行动生命周期与依据有效性分离 |
| 恢复 | application/controlled_conversation.ts ControlledFlow | 继承154读恢复不重发、草稿失败、迟到响应隔离；行动更新需同等级保护 |
| 持久层 | 同一conversation.sqlite；records等9张JSON表及requests/meta/audit | 无独立Action表；拟复用原库追加事件，不新增第二库，不迁移真实库 |
| IPC | src/main.rs固定14命令；host_gateway.rs实际路由 | get_today目前是健康reader，不能悄悄改为行动入口；通过现有get_context_recovery新增版本操作提案 |
| Today | application/health_ui.ts；IA第5节 | 目前空态问候与聊天入口；在原布局最多一个已确认Focus，依据按需展开，无操作按钮或新导航 |
| 模型 | HealthModelPort OfflineA/OfflineB及ModelPort | 解析输出只作候选；任何模型都不拥有Repository或执行权限 |

apple_import中的enum Action是导入命令枚举，旧ui.ts的data-action是UI事件属性，都不是产品Action仓储。架构要求一对象一Repository、语义DTO、TS Domain/Application；不得把新增业务整体塞入Rust或UI直连SQL。现有records/states的健康短期值合同不得复用成行动状态。

已核对155父Manifest315文件、切换增量14文件、候选166文件的每个hash；复制后的candidate未修改、未执行。来源是FINAL_MANIFEST与real-bundle元数据，未探测真实App路径或二进制。完整Shell/Settings/Provider/来源/健康/会话基线保留。模型、DB、App、视觉测试均尚未执行。
