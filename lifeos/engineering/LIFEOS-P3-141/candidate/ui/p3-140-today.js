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
    healthReceipt: null,
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

  function isReal() {
    return runtime.status && runtime.status.input_mode === "real_self_use";
  }

  function healthEditor() {
    const receipt = state.healthReceipt ? `<p class="tiny p3140-receipt">${escape(state.healthReceipt)}</p>` : "";
    return `<section class="context-diff p3141-health-editor" data-p3141-health-editor>
      <strong>Health / Fitness · 五项结构化状态</strong>
      <p class="tiny">仅用于本地 Today；不支持自由文本、医疗诊断或治疗建议。</p>
      <div class="p3140-controls">
        <label>睡眠时长范围<select data-p3141-health="sleep_duration_range"><option value="under_five_hours">少于 5 小时</option><option value="five_to_seven_hours">5–7 小时</option><option value="seven_to_nine_hours" selected>7–9 小时</option><option value="over_nine_hours">超过 9 小时</option></select></label>
        <label>精力<select data-p3141-health="energy">${[1,2,3,4,5].map((value) => `<option value="${value}" ${value === 3 ? "selected" : ""}>${value} / 5</option>`).join("")}</select></label>
        <label>酸痛或疼痛<select data-p3141-health="soreness_or_pain"><option value="false" selected>否</option><option value="true">是</option></select></label>
        <label>训练负荷<select data-p3141-health="training_load"><option value="low">低</option><option value="medium" selected>中</option><option value="high">高</option></select></label>
        <label>可用时间<select data-p3141-health="available_time"><option value="under_thirty_minutes">少于 30 分钟</option><option value="thirty_to_sixty_minutes" selected>30–60 分钟</option><option value="sixty_to_one_hundred_twenty_minutes">60–120 分钟</option><option value="over_one_hundred_twenty_minutes">超过 120 分钟</option></select></label>
        <button type="button" class="button" data-p3141-health-save>保存五项状态</button>
      </div>${receipt}</section>`;
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
      ${healthEditor()}${question}<div class="p3140-card-grid">${response ? cards(response) : ""}</div>${feedback}${disclosure}`;
  }

  async function saveStructuredHealth(button) {
    if (!invoke) return;
    const editor = button.closest("[data-p3141-health-editor]");
    if (!editor) return;
    const value = (field) => editor.querySelector(`[data-p3141-health='${field}']`).value;
    const nonce = `${Date.now().toString(36)}-${Math.floor(Math.random() * 0x1000000).toString(36)}`;
    const real = isReal();
    const payload = {
      operation: "set",
      state_id: real ? `state:p3-141:real:health-ui-${nonce}` : `state:synthetic:health-ui-${nonce}`,
      replacement_id: null,
      state_key: "health_fitness_structured_v1",
      value: null,
      domain: "health",
      source_refs: [real ? "source:local:user-confirmed" : "source:synthetic:memory-fixture"],
      expires_at_ms: Date.now() + 86400000,
      expected_generation: null,
      idempotency_key: real ? `p3-141-real-ui-health-${nonce}` : `p3-141-health-${nonce}`,
      structured_health: {
        sleep_duration_range: value("sleep_duration_range"),
        energy: Number(value("energy")),
        soreness_or_pain: value("soreness_or_pain") === "true",
        training_load: value("training_load"),
        available_time: value("available_time"),
      },
    };
    button.disabled = true;
    try {
      await invoke("update_current_state", { request: payload });
      state.healthReceipt = "已在本地保存五项结构化状态；没有自由文本或医疗判断。";
      request({ kind: "health-state-updated" });
    } catch (error) {
      state.healthReceipt = `未保存：${String(error && (error.message || error.code) || "runtime_rejected")}`;
      render();
    } finally {
      button.disabled = false;
    }
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
    const healthSave = event.target.closest("[data-p3141-health-save]");
    if (healthSave) {
      event.preventDefault();
      event.stopPropagation();
      saveStructuredHealth(healthSave);
      return;
    }
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
