(() => {
  "use strict";

  const SUFFICIENT_TEXT = "整理 LifeOS Context Recovery 合成验收记录。";
  const INSUFFICIENT_TEXT = "LifeOS Context Recovery 合成记录。";
  const EDITED_TEXT = "整理并复核 LifeOS Context Recovery 合成验收记录。";
  const CONTEXT_ID = "ctx:project:synthetic-lifeos-product";
  const app = document.getElementById("app");
  const state = { page: "today", status: null, today: null, recovery: null, next: null, error: null, busy: false, selection: true, receipt: "" };

  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
  const invoke = async (name, request) => {
    const fn = window.__TAURI__?.core?.invoke;
    if (typeof fn !== "function") throw { code: "tauri_invoke_unavailable", message: "Tauri IPC 不可用；未显示成功。" };
    return fn(name, { request });
  };
  const message = (error) => `${error?.code || "runtime_error"}: ${error?.message || "受控本地运行时未完成操作。"}`;
  const badge = (label, variant = "user") => `<span class="identity ${variant}">${esc(label)}</span>`;
  const button = (label, action, extra = "") => `<button type="button" class="button ${extra}" data-action="${action}" ${state.busy ? "disabled" : ""}>${label}</button>`;
  const rail = (label, action, active) => `<button class="rail-button" type="button" data-tooltip="${label}" aria-label="${label}" data-action="${action}" ${active ? 'aria-current="page"' : ""}>${label.slice(0, 1)}</button>`;
  const gap = () => state.recovery?.evidence_gap ? `<div class="notice danger" role="status"><strong>Evidence gap</strong><br>${esc(state.recovery.evidence_gap)}。没有候选 Action，也没有写入 Action / Memory。</div>` : "";
  const currentCapture = () => state.today?.records?.at(-1);
  const openAction = () => state.today?.confirmed_actions?.[0];
  const evidence = () => `<pre id="runtime-evidence" class="evidence-box" aria-label="actual runtime state">${esc(JSON.stringify({ ipc_allowlist: state.status?.ipc_allowlist || [], context_state: state.recovery?.state || "loading", candidate_rule: state.status?.candidate_rule || "loading", confirmed_action_count: state.today?.confirmed_actions?.length || 0, today_focus: state.today?.todays_focus ?? null }, null, 2))}</pre>`;

  function todayPage() {
    const record = currentCapture();
    const action = openAction();
    const candidate = state.next?.candidates?.[0];
    const recoveryState = state.recovery?.state || "loading";
    return `<main id="main-content" class="workspace-reference" tabindex="-1">
      <header class="workspace-top"><div><p class="eyebrow">Today · evidence-backed next action</p><h1>只把已确认的安排放入 Today。</h1><p class="subhead">系统最多提出一条由本地规则导出的 Candidate Next Action；用户始终可接受、编辑后接受、拒绝或暂缓。</p></div>${badge("P3-131 · synthetic only")}</header>
      <div class="workspace-reference-grid"><section class="workspace-center">
        <section class="panel workspace-prompt"><span class="section-label">1 · 用户原文 Capture</span><h2>${esc(SUFFICIENT_TEXT)}</h2><p class="quiet">固定合成输入。原文身份只保留在 Capture，不复制到 Memory。</p><div class="actions">${button(record ? "重试同一 capture（幂等）" : "记录有充分证据的原文", "capture", "primary")}${button("记录证据不足原文", "capture-insufficient")}${button("刷新", "refresh")}</div>${state.receipt ? `<p class="notice mint" role="status">${esc(state.receipt)}</p>` : ""}</section>
        <section class="panel"><div class="section-head"><div><span class="section-label">2 · Project-backed Context</span><h2>LifeOS 产品开发</h2></div>${badge(recoveryState, recoveryState === "confirmed" ? "decision" : "derivation")}</div><p class="quiet">Context: ${CONTEXT_ID}<br>Project: synthetic-lifeos-product · Person: person:synthetic-owner</p>${record ? `<div class="evidence-box"><strong>Capture 引用</strong><br>${esc(record.id)} · ${esc(record.source_id)} · ${esc(record.artifact_version)}<br><small>typed link: ${esc(state.recovery?.typed_link_ref || "candidate")}</small></div>` : `<p class="quiet">尚无 Capture。系统不会自行生成 Project link 或 Action。</p>`}${record && recoveryState === "candidate" ? `<div class="actions">${button("确认纳入 Project Context", "confirm", "primary")}${button("拒绝候选 link", "link-reject", "danger")}</div>` : ""}${gap()}</section>
        <section class="panel"><div class="section-head"><div><span class="section-label">3 · Candidate Next Action</span><h2>${candidate ? "由证据导出的候选" : "尚无候选"}</h2></div>${candidate ? badge("system derived", "derivation") : badge("no automatic action", "warning")}</div>${candidate ? `<p class="focus-title">${esc(candidate.text)}</p><p class="quiet">${esc(candidate.why)}</p><div class="evidence-box">rule: ${esc(candidate.processor)} · derivation: ${esc(candidate.derivation_id)}<br>basis: ${candidate.basis_refs.map(esc).join(" · ")}</div><div class="actions">${button("接受并创建 Action", "accept", "primary")}${button("编辑后接受", "edit-accept")}${button("拒绝", "candidate-reject", "danger")}${button("暂缓", "defer")}</div>` : `<p class="quiet">仅在证据、Source/Artifact、Project link 与用户确认全部满足时，才有零或一条候选。候选本身不会进入 Today。</p>${state.next?.disclosure ? `<p class="notice" role="status">${esc(state.next.disclosure)}</p>` : ""}${button("读取 Candidate", "next")}`}</section>
        <section class="panel"><div class="section-head"><div><span class="section-label">4 · Today 的用户确认安排</span><h2>${action ? "已确认，尚待结果" : "没有自动安排"}</h2></div>${badge(action ? "user confirmed" : "no auto action", action ? "decision" : "warning")}</div>${action ? `<p class="focus-title">${esc(action.text)}</p><p class="quiet">${esc(action.action_id)} · ${esc(action.confirmation_kind)} · Candidate ref: ${esc(action.candidate_ref)}</p><div class="actions">${button("记录已完成结果", "complete", "primary")}</div>` : `<p class="quiet">Today Focus 保持为空。Candidate、拒绝、暂缓和证据不足都不会自动变成 Today Action。</p>`}</section>
        <section class="panel"><span class="section-label">Actual runtime receipt</span>${evidence()}</section>
      </section><aside class="workspace-inspector">
        <section class="panel context-summary"><span class="section-label">Inspector</span><h2>可审计的恢复边</h2><p class="quiet">Source / Artifact / Project link / Derivation / Feedback / Action / Result 都是带身份的独立引用。</p>${button("打开 provenance", "nav:memory")}</section>
        <section class="panel workspace-tools"><span class="section-label">页面选中内容</span><p class="quiet">${state.selection ? "当前本地展示纳入了选中内容。" : "当前本地展示未纳入选中内容。"}</p>${button(state.selection ? "移出选中" : "加入选中", "selection")}</section>
        <section class="panel"><span class="section-label">Boundary</span><p class="quiet">离线；无模型、Agent、网络、通用 Action API、通用 Context 表或原文 Memory 复制。</p></section>
      </aside></div>
    </main>`;
  }

  function contextPage() {
    return `<main id="main-content" class="workspace-reference" tabindex="-1"><header class="workspace-top"><div><p class="eyebrow">Project Context</p><h1>恢复，而不是泛化存储。</h1><p class="subhead">一个固定 Project-backed Context；Evidence 任一不可信便停止在 evidence gap。</p></div>${badge(state.recovery?.state || "loading")}</header><div class="workspace-reference-grid"><section class="workspace-center"><section class="panel"><span class="section-label">Context Recovery</span><h2>${esc(state.recovery?.state || "loading")}</h2><p class="quiet">${esc(state.recovery?.typed_link_ref || "尚无 confirmed typed link")}</p>${gap()}<div class="actions">${button("重新读取 recovery", "recovery", "primary")}${button("读取 Candidate", "next")}</div></section><section class="panel"><span class="section-label">Evidence contract</span><p class="quiet">只接受当前 Project、固定 Source/Artifact、用户明确 Context feedback 与审计链。没有足够依据时结果是零条 Candidate。</p></section></section><aside class="workspace-inspector"><section class="panel"><span class="section-label">Not implemented</span><p class="quiet">无 Person Profile、Domain ACL、外部数据、模型代理、云同步或泛化 Context API。</p></section></aside></div></main>`;
  }

  function memoryPage() {
    const memory = state.today?.memory_provenance;
    const list = (title, values) => `<section class="panel"><span class="section-label">${title}</span><p class="quiet">${(values?.length ? values : ["none"]).map(esc).join("<br>")}</p></section>`;
    return `<main id="main-content" class="workspace-reference" tabindex="-1"><header class="workspace-top"><div><p class="eyebrow">Memory provenance</p><h1>可追溯，不复制原文。</h1><p class="subhead">这里仅显示 Derivation、Candidate、Feedback、Action 与 Result 引用边。</p></div>${badge("reference only")}</header><div class="workspace-reference-grid"><section class="workspace-center">${list("Derivation", memory?.derivation_refs)}${list("Candidate", memory?.candidate_refs)}${list("Feedback", memory?.feedback_refs)}${list("Action", memory?.action_refs)}${list("Result", memory?.result_refs)}</section><aside class="workspace-inspector"><section class="panel"><span class="section-label">Original-content boundary</span><p class="quiet">memory_copy_created: ${esc(String(state.recovery?.memory_copy_created ?? false))}<br>用户 Capture 原文从不在此处复制或重写。</p>${button("返回 Today", "nav:today")}</section></aside></div></main>`;
  }

  function render() {
    const page = state.page === "context" ? contextPage() : state.page === "memory" ? memoryPage() : todayPage();
    app.innerHTML = `<div class="app-shell workspace-shell"><nav class="icon-rail" aria-label="主导航"><div class="brand-mark" aria-hidden="true">L</div>${rail("Today", "nav:today", state.page === "today")}${rail("Project Context", "nav:context", state.page === "context")}${rail("Memory provenance", "nav:memory", state.page === "memory")}<span class="rail-spacer"></span>${rail("刷新实际运行时", "refresh", false)}</nav><div class="workspace">${state.error ? `<section class="notice danger" role="alert">${esc(state.error)}</section>` : ""}${page}</div></div>`;
  }

  async function load() {
    state.status = await invoke("runtime_status", {});
    state.today = await invoke("get_today", {});
    state.recovery = await invoke("get_context_recovery", { context_id: CONTEXT_ID });
    state.next = await invoke("get_context_next_action", { context_id: CONTEXT_ID });
  }
  async function decide(decision, editedText) {
    const candidate = state.next?.candidates?.[0];
    if (!candidate) throw { code: "candidate_missing", message: "没有可决定的 Candidate Next Action。" };
    return invoke("decide_context_next_action", { candidate_id: candidate.candidate_id, decision, ...(editedText ? { edited_text: editedText } : {}), idempotency_key: `p3-131-ui-${decision}-001` });
  }
  async function action(name) {
    if (name.startsWith("nav:")) { state.page = name.slice(4); render(); return; }
    if (name === "selection") { state.selection = !state.selection; state.receipt = "本地展示选中状态已改变；未写入 Runtime。"; render(); return; }
    state.busy = true; state.error = null; render();
    try {
      if (name === "capture") { const result = await invoke("capture_record", { text: SUFFICIENT_TEXT, key: "p3-130-capture-001" }); state.receipt = `capture_record: ${result.status}`; }
      if (name === "capture-insufficient") { const result = await invoke("capture_record", { text: INSUFFICIENT_TEXT, key: "p3-131-insufficient-001" }); state.receipt = `capture_record: ${result.status} · ${result.link_status}`; }
      if (name === "confirm" || name === "link-reject") { const record = currentCapture(); if (!record) throw { code: "capture_missing", message: "没有可确认的 Capture。" }; const result = await invoke("confirm_capture_context", { capture_id: record.id, context_id: CONTEXT_ID, decision: name === "confirm" ? "confirm" : "reject", idempotency_key: `p3-131-ui-link-${name}` }); state.receipt = `confirm_capture_context: ${result.status} · ${result.decision}`; }
      if (name === "accept") { const result = await decide("accept"); state.receipt = `candidate decision: ${result.decision} · ${result.action?.action_id || "no action"}`; }
      if (name === "edit-accept") { const result = await decide("edit_accept", EDITED_TEXT); state.receipt = `candidate decision: ${result.decision} · ${result.action?.action_id || "no action"}`; }
      if (name === "candidate-reject") { const result = await decide("reject"); state.receipt = `candidate decision: ${result.decision}`; }
      if (name === "defer") { const result = await decide("defer"); state.receipt = `candidate decision: ${result.decision}`; }
      if (name === "complete") { const current = openAction(); if (!current) throw { code: "action_missing", message: "没有可完成的已确认 Action。" }; const result = await invoke("record_action_result", { action_id: current.action_id, result: "completed", result_text: "已完成合成验收记录整理与复核。", idempotency_key: "p3-131-ui-result-001" }); state.receipt = `record_action_result: ${result.status} · ${result.result}`; }
      await load();
    } catch (error) { state.error = message(error); }
    state.busy = false; render();
  }
  app.addEventListener("click", (event) => { const target = event.target.closest("[data-action]"); if (target) action(target.dataset.action); });
  (async () => { try { await load(); } catch (error) { state.error = message(error); } render(); })();
})();
