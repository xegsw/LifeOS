(() => {
  "use strict";

  const TASK = "LIFEOS-P3-122";
  const SYNTHETIC_ONE = "明天先把发布页的第一屏文字读一遍，再决定是否继续做视觉细节。";
  const KEY_ONE = "p3-122-synthetic-one";
  const app = document.getElementById("app");
  const invoke = window.__TAURI__?.core?.invoke;
  const runtime = {
    status: "initializing",
    today: null,
    receipt: "",
    error: null,
  };
  let scheduled = false;

  const command = async (name, request) => {
    if (typeof invoke !== "function") {
      throw { status: "blocked", code: "tauri_invoke_unavailable", message: "Tauri IPC 不可用；未显示成功。" };
    }
    return invoke(name, { request });
  };

  const currentPage = () => {
    if (document.querySelector(".ai-panel.open")) return "global-ai";
    if (document.querySelector(".workspace-page")) return "ai-workspace";
    const selected = document.querySelector('[aria-current="page"]');
    return selected?.getAttribute("aria-label")?.toLowerCase() || "today";
  };

  const geometry = () => {
    const pageRoot = document.querySelector("#main-content > :first-child, .workspace-page");
    const shell = document.querySelector(".app-shell");
    const layoutNode = (selector) => {
      const node = document.querySelector(selector);
      if (!node) return null;
      const style = getComputedStyle(node);
      const bounds = node.getBoundingClientRect();
      return {
        selector,
        bounds: {
          x: Number(bounds.x.toFixed(3)),
          y: Number(bounds.y.toFixed(3)),
          width: Number(bounds.width.toFixed(3)),
          height: Number(bounds.height.toFixed(3)),
        },
        display: style.display,
        position: style.position,
        gridTemplateColumns: style.gridTemplateColumns,
        overflowX: style.overflowX,
        overflowY: style.overflowY,
        zIndex: style.zIndex,
      };
    };
    const bodyStyle = getComputedStyle(document.body);
    const shellStyle = shell ? getComputedStyle(shell) : null;
    const pageStyle = pageRoot ? getComputedStyle(pageRoot) : null;
    const rect = pageRoot?.getBoundingClientRect();
    const visualSelector = {
      today: ".today-grid",
      me: ".me-current-card",
      contexts: ".context-row",
      memory: ".memory-reference-grid",
      "global-ai": ".ai-panel.open",
      "ai-workspace": ".workspace-reference-grid",
    }[currentPage()];
    const visualNode = visualSelector ? document.querySelector(visualSelector) : null;
    const visualStyle = visualNode ? getComputedStyle(visualNode) : null;
    const visualRect = visualNode?.getBoundingClientRect();
    return {
      task: TASK,
      source: "actual-tauri-webview-dom",
      page: currentPage(),
      viewport: {
        innerWidth: window.innerWidth,
        innerHeight: window.innerHeight,
        devicePixelRatio: window.devicePixelRatio,
        screenWidth: window.screen.width,
        screenHeight: window.screen.height,
        screenAvailWidth: window.screen.availWidth,
        screenAvailHeight: window.screen.availHeight,
      },
      dom: {
        title: document.title,
        pageRootClass: pageRoot?.className || null,
        pageRootRect: rect ? {
          x: Number(rect.x.toFixed(3)),
          y: Number(rect.y.toFixed(3)),
          width: Number(rect.width.toFixed(3)),
          height: Number(rect.height.toFixed(3)),
        } : null,
        navigationButtons: document.querySelectorAll(".rail-button").length,
        panels: document.querySelectorAll(".panel").length,
        headings: document.querySelectorAll("h1, h2, h3").length,
        documentClientWidth: document.documentElement.clientWidth,
        documentScrollWidth: document.documentElement.scrollWidth,
        horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
        workspaceGrid: layoutNode(".workspace-reference-grid"),
        workspaceCenter: layoutNode(".workspace-reference .workspace-center"),
        workspaceInspector: layoutNode(".workspace-reference .workspace-inspector"),
        visualKey: visualNode && visualStyle && visualRect ? {
          selector: visualSelector,
          bounds: {
            x: Number(visualRect.x.toFixed(3)),
            y: Number(visualRect.y.toFixed(3)),
            width: Number(visualRect.width.toFixed(3)),
            height: Number(visualRect.height.toFixed(3)),
          },
          display: visualStyle.display,
          gridTemplateColumns: visualStyle.gridTemplateColumns,
          gap: visualStyle.gap,
          padding: visualStyle.padding,
          borderRadius: visualStyle.borderRadius,
          backgroundColor: visualStyle.backgroundColor,
          color: visualStyle.color,
          fontSize: visualStyle.fontSize,
        } : null,
      },
      computed: {
        media1120: window.matchMedia("(max-width: 1120px)").matches,
        media820: window.matchMedia("(max-width: 820px)").matches,
        media520: window.matchMedia("(max-width: 520px)").matches,
        bodyFontFamily: bodyStyle.fontFamily,
        bodyFontSize: bodyStyle.fontSize,
        bodyColor: bodyStyle.color,
        bodyBackgroundColor: bodyStyle.backgroundColor,
        shellDisplay: shellStyle?.display || null,
        shellGridTemplateColumns: shellStyle?.gridTemplateColumns || null,
        pageDisplay: pageStyle?.display || null,
        pageColor: pageStyle?.color || null,
        pageBackgroundColor: pageStyle?.backgroundColor || null,
      },
      runtime: {
        status: runtime.status,
        recordCount: runtime.today?.records?.length ?? null,
        auditEventCount: runtime.today?.audit?.event_count ?? null,
        errorCode: runtime.error?.code || null,
      },
    };
  };

  const renderRuntimeSlots = () => {
    const statusText = runtime.error
      ? `固定合成 Runtime · Blocked (${runtime.error.code})`
      : runtime.status === "restricted_offline"
        ? "固定合成 Runtime · Offline · 3 IPC"
        : "固定合成 Runtime · 初始化中";
    document.querySelectorAll(".synthetic-mark").forEach((node) => {
      if (node.textContent !== statusText) node.textContent = statusText;
    });

    const receipt = document.querySelector(".state-receipt");
    if (receipt && runtime.receipt && receipt.textContent !== runtime.receipt) {
      receipt.textContent = runtime.receipt;
    }

    const recent = document.querySelector(".recent-list");
    if (recent && runtime.today) {
      const records = runtime.today.records || [];
      const html = records.length
        ? records.map((record) => `<li data-runtime-record="${record.id}"><span><i></i>${record.content}</span><b>›</b></li>`).join("")
        : '<li data-runtime-empty="true"><span><i></i>尚无 Runtime capture</span><b>›</b></li>';
      if (recent.innerHTML !== html) recent.innerHTML = html;
    }

    const attestation = geometry();
    const compactBounds = (bounds) => bounds ? { x: bounds.x, y: bounds.y, w: bounds.width, h: bounds.height } : null;
    const visual = attestation.dom.visualKey;
    const ariaAttestation = {
      t: attestation.task,
      p: attestation.page,
      vp: {
        w: attestation.viewport.innerWidth,
        h: attestation.viewport.innerHeight,
        d: attestation.viewport.devicePixelRatio,
        sw: attestation.viewport.screenWidth,
        sh: attestation.viewport.screenHeight,
        aw: attestation.viewport.screenAvailWidth,
        ah: attestation.viewport.screenAvailHeight,
      },
      m: [attestation.computed.media1120, attestation.computed.media820, attestation.computed.media520],
      doc: [attestation.dom.documentClientWidth, attestation.dom.documentScrollWidth, attestation.dom.horizontalOverflow],
      vis: visual ? {
        s: visual.selector,
        r: compactBounds(visual.bounds),
        d: visual.display,
        g: visual.gridTemplateColumns,
        gap: visual.gap,
        pad: visual.padding,
        br: visual.borderRadius,
        bg: visual.backgroundColor,
        c: visual.color,
        fs: visual.fontSize,
      } : null,
      ws: {
        g: attestation.dom.workspaceGrid?.gridTemplateColumns || null,
        gr: compactBounds(attestation.dom.workspaceGrid?.bounds),
        cr: compactBounds(attestation.dom.workspaceCenter?.bounds),
        ir: compactBounds(attestation.dom.workspaceInspector?.bounds),
      },
      rt: [attestation.runtime.status, attestation.runtime.recordCount, attestation.runtime.auditEventCount, attestation.runtime.errorCode],
    };
    app.setAttribute("aria-label", `P3_122_ATTESTATION ${JSON.stringify(ariaAttestation)}`);
    window.LIFEOS_P3_122_ATTESTATION = attestation;
  };

  const schedule = () => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => {
      scheduled = false;
      renderRuntimeSlots();
    });
  };

  const refreshToday = async () => {
    try {
      runtime.today = await command("get_today", {});
      runtime.error = null;
    } catch (error) {
      runtime.error = error;
      runtime.receipt = `Runtime 读取已阻断：${error.code || "unknown_error"}；未显示成功。`;
    }
    schedule();
    return runtime.today;
  };

  const initialize = async () => {
    try {
      const status = await command("runtime_status", {});
      runtime.status = status.status;
      runtime.error = null;
      await refreshToday();
    } catch (error) {
      runtime.status = "blocked";
      runtime.error = error;
      schedule();
    }
  };

  app.addEventListener("click", async (event) => {
    const target = event.target.closest('[data-action="capture-confirm"]');
    if (!target) return;
    runtime.receipt = "Runtime 正在保存固定合成原文…";
    schedule();
    try {
      const response = await command("capture_record", { text: SYNTHETIC_ONE, key: KEY_ONE });
      runtime.receipt = response.status === "idempotent_repeat"
        ? `Runtime 幂等重复：沿用 ${response.record.id}；未创建重复记录。`
        : `Runtime 已保存用户原文：${response.record.id}；关联建议仍由你确认。`;
      runtime.error = null;
      await refreshToday();
    } catch (error) {
      runtime.error = error;
      runtime.receipt = `Runtime 保存已阻断：${error.code || "unknown_error"}；未显示成功。`;
      schedule();
    }
  }, true);

  new MutationObserver(schedule).observe(app, { childList: true, subtree: true });
  window.addEventListener("resize", schedule);
  window.addEventListener("focus", refreshToday);
  initialize();
  schedule();
})();
