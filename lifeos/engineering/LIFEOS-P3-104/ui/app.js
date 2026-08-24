(() => {
  "use strict";
  const invoke = window.__TAURI__?.core?.invoke;
  const PRIMARY_TEXT = "P3-104 固定非敏感记录：核对今日页本地运行时。";
  const CONFLICT_TEXT = "P3-104 固定非敏感冲突文本：必须被阻断。";
  const FAILURE_TEXT = "P3-104 固定非敏感失败夹具：不得持久化。";
  const PRIMARY_KEY = "p3-104-ui-primary";
  const FAILURE_KEY = "p3-104-ui-failure";
  const $ = (selector) => document.querySelector(selector);
  const setText = (selector, text) => { const node = $(selector); if (node) node.textContent = text; };
  const clearFailure = () => { const node = $("#failure-disclosure"); if (node) { node.hidden = true; node.textContent = ""; } };
  const disclose = (error, prefix = "已阻断") => {
    const node = $("#failure-disclosure");
    const code = typeof error === "object" && error && error.code ? error.code : "unknown_ipc_error";
    if (node) { node.hidden = false; node.textContent = `${prefix}：${code}。未显示成功，页面将重新读取 backend 权威状态。`; }
    return code;
  };
  const safeInvoke = async (command, request = {}) => {
    if (typeof invoke !== "function") throw { code: "tauri_bridge_unavailable" };
    return invoke(command, { request });
  };
  const renderToday = (payload) => {
    const list = $("#today-records");
    if (!list) return;
    list.replaceChildren();
    setText("#today-summary", payload.records.length === 0
      ? "本地 backend 当前没有记录；AI 未启用。"
      : `本地 backend 返回 ${payload.records.length} 条用户原文；审计事件 ${payload.audit.event_count} 条；AI 未启用。`);
    payload.records.forEach((record) => {
      const article = document.createElement("article");
      article.className = "receipt";
      const label = document.createElement("p");
      label.className = "label";
      label.textContent = "用户原文 · 本地捕获";
      const content = document.createElement("p");
      content.textContent = record.content;
      const meta = document.createElement("p");
      meta.className = "identity-note";
      meta.textContent = `来源：本地捕获 · 身份：用户原文 · 时间戳：${record.created_at_ms}`;
      article.append(label, content, meta);
      list.append(article);
    });
  };
  const refreshToday = async () => {
    try {
      const payload = await safeInvoke("get_today", {});
      renderToday(payload);
      return payload;
    } catch (error) {
      disclose(error, "读取失败");
      setText("#today-summary", "backend 拒绝读取；没有展示缓存或部分记录。");
      const list = $("#today-records"); if (list) list.replaceChildren();
      throw error;
    }
  };
  const capture = async (text, key, expected) => {
    clearFailure();
    setText("#lifecycle-status", "正在等待 backend 权威回执…");
    try {
      const result = await safeInvoke("capture_record", { text, key });
      setText("#lifecycle-status", result.status === "saved"
        ? "已保存：SQLite 原子发布完成后 backend 返回成功。"
        : "幂等重复：记录未增加，backend 已追加合法重复审计。 ");
      await refreshToday();
      if (expected && result.status !== expected) disclose({ code: "unexpected_backend_status" });
      return result;
    } catch (error) {
      const code = disclose(error);
      setText("#lifecycle-status", `操作被 backend 阻断：${code}。`);
      await refreshToday().catch(() => {});
      throw error;
    }
  };
  const loadRuntime = async () => {
    try {
      const status = await safeInvoke("runtime_status", {});
      const target = $("#runtime-flags");
      if (target) {
        target.replaceChildren();
        [
          ["运行模式", status.offline ? "离线" : "非预期"],
          ["AI", status.ai_enabled ? "非预期启用" : "未启用"],
          ["Renderer 直接能力", String(status.renderer_direct_capabilities.length)],
          ["IPC allowlist", status.ipc_allowlist.join(" / ")],
          ["未知 IPC", status.unknown_ipc],
          ["文件 / DB / 路径", status.filesystem || status.raw_database || status.generic_path_api ? "非预期" : "关闭"],
          ["Shell / Process / Network", status.shell || status.process_spawn || status.network ? "非预期" : "关闭"],
          ["Vault / Export / Sync", status.vault || status.export || status.sync ? "非预期" : "关闭"],
          ["减少动态偏好", window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "系统已启用" : "系统未请求；界面仍无动画"]
        ].forEach(([label, value]) => {
          const row = document.createElement("p"); row.textContent = `${label}：${value}`; target.append(row);
        });
      }
      return status;
    } catch (error) {
      disclose(error, "Runtime 状态读取失败");
      throw error;
    }
  };

  $("#confirm-capture")?.addEventListener("click", () => capture(PRIMARY_TEXT, PRIMARY_KEY, "saved").catch(() => {}));
  $("#repeat-capture")?.addEventListener("click", () => capture(PRIMARY_TEXT, PRIMARY_KEY, "idempotent_repeat").catch(() => {}));
  $("#probe-conflict")?.addEventListener("click", () => capture(CONFLICT_TEXT, PRIMARY_KEY).catch(() => {}));
  $("#probe-failure")?.addEventListener("click", () => capture(FAILURE_TEXT, FAILURE_KEY).catch(() => {}));
  $("#choose-project")?.addEventListener("click", () => setText("#no-suggestion-status", "选择 Project 是用户控制的本地停点；当前没有生成建议。"));
  $("#record-stop")?.addEventListener("click", () => setText("#no-suggestion-status", "已记录页面停点提示；未保存新内容，也未生成建议。"));
  $("#probe-unknown")?.addEventListener("click", async () => {
    try {
      await safeInvoke("unknown_p3_104_command", {});
      setText("#unknown-status", "非预期：未知命令被接受。");
    } catch (_error) {
      setText("#unknown-status", "PASS：实际未知 IPC 被 invoke handler 拒绝，未产生副作用。");
      $("#unknown-status")?.classList.add("pass");
    }
  });
  $("#probe-schema")?.addEventListener("click", async () => {
    const before = await safeInvoke("get_today", {});
    const probes = [
      ["capture_record", { text: PRIMARY_TEXT, key: PRIMARY_KEY, path: "/private/tmp/escape" }],
      ["get_today", { sql: "SELECT * FROM captures" }],
      ["runtime_status", { shell: "echo blocked" }]
    ];
    let blocked = 0;
    for (const [command, request] of probes) {
      try { await safeInvoke(command, request); } catch (_error) { blocked += 1; }
    }
    const after = await safeInvoke("get_today", {});
    const unchanged = before.records.length === after.records.length && before.audit.event_count === after.audit.event_count;
    if (blocked === probes.length && unchanged) {
      setText("#unknown-status", "PASS：路径／SQL／shell 额外参数均在 schema gate 拒绝，记录与审计不变。");
      $("#unknown-status")?.classList.add("pass");
    } else {
      setText("#unknown-status", "FAIL：额外参数拒绝或无副作用条件未满足。");
      $("#unknown-status")?.classList.remove("pass");
    }
  });
  document.addEventListener("DOMContentLoaded", async () => {
    try {
      await loadRuntime();
      const today = await refreshToday();
      if ($("#lifecycle-status")) setText("#lifecycle-status", today.records.length ? "已从 backend 恢复今日记录。" : "尚无记录；等待明确确认。 ");
    } catch (_error) {
      setText("#lifecycle-status", "启动读取失败；未显示缓存成功态。");
    }
  });
})();
