(() => {
  "use strict";

  const sourceRef = "source:synthetic:memory-fixture";
  const personAuth = "AUTH-SYN-PERSON-GRANTED";
  const crossAuth = "AUTH-SYN-CROSS-GRANTED";
  // Tauri v2 command arguments are keyed by their Rust parameter name.  The
  // explicit wrapper keeps every Inspector request on the four fixed P3-139
  // IPCs rather than silently falling back to a renderer-only path.
  const call = (command, request) => {
    const invoke = window.__TAURI__?.core?.invoke;
    if (!invoke) return Promise.reject({ code: "tauri_invoke_unavailable", message: "仅 actual Tauri 可运行本地 Context Inspector。" });
    return invoke(command, { request });
  };

  const memory = (memory_id, domain, statement, memory_type) => ({
    operation: "create", memory_id, replacement_id: null, statement, memory_type,
    source_refs: [sourceRef], observed_at_ms: null, domain, scope: "person",
    expected_generation: null, idempotency_key: `p3-139-ui-create-${memory_id}`
  });
  const state = (state_id, state_key, value, domain) => ({
    operation: "set", state_id, replacement_id: null, state_key, value, domain,
    source_refs: [sourceRef], expires_at_ms: Date.now() + 86_400_000,
    expected_generation: null, idempotency_key: `p3-139-ui-state-${state_id}`
  });
  const isAlreadyStored = (error) => error?.code === "memory_exists" || error?.code === "state_exists";

  function renderInspector() {
    const section = document.createElement("section");
    section.id = "p3-139-context-inspector";
    section.className = "p3-139-context-inspector";
    section.dataset.runtime = "actual-tauri-required";
    section.innerHTML = `
      <div class="p3-139-heading">
        <div><span class="section-label">本地最小披露</span><h2>Context Inspector</h2></div>
        <span class="p3-139-status" data-p3-139-status>未初始化</span>
      </div>
      <p data-p3-139-summary>固定合成 Memory 与 Current State 只在本地 SQLite 中使用；本面板不发起外部派发。</p>
      <div class="p3-139-actions">
        <button class="button primary" type="button" data-p3-139-action="seed">写入固定合成资料</button>
        <button class="button" type="button" data-p3-139-action="work">解析 Work Context</button>
        <button class="button" type="button" data-p3-139-action="remove-health">跨领域解析并临时移除 Health</button>
        <button class="button ghost" type="button" data-p3-139-action="receipt">读取非内容收据</button>
        <button class="button ghost" type="button" data-p3-139-action="reject">验证无效 Authorization</button>
      </div>
      <div class="p3-139-columns" aria-live="polite">
        <div><strong>本次使用</strong><ul data-p3-139-included><li>尚无 request</li></ul></div>
        <div><strong>本次排除</strong><ul data-p3-139-excluded><li>尚无 request</li></ul></div>
      </div>
      <dl class="p3-139-meta">
        <div><dt>request</dt><dd data-p3-139-request>—</dd></div>
        <div><dt>预算</dt><dd data-p3-139-budget>—</dd></div>
        <div><dt>外部派发</dt><dd data-p3-139-dispatch>0</dd></div>
      </dl>`;
    document.body.append(section);
    const style = document.createElement("style");
    style.textContent = `
      .p3-139-context-inspector{position:fixed;right:22px;bottom:22px;z-index:20;width:min(500px,calc(100vw - 44px));padding:18px;border:1px solid #d4e2db;border-radius:18px;background:rgba(255,255,255,.98);box-shadow:0 16px 42px rgba(35,55,46,.18);color:#1d3328;font:14px/1.45 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}.p3-139-heading,.p3-139-actions,.p3-139-meta{display:flex;align-items:center;gap:10px}.p3-139-heading{justify-content:space-between}.p3-139-heading h2{margin:2px 0 0;font-size:19px}.p3-139-status{border-radius:999px;background:#e7f3ed;padding:5px 9px;font-size:12px}.p3-139-actions{flex-wrap:wrap;margin:12px 0}.p3-139-columns{display:grid;grid-template-columns:1fr 1fr;gap:12px}.p3-139-columns>div{min-height:90px;padding:10px;border-radius:10px;background:#f6faf7}.p3-139-columns ul{margin:7px 0 0;padding-left:18px}.p3-139-meta{justify-content:space-between;margin:12px 0 0}.p3-139-meta div{min-width:0}.p3-139-meta dt{font-size:11px;color:#607269}.p3-139-meta dd{margin:2px 0 0;word-break:break-word}@media(max-width:700px){.p3-139-context-inspector{right:12px;bottom:12px;width:calc(100vw - 24px)}.p3-139-columns{grid-template-columns:1fr}.p3-139-meta{flex-wrap:wrap}}`;
    document.head.append(style);
    return section;
  }

  function list(root, selector, entries) {
    const host = root.querySelector(selector);
    host.replaceChildren(...(entries.length ? entries : [{ reference: "无", reason: "—" }]).map((entry) => {
      const row = document.createElement("li");
      row.textContent = `${entry.reference} · ${entry.reason}`;
      return row;
    }));
  }

  function show(root, result, label) {
    root.querySelector("[data-p3-139-status]").textContent = label;
    root.querySelector("[data-p3-139-summary]").textContent = "收据只包含 refs、理由、Authorization 与预算；不显示 Memory/State 原文。";
    root.querySelector("[data-p3-139-request]").textContent = result.request_id;
    root.querySelector("[data-p3-139-budget]").textContent = `${result.used_token_estimate}/${result.token_budget} · Top-${result.top_k}`;
    root.querySelector("[data-p3-139-dispatch]").textContent = String(result.model_dispatch_count);
    list(root, "[data-p3-139-included]", result.included || []);
    list(root, "[data-p3-139-excluded]", result.excluded || []);
  }

  async function seed(root) {
    const profiles = [
      ["memory:synthetic:person", "person", "Synthetic Person: prefers concise daily planning.", "identity"],
      ["memory:synthetic:work", "work", "Synthetic Work: weekday focus block supports review planning.", "preference"],
      ["memory:synthetic:health", "health", "Synthetic Health: low-impact recovery only when explicitly authorized.", "constraint"],
      ["memory:synthetic:candidate", "work", "Synthetic Candidate: unconfirmed preference.", "preference"]
    ];
    for (const [memory_id, domain, statement, memory_type] of profiles) {
      try {
        const created = await call("upsert_durable_memory", memory(memory_id, domain, statement, memory_type));
        if (memory_id !== "memory:synthetic:candidate") {
          await call("upsert_durable_memory", { operation: "confirm", memory_id, replacement_id: null, statement: null, memory_type: null, source_refs: null, observed_at_ms: null, domain, scope: "person", expected_generation: created.generation, idempotency_key: `p3-139-ui-confirm-${memory_id}` });
        }
      } catch (error) { if (!isAlreadyStored(error)) throw error; }
    }
    for (const input of [
      ["state:synthetic:load", "work_load", "synthetic_work_load_high", "work"],
      ["state:synthetic:fatigue", "fatigue", "synthetic_fatigue_moderate", "health"]
    ]) {
      try { await call("update_current_state", state(...input)); } catch (error) { if (!isAlreadyStored(error)) throw error; }
    }
    root.querySelector("[data-p3-139-status]").textContent = "本地 fixture 已写入";
    root.querySelector("[data-p3-139-summary]").textContent = "已保存 4 条 Durable Memory（其中 1 条未确认）与 2 条 Current State；没有外部派发。";
  }

  async function resolve(root, kind) {
    const removed = kind === "remove-health" ? ["health"] : null;
    const response = await call("resolve_request_context", {
      request_id: kind === "work" ? "request:synthetic:ui-work" : "request:synthetic:ui-cross-removed",
      task_type: kind === "work" ? "work" : "cross_domain",
      query_text: kind === "work" ? "planning" : "recovery",
      authorization_id: kind === "work" ? personAuth : crossAuth,
      health_necessary: kind !== "work", removed_domains: removed, top_k: 3, token_budget: 256
    });
    show(root, response, kind === "work" ? "Work 已解析" : "Health 仅本次移除");
  }

  function boot() {
    const root = renderInspector();
    root.addEventListener("click", async (event) => {
      const action = event.target.closest("[data-p3-139-action]")?.getAttribute("data-p3-139-action");
      if (!action) return;
      try {
        if (action === "seed") await seed(root);
        if (action === "work" || action === "remove-health") await resolve(root, action);
        if (action === "receipt") show(root, await call("get_context_disclosure_receipt", { request_id: "request:synthetic:ui-cross-removed" }), "重启后可读取");
        if (action === "reject") {
          await call("resolve_request_context", { request_id: "request:synthetic:ui-rejected", task_type: "work", query_text: "planning", authorization_id: "AUTH-SYN-REVOKED", health_necessary: false, removed_domains: null, top_k: 3, token_budget: 256 });
        }
      } catch (error) {
        root.querySelector("[data-p3-139-status]").textContent = error?.code || "failed_closed";
        root.querySelector("[data-p3-139-summary]").textContent = error?.message || "本地请求未显示成功。";
      }
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot, { once: true }); else boot();
})();
