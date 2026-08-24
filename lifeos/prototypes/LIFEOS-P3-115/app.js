(() => {
  "use strict";
  const F = window.LIFEOS_FIXTURE;
  const app = document.querySelector(".app-shell");
  const state = {
    answer: "unanswered",
    feedback: "none",
    execution: "not_executed",
    result: "none",
    memory: "none",
    sourceFailure: null,
    motion: "full",
  };

  const $ = (s) => document.querySelector(s);
  const $$ = (s) => [...document.querySelectorAll(s)];
  const renderViewport = () => { $("#viewport-readout").textContent = `视口：${window.innerWidth} × ${window.innerHeight}`; };
  const toast = $("#toast");
  let toastTimer;
  const announce = (message) => {
    toast.textContent = message;
    toast.classList.add("show");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove("show"), 4300);
  };
  const show = (el, visible = true) => el.classList.toggle("hidden", !visible);
  const label = (value) => ({
    unanswered: "尚未回答", safe: "无加重／无警示", skip: "已跳过", warning: "警示信号",
    none: "尚无", accepted: "已认可", modified: "修改后接受", rejected: "已拒绝", deferred: "已延后",
    not_executed: "未执行", executed: "已执行", reported: "已报告结果", pending: "待确认", confirmed: "已确认", rejected_memory: "已拒绝",
  }[value] || value);

  const evidence = {
    work: [
      ["Advice", F.workAdvice.text], ["Why now", F.workAdvice.why], ["Source", `${F.domains.work.source} · 合成手工工作计划`], ["Artifact", F.domains.work.artifact], ["时间 / 时效", "2026-08-24 · 仅今天有效"], ["确定性", F.workAdvice.certainty], ["范围", "仅工作领域／产品演示准备"], ["停止条件", "没有可用时间或来源失效时，不显示为可靠建议"], ["身份", "Advice candidate；不会自动成为 Action"],
    ],
    health: [
      ["Advice", F.healthAdvice.text], ["Why now", "回答无警示后，才允许呈现低风险、可停止的选项。"], ["Source", `${F.domains.health.source} + SRC-SYN-INTERACTION-001`], ["Artifact", `${F.domains.health.artifact} + ART-SYN-ANSWER-001@v1`], ["时间 / 时效", "2026-08-24 · 当天有效"], ["确定性", "信息有限；不作医学判断"], ["范围", "仅此固定合成情境"], ["停止条件", "警示、未答、跳过、来源缺失／冲突／失权／过期时停止训练型建议"], ["身份", "Derivation / Advice candidate；用户处置与执行独立"],
    ],
  };

  function openDialog(id) { const d = document.getElementById(id); if (d && !d.open) d.showModal(); }
  function closeDialog(id) { const d = document.getElementById(id); if (d?.open) d.close(); }
  function setActiveView(name) {
    $$(".view").forEach((view) => { const active = view.id === `${name}-view`; view.hidden = !active; view.classList.toggle("active", active); });
    $$("[data-nav]").forEach((el) => { const active = el.dataset.nav === name; el.classList.toggle("active", active); if (el.matches("button")) el.setAttribute("aria-current", active ? "page" : "false"); });
    $("#main").focus({ preventScroll: true });
  }
  function renderTimeline() {
    const q = $("#timeline").children;
    q[1].className = `timeline-step ${state.answer === "unanswered" ? "current" : state.answer === "warning" ? "stale" : "done"}`;
    q[1].querySelector("small").textContent = state.answer === "warning" ? "警示停止" : label(state.answer);
    q[2].className = `timeline-step ${state.feedback !== "none" ? "done" : (state.answer === "safe" ? "current" : "")}`;
    q[2].querySelector("small").textContent = label(state.feedback);
    q[3].className = `timeline-step ${state.execution === "executed" ? "done" : state.feedback === "modified" ? "current" : ""}`;
    q[3].querySelector("small").textContent = label(state.execution);
    q[4].className = `timeline-step ${state.result === "reported" ? "done" : state.execution === "executed" ? "current" : ""}`;
    q[4].querySelector("small").textContent = label(state.result);
    q[5].className = `timeline-step ${state.memory === "pending" || state.memory === "confirmed" ? "done" : state.result === "reported" ? "current" : ""}`;
    q[5].querySelector("small").textContent = state.memory === "pending" ? "待确认候选" : label(state.memory);
  }
  function renderControls() {
    const controls = $("#lifecycle-controls");
    let html = "";
    if (state.feedback === "modified") html += '<p>修改后接受已记录为 Feedback；仍不等于执行。</p><button class="primary-button" type="button" data-action="record-not-executed">记录：尚未执行</button><button class="quiet-button" type="button" data-action="record-executed">记录：已执行</button>';
    if (state.execution === "executed" && state.result === "none") html = '<p>EXE 已是单独事实。下一步可由用户报告结果，而不是系统推定。</p><button class="primary-button" type="button" data-action="record-result">记录结果：未加重，仍感疲劳</button>';
    if (state.result === "reported") html = '<p>RES 已形成当天理解：今晚不再追加训练型建议，优先休息／记录状态。</p><button class="primary-button" type="button" data-action="show-memory">查看待确认 Memory candidate</button>';
    if (["pending", "confirmed", "rejected_memory"].includes(state.memory)) html = `<p>Memory candidate：${label(state.memory)}。它${state.memory === "confirmed" ? "只在此原型中显示为已确认" : "不会影响任何未来日期"}。</p><button class="quiet-button" type="button" data-action="revoke">撤销本次结果／重新关闭派生建议</button>`;
    controls.innerHTML = html;
    show(controls, Boolean(html));
  }
  function renderMemory() {
    const root = $("#memory-content");
    if (!state.memory || state.memory === "none") { root.className = "empty-memory"; root.innerHTML = "<p>还没有待确认的 Memory candidate。</p>"; return; }
    root.className = "empty-memory";
    root.innerHTML = `<span class="identity-tag derivation">MEM-CAND · ${label(state.memory)}</span><h2>${F.memoryCandidate.text}</h2><p>${F.memoryCandidate.scope}</p><div class="choice-row"><button class="primary-button" type="button" data-action="confirm-memory">确认有限范围</button><button class="quiet-button" type="button" data-action="reject-memory">拒绝候选</button></div>`;
  }
  function renderHealth() {
    const stage = $("#advice-stage"); const panel = $("#health-panel"); const pill = $("#health-state-pill"); const title = $("#health-stage-title");
    const failed = state.sourceFailure;
    if (failed) {
      title.textContent = "来源条件不成立：关闭个性化建议"; pill.textContent = `${failed} · fail-closed`; pill.className = "state-pill blocked"; show(stage, false);
      panel.innerHTML = `<div class="safety-icon" aria-hidden="true">!</div><div><h3>不伪装为可靠建议</h3><p>固定合成来源状态为“${failed}”。只显示缺口与保守记录选项；不输出个性化或训练型建议。</p></div><button class="text-button" type="button" data-action="reset">恢复初始原型状态 <span aria-hidden="true">→</span></button>`;
      return;
    }
    if (state.answer === "warning") {
      title.textContent = "健康警示：停止相关建议"; pill.textContent = "警示信号 · 已停止"; pill.className = "state-pill blocked"; show(stage, false);
      panel.innerHTML = '<div class="safety-icon" aria-hidden="true">!</div><div><h3>不要安排训练</h3><p>此原型不会判断伤病。请停止相关建议，并考虑联系合适的专业人士支持。</p></div><button class="text-button" type="button" data-open="evidence-dialog" data-advice="health">查看停止依据 <span aria-hidden="true">→</span></button>';
      return;
    }
    if (state.answer === "skip") {
      title.textContent = "已跳过问题：保持保守"; pill.textContent = "跳过 · 降级"; pill.className = "state-pill waiting"; show(stage, false);
      panel.innerHTML = '<div class="safety-icon" aria-hidden="true">⊘</div><div><h3>不把跳过当成安全回答</h3><p>不显示训练型建议。你可以休息或记录自己的状态；没有任何诊断或训练安排。</p></div><button class="text-button" type="button" data-action="reset">回到初始原型状态 <span aria-hidden="true">→</span></button>';
      return;
    }
    if (state.answer === "safe") {
      title.textContent = "回答无警示：出现一个可停止的选项"; pill.textContent = "无警示 · 低风险候选"; pill.className = "state-pill ready"; show(stage, true);
      panel.innerHTML = '<div class="safety-icon" aria-hidden="true">✓</div><div><h3>仍然是保守的选择</h3><p>只因这个回答会改变安全分类，才显示一个可选的、低强度非冲击恢复活动。</p></div><button class="text-button" type="button" data-open="evidence-dialog" data-advice="health">查看来源与停止条件 <span aria-hidden="true">→</span></button>';
      return;
    }
    title.textContent = "等待你的安全回答"; pill.textContent = "未回答 · 停止训练型建议"; pill.className = "state-pill waiting"; show(stage, false);
    panel.innerHTML = '<div class="safety-icon" aria-hidden="true">⊘</div><div><h3>先保守，再行动</h3><p>你可以休息、记录状态或跳过。此原型不会给出诊断、治疗、保证或训练处方。</p></div><button class="text-button" type="button" data-open="evidence-dialog" data-advice="health">查看来源与停止条件 <span aria-hidden="true">→</span></button>';
  }
  function render() { renderViewport(); renderHealth(); renderTimeline(); renderControls(); renderMemory(); }
  function reset() { Object.assign(state, { answer: "unanswered", feedback: "none", execution: "not_executed", result: "none", memory: "none", sourceFailure: null }); show($("#modify-panel"), false); render(); announce("已回到初始合成原型状态；没有数据被保存。"); }
  function answer(value) { state.sourceFailure = null; state.answer = value; state.feedback = "none"; state.execution = "not_executed"; state.result = "none"; state.memory = "none"; render(); announce(value === "safe" ? "已记录合成回答：无加重／无警示。现在才出现低风险候选。" : value === "skip" ? "已跳过：健康建议保持降级。" : "警示分支已触发：相关建议已停止。"); }
  function openEvidence(kind) { const content = $("#evidence-content"); content.innerHTML = `<div class="evidence-grid">${evidence[kind].map(([k, v]) => `<div class="evidence-cell"><strong>${k}</strong><span>${v}</span></div>`).join("")}</div>`; openDialog("evidence-dialog"); }
  function feedback(value) { state.feedback = value; state.execution = "not_executed"; state.result = "none"; state.memory = "none"; show($("#modify-panel"), false); render(); announce(`已记录 ${label(value)}（Feedback）。这不表示已经执行。`); }
  function revoke() { state.feedback = "none"; state.execution = "not_executed"; state.result = "none"; state.memory = "none"; state.answer = "unanswered"; render(); announce("已撤销本次链路：依赖的理解与建议回到 stale / 不显示；原始 Source 身份没有被改写。"); }
  document.addEventListener("click", (event) => {
    const target = event.target.closest("button, a"); if (!target) return;
    const nav = target.dataset.nav; if (nav) { event.preventDefault(); setActiveView(nav); return; }
    if (target.dataset.open === "evidence-dialog") { openEvidence(target.dataset.advice || "health"); return; }
    if (target.dataset.open) { openDialog(target.dataset.open); return; }
    if (target.dataset.close) { closeDialog(target.dataset.close); return; }
    switch (target.dataset.action) {
      case "capture": openDialog("capture-dialog"); break;
      case "toggle-motion": state.motion = state.motion === "full" ? "reduce" : "full"; app.dataset.motion = state.motion; target.setAttribute("aria-pressed", state.motion === "reduce"); target.textContent = state.motion === "reduce" ? "已启用低动态" : "低动态预览"; announce(state.motion === "reduce" ? "低动态预览已启用：动效改为即时、非位移反馈。" : "已恢复原型的克制过渡效果。"); break;
      case "answer-safe": answer("safe"); break;
      case "answer-skip": answer("skip"); break;
      case "answer-warning": answer("warning"); break;
      case "accept": feedback("accepted"); break;
      case "modify": show($("#modify-panel"), true); $("#modified-choice").focus(); break;
      case "confirm-modify": feedback("modified"); $("#advice-text").textContent = F.healthAdvice.modified; break;
      case "reject": feedback("rejected"); break;
      case "defer": feedback("deferred"); break;
      case "record-not-executed": state.execution = "not_executed"; render(); announce("已明确记录：尚未执行。不会被系统解释为完成。"); break;
      case "record-executed": state.execution = "executed"; render(); announce("已记录 EXE：实际执行由用户报告；仍没有结果结论。"); break;
      case "record-result": state.result = "reported"; render(); announce("已记录 RES：没有自报加重，仍感疲劳。已形成仅当日的理解更新。"); break;
      case "show-memory": state.memory = "pending"; render(); setActiveView("memory"); announce("已形成待确认、有限范围的 Memory candidate；不会影响未来日期。"); break;
      case "confirm-memory": state.memory = "confirmed"; render(); announce("原型中已确认有限范围候选；这不等于任何真实长期写入。"); break;
      case "reject-memory": state.memory = "rejected_memory"; render(); announce("已拒绝 Memory candidate；历史结果仍可见，没有被删除。"); break;
      case "source-failure": state.sourceFailure = target.dataset.failure; state.answer = "unanswered"; state.feedback = "none"; state.execution = "not_executed"; state.result = "none"; state.memory = "none"; render(); announce(`已注入固定合成来源异常：${target.dataset.failure}。建议已 fail-closed。`); break;
      case "reset": reset(); break;
      case "revoke": revoke(); break;
      default: break;
    }
  });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") $$('dialog[open]').forEach((d) => d.close()); });
  window.addEventListener("resize", renderViewport);
  $("[data-fixture='person-name']").textContent = F.person.name;
  $("[data-fixture='date']").textContent = F.person.date;
  render();
})();
