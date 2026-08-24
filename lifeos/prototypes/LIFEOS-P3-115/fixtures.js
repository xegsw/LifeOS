/*
 * P3-115 fixed synthetic fixture. This file is intentionally local, static and
 * non-sensitive. It is not a runtime data source and does not persist input.
 */
window.LIFEOS_FIXTURE = {
  fixtureId: "P3-115-SYN-001",
  label: "仅用于原型的固定合成情境",
  person: { name: "你", date: "2026 年 8 月 24 日 · 周一" },
  domains: {
    work: {
      source: "SRC-SYN-WORK-001",
      artifact: "ART-SYN-WORK-001@v1",
      context: "产品演示准备",
      facts: ["10:00–16:00 有两段 60 分钟准备", "今天工作负荷：高"],
    },
    health: {
      source: "SRC-SYN-HEALTH-001",
      artifact: "ART-SYN-HEALTH-001@v1",
      facts: ["睡眠：5.5 小时", "自报疲劳：7/10", "已确认限制：避免跳跃／冲击", "18:30 有 20 分钟"],
    },
  },
  question: {
    id: "Q-SYN-001@v1",
    text: "今天的膝部不适是否比已确认限制明显加重，或出现无法承重、明显肿胀、受伤后恶化？",
    threshold: "只有回答会改变健康建议是否出现与安全分类，因此今天只问这一题。",
  },
  workAdvice: {
    id: "ADV-SYN-WORK-001@v1",
    text: "在第一段演示准备前，花 5 分钟写下“观众离开时要记住什么”。",
    why: "高工作负荷与两个固定准备时段都在今天有效；这一步只帮助收束表达，不替你安排或执行。",
    certainty: "中等确定性",
  },
  healthAdvice: {
    id: "ADV-SYN-HEALTH-001@v1",
    text: "如你自觉舒适，可选择最多 10 分钟低强度、非冲击的熟悉恢复活动。",
    modified: "5 分钟熟悉的轻柔恢复动作",
    safety: "不做跳跃或跑步；出现不适立即停止。它不是诊断、治疗或训练处方。",
  },
  memoryCandidate: {
    id: "MEM-CAND-SYN-001@v1",
    text: "在高工作负荷且本人报告疲劳时，你有时更倾向短、熟悉、低冲击的恢复活动。",
    scope: "仅此合成情境／仅当日；待你确认；可拒绝或撤销。",
  },
};
