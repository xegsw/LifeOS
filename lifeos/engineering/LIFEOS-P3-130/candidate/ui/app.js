(() => {
  "use strict";

  const FIXED_TEXT = "整理 LifeOS Context Recovery 合成验收记录。";
  const CONTEXT_ID = "ctx:project:synthetic-lifeos-product";
  const app = document.getElementById("app");
  const state = { page: "today", status: null, today: null, recovery: null, error: null, busy: false, selection: true, receipt: "" };
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[char]));
  const invoke = async (name, request) => {
    const fn = window.__TAURI__?.core?.invoke;
    if (typeof fn !== "function") throw { code: "tauri_invoke_unavailable", message: "Tauri IPC 不可用；未显示成功。" };
    return fn(name, { request });
  };
  const errorText = (error) => `${error?.code || "runtime_error"}: ${error?.message || "受控本地运行时未完成操作。"}`;
  const link = (label, action, active = false) => `<button class="rail-button" type="button" data-action="${action}" aria-label="${label}" ${active ? 'aria-current="page"' : ""}>${label.slice(0, 1)}</button>`;
  const button = (label, action, extra = "") => `<button type="button" class="button ${extra}" data-action="${action}" ${state.busy ? "disabled" : ""}>${label}</button>`;
  const badge = (label) => `<span class="identity user">${esc(label)}</span>`;
  const recoveryState = () => state.recovery?.state || "loading";
  const recoveryGap = () => state.recovery?.evidence_gap ? `<section class="notice danger" role="status"><strong>Evidence gap</strong><br>${esc(state.recovery.evidence_gap)}。未形成可靠建议，也未写入任何 Memory 副本。</section>` : "";
  const statusLine = () => `<pre id="runtime-evidence" class="evidence-box" aria-label="实际运行时状态">${esc(JSON.stringify({ ipc: state.status?.ipc_allowlist || [], today: state.today?.status || "loading", context: recoveryState(), selection_included: state.selection }, null, 2))}</pre>`;

  function todayPage() {
    const record = state.today?.records?.[0];
    const audit = state.today?.audit;
    return `<main id="main-content" class="workspace-reference" tabindex="-1">
      <header class="workspace-top"><div><p class="eyebrow">Today · Project-backed Context Recovery</p><h1>从原始记录恢复项目上下文。</h1><p class="subhead">固定合成数据、离线运行；原文、Project link、Feedback 与审计身份彼此分离。</p></div>${badge("P3-130 synthetic only")}</header>
      <div class="workspace-reference-grid"><section class="workspace-center">
        <section class="panel workspace-prompt"><span class="section-label">Capture · 用户原文</span><h2>${esc(FIXED_TEXT)}</h2><p class="quiet">Source: local_capture · ${esc(state.recovery?.source_ref || "SRC-SYN-WORK-001")} · Artifact: ${esc(state.recovery?.artifact_ref || "ART-SYN-CONTEXT-RECOVERY-001@v1")}</p>
          <div class="actions">${button(record ? "重试同一 capture（幂等）" : "记录固定合成原文", "capture", "primary")}${button("刷新 Today", "refresh")}</div>${state.receipt ? `<p class="state-receipt" role="status">${esc(state.receipt)}</p>` : ""}</section>
        <section class="panel"><div class="section-head"><div><span class="section-label">Typed Project link</span><h2>LifeOS 产品开发</h2></div>${badge(recoveryState())}</div>
          <p class="quiet">Context ID: ${CONTEXT_ID}<br>Project: synthetic-lifeos-product · Person: person:synthetic-owner</p>
          ${record ? `<div class="evidence-box"><strong>已保留的用户原文</strong><br>${esc(record.content)}<br><small>capture_id: ${esc(record.id)} · link: ${esc(state.recovery?.typed_link_ref || "candidate")}</small></div>` : `<p class="quiet">尚无 capture。空状态不会自动生成内容、链接或建议。</p>`}
          ${record && recoveryState() === "candidate" ? `<div class="actions">${button("确认纳入此 Project Context", "confirm", "primary")}${button("拒绝候选 link", "reject", "danger")}</div>` : ""}
          ${record && recoveryState() !== "candidate" ? `<p class="state-receipt">Feedback 结果：${esc(recoveryState())}。重复提交使用相同幂等键。</p>` : ""}</section>
        <section class="panel"><div class="section-head"><div><span class="section-label">Audit / lifecycle</span><h2>可复核状态</h2></div>${badge(state.today?.status || "loading")}</div>
          <p class="quiet">records: ${state.today?.records?.length || 0} · audit events: ${audit?.event_count || 0} · saved: ${audit?.saved_count || 0} · repeats: ${audit?.repeat_count || 0}</p>${statusLine()}</section>
      </section><aside class="workspace-inspector">
        <section class="panel context-summary"><span class="section-label">Context Inspector</span><h2>恢复依据</h2><p class="quiet">只呈现 Project 的来源、Artifact、typed link、Feedback 与 audit 引用；不创建通用 Context 表。</p><p>${badge(state.recovery?.reliable_suggestion ? "reliable" : "无可靠建议")}</p></section>
        <section class="panel workspace-tools"><span class="section-label">Person-first inspector</span><p class="quiet">当前页面：Today<br>选中内容：${state.selection ? "纳入本次本地展示" : "不纳入"}</p><div>${button(state.selection ? "移出选中" : "加入选中", "selection")}</div></section>
        <section class="panel"><span class="section-label">Memory provenance</span><p class="quiet">Source / Artifact / Project link / Feedback / Audit 均为引用。没有复制用户原文到 Memory。</p>${button("查看 provenance", "nav:memory")}</section>
      </aside></div>${recoveryGap()}</main>`;
  }
  function contextPage() { return `<main id="main-content" class="workspace-reference" tabindex="-1"><header class="workspace-top"><div><p class="eyebrow">Contexts · Project-backed only</p><h1>LifeOS 产品开发</h1><p class="subhead">Context 是 Project-backed identity，不是泛化 Context 存储。</p></div>${badge(recoveryState())}</header><div class="workspace-reference-grid"><section class="workspace-center"><section class="panel"><span class="section-label">Recovery</span><h2>${esc(state.recovery?.state || "loading")}</h2><p class="quiet">${esc(state.recovery?.typed_link_ref || "尚无 typed capture-project link")}</p>${recoveryGap()}${button("重新读取 Context Recovery", "recovery", "primary")}</section><section class="panel"><span class="section-label">Project evidence</span><p class="quiet">source_available、artifact version、generation、tombstone、authorization 与 evidence 任何一项失效时，恢复结果会明确为 evidence gap。</p></section></section><aside class="workspace-inspector"><section class="panel"><span class="section-label">Scope</span><p class="quiet">无 Person Profile、无 Domain ACL、无外部数据、无网络、无模型或 Agent。</p></section></aside></div></main>`; }
  function memoryPage() { return `<main id="main-content" class="workspace-reference" tabindex="-1"><header class="workspace-top"><div><p class="eyebrow">Memory · provenance view</p><h1>可追溯，不复制原文。</h1><p class="subhead">此页面展示引用边，而非将 Capture 原文复制为新的长期记忆。</p></div>${badge("reference only")}</header><div class="workspace-reference-grid"><section class="workspace-center"><section class="panel"><span class="section-label">Source</span><h2>${esc(state.recovery?.source_ref || "SRC-SYN-WORK-001")}</h2><p class="quiet">Artifact: ${esc(state.recovery?.artifact_ref || "ART-SYN-CONTEXT-RECOVERY-001@v1")}</p></section><section class="panel"><span class="section-label">Links</span><p class="quiet">${esc(state.recovery?.typed_link_ref || "none")}<br>${esc(state.recovery?.feedback_ref || "feedback: none")}<br>${esc(state.recovery?.audit_ref || "audit: none")}</p><p>${badge(state.recovery?.memory_copy_created ? "unexpected copy" : "memory copy: false")}</p></section></section><aside class="workspace-inspector"><section class="panel"><span class="section-label">Boundary</span><p class="quiet">“Memory”在本切片仅作为 provenance 展示；不会承担或复制用户原文权威性。</p></section></aside></div></main>`; }
  function render() {
    const page = state.page === "context" ? contextPage() : state.page === "memory" ? memoryPage() : todayPage();
    app.innerHTML = `<div class="app-shell workspace-shell"><nav class="icon-rail" aria-label="主导航"><div class="brand-mark" aria-hidden="true">L</div>${link("Today", "nav:today", state.page === "today")}${link("Project Context", "nav:context", state.page === "context")}${link("Memory provenance", "nav:memory", state.page === "memory")}<span class="rail-spacer"></span>${link("Runtime status", "refresh")}</nav><div class="workspace">${state.error ? `<section class="notice danger" role="alert">${esc(state.error)}</section>` : ""}${page}</div></div>`;
  }
  async function load() { state.status = await invoke("runtime_status", {}); state.today = await invoke("get_today", {}); state.recovery = await invoke("get_context_recovery", { context_id: CONTEXT_ID }); }
  async function action(name) {
    if (name.startsWith("nav:")) { state.page = name.slice(4); render(); return; }
    if (name === "selection") { state.selection = !state.selection; state.receipt = state.selection ? "仅本次页面展示已重新纳入选中内容。" : "仅本次页面展示已移出选中内容；未调用写入 IPC。"; render(); return; }
    state.busy = true; state.error = null; render();
    try {
      if (name === "capture") { const result = await invoke("capture_record", { text: FIXED_TEXT, key: "p3-130-capture-001" }); state.receipt = `capture_record: ${result.status} · ${result.link_status}`; }
      if (name === "confirm" || name === "reject") { const capture = state.today?.records?.[0]; if (!capture) throw { code: "capture_missing", message: "没有可确认的 capture。" }; const result = await invoke("confirm_capture_context", { capture_id: capture.id, context_id: CONTEXT_ID, decision: name === "confirm" ? "confirm" : "reject", idempotency_key: "p3-130-confirm-001" }); state.receipt = `confirm_capture_context: ${result.status} · ${result.decision}`; }
      await load();
    } catch (error) { state.error = errorText(error); }
    state.busy = false; render();
  }
  app.addEventListener("click", (event) => { const button = event.target.closest("[data-action]"); if (button) action(button.dataset.action); });
  (async () => { try { await load(); } catch (error) { state.error = errorText(error); } render(); })();
})();
