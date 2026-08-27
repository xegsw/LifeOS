(() => {
  "use strict";

  const fixture = window.LIFEOS_FIXTURE;
  const state = {
    page: "today",
    todayMode: "normal",
    contextFilter: "active",
    selectedContext: "launch",
    memoryFilter: "",
    memoryDetail: "m6",
    aiOpen: false,
    aiQuestion: "",
    healthIncluded: true,
    modal: null,
    reducedMotion: false,
    candidate: { observation: "待核对", action: "候选", decision: "候选" },
    captureText: fixture.captureText,
    receipt: "",
  };

  const app = document.getElementById("app");
  const esc = (value) => String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
  const context = () => fixture.contexts.find((item) => item.id === state.selectedContext) || fixture.contexts[0];
  const icon = (name) => {
    const paths = {
      today: '<path d="M4 11.5 12 4l8 7.5"/><path d="M6.5 10v8h11v-8"/><path d="M10 18v-4h4v4"/>',
      me: '<circle cx="12" cy="8" r="3.2"/><path d="M5.5 20c.8-4 3-6 6.5-6s5.7 2 6.5 6"/>',
      contexts: '<path d="M4.5 6.5h15v11h-15z"/><path d="M4.5 10h15"/><path d="M8 3.8v5.4M16 3.8v5.4"/>',
      memory: '<path d="M5.2 5.7A3.7 3.7 0 0 1 8.8 4H19v15H8.8a3.7 3.7 0 0 0-3.6 2.5z"/><path d="M5.2 5.7V21.5"/><path d="M8.5 8h7M8.5 11h7"/>',
      settings: '<circle cx="12" cy="12" r="3"/><path d="M19 12a7.1 7.1 0 0 0-.1-1.2l2-1.5-2-3.4-2.4 1a7.7 7.7 0 0 0-2-1.2L14.2 3h-4.1l-.4 2.6a7.7 7.7 0 0 0-2 1.2l-2.4-1-2 3.4 2 1.5A7.1 7.1 0 0 0 5 12c0 .4 0 .8.1 1.2l-2 1.5 2 3.4 2.4-1a7.7 7.7 0 0 0 2 1.2l.4 2.6h4.1l.4-2.6a7.7 7.7 0 0 0 2-1.2l2.4 1 2-3.4-2-1.5c.1-.4.1-.8.1-1.2z"/>',
      target: '<circle cx="12" cy="12" r="7.5"/><circle cx="12" cy="12" r="3.3"/><path d="m12 2.5 1.2 2.2M21.5 12l-2.2 1.2M12 21.5l-1.2-2.2M2.5 12l2.2-1.2"/>',
      calendar: '<rect x="4.5" y="5.5" width="15" height="14" rx="2"/><path d="M8 3.5v4M16 3.5v4M4.5 10h15"/>',
      sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2.4M12 19.6V22M2 12h2.4M19.6 12H22M4.9 4.9l1.7 1.7M17.4 17.4l1.7 1.7M19.1 4.9l-1.7 1.7M6.6 17.4l-1.7 1.7"/>',
      check: '<path d="m5 12.5 4.2 4.2L19.5 6.5"/>',
      pulse: '<path d="M3 12h4l2.2-5 3.5 10 2.1-5H21"/>',
      heart: '<path d="M20 8.8c0 5-8 10.2-8 10.2S4 13.8 4 8.8C4 6.1 6 4.5 8.2 4.5c1.5 0 2.9.8 3.8 2 1-1.2 2.3-2 3.8-2C18 4.5 20 6.1 20 8.8z"/>',
      clock: '<circle cx="12" cy="12" r="8"/><path d="M12 7v5l3.2 2"/>',
      spark: '<path d="m12 2 1.5 6.5L20 10l-6.5 1.5L12 18l-1.5-6.5L4 10l6.5-1.5z"/><path d="m19 17 .5 2 .5-2 2-.5-2-.5-.5-2-.5 2-2 .5z"/>',
      arrow: '<path d="M5 12h13"/><path d="m13 6 6 6-6 6"/>',
      close: '<path d="m6 6 12 12M18 6 6 18"/>',
      plus: '<path d="M12 5v14M5 12h14"/>',
    };
    return `<svg class="rail-icon" aria-hidden="true" viewBox="0 0 24 24">${paths[name] || paths.spark}</svg>`;
  };
  const button = (label, action, classes = "button") => `<button class="${classes}" type="button" data-action="${action}">${label}</button>`;
  const badge = (label, type = "") => `<span class="identity ${type}">${esc(label)}</span>`;
  const shellChrome = () => `<div class="page-chrome"><span>8月25日　周一</span><span class="header-icon" aria-label="固定合成日历提示">${icon("calendar")}</span><button class="header-icon" type="button" data-action="motion" aria-label="切换低动态预览">${icon("sun")}</button><span class="synthetic-mark">固定合成演示 · 非持久化</span></div>`;
  const pageHeader = (eyebrow, title, subhead) => `
    <header class="page-head">
      <div><p class="eyebrow">${eyebrow}</p><h1>${title}</h1><p class="subhead">${subhead}</p></div>
      ${shellChrome()}
    </header>`;
  const compactIcon = (name, tone = "blue") => `<span class="icon-orb ${tone}" aria-hidden="true">${icon(name)}</span>`;
  const more = () => '<span class="quiet-dots" aria-hidden="true">•••</span>';

  function navButton(id, label) {
    return `<button class="rail-button" type="button" data-action="nav:${id}" data-tooltip="${label}" aria-label="${label}" ${state.page === id ? 'aria-current="page"' : ""}>${icon(id)}</button>`;
  }

  function todayPage() {
    const mode = state.todayMode;
    let focus = "";
    let noticed = "";
    if (mode === "normal") {
      focus = `<section class="focus-card reference-focus"><div class="card-chrome"><span class="card-kicker">${compactIcon("target", "blue")}<span>Today's Focus</span></span>${more()}</div><h2 class="focus-title">LifeOS 产品原型</h2><p class="focus-subtitle">把“以人为主体”的首页交互确定下来</p><div class="focus-reason"><strong>为什么现在值得做</strong><ul><li>${compactIcon("check", "blue")}昨天已确定信息架构</li><li>${compactIcon("check", "blue")}当前开发依赖这一步</li><li>${compactIcon("check", "blue")}过去两天没有新的阻断</li></ul></div>${state.receipt ? `<p class="state-receipt">${esc(state.receipt)}</p>` : ""}<div class="actions">${button("继续", "context:launch", "button primary")}${button("查看依据", "why:focus")}</div>${state.showWhy === "focus" ? `<div class="evidence-box"><strong>候选依据</strong><br>${fixture.focus.evidence}。这是固定合成解释，不会生成真实建议。</div>` : ""}</section>`;
      noticed = `<section class="panel reference-card noticed-card"><div class="card-chrome"><span class="card-kicker">${compactIcon("pulse", "lilac")}<span>LifeOS noticed</span></span>${more()}</div><p class="noticed-copy">你最近三天睡眠时间下降，<br>同时下午工作中断增加。<br>暂时没有足够证据判断两者相关。</p><div class="actions compact-actions">${button("看看为什么  →", "why:noticed", "button ghost")}${button("先忽略", "candidate:observation:ignore", "button ghost")}</div>${state.showWhy === "noticed" ? `<div class="evidence-box">依据：两条固定合成时间线记录。没有足够证据判断因果，因此不提供健康建议。</div>` : ""}</section>`;
    } else if (mode === "empty") {
      focus = `<section class="state-empty"><strong>今天没有特别需要处理的事情。</strong><span>这是一种合法状态。你可以先记录一件事，或从已有 Context 回来。</span><div class="actions" style="justify-content:center">${button("查看 Contexts", "nav:contexts")}${button("快速记录", "capture")}</div></section>`;
      noticed = `<section class="panel soft"><span class="section-label">LifeOS noticed</span><p class="quiet">没有需要主动打断你的内容。</p></section>`;
    } else {
      focus = `<section class="state-empty"><strong>现在没有可靠的 Today's Focus。</strong><span>LifeOS 看到了零散变化，但它们不足以支持一个人的整体优先级判断。</span><div class="actions" style="justify-content:center">${button("查看证据缺口", "why:insufficient")}</div>${state.showWhy === "insufficient" ? `<div class="evidence-box">缺口：缺少你已确认的下一步，也缺少足以建立优先级的近期依据。不会为了填充页面生成建议。</div>` : ""}</section>`;
      noticed = `<section class="notice">证据不足：可以继续查看最近记录或自己决定下一步；此状态不会自动创建 Action、Decision 或 Context。</section>`;
    }
    return `<div class="today-page"><header class="today-hero"><div><p class="eyebrow">Today · Person 的此刻</p><h1>早上好。</h1><p class="today-subhead">今天整体比较稳定，有一件事值得优先处理。</p></div><div class="today-chrome"><span>8月25日　周一</span><span class="header-icon" aria-label="固定合成日历提示">${icon("calendar")}</span><button class="header-icon" type="button" data-action="motion" aria-label="切换低动态预览">${icon("sun")}</button><span class="synthetic-mark">固定合成演示 · 非持久化</span></div></header>
      <div class="mode-switch today-mode-switch" aria-label="Today 合成状态" role="group"><button data-action="today:normal" aria-pressed="${mode === "normal"}">正常</button><button data-action="today:empty" aria-pressed="${mode === "empty"}">合法空状态</button><button data-action="today:insufficient" aria-pressed="${mode === "insufficient"}">证据不足</button></div>
      <div class="today-grid"><div class="today-main stack">${focus}<section class="panel reference-card overview-card"><div class="card-chrome"><span class="card-kicker">${compactIcon("sun", "amber")}<span>Day Overview</span></span>${more()}</div><div class="overview-grid"><div>${compactIcon("check", "mint")}<span class="tiny">状态</span><strong>稳定</strong></div><div>${compactIcon("pulse", "blue")}<span class="tiny">精力</span><strong>中等</strong></div><div>${compactIcon("heart", "lilac")}<span class="tiny">心情</span><strong>平静</strong></div></div><p class="overview-note">根据近期记录和数据综合得出　ⓘ<br><span>固定合成摘要，不是评分或诊断。</span></p></section></div><aside class="today-aside stack">${noticed}<section class="panel reference-card schedule-card"><div class="card-chrome"><span class="card-kicker">${compactIcon("calendar", "mint")}<span>Today</span></span>${more()}</div><ul class="schedule-list"><li><i class="blue-dot"></i><time>10:00</time><span>产品讨论</span></li><li><i class="mint-dot"></i><time>15:30</time><span>训练</span></li><li><i class="amber-dot"></i><time>17:00</time><span>提交设计稿</span></li></ul><p class="tiny">仅显示固定合成的已确认安排；不是外部日历。</p></section><section class="panel reference-card recent-card"><div class="card-chrome"><span class="card-kicker">${compactIcon("clock", "blue")}<span>Recent</span></span>${more()}</div><ul class="recent-list"><li><span><i></i>昨天 · LifeOS 架构</span><b>›</b></li><li><span><i></i>昨天 · 训练记录</span><b>›</b></li><li><span><i></i>周日 · 关于产品定位的决定</span><b>›</b></li></ul></section></aside></div></div>`;
  }

  function mePage() {
    return `${pageHeader("Me · Person 的长期视角", "Me", "LifeOS 对你的整体理解与洞察。")}
      <div class="me-reference-stack"><section class="panel me-current-card"><div class="me-orb" aria-hidden="true"></div><div class="me-current-copy"><div class="section-head"><div><span class="section-label">现在的我</span><h2>${fixture.person.currentSelf}</h2></div>${badge("实时更新", "decision")}</div><p>最近主要精力集中在 LifeOS 产品开发，正在梳理核心价值与关键路径。训练保持稳定，有规律地进行力量与有氧；但睡眠连续几天下降，下午容易感到精力不足。</p><div class="actions">${button("想了解更多？直接问我", "ai", "button ghost")}${button("查看理解依据", "memory:m3", "button ghost")}</div></div><aside class="me-ask"><strong>你可以问</strong>${button("我最近状态怎么样？", "ai", "me-question")}${button("你觉得我现在最大的矛盾是什么？", "ai", "me-question")}${button("我接下来应该把精力放在哪里？", "ai", "me-question")}</aside></section>
      <section class="panel me-section"><div class="section-head"><h2>我正在关注</h2>${button("查看全部　→", "nav:contexts", "button ghost")}</div><div class="me-focus-grid"><button type="button" class="me-focus-card" data-action="context:launch">${compactIcon("target", "blue")}<span><strong>LifeOS 产品开发</strong><em>● 进行中</em><p>MVP 核心价值与关键路径定义，搭建产品基础框架。</p><small>当前主 Context</small></span><b>›</b></button><button type="button" class="me-focus-card" data-action="context:recovery">${compactIcon("heart", "mint")}<span><strong>训练恢复</strong><em class="mint-text">● 进行中</em><p>保持力量与有氧训练节奏，提升基础体能与恢复能力。</p><small>持续关注</small></span><b>›</b></button><button type="button" class="me-focus-card" data-action="context:sleep">${compactIcon("clock", "lilac")}<span><strong>最近睡眠</strong><em class="lilac-text">● 持续关注</em><p>连续记录到较晚结束工作的痕迹，暂不推断因果。</p><small>证据有限</small></span><b>›</b></button></div></section>
      <section class="panel me-section"><div class="section-head"><h2>长期视角</h2>${button("全部视角　→", "activation", "button ghost")}</div><div class="me-domain-grid"><article>${compactIcon("target", "blue")}<div><strong>工作视角</strong>${badge("深度智能已启用", "decision")}<p>当前处于产品定义阶段，重点在于明确核心价值、打磨 MVP 路径。</p><div class="soft-tags"><span>趋势稳定</span><span>专注度高</span><span>创造力活跃</span></div></div><b>›</b></article><article>${compactIcon("heart", "mint")}<div><strong>健康视角</strong>${badge("深度智能已启用", "user")}<p>整体训练稳定；睡眠近期下降只被保守记录，不构成诊断或建议。</p><div class="soft-tags"><span>训练稳定</span><span>恢复一般</span><span>睡眠偏低</span></div></div><b>›</b></article></div></section>
      <section class="panel me-section"><div class="section-head"><h2>LifeOS 对我的理解</h2>${button("管理理解　→", "memory:m6", "button ghost")}</div><div class="me-understanding-grid"><button type="button" data-action="memory:m2">${compactIcon("check", "blue")}<span><strong>做重大产品决策时，你倾向先把系统结构想清楚</strong><small>你确认的事实　｜　基于 12 条相关记录</small></span><b>›</b></button><button type="button" data-action="memory:m4">${compactIcon("pulse", "amber")}<span><strong>在高压力状态下，你会通过训练来恢复专注力</strong><small>LifeOS 推断　｜　基于 8 条相关记录</small></span><b>›</b></button><button type="button" data-action="memory:m3">${compactIcon("heart", "lilac")}<span><strong>近期优先级是把 LifeOS MVP 跑通</strong><small>LifeOS Observation　｜　基于 23 条相关记录</small></span><b>›</b></button><button type="button" data-action="memory:m7">${compactIcon("clock", "blue")}<span><strong>你对长期重复的事更容忍度较低</strong><small>尚待确认　｜　需要更多证据</small></span><b>›</b></button></div></section></div>`;
  }

  function contextsPage() {
    const labels = { active: "正在进行", watching: "持续关注", past: "已结束" };
    const rows = fixture.contexts.filter((item) => item.state === state.contextFilter).map((item) => `<button type="button" class="context-row" data-action="context:${item.id}"><span class="context-main">${badge(item.type)}<h3>${esc(item.title)}</h3><span class="context-meta">${esc(item.domain)} · ${labels[item.state]}</span></span><span class="context-arrow" aria-hidden="true">›</span></button>`).join("") || `<div class="state-empty"><strong>这里暂时没有 Context。</strong><span>空状态不等于需要自动创建一个。</span></div>`;
    return `${pageHeader("Contexts · 正在经历的事", "Contexts", "按你和事情的当前关系组织；Project 只是其中一种 Context 类型。")}
      <div class="tabs" role="tablist" aria-label="Context 状态"><button role="tab" aria-selected="${state.contextFilter === "active"}" data-action="contexts:active">正在进行</button><button role="tab" aria-selected="${state.contextFilter === "watching"}" data-action="contexts:watching">持续关注</button><button role="tab" aria-selected="${state.contextFilter === "past"}" data-action="contexts:past">已结束</button></div>
      <section class="stack" style="margin-top:16px">${rows}<section class="panel soft"><div class="section-head"><div><span class="section-label">建议创建</span><h2 style="margin-top:5px">LifeOS 不能静默创建 Context</h2></div>${badge("候选", "inference")}</div><p class="quiet">“近期旅行安排”看起来可能值得成为 Context，但仍需你确认它的名称、范围和状态。</p><div class="actions">${button("查看建议", "suggest-context")}${button("忽略", "dismiss-suggest")}</div></section></section>`;
  }

  function contextDetailPage() {
    const item = context();
    return `${pageHeader(`Context Detail · ${esc(item.domain)}`, esc(item.title), "从现在、已确认的下一步和最近发生的事恢复上下文；Global AI 会透明地继承此 Context。")}
      <div class="two-column"><div class="stack"><section class="panel"><span class="section-label">现在</span><h2 style="margin-top:6px">${esc(item.now)}</h2><p class="quiet">${badge(item.type)} ${badge(item.domain)}</p></section><section class="panel"><div class="section-head"><div><span class="section-label">Next</span><h2 style="margin-top:5px">${esc(item.next)}</h2></div>${badge("确认事实", "user")}</div><div class="actions">${button("确认继续", "candidate:action:confirm", "button primary")}${button("调整下一步", "candidate:action:edit")}</div></section><section class="panel"><span class="section-label">最近发生</span><div class="timeline" style="margin-top:16px"><div class="timeline-item"><strong>你留下了发布页的原文记录</strong><div class="tiny">用户原文 · 今天</div></div><div class="timeline-item"><strong>LifeOS 生成了可核对的 Observation</strong><div class="tiny">AI Observation · 待你核对</div></div><div class="timeline-item"><strong>你确认先做信息层级</strong><div class="tiny">Decision · 已确认</div></div></div></section></div><aside class="stack"><section class="panel"><span class="section-label">LifeOS understands</span><p style="margin:8px 0">首屏叙事是目前可能的最小阻塞点。</p>${badge("AI Inference", "inference")}<div class="actions">${button("查看依据", "memory:m6")}${button("不准确", "candidate:observation:correct")}</div></section><section class="panel"><span class="section-label">Related / Evidence</span><p class="quiet">你可以沿着 Derivation 回到原文、确认事实与来源指针。</p><div class="actions">${button("打开 Evidence", "memory:m6")}${button("问 Global AI", "ai")}</div></section></aside></div>`;
  }

  function memoryPage() {
    const match = state.memoryFilter.trim().toLowerCase();
    const tone = (item) => item.kind.includes("原文") || item.kind.includes("确认") ? "blue" : item.kind.includes("Inference") ? "amber" : item.kind.includes("Observation") ? "lilac" : item.kind === "Decision" ? "mint" : "blue";
    const rows = fixture.memory.filter((item) => !match || `${item.kind} ${item.title} ${item.scope}`.toLowerCase().includes(match)).map((item) => `<button type="button" class="memory-reference-row" data-action="memory:${item.id}">${compactIcon(item.kind.includes("Decision") ? "check" : item.kind.includes("Inference") ? "pulse" : item.kind.includes("Source") ? "clock" : "memory", tone(item))}<span><strong>${esc(item.title)}</strong><p>${esc(item.source)}</p></span><span class="memory-row-meta">${badge(item.kind, item.kind.includes("确认") ? "user" : item.kind.includes("Inference") ? "inference" : item.kind.includes("Observation") ? "observation" : item.kind === "Decision" ? "decision" : "derivation")}<small>${esc(item.status)}</small></span><b>›</b></button>`).join("") || `<div class="state-empty"><strong>没有匹配的长期记忆。</strong><span>搜索不会伪造一条结果。</span></div>`;
    return `${pageHeader("Memory · Evidence Browser", "Memory", "你的重要经历、经验和知识，沉淀为可随时调用的记忆。")}
      <section class="panel memory-control"><div class="memory-toolbar"><span class="memory-search-icon">${icon("memory")}</span><input data-memory-search type="search" aria-label="筛选长期记忆" value="${esc(state.memoryFilter)}" placeholder="搜索记忆、主题或来源…" />${button("清除", "clear-memory", "button ghost")}</div><div class="memory-filter-row" aria-label="记忆身份提示"><button type="button" data-action="clear-memory">全部</button><button type="button" data-action="memory-kind:用户原文">用户原文</button><button type="button" data-action="memory-kind:确认事实">确认事实</button><button type="button" data-action="memory-kind:AI Observation">AI Observation</button><button type="button" data-action="memory-kind:AI Inference">AI Inference</button><button type="button" data-action="memory-kind:Decision">Decision</button></div></section>
      <div class="memory-reference-grid"><section class="panel memory-list-card"><div class="section-head"><div><h2>最近记忆</h2><p class="quiet">按身份、来源与适用范围恢复，不把记忆简化为文件夹。</p></div>${button("查看全部　→", "clear-memory", "button ghost")}</div><div class="memory-reference-list">${rows}</div></section><section class="panel memory-network-card"><div class="section-head"><div><h2>记忆关系</h2><p class="quiet">围绕 Person、Context 与 Evidence 的可回溯关系。</p></div>${button("查看依据", "memory:m6", "button ghost")}</div><div class="memory-network" aria-label="固定合成记忆关系图"><span class="network-node main">LifeOS<br>MVP</span><span class="network-node n1">用户原文</span><span class="network-node n2">确认事实</span><span class="network-node n3">AI 观察</span><span class="network-node n4">Decision</span><span class="network-node n5">Derivation</span></div><div class="network-legend"><span><i class="blue-dot"></i>用户与确认</span><span><i class="mint-dot"></i>Decision</span><span><i class="lilac-dot"></i>Observation</span><span><i class="amber-dot"></i>推断与依据</span></div></section></div>
      <section class="panel memory-revisit"><div class="section-head"><div><h2>${compactIcon("spark", "blue")} 智能回顾</h2><p class="quiet">基于固定合成记忆的回顾候选，均可查看依据。</p></div><span class="tiny">仅本地演示</span></div><div class="revisit-grid"><button type="button" data-action="memory:m5">${compactIcon("check", "blue")}<span>回顾 7 月的产品决策，有助于推进当前 MVP 规划</span><b>›</b></button><button type="button" data-action="memory:m3">${compactIcon("heart", "mint")}<span>训练恢复上的经验，可能和当前状态有关</span><b>›</b></button><button type="button" data-action="memory:m4">${compactIcon("pulse", "lilac")}<span>关于专注力的知识，在最近的工作中很相关</span><b>›</b></button></div></section>`;
  }

  function memoryDetailPage() {
    const item = fixture.memory.find((entry) => entry.id === state.memoryDetail) || fixture.memory[5];
    const broken = item.id === "m7";
    return `${pageHeader("Memory Detail · 可追溯性", esc(item.title), "重要理解应当能回到 Derivation、Evidence 与 Source；断链和证据不足会明确披露。")}
      <div class="two-column"><section class="stack"><section class="panel"><div class="section-head"><div>${badge(item.kind, item.kind.includes("Inference") ? "inference" : item.kind.includes("Observation") ? "observation" : "derivation")}<h2 style="margin-top:10px">${esc(item.title)}</h2></div>${badge(item.status, item.status.includes("确认") ? "user" : "")}</div><p class="quiet">来源：${esc(item.source)}<br>适用范围：${esc(item.scope)}</p><div class="actions">${button("准确", "candidate:observation:confirm", "button primary")}${button("不准确", "candidate:observation:correct")}${button("纠正", "capture")}</div></section><section class="panel"><span class="section-label">为什么 LifeOS 这样理解</span><div class="trace" style="margin-top:16px"><div class="trace-step"><span class="trace-num">1</span><div><strong>AI Understanding</strong><p>“首屏叙事可能是当前最小阻塞点。”</p></div></div><div class="trace-step"><span class="trace-num">2</span><div><strong>Derivation</strong><p>固定合成推导，声明输入、范围和待核对状态。</p></div></div><div class="trace-step"><span class="trace-num">3</span><div><strong>Evidence</strong><p>用户原文与已确认的工作安排；不是外部模型输出。</p></div></div><div class="trace-step"><span class="trace-num">4</span><div><strong>Source / Artifact</strong><p>${broken ? "来源指针目前不可达；不能把它说成最新或完整。" : "可回到固定合成来源指针和原始记录。"}</p></div></div></div></section></section><aside class="stack"><section class="panel"><span class="section-label">身份与使用范围</span><p class="quiet">每一层都有独立身份。确认、反馈、纠正与撤回不会改写原文或来源。</p></section>${broken ? `<section class="notice danger"><strong>断链披露</strong><br>这个来源指针不可达。LifeOS 不会据此生成可靠建议。</section>` : `<section class="notice mint"><strong>证据可回溯</strong><br>可以继续沿链核对，但仍须由你决定是否接受候选。</section>`}</aside></div>`;
  }

  function settingsPage() {
    return `${pageHeader("Settings · 辅助入口", "原型边界", "设置不是一级工作区：此处只披露原型当前的本地合成、非持久化边界。")}
      <section class="panel"><span class="section-label">Motion</span><h2 style="margin-top:5px">低动态预览</h2><p class="quiet">此开关只改变当前原型的视觉过渡，不写入设备或系统设置。</p><div class="actions">${button(state.reducedMotion ? "已启用低动态" : "启用低动态", "motion", state.reducedMotion ? "button primary" : "button")}</div></section><section class="panel"><span class="section-label">Synthetic boundary</span><p class="quiet">无网络、无远程资源、无 Storage、无真实模型、无数据库、无文件接口。关闭页面会丢弃所有本地演示状态。</p></section>`;
  }

  function workspacePage() {
    return `<div class="workspace-page workspace-reference"><header class="workspace-top"><div><p class="eyebrow">AI Workspace · 深度展开</p><h1>AI Workspace</h1><p class="subhead">你的全局 AI 工作台，随时与你协作。</p></div>${shellChrome()}</header><div class="workspace-reference-grid"><main class="workspace-center" id="main-content" tabindex="-1"><section class="panel workspace-prompt"><form data-ai-form><div class="workspace-prompt-copy">${compactIcon("spark", "blue")}<input aria-label="问 LifeOS" name="aiPrompt" placeholder="今天想和 LifeOS 一起推进什么？" /></div><div class="workspace-suggestions">${button("总结近况", "ai", "workspace-chip")}${button("理清思路", "ai", "workspace-chip")}${button("制定计划", "ai", "workspace-chip")}${button("分析问题", "ai", "workspace-chip")}${button("头脑风暴", "ai", "workspace-chip")}</div><button class="send workspace-send" type="submit" aria-label="发送并展开 Global AI">↑</button></form></section><section class="panel workspace-recommend"><div class="section-head"><div><h2>为你推荐</h2><p class="quiet">候选工作以 Observation／Inference 身份出现，仍需要你的确认。</p></div>${badge("固定合成", "derivation")}</div><div class="workspace-recommend-list"><article>${compactIcon("memory", "blue")}<span><strong>梳理 LifeOS MVP 下一步的关键任务</strong><p>基于当前进展，拆解核心里程碑和优先级。</p></span>${button("开始", "ai", "button")}</article><article>${compactIcon("pulse", "mint")}<span><strong>分析最近训练与睡眠对精力的影响</strong><p>结合已有记录，找出可能影响恢复的关键因素。</p></span>${button("开始", "ai", "button")}</article><article>${compactIcon("spark", "amber")}<span><strong>帮我准备明天的产品讨论</strong><p>提炼重点、可能问题和建议，生成讨论提纲。</p></span>${button("开始", "ai", "button")}</article></div></section><section class="panel workspace-recent"><div class="section-head"><h2>最近的工作</h2>${button("查看全部　→", "nav:memory", "button ghost")}</div><div class="workspace-recent-list"><button type="button" data-action="memory:m1">${compactIcon("memory", "blue")}<span><strong>LifeOS 产品原型评审要点</strong><small>文档　·　基于 12 条记忆</small></span><time>今天 09:42</time></button><button type="button" data-action="memory:m3">${compactIcon("pulse", "mint")}<span><strong>训练计划调整方案</strong><small>计划　·　基于 8 条数据</small></span><time>昨天 18:30</time></button><button type="button" data-action="memory:m4">${compactIcon("heart", "lilac")}<span><strong>关于产品方向的深入讨论</strong><small>讨论　·　基于 5 条记忆</small></span><time>昨天 15:22</time></button></div></section></main><aside class="workspace-inspector"><section class="panel context-summary"><div class="section-head"><h2>当前上下文</h2>${button("管理　→", "ai", "button ghost")}</div><button type="button" class="context-primary" data-action="context:launch">${compactIcon("target", "blue")}<span><strong>LifeOS 产品开发</strong>${badge("主要", "decision")}<small>产品定义阶段　·　进行中</small><i><b></b></i></span></button><div class="context-mini-grid"><button type="button" data-action="context:recovery">${compactIcon("heart", "mint")}<span>训练恢复<small>进行中</small></span></button><button type="button" data-action="context:sleep">${compactIcon("clock", "lilac")}<span>最近睡眠<small>持续关注</small></span></button></div>${state.healthIncluded ? `${button("临时移除 Health Context", "remove-health", "context-manage")}` : `<div class="context-diff">Health 已从本次临时 Context 移除，不改持久事实。</div>${button("重新加入 Health", "add-health", "context-manage")}`}</section><section class="panel workspace-tools"><div class="section-head"><h2>常用工具</h2>${button("编辑", "ai", "button ghost")}</div><div><button type="button" data-action="ai">${compactIcon("memory", "blue")}<span>总结</span></button><button type="button" data-action="ai">${compactIcon("pulse", "mint")}<span>分析</span></button><button type="button" data-action="ai">${compactIcon("spark", "lilac")}<span>头脑风暴</span></button><button type="button" data-action="ai">${compactIcon("check", "amber")}<span>计划</span></button><button type="button" data-action="ai">${compactIcon("heart", "blue")}<span>习惯追踪</span></button><button type="button" data-action="ai">${compactIcon("clock", "lilac")}<span>知识问答</span></button></div></section><section class="panel workspace-commands"><div class="section-head"><h2>快捷指令</h2>${button("管理", "ai", "button ghost")}</div><div>${button("帮我回顾这个月的关键进展", "ai", "command-chip")}${button("我现在的优先级是什么？", "ai", "command-chip")}${button("给我一个专注 90 分钟的计划", "ai", "command-chip")}</div></section></aside></div></div>`;
  }

  function aiPanel() {
    if (!state.aiOpen) return "";
    const question = state.aiQuestion ? `<section class="ai-question"><span class="section-label">本次问题</span><p>${esc(state.aiQuestion)}</p><span class="tiny">仅保留在本次浏览器内存演示中，不会发送或保存。</span></section>` : `<p class="quiet ai-panel-empty">问一个问题，或从这里检查本次 AI 会使用的 Context。</p>`;
    return `<aside class="ai-panel open" aria-label="Global AI" role="dialog" aria-modal="false"><div class="ai-panel-head"><div><span class="eyebrow">Global AI</span><h2>问 LifeOS</h2></div><button class="close" type="button" data-action="close-ai" aria-label="关闭 Global AI">${icon("close")}</button></div><p class="quiet">全局、上下文可见的自然语言入口；本次内容只来自固定合成对象。</p><div class="context-chip-wrap"><span class="context-chip">Person</span><span class="context-chip">Page: ${esc(state.page)}</span><span class="context-chip">Selection: ${esc(context().title)}</span>${state.healthIncluded ? '<span class="context-chip">Health <button aria-label="临时移除 Health Context" data-action="remove-health">×</button></span>' : ""}</div>${question}${!state.healthIncluded ? '<div class="context-diff">Health 已临时移除：候选回答不使用这一类 Context，持久事实保持不变。</div>' : ""}<div class="ai-answer">${badge("AI Observation", "observation")}<p>${state.healthIncluded ? "我看见工作推进和恢复 Context 同时存在，但没有足够证据判断它们的因果关系。" : "我只参考了当前页面、Work 与选中的 Context；没有使用 Health Context。"}</p><div class="actions">${button("查看依据", "memory:m6")}${button("展开 AI Workspace", "workspace", "button primary")}</div></div><section class="candidate-grid" style="margin-top:16px"><article class="ai-card"><div>${badge("Suggested Action", "inference")}</div><p>候选：先核对首屏叙事，再决定是否继续视觉细节。</p><div class="actions">${button("确认", "candidate:action:confirm")}${button("编辑", "candidate:action:edit")}${button("拒绝", "candidate:action:reject", "button danger")}${button("忽略", "candidate:action:ignore")}</div></article><article class="ai-card"><div>${badge("Decision Candidate", "decision")}</div><p>候选决定不会自动持久化或执行；由你决定是否确认。</p><div class="actions">${button("确认", "candidate:decision:confirm")}${button("纠正", "candidate:decision:correct")}</div></article></section><form class="ai-panel-composer" data-ai-form><input aria-label="继续问 LifeOS" name="aiPrompt" placeholder="继续问 LifeOS…" /><button class="send" type="submit" aria-label="发送并更新 Global AI">${icon("arrow")}</button></form></aside>`;
  }

  function modal() {
    if (!state.modal) return "";
    let content = "";
    if (state.modal === "capture") {
      content = `<div class="modal"><div class="section-head"><div><span class="eyebrow">Quick Capture</span><h2>先保留原文，再让你决定关联</h2></div><button class="close" type="button" data-action="close-modal" aria-label="关闭">${icon("close")}</button></div><p>演示状态只保留在内存中：不会保存、发送或创建真实对象。</p><div class="capture-original"><strong>用户原文 · 固定 synthetic 输入</strong>${esc(state.captureText)}</div><div class="select-like"><span>建议关联</span><strong>Work · LifeOS 产品开发</strong></div><div class="select-like"><span>建议 Context</span><strong>LifeOS 产品开发 · 待你确认</strong></div><div class="actions">${button("确认关联", "capture-confirm", "button primary")}${button("忽略建议", "capture-ignore")}</div></div>`;
    } else if (state.modal === "suggest") {
      content = `<div class="modal"><div class="section-head"><div><span class="eyebrow">Context Candidate</span><h2>“近期旅行安排”</h2></div><button class="close" type="button" data-action="close-modal" aria-label="关闭">${icon("close")}</button></div><p>LifeOS 只能提出候选。它不会自动创建 Context，也不会改变任何持久事实。</p><div class="select-like"><span>建议类型</span><strong>Life Event</strong></div><div class="actions">${button("确认创建（仅演示）", "suggest-confirm", "button primary")}${button("拒绝", "close-modal", "button danger")}</div></div>`;
    } else if (state.modal === "activation") {
      content = `<div class="modal"><div class="section-head"><div><span class="eyebrow">Domain Activation</span><h2>新领域一次只能启用一个</h2></div><button class="close" type="button" data-action="close-modal" aria-label="关闭">${icon("close")}</button></div><p>“Finance” 仍未启用深度智能。以下四类 Gate 必须逐项成立，不能用更多导航入口代替。</p><div class="list"><div class="list-item"><span class="dot amber"></span><div><strong>数据 Gate</strong><div class="tiny">未满足：当前只有泛化记录。</div></div></div><div class="list-item"><span class="dot amber"></span><div><strong>价值 Gate</strong><div class="tiny">未满足：没有已验证的用户价值。</div></div></div><div class="list-item"><span class="dot amber"></span><div><strong>反馈 Gate</strong><div class="tiny">未满足：没有对象级反馈生命周期。</div></div></div><div class="list-item"><span class="dot amber"></span><div><strong>安全 Gate</strong><div class="tiny">未满足：高风险边界未定义。</div></div></div></div><div class="actions">${button("保持未启用", "close-modal", "button primary")}</div></div>`;
    }
    return `<div class="modal-backdrop open" data-backdrop><div role="dialog" aria-modal="true" aria-label="原型对话框">${content}</div></div>`;
  }

  function composer() {
    return `<div class="composer"><form data-ai-form aria-label="Global AI Bar"><button class="ai-launch" type="button" data-action="ai" aria-label="打开 Global AI">${icon("spark")}</button><input aria-label="问 LifeOS" name="aiPrompt" placeholder="问 LifeOS…" /><span class="tiny capture-shortcut">Global AI · 仅本地演示</span><button class="capture-plus" type="button" data-action="capture" aria-label="打开 Quick Capture">${icon("plus")}</button><button class="send" type="submit" aria-label="发送并展开 Global AI">↑</button></form></div>`;
  }

  function page() {
    if (state.page === "me") return mePage();
    if (state.page === "contexts") return contextsPage();
    if (state.page === "detail") return contextDetailPage();
    if (state.page === "memory") return memoryPage();
    if (state.page === "memory-detail") return memoryDetailPage();
    if (state.page === "settings") return settingsPage();
    if (state.page === "workspace") return workspacePage();
    return todayPage();
  }

  function render() {
    document.body.classList.toggle("reduced-motion", state.reducedMotion);
    const workspace = state.page === "workspace";
    const rail = `<nav class="icon-rail" aria-label="LifeOS 主导航"><span class="brand-mark" aria-label="LifeOS">✦</span>${navButton("today", "Today")}${navButton("me", "Me")}${navButton("contexts", "Contexts")}${navButton("memory", "Memory")}<span class="rail-spacer"></span><button class="rail-button settings-button" type="button" data-action="nav:settings" data-tooltip="Settings" aria-label="Settings" ${state.page === "settings" ? 'aria-current="page"' : ""}>${icon("settings")}</button></nav>`;
    const futureAgentNote = workspace ? `<section class="panel workspace-future"><div>${badge("Future Agent Task", "")}</div><p>未来能力占位：需要显示执行者、允许权限、过程与 Evidence；当前没有 Agent、工具或真实执行。</p><span class="tiny">诚实占位 · 尚未实现</span></section>` : "";
    app.innerHTML = workspace ? `<div class="app-shell workspace-shell">${rail}<div class="workspace">${page()}${futureAgentNote}</div></div>${aiPanel()}${modal()}` : `<div class="app-shell">${rail}<div class="workspace"><main id="main-content" class="page-wrap" tabindex="-1">${page()}</main></div></div>${composer()}${aiPanel()}${modal()}`;
  }

  function updateCandidate(kind, verb) {
    const copy = { confirm: "已由你确认（演示）", edit: "已编辑候选（演示）", reject: "已拒绝（演示）", ignore: "已忽略（演示）", correct: "已提交纠正（演示）" };
    state.candidate[kind] = copy[verb] || "待核对";
    state.receipt = `${kind === "action" ? "候选 Action" : kind === "decision" ? "Decision Candidate" : "Observation"}${copy[verb] || "已更新"}；原文、证据和候选身份保持分离。`;
  }

  app.addEventListener("click", (event) => {
    const target = event.target.closest("[data-action]");
    if (!target) return;
    const action = target.dataset.action;
    if (action.startsWith("nav:")) { state.page = action.slice(4); state.aiOpen = false; state.modal = null; }
    else if (action.startsWith("today:")) { state.todayMode = action.slice(6); state.showWhy = null; }
    else if (action.startsWith("why:")) { state.showWhy = action.slice(4); }
    else if (action.startsWith("contexts:")) { state.contextFilter = action.slice(9); }
    else if (action.startsWith("context:")) { state.selectedContext = action.slice(8); state.page = "detail"; }
    else if (action.startsWith("memory:")) { state.memoryDetail = action.slice(7); state.page = "memory-detail"; state.aiOpen = false; }
    else if (action.startsWith("memory-kind:")) { state.memoryFilter = action.slice(12); }
    else if (action.startsWith("candidate:")) { const [, kind, verb] = action.split(":"); updateCandidate(kind, verb); }
    else if (action === "ai") { state.aiOpen = true; state.modal = null; }
    else if (action === "close-ai") { state.aiOpen = false; }
    else if (action === "workspace") { state.page = "workspace"; state.aiOpen = false; }
    else if (action === "remove-health") { state.healthIncluded = false; }
    else if (action === "add-health") { state.healthIncluded = true; }
    else if (action === "capture") { state.modal = "capture"; }
    else if (action === "close-modal" || action === "dismiss-suggest") { state.modal = null; }
    else if (action === "suggest-context") { state.modal = "suggest"; }
    else if (action === "activation") { state.modal = "activation"; }
    else if (action === "capture-confirm") { state.receipt = "原文已在本次合成演示中保留；关联建议由你确认，未写入任何真实存储。"; state.modal = null; }
    else if (action === "capture-ignore") { state.receipt = "你已忽略关联建议；原文仍只停留在本次合成演示中。"; state.modal = null; }
    else if (action === "suggest-confirm") { state.receipt = "你确认了一个 Context 候选（演示）；原型不创建持久对象。"; state.modal = null; }
    else if (action === "motion") { state.reducedMotion = !state.reducedMotion; }
    else if (action === "clear-memory") { state.memoryFilter = ""; }
    render();
  });

  app.addEventListener("input", (event) => {
    if (event.target.matches("[data-memory-search]")) { state.memoryFilter = event.target.value; render(); const input = app.querySelector("[data-memory-search]"); if (input) { input.focus(); input.setSelectionRange(input.value.length, input.value.length); } }
  });

  app.addEventListener("submit", (event) => {
    if (!event.target.matches("[data-ai-form]")) return;
    event.preventDefault();
    const input = event.target.elements.aiPrompt;
    state.aiQuestion = input.value.trim();
    state.aiOpen = true;
    state.modal = null;
    render();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && (state.aiOpen || state.modal)) { state.aiOpen = false; state.modal = null; render(); const main = document.getElementById("main-content"); if (main) main.focus(); }
  });

  // P3-134 keeps this P3-116 renderer as the sole page system.  The separately
  // loaded adapter only binds typed Runtime DTOs to these existing nodes.
  window.__P3_116_RUNTIME__ = { state, render, app };
  render();
})();
