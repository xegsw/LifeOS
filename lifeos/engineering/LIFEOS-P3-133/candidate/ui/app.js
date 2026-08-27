(() => {
  "use strict";

  const CONTEXT_ID = "ctx:project:local-work-self-use";
  const SYNTHETIC_TEXT = "整理 LifeOS Context Recovery 合成验收记录。";
  const SYNTHETIC_SHORT = "LifeOS Context Recovery 合成记录。";
  const SYNTHETIC_EDIT = "整理并复核 LifeOS Context Recovery 合成验收记录。";
  const SYNTHETIC_RESULT = "已完成合成验收记录整理与复核。";
  const REAL_RESULT = "用户在本地标记为已完成。";
  const state = { page: "today", status: null, today: null, recovery: null, next: null, global: null, understanding: null, error: null, busy: false, removed: [], includeSelection: true, receipt: "" };
  const root = document.getElementById("app");
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const invoke = async (name, request) => {
    const fn = window.__TAURI__?.core?.invoke;
    if (typeof fn !== "function") throw { code: "tauri_invoke_unavailable", message: "Tauri IPC 不可用；未显示成功。" };
    return fn(name, { request });
  };
  const isReal = () => state.status?.model_adapter === "disabled_in_real_mode";
  const key = (suffix) => isReal() ? `p3-133-real-ui-${suffix}-${crypto.randomUUID()}` : `p3-131-${suffix}-001`;
  const current = () => state.today?.records?.at(-1) || null;
  const candidate = () => state.next?.candidates?.[0] || null;
  const focus = () => state.today?.confirmed_actions?.find((item) => item.action_id === state.today?.todays_focus) || null;
  const button = (label, action, kind = "") => `<button type="button" class="button ${kind}" data-action="${action}" ${state.busy ? "disabled" : ""}>${esc(label)}</button>`;
  const badge = (label, kind = "user") => `<span class="identity ${kind}">${esc(label)}</span>`;
  const safeReceipt = () => ({
    bundle_contract: "LIFEOS-P3-133",
    ipc_allowlist: state.status?.ipc_allowlist || [],
    model_port: state.status?.model_port || "loading",
    model_adapter: state.status?.model_adapter || "loading",
    record_count: state.today?.records?.length || 0,
    confirmed_action_count: state.today?.confirmed_actions?.length || 0,
    todays_focus: state.today?.todays_focus || null,
    lifeos_noticed: state.today?.lifeos_noticed?.state || null,
  });

  function capturePanel() {
    const record = current();
    if (isReal()) {
      const count = state.today?.records?.length || 0;
      return `<section class="panel workspace-prompt"><span class="section-label">1 · 用户原文 Capture</span><h2>${record ? esc(record.content) : "手工输入一条低敏感 Work 短文本"}</h2><p class="quiet">仅用户本人在此 App 内手工输入。最多 3 条，每条最多 200 个 Unicode 字符；不会发往模型、网络或 Evidence。</p>${count < 3 ? `<label class="quiet" for="real-capture-text">Work 短文本</label><textarea id="real-capture-text" maxlength="200" rows="4" aria-label="低敏感 Work 短文本" placeholder="在此手工输入低敏感 Work 短文本"></textarea><div class="actions">${button("本地保存 Capture", "capture-real", "primary")}</div>` : `<p class="notice" role="status">本轮 3 条输入额度已满；系统不会再写入。</p>`}<p class="quiet">已保存 ${count} / 3 条。${record ? ` 当前 Capture 身份：${esc(record.id)}` : ""}</p>${state.receipt ? `<p class="notice mint" role="status">${esc(state.receipt)}</p>` : ""}</section>`;
    }
    return `<section class="panel workspace-prompt"><span class="section-label">1 · 合成 Capture</span><h2>${esc(record?.content || SYNTHETIC_TEXT)}</h2><p class="quiet">固定合成输入，仅用于工程验证。</p><div class="actions">${button(record ? "重试同一 Capture" : "记录充分 Evidence 的合成原文", "capture-synthetic", "primary")}${button("记录证据不足合成原文", "capture-short")}</div>${state.receipt ? `<p class="notice mint" role="status">${esc(state.receipt)}</p>` : ""}</section>`;
  }
  function contextPanel() {
    const record = current();
    const link = state.recovery?.typed_link_ref || "尚无 Context link";
    return `<section class="panel"><div class="section-head"><div><span class="section-label">2 · Project-backed Context</span><h2>LifeOS Work</h2></div>${badge(state.recovery?.state || "loading", state.recovery?.state === "confirmed" ? "decision" : "derivation")}</div><p class="quiet">Context: ${CONTEXT_ID}<br>Person: local owner · Domain: Work</p>${record ? `<div class="evidence-box">Capture identity: ${esc(record.id)}<br><small>${esc(link)}</small></div>` : `<p class="quiet">尚无 Capture；系统不会生成 Context 或 Action。</p>`}${record && state.recovery?.state === "candidate" ? `<div class="actions">${button("确认纳入 Project Context", "confirm", "primary")}${button("拒绝候选 link", "link-reject", "danger")}</div>` : ""}</section>`;
  }
  function understandingPanel() {
    const u = state.understanding;
    const real = isReal();
    if (real) return `<section class="panel"><div class="section-head"><div><span class="section-label">Evidence-backed Understanding</span><h2>真实模型未启用</h2></div>${badge("model disabled", "warning")}</div><p class="notice" role="status">${esc(u?.disclosure || "真实模型未启用；暂时没有足够证据判断。")}</p><p class="quiet">真实文本不会进入 OfflineSyntheticModelAdapter、ModelPort、网络、Agent 或外部进程；不会创建 Understanding、Feedback 或 noticed。</p></section>`;
    const reliable = Boolean(u?.observation || u?.suggestion);
    return `<section class="panel"><div class="section-head"><div><span class="section-label">Evidence-backed Understanding</span><h2>${reliable ? "离线合成观察与建议" : "没有可靠判断"}</h2></div>${badge("Offline synthetic adapter", "derivation")}</div>${reliable ? `<p class="focus-title">${esc(u.observation)}</p><p class="quiet">Suggestion · ${esc(u.suggestion)}</p><div class="evidence-box">processor: ${esc(u.processor)}<br>why: ${esc(u.why)}</div>` : `<p class="notice" role="status">${esc(u?.disclosure || "暂时没有足够证据判断。")}</p>`}</section>`;
  }
  function actionPanel() {
    const item = candidate();
    if (!item) return `<section class="panel"><span class="section-label">显式 Next Action 路径</span><h2>尚无 Candidate</h2><p class="quiet">${esc(state.next?.disclosure || "尚无候选。")}</p>${button("读取 Candidate", "next")}</section>`;
    const realOnly = isReal();
    return `<section class="panel"><div class="section-head"><div><span class="section-label">显式 Next Action 路径</span><h2>Candidate Next Action</h2></div>${badge("system candidate", "derivation")}</div><p class="focus-title">${esc(item.text)}</p><p class="quiet">Candidate 不会自动成为 Today Focus。只有用户明确接受才创建 Action。</p><div class="actions">${button("接受并创建 Action", "accept", "primary")}${realOnly ? "" : button("编辑后接受", "edit-accept")}${button("拒绝", "candidate-reject", "danger")}${button("暂缓", "defer")}</div></section>`;
  }
  function todayPanel() {
    const item = focus();
    const open = state.today?.confirmed_actions || [];
    return `<section class="panel"><div class="section-head"><div><span class="section-label">Today Intelligence Lite</span><h2>${item ? "Today's Focus" : "诚实空状态"}</h2></div>${badge(item ? "user confirmed action" : "no reliable focus", item ? "decision" : "warning")}</div>${item ? `<p class="focus-title">${esc(item.text)}</p><p class="quiet">只来自已确认且仍开放的 Action。selected: ${esc(item.action_id)}</p>${button("记录已完成结果", "complete", "primary")}` : `<p class="quiet">今天没有特别需要你处理的事情。</p>`}<hr><span class="section-label">LifeOS noticed</span><p class="quiet">${isReal() ? "真实模型未启用；暂时没有足够证据判断。" : "合成模式不把 noticed 用作真实判断。"}</p><div class="evidence-box">open confirmed Actions: ${open.length}</div></section>`;
  }
  function inspector() {
    const rows = state.global?.included || [];
    return `<aside class="workspace-inspector"><section class="panel"><span class="section-label">Global AI Context Inspector</span><h2>本次请求的引用</h2>${rows.length ? `<div class="evidence-box">${rows.map((x) => `<strong>${esc(x.kind)}</strong> · ${esc(x.reference)}<br><small>${esc(x.inclusion_reason)} · ${esc(x.authorization)}</small>`).join("<hr>")}</div>` : ""}<div class="actions">${button("重新组装 Context", "refresh", "primary")}</div></section><section class="panel"><span class="section-label">Boundary</span><p class="quiet">离线；无网络、通用 SQL/path、导出、权限、删除或原文 Memory 复制。</p></section></aside>`;
  }
  function memoryPage() {
    const m = state.today?.memory_provenance || {};
    const group = (title, values) => `<section class="panel"><span class="section-label">${title}</span><p class="quiet">${values?.length ? values.map(esc).join("<br>") : "none"}</p></section>`;
    return `<main id="main-content" class="workspace-reference" tabindex="-1"><header class="workspace-top"><div><p class="eyebrow">Memory provenance</p><h1>引用可追溯，原文不复制。</h1></div>${badge("reference only")}</header><div class="workspace-reference-grid"><section class="workspace-center">${group("Candidate", m.candidate_refs)}${group("Action", m.action_refs)}${group("Result", m.result_refs)}</section>${inspector()}</div></main>`;
  }
  function contextPage() { return `<main id="main-content" class="workspace-reference" tabindex="-1"><header class="workspace-top"><div><p class="eyebrow">Global AI Context</p><h1>展示、检查、临时移除。</h1></div>${badge(isReal() ? "real input / model disabled" : "offline synthetic", "derivation")}</header><div class="workspace-reference-grid"><section class="workspace-center">${understandingPanel()}</section>${inspector()}</div></main>`; }
  function todayPage() { return `<main id="main-content" class="workspace-reference" tabindex="-1"><header class="workspace-top"><div><p class="eyebrow">Today · Work self-use</p><h1>把可见的依据留给你，把决定留给你。</h1><p class="subhead">${isReal() ? "真实输入本地持久化；模型未启用。" : "固定合成输入；离线适配器仅用于验证。"}</p></div>${badge(isReal() ? "controlled real input" : "offline synthetic", isReal() ? "decision" : "derivation")}</header><div class="workspace-reference-grid"><section class="workspace-center">${capturePanel()}${contextPanel()}${understandingPanel()}${actionPanel()}${todayPanel()}<section class="panel"><span class="section-label">Actual runtime receipt</span><pre id="runtime-evidence" class="evidence-box" aria-label="actual runtime state">${esc(JSON.stringify(safeReceipt(), null, 2))}</pre></section></section>${inspector()}</div></main>`; }
  function render() { const page = state.page === "context" ? contextPage() : state.page === "memory" ? memoryPage() : todayPage(); root.innerHTML = `<div class="app-shell workspace-shell"><nav class="icon-rail" aria-label="主导航"><div class="brand-mark" aria-hidden="true">L</div><button class="rail-button" data-action="nav:today" aria-label="Today">T</button><button class="rail-button" data-action="nav:context" aria-label="Global AI Context">G</button><button class="rail-button" data-action="nav:memory" aria-label="Memory provenance">M</button><span class="rail-spacer"></span><button class="rail-button" data-action="refresh" aria-label="刷新实际运行时">R</button></nav><div class="workspace">${state.error ? `<section class="notice danger" role="alert">${esc(state.error)}</section>` : ""}${page}</div></div>`; }
  async function load() {
    state.status = await invoke("runtime_status", {});
    state.today = await invoke("get_today", {});
    state.recovery = await invoke("get_context_recovery", { context_id: CONTEXT_ID });
    state.next = await invoke("get_context_next_action", { context_id: CONTEXT_ID });
    const selection = state.includeSelection ? current()?.id : undefined;
    const page = state.page === "context" ? "context_detail" : "today";
    state.global = await invoke("assemble_global_ai_context", { page, ...(selection ? { selection_ref: selection } : {}) });
    state.understanding = await invoke("get_evidence_backed_understanding", { context_id: CONTEXT_ID, page, ...(selection ? { selection_ref: selection } : {}), request_id: isReal() ? "real-mode-disabled" : `p3-132-ui-${selection || "none"}` });
    state.today = await invoke("get_today", {});
  }
  async function act(name) {
    if (name.startsWith("nav:")) { state.page = name.slice(4); await load(); render(); return; }
    // Rendering the real-mode form replaces its textarea.  Preserve the user-entered
    // value before setting busy so the subsequent IPC receives the original input.
    const realCaptureText = name === "capture-real"
      ? (document.getElementById("real-capture-text")?.value || "")
      : null;
    state.busy = true; state.error = null; render();
    try {
      if (name === "capture-synthetic") { const r = await invoke("capture_record", { text: SYNTHETIC_TEXT, key: "p3-130-capture-001" }); state.receipt = `capture_record: ${r.status}`; }
      if (name === "capture-short") { const r = await invoke("capture_record", { text: SYNTHETIC_SHORT, key: "p3-131-insufficient-001" }); state.receipt = `capture_record: ${r.status}`; }
      if (name === "capture-real") { const r = await invoke("capture_record", { text: realCaptureText || "", key: key("capture") }); state.receipt = `capture_record: ${r.status}`; }
      if (name === "confirm" || name === "link-reject") { const r = current(); if (!r) throw { code: "capture_missing", message: "没有可确认的 Capture。" }; const out = await invoke("confirm_capture_context", { capture_id: r.id, context_id: CONTEXT_ID, decision: name === "confirm" ? "confirm" : "reject", idempotency_key: key(`link-${name}`) }); state.receipt = `confirm_capture_context: ${out.decision}`; }
      if (name === "next") { state.receipt = "已读取 Candidate。"; }
      if (["accept", "edit-accept", "candidate-reject", "defer"].includes(name)) { const item = candidate(); if (!item) throw { code: "candidate_missing", message: "没有开放 Candidate。" }; const decision = ({ accept: "accept", "edit-accept": "edit_accept", "candidate-reject": "reject", defer: "defer" })[name]; const out = await invoke("decide_context_next_action", { candidate_id: item.candidate_id, decision, ...(name === "edit-accept" ? { edited_text: SYNTHETIC_EDIT } : {}), idempotency_key: key(`candidate-${decision}`) }); state.receipt = `candidate decision: ${out.decision}`; }
      if (name === "complete") { const item = focus(); if (!item) throw { code: "action_missing", message: "没有开放 Action。" }; const out = await invoke("record_action_result", { action_id: item.action_id, result: "completed", result_text: isReal() ? REAL_RESULT : SYNTHETIC_RESULT, idempotency_key: key("result") }); state.receipt = `record_action_result: ${out.status}`; }
      await load();
    } catch (error) { state.error = `${error?.code || "runtime_error"}: ${error?.message || "受控本地运行时未完成操作。"}`; }
    state.busy = false; render();
  }
  root.addEventListener("click", (event) => { const target = event.target.closest("[data-action]"); if (target) act(target.dataset.action); });
  (async () => { try { await load(); } catch (error) { state.error = `${error?.code || "runtime_error"}: ${error?.message || "受控本地运行时未完成操作。"}`; } render(); })();
})();
