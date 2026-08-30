/* P3-140 is an adapter on the retained Today shell, not a second page system.
 * It invokes only the pre-existing get_today IPC, uses fixed synthetic DTOs,
 * and never invokes a Provider/model/network command. */
(() => {
  "use strict";

  const runtime = window.__P3_116_RUNTIME__;
  const invoke = window.__TAURI__ && window.__TAURI__.core && window.__TAURI__.core.invoke;
  if (!runtime) return;

  const state = {
    serial: 0,
    requestId: null,
    scenario: "normal",
    healthIncluded: true,
    response: null,
    error: null,
    loading: false,
  };
  // A process-local opaque token prevents a post-feedback restart from
  // replaying a superseded request id.  It contains no user content and is
  // never persisted outside the synthetic response audit.
  const sessionToken = `${Date.now().toString(36)}-${Math.floor(Math.random() * 0x1000000).toString(36)}`;

  function escape(value) {
    return String(value).replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[character]);
  }

  function freshId(kind) {
    state.serial += 1;
    return `p3-140:ui-${sessionToken}-${kind}-${state.serial}`;
  }

  function authorization() {
    return state.healthIncluded
      ? "p3-140-synthetic-cross-domain-granted"
      : "p3-140-synthetic-person-granted";
  }

  function panel() {
    const host = document.getElementById("main-content");
    if (!host || runtime.state.page !== "today") return null;
    let element = host.querySelector("[data-p3140-panel]");
    if (!element) {
      element = document.createElement("section");
      element.className = "panel p3140-panel";
      element.dataset.p3140Panel = "true";
      host.prepend(element);
    }
    return element;
  }

  function cards(response) {
    if (!response.results.length) return '<p class="quiet p3140-empty">暂无足够证据形成 Today 候选；LifeOS 没有用编造建议填补空白。</p>';
    return response.results.map((item) => `<article class="p3140-card" data-p3140-result="${escape(item.result_id)}">
      <div class="p3140-card-head"><span class="identity ${item.identity === "health_safety_stop" ? "warning" : ""}">${escape(item.identity === "health_safety_stop" ? "Safety stop" : "System suggestion")}</span><button type="button" class="quiet-link" data-p3140="evidence" data-p3140-result="${escape(item.result_id)}">查看依据</button></div>
      <strong>${escape(item.title)}</strong><p>${escape(item.why_today)}</p>
      <p class="tiny">不确定性：${escape(item.uncertainty)}</p>
      ${item.stop_condition ? `<p class="p3140-stop">停止条件：${escape(item.stop_condition)}</p>` : ""}
      <div class="p3140-evidence" hidden><span>证据引用</span>${item.evidence_refs.map((reference) => `<code>${escape(reference)}</code>`).join("")}</div>
      <div class="actions p3140-feedback">${item.feedback_options.map((decision) => `<button type="button" data-p3140="feedback" data-p3140-decision="${escape(decision)}" data-p3140-result="${escape(item.result_id)}" class="${decision === "confirm" ? "button primary" : decision === "reject" ? "button danger" : "button"}">${({ confirm: "确认", edit: "编辑", reject: "拒绝", ignore: "忽略", correct: "纠正" })[decision]}</button>`).join("")}</div>
    </article>`).join("");
  }

  function render() {
    const target = panel();
    if (!target) return;
    target.dataset.p3140Rendered = "true";
    if (!invoke) {
      target.innerHTML = '<span class="section-label">Today intelligence · P3-140</span><p class="quiet">当前不是 Tauri Runtime；未显示任何 Today Intelligence 成功状态。</p>';
      return;
    }
    const response = state.response;
    const status = state.loading ? "正在读取固定合成证据…" : state.error ? `已失败关闭：${escape(state.error.code || "runtime_rejected")}` : response ? "固定合成 · 候选仍待你决定" : "等待受控请求";
    const question = response && response.question ? `<section class="p3140-question"><strong>需要你确认</strong><p>${escape(response.question.text)}</p><span class="tiny">${escape(response.question.purpose)}</span><div class="actions"><button type="button" class="button" data-p3140="skip-question">跳过本次问题</button></div></section>` : "";
    const disclosure = response ? `<p class="tiny p3140-disclosure">${response.cross_domain_limited ? "本次跨域已受限。" : "本次为受控跨域候选。"} 引用：${response.disclosure_refs.map(escape).join(" · ")}</p>` : "";
    const feedback = response && response.feedback.decision ? `<p class="p3140-receipt">已记录 ${escape(response.feedback.decision)} 反馈；${response.recomputation.invalidated_refs.length ? "仅目标切片失效并重算。" : "候选没有提升为持久事实。"}</p>` : "";
    target.innerHTML = `<div class="section-head p3140-head"><div><span class="section-label">Today intelligence · P3-140</span><h2>跨域 Today 候选</h2><p class="quiet">${status}</p></div><span class="pill">离线 · 无 Provider</span></div>
      <div class="p3140-controls"><label>固定场景<select data-p3140="scenario" ${state.loading ? "disabled" : ""}>${[["normal","常规"],["counterfactual","反事实"],["missing_health","Health 缺失"],["missing_health_skip","跳过后降级"],["health_stop","Health 停止"],["insufficient","证据不足"]].map(([value,label]) => `<option value="${value}" ${state.scenario === value ? "selected" : ""}>${label}</option>`).join("")}</select></label><button type="button" class="button" data-p3140="toggle-health" ${state.loading ? "disabled" : ""}>${state.healthIncluded ? "本次移除 Health" : "本次加入 Health"}</button><button type="button" class="button" data-p3140="failure" ${state.loading ? "disabled" : ""}>验证失败关闭</button></div>
      ${state.error ? `<div class="notice danger"><strong>没有显示成功</strong><br>${escape(state.error.message || "受控请求被拒绝。")}<br><button type="button" class="button" data-p3140="retry">返回受控场景</button></div>` : ""}
      ${question}<div class="p3140-card-grid">${response ? cards(response) : ""}</div>${feedback}${disclosure}`;
  }

  async function request(extra = {}) {
    if (!invoke) return;
    state.loading = true;
    state.error = null;
    if (!extra.request_id) state.requestId = freshId(extra.kind || state.scenario);
    render();
    const payload = {
      scenario: state.scenario,
      request_id: extra.request_id || state.requestId,
      health_included: state.healthIncluded,
      authorization: authorization(),
      ...extra,
    };
    delete payload.kind;
    try {
      const output = await invoke("get_today", { request: payload });
      state.response = output.intelligence || null;
      state.error = state.response ? null : { code: "today_response_missing", message: "Runtime 未返回 P3-140 受控响应。" };
    } catch (error) {
      state.error = typeof error === "object" && error ? error : { code: "runtime_rejected", message: String(error) };
      state.response = null;
    } finally {
      state.loading = false;
      render();
    }
  }

  document.addEventListener("click", (event) => {
    const action = event.target.closest("[data-p3140]");
    if (!action) return;
    event.preventDefault();
    event.stopPropagation();
    const kind = action.dataset.p3140;
    if (kind === "evidence") {
      const card = action.closest(".p3140-card");
      const evidence = card && card.querySelector(".p3140-evidence");
      if (evidence) evidence.hidden = !evidence.hidden;
      return;
    }
    if (kind === "scenario") return;
    if (kind === "toggle-health") {
      state.healthIncluded = !state.healthIncluded;
      request({ kind: "health-change" });
      return;
    }
    if (kind === "failure") {
      request({ kind: "failure", fault: "over_budget" });
      return;
    }
    if (kind === "retry") {
      request({ kind: "retry" });
      return;
    }
    if (kind === "skip-question") {
      state.scenario = "missing_health_skip";
      request({ kind: "skip-question" });
      return;
    }
    if (kind === "feedback" && state.response) {
      request({
        kind: `feedback-${action.dataset.p3140Decision}`,
        feedback: { result_id: action.dataset.p3140Result, decision: action.dataset.p3140Decision, detail: action.dataset.p3140Decision === "correct" ? "缩小范围" : undefined },
        expected_generation: state.response.snapshot_generation,
      });
    }
  }, true);

  document.addEventListener("change", (event) => {
    const action = event.target.closest("[data-p3140='scenario']");
    if (!action) return;
    event.preventDefault();
    event.stopPropagation();
    state.scenario = action.value;
    request({ kind: "scenario-change" });
  }, true);

  let scheduled = false;
  function attach() {
    scheduled = false;
    if (runtime.state.page !== "today") return;
    const target = panel();
    if (!target) return;
    if (!state.response && !state.error && !state.loading) request({ kind: "initial" });
    else if (!target.dataset.p3140Rendered) render();
  }
  new MutationObserver(() => {
    if (!scheduled) {
      scheduled = true;
      queueMicrotask(attach);
    }
  }).observe(document.body, { childList: true, subtree: true });
  attach();
})();
