"use strict";

// P3-134 deliberately leaves the P3-116 renderer in app.js intact.  This
// adapter is the only Runtime seam: it maps typed P3-141 DTOs to existing
// P3-116 nodes and intercepts only the actions that now have a local meaning.
(() => {
  const ui = window.__P3_116_RUNTIME__;
  if (!ui) return;

  const CONTEXT = "ctx:project:local-work-self-use";
  const SYN_TEXT = "整理 LifeOS Context Recovery 合成验收记录。";
  const SYN_KEY = "p3-141-synthetic-capture-001";
  const SYN_SHORT = "LifeOS Context Recovery 合成记录。";
  const SYN_SHORT_KEY = "p3-141-insufficient-001";
  const SYN_EDIT = "整理并复核 LifeOS Context Recovery 合成验收记录。";
  const SYN_RESULT = "已完成合成验收记录整理与复核。";
  const REAL_RESULT = "用户在本地标记为已完成。";
  const runtime = { status: null, today: null, recovery: null, next: null, global: null, understanding: null, provider: null, error: null, busy: false, sequence: 0, removed: [], lastCapture: null, pendingCaptureId: null, selectedWorkId: null, includeRelatedPersonalContent: false, disclosurePending: false, editSuggestion: false, pendingModel: null };

  const invoke = (command, request) => {
    const target = window.__TAURI__?.core?.invoke;
    if (!target) return Promise.reject({ code: "tauri_invoke_unavailable", message: "仅 actual Tauri 可调用本地 Runtime。" });
    return target(command, { request });
  };
  const page = () => ui.state.page === "detail" ? "context_detail" : "today";
  const isReal = () => runtime.status?.input_mode === "real_self_use";
  const key = (label) => {
    if (!isReal()) return `p3-141-ui-${label}-${++runtime.sequence}`;
    const unique = globalThis.crypto?.randomUUID?.() || `${Date.now()}-${++runtime.sequence}`;
    return `p3-141-real-ui-${label}-${unique}`;
  };
  const clean = (value) => String(value || "").replace(/[<>&"']/g, (char) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;", "'": "&#39;" }[char]));
  const localError = (error) => { runtime.error = { code: error?.code || "runtime_unavailable", message: error?.message || "本地 Runtime 未显示成功；没有写入。" }; };

  async function refresh() {
    runtime.status = await invoke("runtime_status", {});
    // P3-140 loads before this adapter and intentionally reads only the
    // retained P3-116 UI container. Publish this non-sensitive mode flag at
    // that fixed seam so its Health DTO uses the same closed source contract.
    ui.p3_141_runtime_status = runtime.status;
    runtime.today = await invoke("get_today", {});
    runtime.recovery = await invoke("get_context_recovery", { context_id: CONTEXT });
    runtime.next = null;
    const selection = runtime.today.records?.find((record) => record.id === runtime.selectedWorkId)?.id || null;
    runtime.global = await invoke("assemble_global_ai_context", { page: page(), ...(selection ? { selection_ref: selection } : {}), ...(runtime.removed.length ? { removed_context_kinds: runtime.removed } : {}), ...(runtime.includeRelatedPersonalContent ? { include_related_personal_content: true } : {}) });
    runtime.provider = await invoke("get_ai_provider_settings", {});
  }

  function setText(node, value) { if (node && node.textContent !== value) node.textContent = value; }
  function runtimeMode() { const actions = runtime.today?.confirmed_actions || []; return actions.length ? "normal" : runtime.today?.records?.length ? "insufficient" : "empty"; }

  function applyToday() {
    const target = runtimeMode();
    if (ui.state.page === "today" && ui.state.todayMode !== target) { ui.state.todayMode = target; ui.render(); return true; }
    const focus = runtime.today?.confirmed_actions?.[0];
    if (focus) {
      setText(document.querySelector(".reference-focus .focus-title"), focus.text);
      setText(document.querySelector(".reference-focus .focus-subtitle"), "已确认的用户选择 · Request-local 建议已完成");
      setText(document.querySelector(".reference-focus .focus-reason"), "来自你已确认且开放的 Action；不是自动创建。");
      const actions = document.querySelector(".reference-focus .actions");
      if (actions && !actions.querySelector("[data-action='runtime:complete']")) actions.insertAdjacentHTML("beforeend", '<button class="button" type="button" data-action="runtime:complete">标记完成</button>');
    }
    const noticed = runtime.today?.lifeos_noticed;
    const noticedCard = document.querySelector(".noticed-card");
    if (noticedCard) {
      const copy = noticedCard.querySelector(".noticed-copy");
      const actions = noticedCard.querySelector(".actions");
      const basis = noticed?.basis_refs || [];
      if (noticed && basis.length) {
        setText(copy, noticed.text);
        noticedCard.hidden = false;
        actions?.removeAttribute("hidden");
        noticedCard.dataset.evidence = "runtime-basis-present";
      } else {
        noticedCard.hidden = true;
        noticedCard.dataset.evidence = "no-reliable-basis";
      }
    }
    return false;
  }

  function disclosure() {
    document.querySelectorAll(".page-wrap .panel, .workspace .panel").forEach((panel) => {
      const label = panel.querySelector(".section-label, .eyebrow");
      if (label && /(现在的我|正在关注|长期视角|理解|Memory|Health|最近睡眠|训练恢复)/.test(panel.textContent || "")) panel.dataset.authority = "fixed-synthetic-or-unwired";
    });
    document.querySelectorAll(".page-wrap p, .workspace p").forEach((node) => {
      if (node.textContent.includes("深度智能已启用")) node.textContent = "固定合成展示；此内容尚未接入 Runtime。";
      if (node.textContent.includes("实时更新")) node.textContent = "固定合成展示；不是 Runtime 事实。";
    });
  }

  function decorateModal() {
    const box = document.querySelector(".capture-original");
    if (!box || box.dataset.runtimeBound) return;
    box.dataset.runtimeBound = "true";
    const buttons = [...document.querySelectorAll(".modal .actions [data-action]")];
    if (isReal()) {
      // This is the single real-mode seam. It retains the P3-134 modal and
      // visual tokens, but never presents a fixed synthetic value as a user
      // input. The value is read before run() can trigger a render.
      box.replaceChildren();
      const label = document.createElement("label");
      label.htmlFor = "real-capture-text";
      label.innerHTML = "<strong>用户原文 · 仅本地保存</strong>";
      const input = document.createElement("textarea");
      input.id = "real-capture-text";
      input.name = "realCaptureText";
      input.maxLength = 200;
      input.rows = 4;
      input.placeholder = "输入一条不超过 200 字的低敏感 Work 记录";
      input.setAttribute("aria-label", "输入一条不超过 200 字的低敏感 Work 记录");
      input.style.cssText = "display:block;width:100%;resize:vertical;border:1px solid #cfd9df;border-radius:9px;padding:10px 11px;background:#fff;color:#263650;font:inherit;line-height:1.5;";
      const hint = document.createElement("small");
      hint.textContent = "只会在此设备的受控本地数据库保存；关联与下一步仍须你显式确认。";
      hint.style.cssText = "display:block;margin-top:7px;color:#63717c;";
      box.append(label, input, hint);
      const modal = box.closest(".modal");
      [...(modal?.querySelectorAll("p") || [])].forEach((node) => {
        if (node.textContent.includes("演示状态只保留在内存中")) node.textContent = "此输入只会保存到此设备的受控本地数据库；不会发送到模型或外部服务。";
      });
      if (runtime.pendingCaptureId) {
        if (buttons[0]) {
          buttons[0].dataset.action = "runtime:confirm";
          buttons[0].textContent = "确认 Context";
          buttons[0].setAttribute("aria-label", "确认这条 Capture 的 Context");
        }
      } else if (buttons[0]) {
        buttons[0].dataset.action = "runtime:capture";
        buttons[0].textContent = "仅保存 Capture";
        buttons[0].setAttribute("aria-label", "仅保存这条 Capture，不确认关联或下一步");
      }
      if (buttons[1]) buttons[1].dataset.action = "close-modal";
      return;
    }
    // Preserve the byte-identical P3-116 Capture surface.  The fixed
    // synthetic value stays inside this adapter and is never rendered as a
    // replacement input control; only the existing control's action changes.
    if (runtime.lastCapture?.record) {
      if (buttons[0]) {
        buttons[0].dataset.action = "runtime:confirm";
        buttons[0].textContent = "确认长期关联";
      }
      if (buttons[1]) {
        buttons[1].dataset.action = "close-modal";
        buttons[1].textContent = "暂不关联";
      }
    } else {
      if (buttons[0]) {
        buttons[0].dataset.action = "runtime:capture";
        buttons[0].textContent = "仅保存 Work";
        buttons[0].setAttribute("aria-label", "仅保存这条 Work，不创建长期关联");
      }
      if (buttons[1]) {
        buttons[1].dataset.action = "close-modal";
        buttons[1].textContent = "关闭";
      }
    }
  }

  function bindContextDetail() {
    if (ui.state.page !== "detail" || !runtime.recovery) return;
    const text = document.querySelector("#main-content");
    if (!text) return;
    text.dataset.runtimeContext = runtime.recovery.context_id;
    const next = runtime.next?.candidates?.[0];
    if (next) { const section = [...text.querySelectorAll("section")].find((item) => /Next/.test(item.textContent || "")); const lead = section?.querySelector("p"); if (lead) lead.textContent = next.text; }
  }

  function bindLegacyGlobal() {
    const panel = document.querySelector(".ai-panel");
    if (!panel || !runtime.global) return;
    panel.dataset.runtimeContext = "request-local";
    if (isReal()) {
      const intro = panel.querySelector(".ai-panel-head + p.quiet");
      if (intro) intro.textContent = "真实输入只会在你完成保存、测试、启用和显式发送后进入已选 Provider；不会自动读取或发送。";
      panel.querySelector("[data-action='remove-health']")?.parentElement.remove();
    }
    const chips = panel.querySelector(".context-chip-wrap");
    if (chips) {
      const existing = new Set([...chips.querySelectorAll(".context-chip")].map((node) => node.textContent.trim()));
      runtime.global.included.forEach((item) => {
        const name = item.kind === "person" ? "Person" : item.kind === "page" ? `Page: ${item.reference}` : item.kind === "selection" ? "Selection" : null;
        if (name && !existing.has(name)) chips.insertAdjacentHTML("beforeend", `<span class="context-chip">${clean(name)}</span>`);
      });
    }
    const existingInspector = panel.querySelector("[data-provider-inspector]");
    if (!existingInspector && runtime.provider) {
      const host = runtime.provider.settings.base_url ? runtime.provider.settings.base_url.replace(/^https?:\/\//, "").split("/")[0] : "未配置";
      const selectedCount = runtime.today?.records?.length ? 1 : 0;
      panel.insertAdjacentHTML("beforeend", `<section class="context-diff" data-provider-inspector><strong>本次发送前检查</strong><br>Provider：${clean(runtime.provider.settings.profile || "未配置")} · 模型：${clean(runtime.provider.settings.model || "未选择")}<br>目标：${clean(host)} · Work 记录：${selectedCount} / 3<br>类别：Person、Page、Selection、Evidence refs；可先移除类别再发送。</section>`);
    }
    const candidate = runtime.next?.candidates?.[0];
    if (candidate) { const candidateText = panel.querySelector(".ai-card p"); if (candidateText) candidateText.textContent = `候选：${candidate.text}`; }
    const answer = panel.querySelector(".ai-answer");
    if (answer) {
      const identity = answer.querySelector(".identity");
      const copy = answer.querySelector("p");
      const actions = answer.querySelector(".actions");
      const provider = runtime.provider;
      if (runtime.understanding?.understanding_id) {
        if (identity) identity.textContent = "AI Observation / Suggestion · 待用户判断";
        if (copy) copy.textContent = runtime.understanding.observation || runtime.understanding.suggestion || runtime.understanding.disclosure || "暂时没有足够证据判断。";
        if (actions) actions.innerHTML = '<input class="feedback-edit" data-understanding-edit placeholder="编辑后确认（可选）"><button class="button" type="button" data-action="runtime:feedback-confirm">确认</button><button class="button" type="button" data-action="runtime:feedback-edit-confirm">编辑确认</button><button class="button ghost" type="button" data-action="runtime:feedback-reject">拒绝</button><button class="button ghost" type="button" data-action="runtime:feedback-ignore">忽略</button><button class="button ghost" type="button" data-action="runtime:feedback-correct">纠正</button>';
        answer.dataset.authority = "provider-output-not-action";
      } else {
        if (identity) identity.textContent = "尚未请求模型";
        if (copy) copy.textContent = provider?.enabled ? `当前 Context 将发送到 ${provider.settings.profile} · ${provider.settings.model}；仅在你点击后执行。` : "请先在 Settings 保存、测试并启用一个 Provider；不会自动调用模型。";
        if (actions) actions.innerHTML = '<button class="button primary" type="button" data-action="runtime:send-understanding">请求当前 Context 的理解</button>';
        answer.dataset.authority = "explicit-user-request-required";
      }
    }
    panel.querySelectorAll("[data-action='candidate:action:confirm']").forEach((button) => { button.dataset.action = "runtime:accept"; });
    panel.querySelectorAll("[data-action='candidate:action:edit']").forEach((button) => {
      if (isReal()) button.remove();
      else button.dataset.action = "runtime:edit-accept";
    });
    panel.querySelectorAll("[data-action='candidate:action:reject']").forEach((button) => { button.dataset.action = "runtime:reject"; });
    panel.querySelectorAll("[data-action='candidate:action:ignore']").forEach((button) => { button.dataset.action = "runtime:defer"; });
    panel.querySelectorAll("[data-action='candidate:decision:confirm']").forEach((button) => { button.dataset.action = "runtime:feedback-confirm"; });
    panel.querySelectorAll("[data-action='candidate:decision:correct']").forEach((button) => { button.dataset.action = "runtime:feedback-correct"; });
  }

  function providerSummary() {
    const settings = runtime.provider?.settings || {};
    const host = settings.base_url ? settings.base_url.replace(/^https?:\/\//, "").split("/")[0] : "未配置";
    return `Provider：${clean(settings.profile || "未配置")} · 模型：${clean(settings.model || "未选择")} · 目标：${clean(host)}`;
  }

  function bindGlobal() {
    const panel = document.querySelector(".ai-panel");
    if (!panel) return;
    const records = runtime.today?.records || [];
    const selected = records.find((record) => record.id === runtime.selectedWorkId) || null;
    const selectedRow = selected
      ? `<section class="context-diff p3137-selection" data-runtime-selection="${clean(selected.id)}"><strong>已选 Work</strong><p>${clean(selected.content)}</p><button class="button ghost" type="button" data-action="runtime:clear-selection">更换</button></section>`
      : `<section class="context-diff"><strong>先选择一条 Work 记录</strong><p>只有你选中的这一条会成为默认请求内容。</p></section>`;
    const rows = records.length
      ? records.map((record) => `<button class="context-primary p3137-work-row" type="button" data-action="runtime:select-work:${clean(record.id)}" aria-pressed="${record.id === runtime.selectedWorkId}"><span><strong>${clean(record.content)}</strong><small>用户原文 · Work</small></span></button>`).join("")
      : `<p class="quiet">还没有可选择的 Work 记录。可先用 Quick Capture 保存一条记录。</p>`;
    const bundle = runtime.global;
    const compactDetails = selected && bundle ? `<details class="panel p3137-inspector"><summary>查看本次范围</summary><p>本次会使用当前记录、页面状态、最小 Work 身份、Project 身份和 Evidence 引用。</p><ul>${bundle.included.map((item) => `<li>${clean(item.kind)}：${clean(item.inclusion_reason)}</li>`).join("")}</ul>${!runtime.includeRelatedPersonalContent ? '<button class="button ghost" type="button" data-action="runtime:include-related">加入 1 项相关资料</button>' : ""}</details>` : "";
    let body = "";
    if (runtime.disclosurePending && bundle?.disclosure_required) {
      body = `<section class="notice mint p3137-disclosure"><strong>将使用当前记录和 ${bundle.additional_personal_count} 项相关资料</strong><p>确认前不会向 Provider 发出请求。${providerSummary()}</p><div class="actions"><button class="button" type="button" data-action="runtime:remove-related">移除相关资料</button><button class="button ghost" type="button" data-action="runtime:cancel-disclosure">取消</button><button class="button primary" type="button" data-action="runtime:confirm-disclosure">确认并请求</button></div></section>`;
    } else if (runtime.understanding?.understanding_id) {
      const text = runtime.understanding.observation || runtime.understanding.suggestion || "暂时没有足够证据给出建议。";
      const editControl = runtime.editSuggestion ? '<label class="feedback-edit">修改后采纳<input data-understanding-edit aria-label="修改建议后采纳" placeholder="写下你确认的下一步"></label><button class="button" type="button" data-action="runtime:edit-adopt">修改后采纳</button>' : '<button class="button" type="button" data-action="runtime:edit-suggestion">修改</button>';
      body = `<section class="ai-answer p3137-understanding"><div><span class="identity observation">AI Observation / Suggestion</span></div><p>${clean(text)}</p><small>Evidence：${runtime.understanding.basis_refs.map(clean).join("、") || "不足"} · 不确定性：${clean(runtime.understanding.evidence_state)}</small><div class="actions"><button class="button primary" type="button" data-action="runtime:adopt">采纳</button>${editControl}<button class="button ghost" type="button" data-action="runtime:ignore">忽略</button><button class="button ghost" type="button" data-action="runtime:reject-understanding">拒绝</button><button class="button ghost" type="button" data-action="runtime:correct-understanding">纠正</button></div></section><details class="panel p3137-link"><summary>可选的长期关联建议</summary><p>这不会影响刚才的请求；只有你确认后才保存为 Persistent Link。</p><div class="actions"><button class="button" type="button" data-action="runtime:confirm-link">确认关联</button><button class="button ghost" type="button" data-action="runtime:reject-link">不关联</button></div></details>`;
    } else if (runtime.understanding?.disclosure) {
      body = `<section class="notice"><strong>尚未生成建议</strong><p>${clean(runtime.understanding.disclosure)}</p><p>${providerSummary()}</p></section>`;
    } else if (selected) {
      body = `<section class="ai-answer p3137-ask"><p>准备好后，一次点击即可请求这一条 Work 的下一步建议。</p><p class="tiny">${providerSummary()}</p><div class="actions"><button class="button primary" type="button" data-action="runtime:ask">帮我理清下一步</button></div></section>`;
    }
    panel.innerHTML = `<div class="ai-panel-head"><div><span class="eyebrow">Work AI</span><h2>帮我理清下一步</h2></div><button class="close" type="button" data-action="close-ai" aria-label="关闭">×</button></div><p class="quiet">选择一条 Work，再决定是否采纳、修改或忽略建议。Context 会在后台按本次请求组装。</p>${selectedRow}<section class="panel p3137-work-list"><span class="section-label">Work 记录</span>${rows}</section>${compactDetails}${body}`;
    panel.dataset.runtimeContext = "request-local";
  }

  function settingsPage() {
    const provider = runtime.provider;
    if (!provider) return;
    const setting = provider.settings;
    const displayMode = setting.mode === "local" ? "local" : "cloud";
    const cloudMode = displayMode === "cloud";
    const option = (value, label) => `<option value="${value}" ${setting.profile === value ? "selected" : ""}>${label}</option>`;
    const profiles = cloudMode ? `${option("openai", "OpenAI")}${option("anthropic", "Anthropic")}${option("deepseek", "DeepSeek")}${option("kimi", "Kimi")}${option("cloud_custom_openai_compatible", "自定义 OpenAI-compatible")}` : `${option("ollama", "Ollama")}${option("lm_studio", "LM Studio")}${option("local_custom_compatible", "自定义本地兼容服务")}`;
    const stateLabel = ({ not_configured: "未配置", not_tested: "未测试", not_tested_after_restart: "需要重新测试", testing: "测试中", connected: "已连接", failed: "失败", disabled: "已停用" })[provider.connection_state] || "未测试";
    const models = Array.isArray(provider.discovered_models) ? provider.discovered_models : [];
    const selectedModel = models.includes(runtime.pendingModel) ? runtime.pendingModel : models.includes(setting.model) ? setting.model : "";
    const active = Boolean(provider.enabled && selectedModel === setting.model);
    const checkedAt = provider.last_tested_at_ms == null ? "—" : new Date(provider.last_tested_at_ms).toLocaleTimeString();
    const keyPresent = Boolean(provider.credential?.present);
    const root = document.querySelector("#main-content");
    if (!root || ui.state.page !== "settings") return;
    const modeCard = (value, glyph, title, detail) => `<label class="mode-card ${displayMode === value ? "selected" : ""}"><span class="mode-glyph" aria-hidden="true">${glyph}</span><span><strong>${title}</strong><small>${detail}</small></span><input name="provider-mode" type="radio" value="${value}" ${displayMode === value ? "checked" : ""}></label>`;
    const modelOptions = models.length ? `<option value="" ${selectedModel ? "" : "selected"} disabled>选择一个可用模型</option>${models.map((model) => `<option value="${clean(model)}" ${selectedModel === model ? "selected" : ""}>${clean(model)}</option>`).join("")}` : '<option value="">测试连接后显示可用模型</option>';
    const modelAction = active ? '<button class="button model-current-action" type="button" disabled>✓ 当前正在使用</button>' : selectedModel ? '<button class="button primary" type="button" data-action="provider:model-select">选择此模型</button><button class="button" type="button" data-action="provider:enable">启用已选模型</button>' : '<button class="button" type="button" disabled>先测试并选择模型</button>';
    const credential = cloudMode ? `<label class="span-2 credential-field">API Key<input name="provider-credential" type="password" autocomplete="new-password" placeholder="${keyPresent ? "已保存；输入新值可更新" : "输入 API Key"}"></label>` : '<div class="span-2 local-connection-note"><strong>本地模型不需要 API Key</strong><span>仅连接到你选择的 loopback 或私有局域网模型服务。</span></div>';
    root.innerHTML = `<header class="page-header provider-header"><div><h1>模型设置</h1><p>配置 LifeOS 使用的云端或本地模型。</p></div></header>
      <section class="panel provider-panel provider-mode-panel"><div class="settings-card-head"><div><span class="section-label">运行模式</span><p>先选择连接方式，再配置并测试。</p></div></div><div class="mode-cards" role="radiogroup" aria-label="运行模式">${modeCard("cloud", "☁", "云端模型", "OpenAI、Anthropic、DeepSeek、Kimi 或 OpenAI-compatible 服务")}${modeCard("local", "▣", "本地模型", "Ollama、LM Studio 或本地兼容服务")}</div></section>
      <div class="provider-layout"><div class="provider-left stack"><section class="panel provider-panel provider-connection-card"><div class="settings-card-head"><div><span class="section-label">连接配置</span><p>保存、测试、选择、启用和发送是彼此分离的操作。</p></div><span class="mode-chip">${cloudMode ? "云端" : "本地"}</span></div><div class="provider-grid"><label>Provider<select name="provider-profile">${profiles}</select></label><label>接口地址<input name="provider-base-url" value="${clean(setting.base_url)}" autocomplete="off" spellcheck="false" placeholder="${cloudMode ? "https://api.example.com" : "http://127.0.0.1:11434"}"></label>${credential}</div><p class="session-boundary-note"><span aria-hidden="true">✓</span>${cloudMode ? (keyPresent ? `API Key 已加密保存（${clean(provider.credential?.masked || "已保存")}）；可更新或删除。` : "API Key 将加密保存到受控本地 SQLite，密钥材料与数据库分离。") : "本地连接不会索取或保存 API Key。"}</p><div class="actions"><button class="button" type="button" data-action="provider:save">保存配置</button>${cloudMode ? '<button class="button" type="button" data-action="provider:credential-save">保存 API Key</button>' : ""}<button class="button primary" type="button" data-action="provider:test">测试连接</button>${cloudMode && keyPresent ? '<button class="button danger-quiet" type="button" data-action="provider:clear-credential">删除已保存 API Key</button>' : ""}</div></section>
        <section class="panel provider-panel connection-status" data-provider-state="${clean(provider.connection_state)}"><div class="settings-card-head"><div><span class="section-label">连接状态</span><p>手动测试后显示可用模型。</p></div></div><div class="connection-metrics"><div><span>状态</span><strong class="${provider.connection_state === "connected" ? "status-ok" : ""}">${stateLabel}</strong></div><div><span>延迟</span><strong>${provider.last_latency_ms == null ? "—" : `${provider.last_latency_ms} ms`}</strong></div><div><span>最近检查</span><strong>${checkedAt}</strong></div></div><p class="tiny">连接测试不发送个人 Context。</p></section></div>
        <aside class="stack"><section class="panel provider-panel current-model-card"><div class="settings-card-head"><div><span class="section-label">当前启用模型</span><p>从刚刚测试成功的接口返回结果中选择。</p></div>${active ? '<span class="pill mint">正在使用</span>' : ""}</div><div class="active-model-display"><span>${active ? `${clean(setting.model)} · ${clean(setting.profile)}` : "尚未选择模型"}</span>${active ? '<span class="pill mint">正在使用</span>' : '<span class="pill">未启用</span>'}</div><label class="model-input">可用模型<select name="provider-model" ${models.length ? "" : "disabled"}>${modelOptions}</select></label><div class="actions model-enable-action">${modelAction}</div></section><details class="panel provider-panel advanced-settings"><summary><span>高级参数</span><small>可选</small></summary><div class="advanced-grid"><label>温度<input name="provider-temperature" type="number" min="0" max="2" step="0.01" value="${(setting.temperature_bps / 100).toFixed(2)}"><input name="provider-temperature-range" type="range" min="0" max="2" step="0.01" value="${(setting.temperature_bps / 100).toFixed(2)}"></label><label>最大输出 Token<input name="provider-max-tokens" type="number" min="1" max="8192" step="1" value="${setting.max_output_tokens}"><input name="provider-max-tokens-range" type="range" min="1" max="8192" step="1" value="${setting.max_output_tokens}"></label><label>请求超时时间<input name="provider-timeout" type="number" min="1" max="120" step="1" value="${Math.round(setting.timeout_ms / 1000)}"><input name="provider-timeout-range" type="range" min="1" max="120" step="1" value="${Math.round(setting.timeout_ms / 1000)}"></label></div></details></aside></div>`;
  }

  function providerSettingsFromPage() {
    const value = (name) => document.querySelector(`[name='${name}']${name === "provider-mode" ? ":checked" : ""}`)?.value ?? "";
    return { mode: value("provider-mode"), profile: value("provider-profile"), base_url: value("provider-base-url").trim(), model: value("provider-model") || "", temperature_bps: Math.round(Number(value("provider-temperature")) * 100), max_output_tokens: Number(value("provider-max-tokens")), timeout_ms: Number(value("provider-timeout")) * 1000 };
  }

  function decorate() {
    if (runtime.busy) return;
    document.documentElement.dataset.runtime = isReal() ? "p3-141-real-self-use" : "p3-141-offline-synthetic";
    if (applyToday()) { queueMicrotask(decorate); return; }
    settingsPage(); disclosure(); decorateModal(); bindContextDetail(); bindGlobal();
    const main = document.querySelector("#main-content");
    if (main && runtime.error && !main.querySelector("[data-runtime-error]")) main.insertAdjacentHTML("afterbegin", `<section class="notice danger" data-runtime-error><strong>本地操作未显示成功</strong><br>${clean(runtime.error.message)} (${clean(runtime.error.code)})</section>`);
  }
  async function rerender() { ui.render(); await Promise.resolve(); decorate(); }

  async function run(action, input) {
    if (runtime.busy) return;
    runtime.busy = true; runtime.error = null;
    try {
      if (action === "select-work") {
        const record = runtime.today?.records?.find((item) => item.id === input);
        if (!record) throw { code: "selection_stale", message: "这条 Work 记录已失效；没有请求模型。" };
        runtime.selectedWorkId = record.id; runtime.understanding = null; runtime.disclosurePending = false; runtime.editSuggestion = false;
      } else if (action === "ask" || action === "confirm-disclosure") {
        const selection = runtime.today?.records?.find((item) => item.id === runtime.selectedWorkId)?.id;
        if (!selection) throw { code: "selection_required", message: "请先选择一条 Work 记录。" };
        const related = runtime.includeRelatedPersonalContent;
        runtime.global = await invoke("assemble_global_ai_context", { page: page(), selection_ref: selection, ...(related ? { include_related_personal_content: true } : {}), ...(runtime.removed.length ? { removed_context_kinds: runtime.removed } : {}) });
        if (runtime.global.disclosure_required && action !== "confirm-disclosure") {
          runtime.disclosurePending = true; runtime.understanding = null;
        } else {
          runtime.disclosurePending = false;
          runtime.understanding = await invoke("get_evidence_backed_understanding", { context_id: "request-local", page: page(), selection_ref: selection, ...(related ? { include_related_personal_content: true, additional_context_confirmed: true } : {}), ...(runtime.removed.length ? { removed_context_kinds: runtime.removed } : {}), request_id: `p3-137-ui-explicit-${++runtime.sequence}` });
        }
      } else if (action === "confirm-link" || action === "reject-link") {
        const selection = runtime.today?.records?.find((item) => item.id === runtime.selectedWorkId)?.id;
        if (!selection) throw { code: "selection_required", message: "没有可关联的 Work 记录。" };
        await invoke("confirm_capture_context", { capture_id: selection, context_id: CONTEXT, decision: action === "confirm-link" ? "confirm" : "reject", idempotency_key: key(`persistent-link-${action}`) });
      } else if (action === "capture") {
        const text = input; // Read before any render: the modal textarea is about to be re-created.
        if (isReal()) {
          if (typeof text !== "string") throw { code: "real_capture_input_missing", message: "没有读取到本地输入；未写入。" };
          runtime.lastCapture = await invoke("capture_record", { text, key: key("capture") });
        } else {
          if (text !== SYN_TEXT) throw { code: "synthetic_input_rejected", message: "此离线 run 只接受固定合成文本；未写入。" };
          runtime.lastCapture = await invoke("capture_record", { text, key: SYN_KEY });
        }
      } else if (action === "capture-short") {
        runtime.lastCapture = await invoke("capture_record", { text: SYN_SHORT, key: SYN_SHORT_KEY });
      } else if (action === "confirm") {
        const capture = runtime.pendingCaptureId ? { id: runtime.pendingCaptureId } : (runtime.lastCapture?.record || runtime.today?.records?.[0]);
        if (!capture) throw { code: "capture_missing", message: "没有可确认的 Capture；未写入。" };
        await invoke("confirm_capture_context", { capture_id: capture.id, context_id: CONTEXT, decision: "confirm", idempotency_key: key("context-confirm") });
        runtime.lastCapture = null;
        runtime.pendingCaptureId = null;
        ui.state.modal = null;
        // The user has just explicitly confirmed this path.  Show the existing
        // Global AI surface so its Candidate can be examined, never accepted automatically.
        ui.state.aiOpen = true;
      } else if (["accept", "edit-accept", "reject", "defer"].includes(action)) {
        const candidate = runtime.next?.candidates?.[0];
        if (!candidate) throw { code: "candidate_missing", message: "没有可靠 Candidate；没有创建 Action。" };
        const decision = action === "edit-accept" ? "edit_accept" : action;
        await invoke("decide_context_next_action", { candidate_id: candidate.candidate_id, decision, ...(decision === "edit_accept" ? { edited_text: SYN_EDIT } : {}), idempotency_key: key(`candidate-${decision}`) });
        if (decision === "accept" || decision === "edit_accept") ui.state.aiOpen = false;
      } else if (action === "complete") {
        const current = runtime.today?.confirmed_actions?.[0];
        if (!current) throw { code: "open_action_missing", message: "没有开放 Action；未写入结果。" };
        await invoke("record_action_result", { action_id: current.action_id, result: "completed", result_text: isReal() ? REAL_RESULT : SYN_RESULT, idempotency_key: key("action-complete") });
      } else if (action.startsWith("feedback-")) {
        const decision = action.slice("feedback-".length); const understanding = runtime.understanding?.understanding_id;
        if (!understanding) throw { code: "understanding_missing", message: "没有可反馈的 Understanding；未写入。" };
        const edited_text = decision === "edit-confirm" ? document.querySelector("[data-understanding-edit]")?.value : undefined;
        await invoke("decide_understanding_feedback", { understanding_id: understanding, decision: decision.replace("-", "_"), ...(edited_text ? { edited_text } : {}), idempotency_key: `p3-137-ui-feedback-${decision}-${++runtime.sequence}` });
        runtime.understanding = null; runtime.editSuggestion = false;
        ui.state.receipt = decision === "confirm" || decision === "edit-confirm" ? "你已确认一条候选 Action。" : "你的反馈已记录；不会自动创建 Action。";
      } else if (action === "send-understanding") {
        const selection = runtime.today?.records?.at(-1)?.id;
        runtime.understanding = await invoke("get_evidence_backed_understanding", { context_id: CONTEXT, page: page(), ...(selection ? { selection_ref: selection } : {}), ...(runtime.removed.length ? { removed_context_kinds: runtime.removed } : {}), request_id: `p3-136-ui-explicit-${++runtime.sequence}` });
      } else if (action === "provider-save") {
        const settings = providerSettingsFromPage();
        runtime.provider = await invoke("save_ai_provider_settings", { settings });
        runtime.understanding = null;
      } else if (action === "provider-credential-save") {
        const api_key = document.querySelector("[name='provider-credential']")?.value.trim() || "";
        if (!api_key) throw { code: "credential_required", message: "请输入要加密保存的 API Key。" };
        runtime.provider = await invoke("save_ai_provider_credential", { operation: "store_or_update", api_key });
        runtime.understanding = null;
      } else if (action === "provider-test") {
        await invoke("test_ai_provider_connection", {});
        runtime.provider = await invoke("get_ai_provider_settings", {}); runtime.understanding = null;
      } else if (action === "provider-model-select") {
        const settings = providerSettingsFromPage();
        if (!(runtime.provider?.discovered_models || []).includes(settings.model)) throw { code: "provider_model_not_tested", message: "请从刚刚测试成功返回的模型中选择。" };
        runtime.provider = await invoke("save_ai_provider_settings", { settings });
        runtime.pendingModel = null; runtime.understanding = null;
      } else if (action === "provider-enable") {
        runtime.provider = await invoke("set_ai_provider_enabled", { enabled: true }); runtime.understanding = null;
      } else if (action === "provider-clear-credential") {
        runtime.provider = await invoke("save_ai_provider_credential", { operation: "delete" }); runtime.understanding = null;
      }
      await refresh();
      if (action === "capture" && isReal()) runtime.pendingCaptureId = runtime.today?.records?.at(-1)?.id || null;
    } catch (error) { localError(error); }
    finally { runtime.busy = false; await rerender(); }
  }

  document.addEventListener("click", (event) => {
    const target = event.target.closest("[data-action]"); if (!target) return;
    const action = target.dataset.action;
    if (action === "provider:defaults") {
      event.preventDefault(); event.stopImmediatePropagation();
      const set = (name, value) => { const node = document.querySelector(`[name='${name}']`); if (node) node.value = value; };
      set("provider-temperature", "0.70"); set("provider-temperature-range", "0.70"); set("provider-max-tokens", "2048"); set("provider-max-tokens-range", "2048"); set("provider-timeout", "60"); set("provider-timeout-range", "60");
      return;
    }
    if (action.startsWith("runtime:select-work:")) { event.preventDefault(); event.stopImmediatePropagation(); run("select-work", action.slice("runtime:select-work:".length)); return; }
    if (["runtime:clear-selection", "runtime:include-related", "runtime:remove-related", "runtime:cancel-disclosure", "runtime:edit-suggestion"].includes(action)) {
      event.preventDefault(); event.stopImmediatePropagation();
      if (action === "runtime:clear-selection") { runtime.selectedWorkId = null; runtime.understanding = null; runtime.disclosurePending = false; runtime.editSuggestion = false; }
      if (action === "runtime:include-related") runtime.includeRelatedPersonalContent = true;
      if (action === "runtime:remove-related" || action === "runtime:cancel-disclosure") { runtime.includeRelatedPersonalContent = false; runtime.disclosurePending = false; }
      if (action === "runtime:edit-suggestion") runtime.editSuggestion = true;
      queueMicrotask(async () => { try { await refresh(); } catch (error) { localError(error); } await rerender(); });
      return;
    }
    const map = { "runtime:capture": "capture", "runtime:capture-short": "capture-short", "runtime:confirm": "confirm", "runtime:accept": "accept", "runtime:edit-accept": "edit-accept", "runtime:reject": "reject", "runtime:defer": "defer", "runtime:complete": "complete", "runtime:ask": "ask", "runtime:confirm-disclosure": "confirm-disclosure", "runtime:confirm-link": "confirm-link", "runtime:reject-link": "reject-link", "runtime:adopt": "feedback-confirm", "runtime:edit-adopt": "feedback-edit-confirm", "runtime:ignore": "feedback-ignore", "runtime:reject-understanding": "feedback-reject", "runtime:correct-understanding": "feedback-correct", "runtime:feedback-confirm": "feedback-confirm", "runtime:feedback-edit-confirm": "feedback-edit-confirm", "runtime:feedback-reject": "feedback-reject", "runtime:feedback-ignore": "feedback-ignore", "runtime:feedback-correct": "feedback-correct", "runtime:send-understanding": "send-understanding", "provider:save": "provider-save", "provider:credential-save": "provider-credential-save", "provider:test": "provider-test", "provider:model-select": "provider-model-select", "provider:enable": "provider-enable", "provider:clear-credential": "provider-clear-credential" };
    if (map[action]) {
      event.preventDefault(); event.stopImmediatePropagation();
      const input = action === "runtime:capture" ? (isReal() ? document.querySelector("#real-capture-text")?.value : SYN_TEXT) : undefined;
      run(map[action], input); return;
    }
    if (action === "capture-confirm") { event.preventDefault(); event.stopImmediatePropagation(); run("confirm"); return; }
    if (action === "remove-health" || action === "add-health") {
      runtime.removed = action === "remove-health" ? ["domain"] : [];
      queueMicrotask(async () => { try { await refresh(); } catch (error) { localError(error); } await rerender(); });
      return;
    }
    // P3-116 handles unbound navigation synchronously.  Decorate once after
    // that renderer returns, without observing subsequent live-region updates.
    setTimeout(decorate, 0);
  }, true);

  document.addEventListener("change", (event) => {
    const node = event.target;
    if (node?.name === "provider-model") { runtime.pendingModel = node.value; queueMicrotask(rerender); return; }
    if (node?.name !== "provider-mode") return;
    runtime.pendingModel = null;
    queueMicrotask(async () => { try { runtime.provider = await invoke("get_ai_provider_settings", { mode: node.value }); } catch (error) { localError(error); } await rerender(); });
  }, true);

  document.addEventListener("input", (event) => {
    const node = event.target;
    if (node?.name === "provider-temperature-range") {
      const numeric = document.querySelector("[name='provider-temperature']");
      if (numeric) numeric.value = node.value;
    } else if (node?.name === "provider-temperature") {
      const slider = document.querySelector("[name='provider-temperature-range']");
      if (slider) slider.value = node.value;
    } else if (node?.name === "provider-max-tokens-range") {
      const numeric = document.querySelector("[name='provider-max-tokens']");
      if (numeric) numeric.value = node.value;
    } else if (node?.name === "provider-max-tokens") {
      const slider = document.querySelector("[name='provider-max-tokens-range']");
      if (slider) slider.value = node.value;
    } else if (node?.name === "provider-timeout-range") {
      const numeric = document.querySelector("[name='provider-timeout']");
      if (numeric) numeric.value = node.value;
    } else if (node?.name === "provider-timeout") {
      const slider = document.querySelector("[name='provider-timeout-range']");
      if (slider) slider.value = node.value;
    }
  }, true);

  document.addEventListener("keydown", (event) => { if (event.key === "Escape" && runtime.busy) runtime.busy = false; });
  // Do not observe the P3-116 live renderer: its aria-live updates can recurse
  // through DOM decoration.  Every typed Runtime operation above finishes with
  // rerender(), while untouched P3-116 navigation continues to render itself.
  refresh().then(rerender).catch((error) => { localError(error); return rerender(); });
})();
