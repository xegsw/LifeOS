"use strict";

// P3-134 deliberately leaves the P3-116 renderer in app.js intact.  This
// adapter is the only Runtime seam: it maps typed P3-133 DTOs to existing
// P3-116 nodes and intercepts only the actions that now have a local meaning.
(() => {
  const ui = window.__P3_116_RUNTIME__;
  if (!ui) return;

  const CONTEXT = "ctx:project:local-work-self-use";
  const SYN_TEXT = "整理 LifeOS Context Recovery 合成验收记录。";
  const SYN_KEY = "p3-130-capture-001";
  const SYN_SHORT = "LifeOS Context Recovery 合成记录。";
  const SYN_SHORT_KEY = "p3-131-insufficient-001";
  const SYN_EDIT = "整理并复核 LifeOS Context Recovery 合成验收记录。";
  const SYN_RESULT = "已完成合成验收记录整理与复核。";
  const runtime = { status: null, today: null, recovery: null, next: null, global: null, understanding: null, error: null, busy: false, sequence: 0, removed: [], lastCapture: null };

  const invoke = (command, request) => {
    const target = window.__TAURI__?.core?.invoke;
    if (!target) return Promise.reject({ code: "tauri_invoke_unavailable", message: "仅 actual Tauri 可调用本地 Runtime。" });
    return target(command, { request });
  };
  const page = () => ui.state.page === "detail" ? "context_detail" : "today";
  const key = (label) => `p3-131-ui-${label}-${++runtime.sequence}`;
  const clean = (value) => String(value || "").replace(/[<>&]/g, (char) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;" }[char]));
  const localError = (error) => { runtime.error = { code: error?.code || "runtime_unavailable", message: error?.message || "本地 Runtime 未显示成功；没有写入。" }; };

  async function refresh() {
    runtime.status = await invoke("runtime_status", {});
    runtime.today = await invoke("get_today", {});
    runtime.recovery = await invoke("get_context_recovery", { context_id: CONTEXT });
    runtime.next = await invoke("get_context_next_action", { context_id: CONTEXT });
    const selection = runtime.today.records?.[runtime.today.records.length - 1]?.id;
    runtime.global = await invoke("assemble_global_ai_context", { page: page(), ...(selection ? { selection_ref: selection } : {}), ...(runtime.removed.length ? { removed_context_kinds: runtime.removed } : {}) });
    runtime.understanding = await invoke("get_evidence_backed_understanding", { context_id: CONTEXT, page: page(), ...(selection ? { selection_ref: selection } : {}), ...(runtime.removed.length ? { removed_context_kinds: runtime.removed } : {}), request_id: `p3-132-ui-${++runtime.sequence}` });
  }

  function setText(node, value) { if (node && node.textContent !== value) node.textContent = value; }
  function runtimeMode() { const actions = runtime.today?.confirmed_actions || []; return actions.length ? "normal" : runtime.today?.records?.length ? "insufficient" : "empty"; }

  function applyToday() {
    const target = runtimeMode();
    if (ui.state.page === "today" && ui.state.todayMode !== target) { ui.state.todayMode = target; ui.render(); return true; }
    const focus = runtime.today?.confirmed_actions?.[0];
    if (focus) {
      setText(document.querySelector(".reference-focus .focus-title"), focus.text);
      setText(document.querySelector(".reference-focus .focus-subtitle"), `已确认 Project-backed Context · ${runtime.recovery?.project_title || "本地 Work"}`);
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
    // Preserve the byte-identical P3-116 Capture surface.  The fixed
    // synthetic value stays inside this adapter and is never rendered as a
    // replacement input control; only the existing control's action changes.
    const buttons = [...document.querySelectorAll(".modal .actions [data-action]")];
    if (runtime.lastCapture?.record) {
      if (buttons[0]) buttons[0].dataset.action = "runtime:confirm";
      if (buttons[1]) buttons[1].dataset.action = "close-modal";
    } else {
      if (buttons[0]) buttons[0].dataset.action = "runtime:capture";
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

  function bindGlobal() {
    const panel = document.querySelector(".ai-panel");
    if (!panel || !runtime.global) return;
    panel.dataset.runtimeContext = "request-local";
    const chips = panel.querySelector(".context-chip-wrap");
    if (chips) {
      const existing = new Set([...chips.querySelectorAll(".context-chip")].map((node) => node.textContent.trim()));
      runtime.global.included.forEach((item) => {
        const name = item.kind === "person" ? "Person" : item.kind === "page" ? `Page: ${item.reference}` : item.kind === "selection" ? "Selection" : null;
        if (name && !existing.has(name)) chips.insertAdjacentHTML("beforeend", `<span class="context-chip">${clean(name)}</span>`);
      });
    }
    const candidate = runtime.next?.candidates?.[0];
    if (candidate) { const candidateText = panel.querySelector(".ai-card p"); if (candidateText) candidateText.textContent = `候选：${candidate.text}`; }
    panel.querySelectorAll("[data-action='candidate:action:confirm']").forEach((button) => { button.dataset.action = "runtime:accept"; });
    panel.querySelectorAll("[data-action='candidate:action:edit']").forEach((button) => { button.dataset.action = "runtime:edit-accept"; });
    panel.querySelectorAll("[data-action='candidate:action:reject']").forEach((button) => { button.dataset.action = "runtime:reject"; });
    panel.querySelectorAll("[data-action='candidate:action:ignore']").forEach((button) => { button.dataset.action = "runtime:defer"; });
    panel.querySelectorAll("[data-action='candidate:decision:confirm']").forEach((button) => { button.dataset.action = "runtime:feedback-confirm"; });
    panel.querySelectorAll("[data-action='candidate:decision:correct']").forEach((button) => { button.dataset.action = "runtime:feedback-correct"; });
  }

  function decorate() {
    if (runtime.busy) return;
    document.documentElement.dataset.runtime = "p3-133-offline-synthetic";
    if (applyToday()) { queueMicrotask(decorate); return; }
    disclosure(); decorateModal(); bindContextDetail(); bindGlobal();
    const main = document.querySelector("#main-content");
    if (main && runtime.error && !main.querySelector("[data-runtime-error]")) main.insertAdjacentHTML("afterbegin", `<section class="notice danger" data-runtime-error><strong>本地操作未显示成功</strong><br>${clean(runtime.error.message)} (${clean(runtime.error.code)})</section>`);
  }
  async function rerender() { ui.render(); await Promise.resolve(); decorate(); }

  async function run(action, input) {
    runtime.busy = true; runtime.error = null;
    try {
      if (action === "capture") {
        const text = input; // Read before any render: the modal textarea is about to be re-created.
        if (text !== SYN_TEXT) throw { code: "synthetic_input_rejected", message: "此离线 run 只接受固定合成文本；未写入。" };
        runtime.lastCapture = await invoke("capture_record", { text, key: SYN_KEY });
      } else if (action === "capture-short") {
        runtime.lastCapture = await invoke("capture_record", { text: SYN_SHORT, key: SYN_SHORT_KEY });
      } else if (action === "confirm") {
        const capture = runtime.lastCapture?.record || runtime.today?.records?.[0];
        if (!capture) throw { code: "capture_missing", message: "没有可确认的 Capture；未写入。" };
        await invoke("confirm_capture_context", { capture_id: capture.id, context_id: CONTEXT, decision: "confirm", idempotency_key: key("context-confirm") });
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
        await invoke("record_action_result", { action_id: current.action_id, result: "completed", result_text: SYN_RESULT, idempotency_key: key("action-complete") });
      } else if (action.startsWith("feedback-")) {
        const decision = action.slice("feedback-".length); const understanding = runtime.understanding?.understanding_id;
        if (!understanding) throw { code: "understanding_missing", message: "没有可反馈的 Understanding；未写入。" };
        await invoke("decide_understanding_feedback", { understanding_id: understanding, decision, idempotency_key: key(`feedback-${decision}`) });
      }
      await refresh();
    } catch (error) { localError(error); }
    finally { runtime.busy = false; await rerender(); }
  }

  document.addEventListener("click", (event) => {
    const target = event.target.closest("[data-action]"); if (!target) return;
    const action = target.dataset.action;
    const map = { "runtime:capture": "capture", "runtime:capture-short": "capture-short", "runtime:confirm": "confirm", "runtime:accept": "accept", "runtime:edit-accept": "edit-accept", "runtime:reject": "reject", "runtime:defer": "defer", "runtime:complete": "complete", "runtime:feedback-confirm": "feedback-confirm", "runtime:feedback-correct": "feedback-correct" };
    if (map[action]) {
      event.preventDefault(); event.stopImmediatePropagation();
      const input = action === "runtime:capture" ? SYN_TEXT : undefined;
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

  document.addEventListener("keydown", (event) => { if (event.key === "Escape" && runtime.busy) runtime.busy = false; });
  // Do not observe the P3-116 live renderer: its aria-live updates can recurse
  // through DOM decoration.  Every typed Runtime operation above finishes with
  // rerender(), while untouched P3-116 navigation continues to render itself.
  refresh().then(rerender).catch((error) => { localError(error); return rerender(); });
})();
