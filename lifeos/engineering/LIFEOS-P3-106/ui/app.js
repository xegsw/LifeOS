(() => {
  "use strict";
  const invoke = window.__TAURI__?.core?.invoke;
  const PRIMARY_TEXT = "P3-104 固定非敏感记录：核对今日页本地运行时。";
  const CONFLICT_TEXT = "P3-104 固定非敏感冲突文本：必须被阻断。";
  const FAILURE_TEXT = "P3-104 固定非敏感失败夹具：不得持久化。";
  const PRIMARY_KEY = "p3-104-ui-primary";
  const FAILURE_KEY = "p3-104-ui-failure";
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const setText = (selector, text) => { const node = $(selector); if (node) node.textContent = text; };
  const errorCode = (error) => typeof error === "object" && error && error.code ? error.code : "unknown_ipc_error";

  const showNotice = (message, error = false) => {
    const notice = $("#composer-status");
    if (!notice) return;
    notice.textContent = message;
    notice.classList.toggle("error", error);
    notice.hidden = false;
  };
  const safeInvoke = async (command, request = {}) => {
    if (typeof invoke !== "function") throw { code: "tauri_bridge_unavailable" };
    return invoke(command, { request });
  };
  const renderToday = (payload) => {
    const record = payload.records[0];
    $$('[data-backend="record-count"]').forEach((node) => { node.textContent = String(payload.records.length); });
    $$('[data-backend="audit-count"]').forEach((node) => { node.textContent = String(payload.audit.event_count); });
    $$('[data-backend="record-text"]').forEach((node) => { node.textContent = record ? record.content : "尚无本地记录；等待你明确发送固定非敏感文本。"; });
    $$('[data-backend="save-fact"]').forEach((node) => { node.textContent = record ? "已由本地 backend 耐久恢复" : "尚未保存 · AI 与外部能力关闭"; });
    document.documentElement.dataset.backendState = record ? "loaded" : "empty";
  };
  const refreshToday = async () => {
    try {
      const payload = await safeInvoke("get_today", {});
      renderToday(payload);
      return payload;
    } catch (error) {
      $$('[data-backend="record-text"]').forEach((node) => { node.textContent = "backend 拒绝读取；未展示缓存或部分记录。"; });
      showNotice(`读取被阻断：${errorCode(error)}。`, true);
      throw error;
    }
  };
  const capture = async (text, key, expected) => {
    showNotice("正在等待本地 backend 权威回执…");
    try {
      const result = await safeInvoke("capture_record", { text, key });
      showNotice(result.status === "saved" ? "已保存：SQLite 原子发布完成，用户原文身份保持不变。" : "幂等重复：记录未增加，backend 追加了合法重复审计。");
      await refreshToday();
      if (expected && result.status !== expected) throw { code: "unexpected_backend_status" };
      return result;
    } catch (error) {
      showNotice(`已阻断：${errorCode(error)}。未显示成功，backend 状态将重新读取。`, true);
      await refreshToday().catch(() => {});
      throw error;
    }
  };
  const loadRuntime = async () => {
    const status = await safeInvoke("runtime_status", {});
    const target = $("#runtime-flags");
    if (target) {
      target.replaceChildren();
      [
        ["运行模式", status.offline ? "离线" : "非预期"], ["AI", status.ai_enabled ? "非预期启用" : "未启用"],
        ["Renderer 直接能力", String(status.renderer_direct_capabilities.length)], ["IPC allowlist", status.ipc_allowlist.join(" / ")],
        ["未知 IPC", status.unknown_ipc], ["文件 / DB / 路径", status.filesystem || status.raw_database || status.generic_path_api ? "非预期" : "关闭"],
        ["Shell / Process / Network", status.shell || status.process_spawn || status.network ? "非预期" : "关闭"],
        ["Vault / Export / Sync", status.vault || status.export || status.sync ? "非预期" : "关闭"],
        ["减少动态偏好", window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "系统已启用" : "系统未请求"]
      ].forEach(([label, value]) => { const row = document.createElement("p"); row.textContent = `${label}：${value}`; target.append(row); });
    }
    return status;
  };

  $$('[data-action="capture"]').forEach((button) => button.addEventListener("click", () => capture(PRIMARY_TEXT, PRIMARY_KEY).catch(() => {})));
  $("#repeat-capture")?.addEventListener("click", () => capture(PRIMARY_TEXT, PRIMARY_KEY, "idempotent_repeat").catch(() => {}));
  $("#probe-conflict")?.addEventListener("click", () => capture(CONFLICT_TEXT, PRIMARY_KEY).catch(() => {}));
  $("#probe-failure")?.addEventListener("click", () => capture(FAILURE_TEXT, FAILURE_KEY).catch(() => {}));
  $$('[data-unimplemented]').forEach((button) => button.addEventListener("click", () => showNotice(`${button.dataset.unimplemented || "此功能"}未启用；没有调用 IPC，也没有更改本地记录。`)));

  $("#toggle-diagnostics")?.addEventListener("click", () => {
    const panel = $("#diagnostics-panel"); if (!panel) return;
    panel.hidden = !panel.hidden;
    $("#toggle-diagnostics").setAttribute("aria-expanded", String(!panel.hidden));
    if (!panel.hidden) panel.querySelector("button")?.focus();
  });
  $("#close-diagnostics")?.addEventListener("click", () => {
    const panel = $("#diagnostics-panel"); if (panel) panel.hidden = true;
    $("#toggle-diagnostics")?.setAttribute("aria-expanded", "false"); $("#toggle-diagnostics")?.focus();
  });
  $("#probe-unknown")?.addEventListener("click", async () => {
    try { await safeInvoke("unknown_p3_104_command", {}); setText("#diagnostic-result", "FAIL：未知命令被接受。"); }
    catch (_error) { setText("#diagnostic-result", "PASS：未知 IPC 被 invoke handler 拒绝，零副作用。"); $("#diagnostic-result")?.classList.add("pass"); }
  });
  $("#probe-schema")?.addEventListener("click", async () => {
    const before = await safeInvoke("get_today", {});
    const probes = [["capture_record", { text: PRIMARY_TEXT, key: PRIMARY_KEY, path: "/private/tmp/escape" }], ["get_today", { sql: "SELECT * FROM captures" }], ["runtime_status", { shell: "echo blocked" }]];
    let blocked = 0;
    for (const [command, request] of probes) { try { await safeInvoke(command, request); } catch (_error) { blocked += 1; } }
    const after = await safeInvoke("get_today", {});
    const passed = blocked === probes.length && before.records.length === after.records.length && before.audit.event_count === after.audit.event_count;
    setText("#diagnostic-result", passed ? "PASS：路径／SQL／shell 额外字段全部拒绝，记录与审计不变。" : "FAIL：额外字段拒绝或无副作用条件未满足。");
    $("#diagnostic-result")?.classList.toggle("pass", passed);
  });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape" && !$("#diagnostics-panel")?.hidden) $("#close-diagnostics")?.click(); });
  document.addEventListener("DOMContentLoaded", async () => {
    try { await loadRuntime(); await refreshToday(); }
    catch (_error) { showNotice("启动读取失败；未显示缓存成功态。", true); }
  });
})();
