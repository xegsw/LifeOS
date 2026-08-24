(() => {
  "use strict";
  const invoke = window.__TAURI__?.core?.invoke;
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
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
  const pendingKey = () => {
    const stored = window.sessionStorage.getItem("lifeos-p3-111-pending-key");
    if (stored) return stored;
    const random = window.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    const key = `p3-111-ui-${random}`;
    window.sessionStorage.setItem("lifeos-p3-111-pending-key", key);
    return key;
  };
  const renderToday = (payload) => {
    $$('[data-backend="record-count"]').forEach((node) => { node.textContent = String(payload.records.length); });
    $$('[data-backend="audit-count"]').forEach((node) => { node.textContent = String(payload.audit.event_count); });
    $$('[data-backend="save-fact"]').forEach((node) => {
      node.textContent = payload.records.length ? "已由本地 SQLite backend 耐久恢复 · AI 与外部能力关闭" : "尚未保存 · AI 与外部能力关闭";
    });
    $$('[data-backend="record-list"]').forEach((list) => {
      list.replaceChildren();
      if (!payload.records.length) {
        const empty = document.createElement("p");
        empty.textContent = "尚无本地记录；请手工输入一条简短、非敏感的原文。";
        list.append(empty);
        return;
      }
      payload.records.forEach((record) => {
        const item = document.createElement("article");
        item.className = "local-record";
        const label = document.createElement("strong");
        label.textContent = "你的记录 · 原文 · 本地捕获";
        const content = document.createElement("p");
        content.textContent = record.content;
        item.append(label, content);
        list.append(item);
      });
    });
    document.documentElement.dataset.backendState = payload.records.length ? "loaded" : "empty";
  };
  const refreshToday = async () => {
    try {
      const payload = await safeInvoke("get_today", {});
      renderToday(payload);
      return payload;
    } catch (error) {
      $$('[data-backend="record-list"]').forEach((node) => { node.textContent = "backend 拒绝读取；未展示缓存或部分记录。"; });
      showNotice(`读取被阻断：${errorCode(error)}。`, true);
      throw error;
    }
  };
  const capture = async () => {
    const input = $("#capture-text");
    const text = input?.value ?? "";
    if (!text.trim()) {
      showNotice("请先手工输入一条简短、非敏感的本地原文。", true);
      input?.focus();
      return;
    }
    showNotice("正在等待本地 backend 权威回执…");
    try {
      const result = await safeInvoke("capture_record", { text, key: pendingKey() });
      if (result.status !== "saved" && result.status !== "idempotent_repeat") throw { code: "unexpected_backend_status" };
      await refreshToday();
      if (result.status === "saved") {
        if (input) input.value = "";
        window.sessionStorage.removeItem("lifeos-p3-111-pending-key");
        showNotice("已保存：SQLite 原子发布完成；用户原文身份保持不变。");
      } else {
        showNotice("幂等重复：记录未增加；backend 已验证同一原文。 ");
      }
    } catch (error) {
      showNotice(`已阻断：${errorCode(error)}。未显示成功，backend 状态将重新读取。`, true);
      await refreshToday().catch(() => {});
    }
  };
  const loadRuntime = async () => {
    const status = await safeInvoke("runtime_status", {});
    const expected = status.offline && !status.ai_enabled && status.ipc_allowlist.join(",") === "capture_record,get_today,runtime_status";
    $$('[data-backend="runtime-state"]').forEach((node) => {
      node.textContent = expected ? "离线本地模式；AI、网络、导出、同步与外部来源关闭" : "运行时状态异常；请勿继续保存";
      node.classList.toggle("error-text", !expected);
    });
    if (!expected) throw { code: "runtime_contract_rejected" };
    return status;
  };

  $$('[data-action="capture"]').forEach((button) => button.addEventListener("click", () => { capture(); }));
  $("#capture-text")?.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) { event.preventDefault(); capture(); }
  });
  $$('[data-unimplemented]').forEach((button) => button.addEventListener("click", () => showNotice(`${button.dataset.unimplemented || "此功能"}未启用；没有调用 IPC，也没有更改本地记录。`)));
  document.addEventListener("DOMContentLoaded", async () => {
    try { await loadRuntime(); await refreshToday(); }
    catch (_error) { showNotice("启动读取失败；未显示缓存成功态。", true); }
  });
})();
