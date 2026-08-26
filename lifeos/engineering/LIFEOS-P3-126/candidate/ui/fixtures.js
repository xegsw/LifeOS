/* Fixed, non-sensitive synthetic fixture. It is rendered only in in-memory UI state. */
window.LIFEOS_FIXTURE = Object.freeze({
  notice: "这是完全本地、固定合成内容的原型演示；不会保存、发送或调用模型。",
  person: {
    name: "你",
    phase: "正在把工作节奏和恢复感重新放回同一张生活地图里。",
    currentSelf: "这周的工作推进感稳定，但恢复时间需要被认真对待。",
  },
  focus: {
    title: "为发布页改版确定下一步",
    context: "LifeOS 产品开发 · Work / Project",
    why: "你已确认这周要完成信息层级梳理；最近两条工作记录都指向同一个待决问题。",
    evidence: "用户确认的工作安排 · 2 条近期原始记录",
  },
  contexts: [
    { id: "launch", title: "LifeOS 产品开发", type: "Project", domain: "Work", state: "active", now: "发布页的信息层级正在收口。", next: "确认首屏叙事后，整理下一版。" },
    { id: "recovery", title: "训练恢复", type: "Period / Program", domain: "Health", state: "watching", now: "连续训练后的恢复感正在被持续关注。", next: "暂不生成训练调整；先记录下一次主观感受。" },
    { id: "sleep", title: "最近睡眠", type: "Observed Context", domain: "Health", state: "watching", now: "有两次较晚结束工作的记录。", next: "证据不足，不作因果判断。" },
    { id: "move", title: "搬家准备", type: "Life Event", domain: "Other Life Data", state: "past", now: "已结束。", next: "没有待确认的下一步。" },
  ],
  memory: [
    { id: "m1", kind: "用户原文", title: "“发布页需要先让人知道它在帮谁。”", source: "2026-08-25 · 手动记录", status: "原文保留", scope: "Work / LifeOS 产品开发" },
    { id: "m2", kind: "确认事实", title: "你已确认本周优先完成首屏信息层级。", source: "用户确认 · 2026-08-25", status: "已确认", scope: "Work / LifeOS 产品开发" },
    { id: "m3", kind: "AI Observation", title: "两条近期工作记录都在讨论首屏叙事。", source: "固定合成推导 · 2 条输入", status: "待你核对", scope: "Work" },
    { id: "m4", kind: "AI Inference", title: "首屏叙事可能是当前最小阻塞点。", source: "证据有限 · 不是确认事实", status: "待你核对", scope: "Work" },
    { id: "m5", kind: "Decision", title: "先完成信息层级，再讨论视觉细节。", source: "你已确认 · 2026-08-25", status: "已确认", scope: "Work / LifeOS 产品开发" },
    { id: "m6", kind: "Derivation", title: "Today's Focus 的候选依据", source: "m1 + m2 + m3", status: "可回溯", scope: "Work" },
    { id: "m7", kind: "External Source", title: "发布页草稿（合成来源指针）", source: "来源未读取 · 仅作为指针", status: "来源可见", scope: "Work" },
  ],
  captureText: "明天先把发布页的第一屏文字读一遍，再决定是否继续做视觉细节。",
});
