(() => {
  "use strict";

  const invoke = window.__TAURI__?.core?.invoke;
  const app = document.getElementById("app");
  const syntheticTexts = new Set([
    "P3-120 synthetic capture one",
    "P3-120 synthetic capture two",
  ]);
  const samples = [
    { text: "P3-120 synthetic capture one", key: "p3-120-synthetic-one", label: "记录合成样本一" },
    { text: "P3-120 synthetic capture two", key: "p3-120-synthetic-two", label: "记录合成样本二" },
  ];
  const state = {
    page: "today",
    aiOpen: false,
    runtime: null,
    today: { status: "loading", records: [], audit: { event_count: 0, repeat_count: 0 } },
    notice: "正在核对离线本地 Runtime…",
    error: false,
  };

  const errorCode = (error) => (error && typeof error === "object" && error.code) || "runtime_contract_rejected";
  const safeInvoke = async (command, request = {}) => {
    if (typeof invoke !== "function") throw { code: "tauri_bridge_unavailable" };
    return invoke(command, { request });
  };
  const setNotice = (notice, error = false) => {
    state.notice = notice;
    state.error = error;
    render();
  };
  const esc = (value) => String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
  const badge = (label, type = "") => `<span class="badge ${type}">${esc(label)}</span>`;
  const nav = (id, label, icon) => `<button class="nav-button" type="button" data-action="nav:${id}" aria-current="${state.page === id ? "page" : "false"}" aria-label="${label}"><span aria-hidden="true">${icon}</span><em>${label}</em></button>`;

  function statusSummary() {
    if (!state.runtime) return "Runtime 正在核对；此时不显示缓存成功态。";
    return "离线 · 本地 · 固定 synthetic SQLite · 仅三项 IPC";
  }

  function recordsMarkup() {
    const records = state.today.records;
    if (!records.length) return `<div class="empty-state"><strong>今天还没有 Runtime 记录。</strong><p>可明确提交一条固定合成样本；不会接收真实文本。</p></div>`;
    return `<div class="records">${records.map((record, index) => `<article class="record"><div>${badge("用户原文", "user")}<span class="record-index">合成记录 ${index + 1}</span></div><p>${esc(record.content)}</p><small>通过 get_today 从 task-local SQLite 读取 · AI 未参与</small></article>`).join("")}</div>`;
  }

  function todayPage() {
    return `<main id="main" class="page today-page" tabindex="-1">
      <header class="page-header hero"><div><p class="eyebrow">Today · Person 的此刻</p><h1>先回到这个人正在经历的事。</h1><p>Runtime 只持久化下面两条明确标记的合成原文；其他产品内容是只读 synthetic fixture。</p></div><span class="runtime-pill">${statusSummary()}</span></header>
      <section class="focus-card"><div class="section-top"><div>${badge("Today's Focus", "decision")}<h2>今天先让产品 Runtime 闭环可靠。</h2></div><span class="quiet-label">固定 fixture · 非持久化</span></div><p>当前焦点只有一个：确认 capture、找回与刷新后的内容身份一致。它不是 AI 建议，也不会自动创建 Action、Decision 或 Context。</p><div class="reason"><strong>为什么现在值得做</strong><span>此 MVP 只验证本地受控闭环，不外推为真实个人使用或生产能力。</span></div></section>
      <section class="two-column">
        <section class="panel"><div class="section-top"><div><p class="eyebrow">Quick Capture · Synthetic demo</p><h2>明确选择一条合成原文</h2></div>${badge("仅此两条", "warning")}</div><p class="muted">没有自由文本输入、文件入口或导入入口。重复点击同一条会得到确定的幂等回执。</p><div class="capture-actions">${samples.map((sample) => `<button class="primary" type="button" data-action="capture:${sample.key}">${sample.label}<small>${sample.text}</small></button>`).join("")}</div><p class="boundary-note">capture_record 是唯一写入入口；成功后才会调用 get_today 重读并显示。</p></section>
        <section class="panel status-card"><p class="eyebrow">Runtime Status</p><h2>受控关闭态</h2><ul><li>本地单进程、离线</li><li>模型、网络、文件、导出、同步均未启用</li><li>renderer 没有 SQLite、shell 或路径 API</li></ul><button class="quiet-button" type="button" data-action="refresh">刷新 Today</button></section>
      </section>
      <section class="panel today-records"><div class="section-top"><div><p class="eyebrow">Recent · Runtime data</p><h2>从本地原文找回</h2></div><span class="quiet-label">${state.today.records.length} 条记录 · ${state.today.audit.event_count || 0} 条审计事件</span></div>${recordsMarkup()}</section>
      <section class="fixture-strip"><div><strong>LifeOS noticed</strong><p>固定合成观察：此页面只验证记录闭环，不判断 Work 与 Health 的因果，也不给出健康建议。</p></div>${badge("AI Observation", "observation")}</section>
    </main>`;
  }

  function mePage() {
    return `<main id="main" class="page" tabindex="-1"><header class="page-header"><div><p class="eyebrow">Me · Person 的长期视角</p><h1>LifeOS 如何理解这个人</h1><p>以下均为明确标记的 read-only synthetic fixture，不来自 Runtime 数据库。</p></div>${badge("固定 synthetic fixture", "fixture")}</header>
      <section class="me-card"><div class="person-orb" aria-hidden="true">✦</div><div><p class="eyebrow">Current Self</p><h2>工作推进感稳定，同时需要给恢复留出位置。</h2><p>这不是画像或诊断。它是可查看依据、可被纠正的固定演示内容。</p><div class="inline-actions"><button class="quiet-button" data-action="memory-detail">查看理解依据</button><button class="quiet-button" data-action="ai-open">问 Global AI</button></div></div></section>
      <section class="cards"><article><h2>长期视角 / Domains</h2>${badge("Work · 已激活", "decision")} ${badge("Health · 已激活", "user")}<p>其他人生数据可被承接，但未启用深度智能。</p></article><article><h2>当前关注 / Contexts</h2><p><strong>LifeOS 产品开发</strong><br><span class="muted">Work · Project · 正在进行</span></p><p><strong>训练恢复</strong><br><span class="muted">Health · Program · 持续关注</span></p></article><article><h2>身份与权威</h2><p>${badge("用户确认", "user")} 与 ${badge("AI 候选", "warning")} 始终分开。当前没有任何候选被 Runtime 写入。</p></article></section></main>`;
  }

  function contextsPage() {
    return `<main id="main" class="page" tabindex="-1"><header class="page-header"><div><p class="eyebrow">Contexts · 正在经历的事</p><h1>按人与事情的关系恢复上下文。</h1><p>Project 只是 Context 的一种；本页为只读 synthetic fixture。</p></div>${badge("read-only fixture", "fixture")}</header>
      <section class="context-list"><button data-action="context-detail"><span>${badge("Project", "decision")}<strong>LifeOS 产品开发</strong><small>Work · 正在进行 · 现在：Runtime 闭环收口</small></span><b>›</b></button><button data-action="context-detail"><span>${badge("Program", "user")}<strong>训练恢复</strong><small>Health · 持续关注 · 不生成诊断或训练调整</small></span><b>›</b></button><button data-action="context-detail"><span>${badge("Observed Context", "observation")}<strong>最近睡眠</strong><small>Health · 证据有限 · 不作因果判断</small></span><b>›</b></button></section>
      <section class="fixture-strip"><div><strong>Candidate Context</strong><p>系统可以提出候选，但没有创建按钮；Context 不会被静默持久化。</p></div>${badge("未启用", "warning")}</section></main>`;
  }

  function contextDetailPage() {
    return `<main id="main" class="page" tabindex="-1"><button class="back" data-action="nav:contexts">‹ Contexts</button><header class="page-header"><div><p class="eyebrow">Context Detail · Work</p><h1>LifeOS 产品开发</h1><p>固定演示详情：现在、已确认下一步、最近发生与可追溯理解分层显示。</p></div>${badge("synthetic fixture", "fixture")}</header>
      <section class="two-column"><div class="stack"><article class="panel"><p class="eyebrow">现在</p><h2>Person-centered Runtime MVP 正在收口。</h2></article><article class="panel"><p class="eyebrow">Next</p><h2>先验证 capture → Today → 刷新 → 重开。</h2>${badge("用户确认的演示事实", "user")}</article><article class="panel"><p class="eyebrow">最近发生</p><ol class="timeline"><li>用户原文以固定 synthetic 身份进入 Runtime</li><li>Today 只从 get_today 找回</li><li>AI 输出仍是未执行的界面候选</li></ol></article></div><aside class="stack"><article class="panel"><p class="eyebrow">LifeOS understands</p><p>该 Context 的最小阻塞点是可靠闭环，而不是生成更多建议。</p>${badge("AI Inference · fixture", "warning")}</article><article class="panel"><p class="eyebrow">Related / Evidence</p><p>Memory Detail 会显示来源层级；本轮不读取真实 Source。</p><button class="quiet-button" data-action="memory-detail">打开 Memory Detail</button></article></aside></section></main>`;
  }

  function memoryPage() {
    return `<main id="main" class="page" tabindex="-1"><header class="page-header"><div><p class="eyebrow">Memory · Evidence Browser</p><h1>认识必须能回到它的依据。</h1><p>本页使用固定 read-only synthetic fixture，不能伪称已接入 Runtime 持久化。</p></div>${badge("fixture ≠ runtime", "fixture")}</header>
      <section class="memory-list"><button data-action="memory-detail"><span>${badge("用户原文", "user")}<strong>“先把本地闭环做可靠。”</strong><small>固定合成 Source · Work</small></span><b>›</b></button><button data-action="memory-detail"><span>${badge("确认事实", "user")}<strong>本轮只接入两条固定 capture。</strong><small>固定合成确认 · Runtime boundary</small></span><b>›</b></button><button data-action="memory-detail"><span>${badge("AI Observation", "observation")}<strong>两个领域 Context 同时存在。</strong><small>固定合成推导 · 待核对</small></span><b>›</b></button><button data-action="memory-detail"><span>${badge("Decision Candidate", "warning")}<strong>下一步先验证重开，再扩展能力。</strong><small>候选 · 不会执行或落库</small></span><b>›</b></button></section></main>`;
  }

  function memoryDetailPage() {
    return `<main id="main" class="page" tabindex="-1"><button class="back" data-action="nav:memory">‹ Memory</button><header class="page-header"><div><p class="eyebrow">Memory Detail · 可追溯性</p><h1>Runtime 闭环的候选依据</h1><p>这里只呈现固定 synthetic 的身份链，绝不冒充真实来源或模型输出。</p></div>${badge("Derivation · fixture", "fixture")}</header>
      <section class="two-column"><article class="panel"><p class="eyebrow">为什么这样理解</p><ol class="trace"><li><strong>用户原文</strong><span>固定 synthetic capture；Runtime 中会以 user_original 身份保存。</span></li><li><strong>确认事实</strong><span>仅三项 IPC，且禁止网络、模型、导出与文件能力。</span></li><li><strong>Observation</strong><span>固定演示观察，不推断健康或工作因果。</span></li><li><strong>Candidate</strong><span>下一步仅供用户审阅；当前没有执行、写入或确认。</span></li></ol></article><aside class="stack"><article class="panel"><p class="eyebrow">来源状态</p><h2>固定、可审阅、非真实来源</h2><p>真实 Source、外部文件和网络均未接入。</p></article><article class="panel"><p class="eyebrow">反馈</p><p>本轮不实现反馈持久化；不能把界面点击写成已确认事实。</p>${badge("未启用", "warning")}</article></aside></section></main>`;
  }

  function workspacePage() {
    return `<main id="main" class="page workspace-page" tabindex="-1"><header class="page-header"><div><p class="eyebrow">AI Workspace · 深度展开</p><h1>把 AI 放在可检查的边界里。</h1><p>此页面是本地合成交互壳：没有模型调用、网络请求、工具执行或 AI 写入。</p></div>${badge("模型未启用", "warning")}</header>
      <section class="workspace-grid"><article class="panel"><p class="eyebrow">Conversation + Work</p><h2>当前没有可执行的 AI 回复。</h2><p>可以展示 Observation、Suggestion 与 Decision Candidate 的身份，但它们都保持为固定 fixture，不会被提升为事实。</p><div class="fixture-strip"><div><strong>候选：先验证生命周期</strong><p>需用户审阅；不创建 Action、Decision 或 Agent Task。</p></div>${badge("Suggested Action", "warning")}</div></article><aside class="stack"><article class="panel"><p class="eyebrow">Context Inspector</p><p>${badge("Person", "fixture")} ${badge("Work", "fixture")} ${badge("Health", "fixture")}</p><p class="muted">所有范围均为展示用固定内容；本次没有真实数据被使用。</p></article><article class="panel"><p class="eyebrow">Future Agent Task</p><p>诚实占位：没有 Agent、权限、工具或执行记录。</p>${badge("未实现", "warning")}</article></aside></section></main>`;
  }

  function settingsPage() {
    return `<main id="main" class="page" tabindex="-1"><header class="page-header"><div><p class="eyebrow">Settings · 弱化入口</p><h1>本轮的真实边界</h1><p>设置不是一级工作区，也不包含权限、恢复、导出或真实路径功能。</p></div>${badge("restricted", "warning")}</header><section class="cards"><article><h2>允许</h2><p>新 task-local SQLite；capture_record、get_today、runtime_status；固定合成原文。</p></article><article><h2>关闭</h2><p>网络、模型、文件、Vault、导入、clear、export、恢复、同步、多设备与外部用户。</p></article><article><h2>透明性</h2><p>刷新和重开会读取 Runtime 数据；Me、Contexts、Memory 与 AI 仍是显式 fixture。</p></article></section></main>`;
  }

  function aiPanel() {
    if (!state.aiOpen) return "";
    return `<aside class="ai-panel" role="dialog" aria-label="Global AI" aria-modal="false"><div class="section-top"><div><p class="eyebrow">Global AI</p><h2>问 LifeOS</h2></div><button class="icon-button" data-action="ai-close" aria-label="关闭 Global AI">×</button></div><p>全局入口保持可达，但模型未启用。本次不会发送、保存或推断任何内容。</p><div class="context-chips">${badge("Person", "fixture")} ${badge(`Page: ${state.page}`, "fixture")} ${badge("Selection: LifeOS 产品开发", "fixture")}</div><div class="fixture-strip"><div><strong>AI Observation · 固定演示</strong><p>工作与 Health Context 同时存在；没有足够证据判断它们是否相关。</p></div>${badge("无模型", "warning")}</div><button class="primary" data-action="workspace">展开 AI Workspace</button><p class="panel-footer">Suggested Action 与 Decision Candidate 均未执行、未确认、未落库。</p></aside>`;
  }

  function shell(pageMarkup) {
    return `<div class="shell"><nav class="rail" aria-label="LifeOS 主导航"><span class="brand" aria-label="LifeOS">✦</span>${nav("today", "Today", "◌")}${nav("me", "Me", "◐")}${nav("contexts", "Contexts", "□")}${nav("memory", "Memory", "▤")}<span class="rail-spacer"></span>${nav("settings", "Settings", "⚙")}</nav><section class="content">${pageMarkup}</section><footer class="composer"><button class="composer-ai" data-action="ai-open" aria-label="打开 Global AI">✦</button><span>Global AI · 模型未启用</span><button class="quiet-button" data-action="ai-open">查看范围</button></footer><p class="notice ${state.error ? "error" : ""}" role="status">${esc(state.notice)}</p>${aiPanel()}</div>`;
  }

  function pageMarkup() {
    if (state.page === "me") return mePage();
    if (state.page === "contexts") return contextsPage();
    if (state.page === "context-detail") return contextDetailPage();
    if (state.page === "memory") return memoryPage();
    if (state.page === "memory-detail") return memoryDetailPage();
    if (state.page === "workspace") return workspacePage();
    if (state.page === "settings") return settingsPage();
    return todayPage();
  }
  function render() { app.innerHTML = shell(pageMarkup()); }

  function validateStatus(status) {
    const expected = ["capture_record", "get_today", "runtime_status"];
    const closed = ["filesystem", "raw_database", "generic_path_api", "shell", "process_spawn", "network", "vault", "export", "sync"];
    if (!status || status.status !== "restricted_offline" || !status.offline || status.ai_enabled || status.unknown_ipc !== "deny" || !Array.isArray(status.renderer_direct_capabilities) || status.renderer_direct_capabilities.length !== 0 || status.ipc_allowlist?.join(",") !== expected.join(",") || closed.some((key) => status[key] !== false)) throw { code: "runtime_contract_rejected" };
    return status;
  }
  function validateToday(payload) {
    if (!payload || !["empty", "loaded"].includes(payload.status) || !Array.isArray(payload.records) || !payload.audit || payload.ai_status !== "disabled" || payload.source !== "local_capture") throw { code: "today_contract_rejected" };
    const unique = new Set();
    for (const record of payload.records) {
      if (!record || !syntheticTexts.has(record.content) || record.identity !== "user_original" || record.source !== "local_capture" || !record.id || unique.has(record.id)) throw { code: "today_identity_rejected" };
      unique.add(record.id);
    }
    if (payload.records.length > 2) throw { code: "today_limit_rejected" };
    return payload;
  }
  async function refreshToday(showReceipt = true) {
    try {
      state.today = validateToday(await safeInvoke("get_today", {}));
      if (showReceipt) { state.notice = `Today 已从 get_today 重读：${state.today.records.length} 条固定合成原文。`; state.error = false; }
      render();
      return state.today;
    } catch (error) {
      state.today = { status: "blocked", records: [], audit: { event_count: 0, repeat_count: 0 } };
      state.notice = `读取被阻断：${errorCode(error)}。未展示缓存或部分记录。`;
      state.error = true;
      render();
      throw error;
    }
  }
  async function capture(sample) {
    setNotice("正在等待 capture_record 的权威回执…");
    try {
      const result = await safeInvoke("capture_record", { text: sample.text, key: sample.key });
      if (!result || !["saved", "idempotent_repeat"].includes(result.status) || !result.record || result.record.content !== sample.text || result.record.identity !== "user_original") throw { code: "capture_contract_rejected" };
      await refreshToday(false);
      state.notice = result.status === "saved" ? "已保存：先完成 SQLite 原子发布，再经 get_today 找回。" : "幂等重复：记录未增加；同一固定原文身份保持不变。";
      state.error = false;
      render();
    } catch (error) {
      state.notice = `已阻断：${errorCode(error)}。没有显示成功态；将重新读取权威状态。`;
      state.error = true;
      render();
      await refreshToday(false).catch(() => {});
    }
  }

  app.addEventListener("click", (event) => {
    const target = event.target.closest("[data-action]");
    if (!target) return;
    const action = target.dataset.action;
    if (action.startsWith("nav:")) { state.page = action.slice(4); state.aiOpen = false; render(); return; }
    if (action.startsWith("capture:")) { const sample = samples.find((item) => item.key === action.slice(8)); if (sample) capture(sample); return; }
    if (action === "refresh") { refreshToday(); return; }
    if (action === "ai-open") { state.aiOpen = true; render(); return; }
    if (action === "ai-close") { state.aiOpen = false; render(); return; }
    if (action === "workspace") { state.page = "workspace"; state.aiOpen = false; render(); return; }
    if (action === "context-detail") { state.page = "context-detail"; render(); return; }
    if (action === "memory-detail") { state.page = "memory-detail"; render(); }
  });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape" && state.aiOpen) { state.aiOpen = false; render(); document.getElementById("main")?.focus(); } });

  async function init() {
    render();
    try {
      state.runtime = validateStatus(await safeInvoke("runtime_status", {}));
      await refreshToday(false);
      state.notice = "Runtime 已核对：离线、本地、固定 synthetic 数据与三项 IPC 均处于受控边界。";
      state.error = false;
    } catch (error) {
      state.notice = `启动被阻断：${errorCode(error)}。未显示成功或缓存状态。`;
      state.error = true;
    }
    render();
  }
  init();
})();
