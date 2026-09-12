(() => {
  "use strict";

  const app = document.querySelector("#app");
  const SYNTHETIC_CREDENTIAL = "synthetic-credential-fixture-v1";
  const capabilityNames = {
    "text.reasoning": "文字推理",
    "vision.understanding": "视觉理解",
    "speech.transcription": "语音输入",
    "speech.synthesis": "语音输出",
    "tool.use": "工具调用",
    "long_context": "长文本",
    "structured_output": "结构化输出",
    embedding: "嵌入",
  };
  const overrideKeys = ["text", "vision", "speech_input", "speech_output", "tool_use", "long_context"];
  const state = {
    settings: null,
    section: "model",
    page: "settings",
    notice: "",
    busy: false,
    drafts: {
      cloud: { providerId: "openai", modelLabel: "synthetic-text-v1" },
      local: { providerId: "ollama", modelLabel: "synthetic-local-v1" },
    },
    draftMode: "cloud",
  };

  const escape = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
  const invoke = (command, request) => {
    const target = window.__TAURI__?.core?.invoke;
    if (!target) return Promise.reject({ message: "仅 actual Tauri 可调用合成离线 Runtime。" });
    return target(command, { request });
  };
  const active = () => state.settings?.settings?.primary || null;
  const modeName = (mode) => mode === "cloud" ? "云端服务" : "本地服务";
  const registry = () => state.settings?.providerRegistry || [];
  const providers = (mode) => registry().filter((item) => item.mode === mode);
  const provider = (id) => registry().find((item) => item.id === id);
  const label = (id) => provider(id)?.label || "未选择服务";
  const connectionLabel = (value) => ({
    not_configured: "未配置",
    not_tested: "等待离线测试",
    synthetic_connected: "离线能力已验证",
  })[value] || "暂时不可用";
  const statusClass = (value) => value === "synthetic_connected" ? "success" : value === "not_configured" ? "muted" : "warning";
  const icon = (name) => ({ today: "⌂", me: "◌", contexts: "▢", memory: "▤", settings: "⚙", spark: "✦", cloud: "☁", local: "⌘", check: "✓", arrow: "›", tuning: "◒", lock: "◇" })[name] || "•";

  function defaultSettings() {
    const draft = state.drafts[state.draftMode];
    return {
      version: 1,
      primary: {
        mode: state.draftMode,
        providerId: draft.providerId,
        modelLabel: draft.modelLabel || (state.draftMode === "cloud" ? "synthetic-text-v1" : "synthetic-local-v1"),
        endpointUrl: state.draftMode === "cloud" ? `offline://catalog/cloud/${draft.providerId}` : null,
        localRuntime: state.draftMode === "local" ? "synthetic-local-runtime-v1" : null,
      },
      routingPolicy: {
        preferLocal: state.settings?.settings?.routingPolicy?.preferLocal ?? true,
        allowCloudSupplement: state.settings?.settings?.routingPolicy?.allowCloudSupplement ?? false,
        allowAutomaticFailover: state.settings?.settings?.routingPolicy?.allowAutomaticFailover ?? false,
        preferFastResponse: state.settings?.settings?.routingPolicy?.preferFastResponse ?? false,
      },
      fallback: { configured: false, providerId: null },
      advanced: {
        expanded: false,
        capabilityOverrides: Object.fromEntries(overrideKeys.map((key) => [key, "auto"])),
        temperature: 70,
        maxOutputTokens: 2048,
        timeoutSeconds: 60,
        contextWindow: 32,
      },
    };
  }

  function proposed() {
    const base = state.settings?.settings ? structuredClone(state.settings.settings) : defaultSettings();
    const draft = state.drafts[state.draftMode];
    base.primary = {
      mode: state.draftMode,
      providerId: draft.providerId,
      modelLabel: draft.modelLabel || (state.draftMode === "cloud" ? "synthetic-text-v1" : "synthetic-local-v1"),
      endpointUrl: state.draftMode === "cloud" ? `offline://catalog/cloud/${draft.providerId}` : null,
      localRuntime: state.draftMode === "local" ? "synthetic-local-runtime-v1" : null,
    };
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
    }
  }

  function railButton(id, labelText) {
    return `<button class="rail-button ${state.page === id ? "is-current" : ""}" data-action="page:${id}" aria-label="${labelText}" title="${labelText}">${icon(id)}</button>`;
  }

  function shell() {
    return `<nav class="rail" aria-label="LifeOS 主导航">
      <div class="brand" aria-label="LifeOS">${icon("spark")}</div>
      ${railButton("today", "Today")}${railButton("me", "Me")}${railButton("contexts", "Contexts")}${railButton("memory", "Memory")}
      <span class="rail-spacer"></span>${railButton("settings", "设置")}
    </nav>`;
  }

  function secondaryNav() {
    const items = [["general", "通用"], ["model", "模型设置"], ["privacy", "数据与隐私"], ["backup", "备份与导出"], ["about", "关于"]];
    return `<aside class="settings-nav" aria-label="设置导航"><p>设置</p>${items.map(([id, text]) => `<button data-action="section:${id}" class="${state.section === id ? "selected" : ""}">${text}${id !== "model" ? "<span>暂未开放</span>" : ""}</button>`).join("")}</aside>`;
  }

  function quietPage() {
    const names = { today: "Today", me: "Me", contexts: "Contexts", memory: "Memory" };
    return `<main class="quiet-page"><p class="eyebrow">LifeOS · ${names[state.page]}</p><h1>${names[state.page]}</h1><p>这个入口保持可达。P3-142 仅实现“模型设置”二级区域，不把其他页面伪装为已实现能力。</p><button class="button secondary" data-action="page:settings">前往模型设置</button></main>`;
  }

  function unavailablePage() {
    const title = { general: "通用", privacy: "数据与隐私", backup: "备份与导出", about: "关于" }[state.section];
    return `<section class="unavailable"><p class="eyebrow">Settings</p><h1>${title}</h1><p>暂未开放。此任务未实现该设置分类，也不会显示为可用能力。</p></section>`;
  }

  function serviceCard() {
    const current = active();
    if (!current) return `<section class="service-card empty" data-testid="primary-unconfigured"><div><span class="slot-icon">${icon("spark")}</span><p class="eyebrow">主 AI 服务</p><h2>还没有配置服务</h2><p>只需添加一个主服务。文字、视觉、语音和工具能力由 LifeOS 根据服务 metadata 自动匹配。</p></div><button class="button primary" data-action="focus-form">添加服务</button></section>`;
    const supported = state.settings.capabilityRegistry?.[current.providerId] || [];
    return `<section class="service-card" data-testid="primary-configured"><div class="service-head"><div><span class="slot-icon">${current.mode === "cloud" ? icon("cloud") : icon("local")}</span><p class="eyebrow">主 AI 服务</p><h2>${escape(label(current.providerId))}</h2><p>${escape(current.modelLabel)} · ${current.mode === "cloud" ? "合成云端目录" : "合成本地 Runtime"}</p></div><span class="state-dot ${statusClass(state.settings.connectionState)}">${connectionLabel(state.settings.connectionState)}</span></div><div class="capability-pills">${supported.slice(0, 5).map((item) => `<span>${icon("check")} ${capabilityNames[item] || item}</span>`).join("")}</div></section>`;
  }

  function modeControl() {
    return `<div class="mode-control" role="group" aria-label="服务处理位置">
      <button data-action="mode:cloud" aria-pressed="${state.draftMode === "cloud"}"><strong>${icon("cloud")} 云端服务</strong><small>使用可替换的云端服务目录</small></button>
      <button data-action="mode:local" aria-pressed="${state.draftMode === "local"}"><strong>${icon("local")} 本地服务</strong><small>使用设备上的本地服务目录</small></button>
    </div>`;
  }

  function configForm() {
    const draft = state.drafts[state.draftMode];
    const list = providers(state.draftMode);
    const pending = isPending();
    return `<section class="config-card" id="service-form"><div class="section-heading"><div><p class="eyebrow">${pending ? "未保存草稿" : "当前配置"}</p><h2>${active() ? "更换或调整服务" : "添加主服务"}</h2></div><span class="microcopy">${pending ? "保存前不会成为活动服务" : "已保存的活动服务"}</span></div>
      ${modeControl()}
      <div class="form-grid">
        <label>模型提供方<select data-field="providerId">${list.map((item) => `<option value="${item.id}" ${draft.providerId === item.id ? "selected" : ""}>${escape(item.label)}</option>`).join("")}</select></label>
        <label>模型名称<input data-field="modelLabel" value="${escape(draft.modelLabel)}" maxlength="96" /></label>
        ${state.draftMode === "cloud" ? `<label class="wide">合成服务端点<input value="offline://catalog/cloud/${escape(draft.providerId)}" readonly aria-label="合成服务端点" /><small>仅用于离线目录识别；不会发起网络连接。</small></label><label class="wide credential">API Key（固定非秘密夹具）<div><input type="password" value="${SYNTHETIC_CREDENTIAL}" readonly aria-label="固定非秘密 API Key 夹具" /><button class="button secondary" data-action="credential">保存合成凭据引用</button></div><small>页面只显示掩码；持久化仅保存不可用的合成引用。</small></label>` : `<label class="wide">本地 Runtime<input value="synthetic-local-runtime-v1" readonly aria-label="合成本地 Runtime" /><small>这是离线 Adapter 标识，不会探测 Ollama、LM Studio 或本地进程。</small></label>`}
      </div>
      <div class="form-actions"><button class="button primary" data-action="save" ${state.busy ? "disabled" : ""}>保存配置</button><button class="button secondary" data-action="test" ${state.busy || !active() ? "disabled" : ""}>${state.busy ? "测试中…" : "离线测试连接"}</button><button class="button quiet" data-action="enable" ${state.settings?.connectionState !== "synthetic_connected" ? "disabled" : ""}>${state.settings?.enabled ? "已启用" : "显式启用"}</button></div>
      ${state.notice ? `<p class="notice" role="status">${escape(state.notice)}</p>` : ""}
    </section>`;
  }

  function capabilityList() {
    const current = active();
    const supported = new Set(current ? state.settings.capabilityRegistry?.[current.providerId] || [] : []);
    const keys = ["text.reasoning", "vision.understanding", "speech.transcription", "speech.synthesis", "tool.use", "long_context", "structured_output", "embedding"];
    return `<section class="capability-card"><div class="section-heading"><div><p class="eyebrow">能力状态</p><h2>LifeOS 自动匹配</h2></div><span class="microcopy">不需要逐项选择模型</span></div><div class="capability-list">${keys.map((key) => `<div><span class="cap-icon">${supported.has(key) ? icon("check") : "–"}</span><strong>${capabilityNames[key]}</strong><small>${supported.has(key) ? (current?.mode === "local" ? "本地处理" : "可用") : current ? "当前服务不支持 · 前往服务目录补齐" : "尚未配置"}</small></div>`).join("")}</div></section>`;
  }

  function routing() {
    const policy = proposed().routingPolicy;
    return `<section class="routing-card"><div class="section-heading"><div><p class="eyebrow">运行策略</p><h2>按需要匹配能力</h2></div><span class="microcopy">默认失败关闭</span></div><div class="policy-list">
      ${[["preferLocal", "优先使用本地", "优先考虑当前已配置的本地能力"], ["allowCloudSupplement", "允许云端补齐", "默认关闭；没有明确授权时不选择云端"], ["allowAutomaticFailover", "服务失败时自动切换", "默认关闭；不会静默切到备用服务"], ["preferFastResponse", "优先响应更快", "只在已授权、能力匹配的服务中排序"]].map(([key, title, detail]) => `<label><input type="checkbox" data-policy="${key}" ${policy[key] ? "checked" : ""}/><span><strong>${title}</strong><small>${detail}</small></span></label>`).join("")}
    </div><div class="fallback"><span>${icon("tuning")}</span><div><strong>备用服务（可选）</strong><p>尚未配置，不会阻塞主服务。</p></div><span class="microcopy">视觉弱化</span></div></section>`;
  }

  function advanced() {
    return `<details class="advanced"><summary><span><b>高级设置</b><small>默认折叠 · 所有能力覆盖保持“自动”</small></span><i>⌄</i></summary><div class="advanced-body"><div class="overrides">${overrideKeys.map((key) => `<label>${({ text: "文字", vision: "视觉", speech_input: "语音输入", speech_output: "语音输出", tool_use: "工具调用", long_context: "长文本" })[key]}<select disabled><option>自动</option></select></label>`).join("")}</div><div class="advanced-values"><span>温度 <b>0.70</b></span><span>最大输出 <b>2048</b></span><span>超时 <b>60 秒</b></span><span>上下文 <b>32k</b></span></div><p>这些合成偏好只进入版本化 Settings DTO，不改变 Core Domain。</p></div></details>`;
  }

  function modelPage() {
    return `<main class="settings-content" data-testid="model-settings"><header><div><p class="eyebrow">Settings · 辅助入口</p><h1>模型设置</h1><p>配置一个可替换的主 AI 服务；LifeOS 会按授权、处理位置与能力状态自动匹配。</p></div><span class="offline-mark">${icon("lock")} 合成离线 · 无网络</span></header>${serviceCard()}<div class="settings-grid"><div class="main-stack">${configForm()}${routing()}${advanced()}</div><aside>${capabilityList()}</aside></div></main>`;
  }

  function composer() {
    return `<div class="global-ai" aria-label="Global AI 合成占位"><span>${icon("spark")}</span><span>问 LifeOS…</span><small>Settings 页面已弱化</small><button aria-label="发送" disabled>↑</button></div>`;
  }

  function render() {
    const content = state.page !== "settings" ? quietPage() : `<div class="settings-shell">${secondaryNav()}${state.section === "model" ? modelPage() : unavailablePage()}</div>`;
    app.innerHTML = `<div class="app-shell">${shell()}${content}</div>${composer()}`;
  }

  async function action(name) {
    state.notice = "";
    try {
      if (name === "save") {
        state.busy = true; render();
        state.settings = await invoke("save_ai_provider_settings", { version: 1, settings: proposed() });
        state.notice = "配置已保存；请运行离线测试后再显式启用。";
      } else if (name === "credential") {
        state.settings = await invoke("save_ai_provider_credential", { version: 1, operation: "store_synthetic_reference", credentialFixture: SYNTHETIC_CREDENTIAL });
        state.notice = "已保存合成凭据引用；没有保存真实 API Key。";
      } else if (name === "test") {
        state.busy = true; render();
        state.settings = await invoke("test_ai_provider_connection", { version: 1, simulate: "offline_metadata" });
        state.notice = "离线 metadata Adapter 测试成功；未执行 DNS、HTTP(S) 或模型探测。";
      } else if (name === "enable") {
        state.settings = await invoke("set_ai_provider_enabled", { version: 1, enabled: true });
        state.notice = "主 AI 服务已显式启用，仅限合成离线能力状态。";
      }
    } catch (error) {
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
    if (kind === "page") { state.page = value; state.notice = ""; render(); }
    if (kind === "section") { state.section = value; state.notice = ""; render(); }
    if (kind === "mode") { state.draftMode = value; state.notice = ""; render(); }
    if (kind === "focus-form") document.querySelector("#service-form")?.scrollIntoView({ behavior: "smooth", block: "start" });
    if (["save", "credential", "test", "enable"].includes(kind)) action(kind);
  });

  document.addEventListener("change", (event) => {
    const node = event.target;
    if (node.dataset.field) {
      state.drafts[state.draftMode][node.dataset.field] = node.value;
      state.notice = "草稿尚未保存，不会跨模式成为活动服务。";
      render();
    }
    if (node.dataset.policy) {
      const base = state.settings?.settings || defaultSettings();
      if (!state.settings) state.settings = { settings: base, connectionState: "not_configured", enabled: false, providerRegistry: registry(), capabilityRegistry: {} };
      state.settings.settings.routingPolicy[node.dataset.policy] = node.checked;
      state.notice = "运行策略将与保存动作一起进入严格 DTO。";
      render();
    }
  });

  refresh().then(render).catch((error) => { state.notice = error?.message || "合成 Runtime 暂不可用。"; render(); });
})();
