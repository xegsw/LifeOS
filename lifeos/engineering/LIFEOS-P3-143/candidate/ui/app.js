(() => {
  "use strict";

  const app = document.querySelector("#app");
  const capabilityNames = {
    "text.reasoning": "文字推理", "vision.understanding": "视觉理解", "speech.transcription": "语音输入",
    "speech.synthesis": "语音输出", "tool.use": "工具调用", "long_context": "长文本",
    "structured_output": "结构化输出", embedding: "嵌入",
  };
  const overrideKeys = ["text", "vision", "speech_input", "speech_output", "tool_use", "long_context"];
  const state = {
    settings: null, section: "model", page: "settings", notice: "", busy: false, transientResponse: "", pendingModel: "",
    drafts: { cloud: { providerId: "deepseek", modelLabel: "待连接测试后选择" }, local: { providerId: "ollama", modelLabel: "synthetic-local-v1" } },
    draftMode: "cloud",
  };

  const escape = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
  const invoke = (command, request) => {
    const target = window.__TAURI__?.core?.invoke;
    if (!target) return Promise.reject({ message: "仅 actual Tauri 可调用受控 Runtime。" });
    return target(command, { request });
  };
  const active = () => state.settings?.settings?.primary || null;
  const registry = () => state.settings?.providerRegistry || [];
  const providers = (mode) => registry().filter((item) => item.mode === mode);
  const provider = (id) => registry().find((item) => item.id === id);
  const label = (id) => provider(id)?.label || "未选择服务";
  const isDeepSeek = (value = active()) => value?.mode === "cloud" && value?.providerId === "deepseek" && value?.endpointUrl === "https://api.deepseek.com";
  const hasSuccessfulTest = () => ["synthetic_connected", "real_connected"].includes(state.settings?.connectionState);
  const gateIsReal = () => state.settings?.runMode === "real_gate";
  const connectionLabel = (value) => ({ credential_missing: "等待凭据", not_configured: "未配置", not_tested: "等待用户测试", synthetic_connected: "合成验证成功", real_connected: "真实连接已验证" })[value] || "未验证";
  const statusClass = (value) => ["synthetic_connected", "real_connected"].includes(value) ? "success" : value === "credential_missing" || value === "not_configured" ? "muted" : "warning";
  const icon = (name) => ({ today: "⌂", me: "◌", contexts: "▢", memory: "▤", settings: "⚙", spark: "✦", cloud: "☁", local: "⌘", check: "✓", arrow: "›", tuning: "◒", lock: "◇", shield: "◈" })[name] || "•";

  function primaryFromDraft(draft, mode) {
    const deepSeekDraft = mode === "cloud" && draft.providerId === "deepseek";
    return {
      mode, providerId: draft.providerId,
      modelLabel: draft.modelLabel || (deepSeekDraft ? "待连接测试后选择" : mode === "cloud" ? "synthetic-text-v1" : "synthetic-local-v1"),
      endpointUrl: mode === "cloud" ? (deepSeekDraft ? "https://api.deepseek.com" : `offline://catalog/cloud/${draft.providerId}`) : null,
      localRuntime: mode === "local" ? "synthetic-local-runtime-v1" : null,
    };
  }

  function defaultSettings() {
    const draft = state.drafts[state.draftMode];
    return {
      version: 1, primary: primaryFromDraft(draft, state.draftMode),
      routingPolicy: { preferLocal: true, allowCloudSupplement: false, allowAutomaticFailover: false, preferFastResponse: false },
      fallback: { configured: false, providerId: null },
      advanced: { expanded: false, capabilityOverrides: Object.fromEntries(overrideKeys.map((key) => [key, "auto"])), temperature: 70, maxOutputTokens: 2048, timeoutSeconds: 60, contextWindow: 32 },
    };
  }

  function proposed() {
    const base = state.settings?.settings ? structuredClone(state.settings.settings) : defaultSettings();
    base.primary = primaryFromDraft(state.drafts[state.draftMode], state.draftMode);
    return base;
  }

  function isPending() {
    const current = active();
    const draft = state.drafts[state.draftMode];
    return !current || current.mode !== state.draftMode || current.providerId !== draft.providerId || current.modelLabel !== draft.modelLabel;
  }

  async function refresh() {
    state.settings = await invoke("get_ai_provider_settings", { version: 1 });
    const current = active();
    if (current) {
      state.drafts[current.mode] = { providerId: current.providerId, modelLabel: current.modelLabel };
      state.draftMode = current.mode;
    }
  }

  function railButton(id, text) { return `<button class="rail-button ${state.page === id ? "is-current" : ""}" data-action="page:${id}" aria-label="${text}" title="${text}">${icon(id)}</button>`; }
  function shell() { return `<nav class="rail" aria-label="LifeOS 主导航"><div class="brand" aria-label="LifeOS">${icon("spark")}</div>${railButton("today", "Today")}${railButton("me", "Me")}${railButton("contexts", "Contexts")}${railButton("memory", "Memory")}<span class="rail-spacer"></span>${railButton("settings", "设置")}</nav>`; }
  function secondaryNav() {
    const items = [["general", "通用"], ["model", "模型设置"], ["privacy", "数据与隐私"], ["backup", "备份与导出"], ["about", "关于"]];
    return `<aside class="settings-nav" aria-label="设置导航"><p>设置</p>${items.map(([id, text]) => `<button data-action="section:${id}" class="${state.section === id ? "selected" : ""}">${text}${id !== "model" ? "<span>暂未开放</span>" : ""}</button>`).join("")}</aside>`;
  }
  function quietPage() {
    const names = { today: "Today", me: "Me", contexts: "Contexts", memory: "Memory" };
    return `<main class="quiet-page"><p class="eyebrow">LifeOS · ${names[state.page]}</p><h1>${names[state.page]}</h1><p>这个入口保持可达。P3-143 只实现“模型设置”二级区域，不把其他页面伪装为已实现能力。</p><button class="button secondary" data-action="page:settings">前往模型设置</button></main>`;
  }
  function unavailablePage() {
    const title = { general: "通用", privacy: "数据与隐私", backup: "备份与导出", about: "关于" }[state.section];
    return `<section class="unavailable"><p class="eyebrow">Settings</p><h1>${title}</h1><p>暂未开放。本任务不把这个设置分类显示为可用能力。</p></section>`;
  }

  function serviceCard() {
    const current = active();
    if (!current) return `<section class="service-card empty" data-testid="primary-unconfigured"><div><span class="slot-icon">${icon("spark")}</span><p class="eyebrow">主 AI 服务</p><h2>还没有配置服务</h2><p>目录保持可替换；只有 DeepSeek 能进入本轮受控真实验证，其他服务仍为未验证。</p></div><button class="button primary" data-action="focus-form">配置 DeepSeek</button></section>`;
    const supported = state.settings.capabilityRegistry?.[current.providerId] || [];
    const displayModel = state.settings.selectedModel || current.modelLabel;
    const location = isDeepSeek(current) ? (gateIsReal() ? "DeepSeek · 用户受控真实 Gate" : "DeepSeek · 合成离线验证") : current.mode === "cloud" ? "云端目录 · 本轮未验证" : "本地目录 · 本轮未验证";
    return `<section class="service-card" data-testid="primary-configured"><div class="service-head"><div><span class="slot-icon">${current.mode === "cloud" ? icon("cloud") : icon("local")}</span><p class="eyebrow">主 AI 服务</p><h2>${escape(label(current.providerId))}</h2><p>${escape(displayModel)} · ${location}</p></div><span class="state-dot ${statusClass(state.settings.connectionState)}">${connectionLabel(state.settings.connectionState)}</span></div><div class="capability-pills">${supported.slice(0, 5).map((item) => `<span>${icon("check")} ${capabilityNames[item] || item}</span>`).join("")}</div></section>`;
  }

  function modeControl() { return `<div class="mode-control" role="group" aria-label="服务处理位置"><button data-action="mode:cloud" aria-pressed="${state.draftMode === "cloud"}"><strong>${icon("cloud")} 云端服务</strong><small>DeepSeek 仅在用户逐次操作后真实连接</small></button><button data-action="mode:local" aria-pressed="${state.draftMode === "local"}"><strong>${icon("local")} 本地服务</strong><small>目录保留；本轮不探测本地进程</small></button></div>`; }

  function credentialControls() {
    if (!isDeepSeek()) return `<div class="credential-status"><strong>本轮未验证此 Provider</strong><p>目录仍保留，但不接收凭据、不会发起连接测试或网络请求。</p></div>`;
    return `<div class="credential-area"><p class="eyebrow">凭据与用户 Gate</p><div class="credential-status"><strong>${state.settings.hasCredential ? `已保存加密凭据 ${escape(state.settings.credentialMask || "")}` : "尚未保存凭据"}</strong><p>SQLite 仅保存密文；密钥材料只在 P3-143 专用 Keychain 项中。输入不会回显、不会进入日志或 Evidence。</p></div><label class="wide credential">DeepSeek API Key<div><input type="password" data-secret-field="apiKey" autocomplete="off" spellcheck="false" aria-label="DeepSeek API Key" placeholder="仅在此处手工输入" /><button class="button secondary" data-action="credential" ${state.busy ? "disabled" : ""}>加密保存</button></div><small>保存后输入框立即清空；保存本身不触发测试、模型读取、启用或发送。</small></label><div class="form-actions"><button class="button quiet danger" data-action="delete-credential" ${state.busy || !state.settings.hasCredential ? "disabled" : ""}>删除凭据</button></div></div>`;
  }

  function activationControls() {
    const deepSeek = isDeepSeek();
    const tested = hasSuccessfulTest();
    const models = state.settings?.availableModels || [];
    const selected = state.settings?.selectedModel || "";
    const pendingModel = state.pendingModel || selected;
    const allowCanary = deepSeek && tested && selected && state.settings?.enabled;
    const phase = gateIsReal() ? "真实 Gate：测试与 canary 仅在用户点击后访问 https://api.deepseek.com。" : "合成工程验证：所有动作无网络；真实 Gate 尚未启用。";
    return `<div class="activation-area"><p class="eyebrow">逐次激活</p><p class="gate-note">${icon("shield")} ${phase}</p><div class="form-actions"><button class="button secondary" data-action="test" ${state.busy || !deepSeek || !state.settings?.hasCredential ? "disabled" : ""}>${state.busy ? "正在测试…" : "测试并读取模型"}</button></div>${tested ? `<label class="wide">从刚刚测试的目录选择模型<select data-model-select aria-label="选择已测试模型"><option value="">请选择模型</option>${models.map((item) => `<option value="${escape(item)}" ${item === pendingModel ? "selected" : ""}>${escape(item)}</option>`).join("")}</select><small>选择后仍需点击“确认选择模型”；测试本身不会选择模型。</small></label><div class="form-actions"><button class="button secondary" data-action="confirm-model" ${state.busy || !state.pendingModel ? "disabled" : ""}>确认选择模型</button><button class="button secondary" data-action="enable" ${state.busy || !selected ? "disabled" : ""}>${state.settings?.enabled ? "禁用服务" : "显式启用所选模型"}</button><button class="button primary" data-action="canary" ${state.busy || !allowCanary ? "disabled" : ""}>发送固定无个人含义 canary</button></div>` : ""}${state.transientResponse ? `<div class="transient-response"><strong>瞬时响应（不保存）</strong><p>${escape(state.transientResponse)}</p><button class="button quiet" data-action="clear-response">清除瞬时响应</button></div>` : ""}</div>`;
  }

  function configForm() {
    const draft = state.drafts[state.draftMode];
    const list = providers(state.draftMode);
    const pending = isPending();
    const deepSeekDraft = state.draftMode === "cloud" && draft.providerId === "deepseek";
    const endpoint = deepSeekDraft ? "https://api.deepseek.com" : `offline://catalog/cloud/${draft.providerId}`;
    return `<section class="config-card" id="service-form"><div class="section-heading"><div><p class="eyebrow">${pending ? "未保存草稿" : "当前配置"}</p><h2>${active() ? "更换或调整服务" : "添加主服务"}</h2></div><span class="microcopy">保存前不会成为活动服务</span></div>${modeControl()}<div class="form-grid"><label>模型提供方<select data-field="providerId">${list.map((item) => `<option value="${item.id}" ${draft.providerId === item.id ? "selected" : ""}>${escape(item.label)}</option>`).join("")}</select></label><label>模型名称<input data-field="modelLabel" value="${escape(draft.modelLabel)}" maxlength="96" /></label>${state.draftMode === "cloud" ? `<label class="wide">服务端点<input value="${escape(endpoint)}" readonly aria-label="服务端点" /><small>${deepSeekDraft ? "固定精确 authority；不接受 HTTP、redirect 或自定义 endpoint。" : "仅目录识别。本轮不验证此 Provider，也不发起网络连接。"}</small></label>` : `<label class="wide">本地 Runtime<input value="synthetic-local-runtime-v1" readonly aria-label="本地 Runtime" /><small>这是离线 Adapter 标识；本轮不探测 Ollama、LM Studio 或本地进程。</small></label>`}</div><div class="form-actions"><button class="button primary" data-action="save" ${state.busy ? "disabled" : ""}>保存配置</button></div>${credentialControls()}${activationControls()}${state.notice ? `<p class="notice" role="status">${escape(state.notice)}</p>` : ""}</section>`;
  }

  function capabilityList() {
    const current = active();
    const supported = new Set(current ? state.settings.capabilityRegistry?.[current.providerId] || [] : []);
    const keys = ["text.reasoning", "vision.understanding", "speech.transcription", "speech.synthesis", "tool.use", "long_context", "structured_output", "embedding"];
    return `<section class="capability-card"><div class="section-heading"><div><p class="eyebrow">能力状态</p><h2>LifeOS 自动匹配</h2></div><span class="microcopy">目录 metadata，不等同真实验证</span></div><div class="capability-list">${keys.map((key) => `<div><span class="cap-icon">${supported.has(key) ? icon("check") : "–"}</span><strong>${capabilityNames[key]}</strong><small>${supported.has(key) ? (isDeepSeek() && !hasSuccessfulTest() ? "目录声明；尚未验证" : "可用") : current ? "当前服务不支持" : "尚未配置"}</small></div>`).join("")}</div></section>`;
  }

  function routing() {
    const policy = proposed().routingPolicy;
    const rows = [["preferLocal", "优先使用本地", "优先考虑当前已配置的本地能力"], ["allowCloudSupplement", "允许云端补齐", "默认关闭；没有明确授权时不选择云端"], ["allowAutomaticFailover", "服务失败时自动切换", "默认关闭；不会静默切到备用服务"], ["preferFastResponse", "优先响应更快", "只在已授权、能力匹配的服务中排序"]];
    return `<section class="routing-card"><div class="section-heading"><div><p class="eyebrow">运行策略</p><h2>按需要匹配能力</h2></div><span class="microcopy">默认失败关闭</span></div><div class="policy-list">${rows.map(([key, title, detail]) => `<label><input type="checkbox" data-policy="${key}" ${policy[key] ? "checked" : ""}/><span><strong>${title}</strong><small>${detail}</small></span></label>`).join("")}</div><div class="fallback"><span>${icon("tuning")}</span><div><strong>备用服务（可选）</strong><p>尚未配置，不会阻塞主服务。</p></div><span class="microcopy">视觉弱化</span></div></section>`;
  }

  function advanced() {
    return `<details class="advanced"><summary><span><b>高级设置</b><small>默认折叠 · 所有能力覆盖保持“自动”</small></span><i>⌄</i></summary><div class="advanced-body"><div class="overrides">${overrideKeys.map((key) => `<label>${({ text: "文字", vision: "视觉", speech_input: "语音输入", speech_output: "语音输出", tool_use: "工具调用", long_context: "长文本" })[key]}<select disabled><option>自动</option></select></label>`).join("")}</div><div class="advanced-values"><span>温度 <b>0.70</b></span><span>最大输出 <b>2048</b></span><span>超时 <b>60 秒</b></span><span>上下文 <b>32k</b></span></div><p>这些偏好只进入版本化 Settings DTO，不改变 Core Domain。</p></div></details>`;
  }

  function modelPage() {
    const gateLabel = gateIsReal() ? `${icon("shield")} DeepSeek 真实 Gate · 用户逐次操作` : `${icon("lock")} 合成离线工程验证 · 无网络`;
    return `<main class="settings-content" data-testid="model-settings"><header><div><p class="eyebrow">Settings · 辅助入口</p><h1>模型设置</h1><p>配置可替换的主 AI 服务。真实连接只限用户主动启用的 DeepSeek，且只发送固定无个人含义的 canary。</p></div><span class="offline-mark">${gateLabel}</span></header>${serviceCard()}<div class="settings-grid"><div class="main-stack">${configForm()}${routing()}${advanced()}</div><aside>${capabilityList()}</aside></div></main>`;
  }
  function composer() { return `<div class="global-ai" aria-label="Global AI 空间占位"><span>${icon("spark")}</span><span>问 LifeOS…</span><small>Settings 页面已弱化</small><button aria-label="发送" disabled>↑</button></div>`; }
  function render() { const content = state.page !== "settings" ? quietPage() : `<div class="settings-shell">${secondaryNav()}${state.section === "model" ? modelPage() : unavailablePage()}</div>`; app.innerHTML = `<div class="app-shell">${shell()}${content}</div>${composer()}`; }

  async function action(name, detail = "") {
    state.notice = "";
    try {
      if (name === "save") {
        state.busy = true; render();
        state.settings = await invoke("save_ai_provider_settings", { version: 1, settings: proposed() });
        state.pendingModel = "";
        state.notice = "配置已保存；保存本身不会测试、读取模型、启用或发送。";
      } else if (name === "credential") {
        const input = document.querySelector("[data-secret-field='apiKey']");
        let apiKey = input?.value || "";
        if (input) input.value = "";
        state.busy = true; render();
        try { state.settings = await invoke("save_ai_provider_credential", { version: 1, operation: "store", providerId: "deepseek", profileId: "default", apiKey }); } finally { apiKey = ""; }
        state.pendingModel = "";
        state.notice = "凭据已加密保存；输入框已清空，尚未测试或发送。";
      } else if (name === "delete-credential") {
        state.busy = true; render();
        state.settings = await invoke("save_ai_provider_credential", { version: 1, operation: "delete", providerId: "deepseek", profileId: "default" });
        state.pendingModel = "";
        state.transientResponse = "";
        state.notice = "凭据、密文 reference 与启用状态已删除；后续调用将失败关闭。";
      } else if (name === "test") {
        state.busy = true; render();
        state.settings = await invoke("test_ai_provider_connection", { version: 1, userAction: "user_test" });
        state.pendingModel = "";
        state.notice = gateIsReal() ? "测试完成；模型目录仅供本次明确选择。" : "合成模型目录测试完成；未执行网络请求。";
      } else if (name === "select-model") {
        if (!detail) return;
        state.settings = await invoke("set_ai_provider_enabled", { version: 1, operation: "select_model", modelId: detail });
        state.pendingModel = "";
        state.notice = "模型已选择；尚未启用或发送。";
      } else if (name === "confirm-model") {
        if (!state.pendingModel) return;
        await action("select-model", state.pendingModel);
        return;
      } else if (name === "enable") {
        state.settings = await invoke("set_ai_provider_enabled", { version: 1, operation: "set_enabled", enabled: !state.settings?.enabled });
        state.notice = state.settings.enabled ? "服务已显式启用；仍需单独点击发送。" : "服务已禁用；发送将被阻断。";
      } else if (name === "canary") {
        state.busy = true; render();
        const result = await invoke("assemble_global_ai_context", { version: 1, operation: "send_fixed_canary" });
        state.transientResponse = result.transientResponse || "";
        state.notice = "固定无个人含义 canary 已完成；响应仅在当前界面瞬时显示。";
      } else if (name === "clear-response") {
        state.transientResponse = "";
        state.notice = "瞬时响应已清除。";
      }
    } catch (error) {
      state.transientResponse = "";
      state.notice = error?.message || error?.code || "操作未完成，状态保持失败关闭。";
    } finally {
      state.busy = false;
      render();
    }
  }

  document.addEventListener("click", (event) => {
    const control = event.target.closest("[data-action]");
    if (!control) return;
    const [kind, value] = control.dataset.action.split(":");
    if (kind === "page") { state.page = value; state.notice = ""; state.transientResponse = ""; render(); return; }
    if (kind === "section") { state.section = value; state.notice = ""; state.transientResponse = ""; render(); return; }
    if (kind === "mode") { state.draftMode = value; state.notice = ""; state.transientResponse = ""; render(); return; }
    if (kind === "focus-form") { document.querySelector("#service-form")?.scrollIntoView({ behavior: "smooth", block: "start" }); return; }
    if (["save", "credential", "delete-credential", "test", "confirm-model", "enable", "canary", "clear-response"].includes(kind)) action(kind);
  });

  document.addEventListener("change", (event) => {
    const node = event.target;
    if (node.dataset.field) {
      state.drafts[state.draftMode][node.dataset.field] = node.value;
      state.notice = "草稿尚未保存，不会成为活动服务。";
      state.transientResponse = "";
      render();
    } else if ("modelSelect" in node.dataset) {
      state.pendingModel = node.value;
      state.notice = node.value ? "模型待确认；点击“确认选择模型”后才会保存选择。" : "";
      render();
    } else if (node.dataset.policy) {
      const base = state.settings?.settings || defaultSettings();
      if (!state.settings) state.settings = { settings: base, connectionState: "not_configured", enabled: false, hasCredential: false, providerRegistry: registry(), capabilityRegistry: {} };
      state.settings.settings.routingPolicy[node.dataset.policy] = node.checked;
      state.notice = "运行策略将与保存动作一起进入严格 DTO。";
      render();
    }
  });

  refresh().then(render).catch((error) => { state.notice = error?.message || "受控 Runtime 暂不可用。"; render(); });
})();
