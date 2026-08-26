(() => {
  "use strict";

  // P3-117 task-local, display-only probe. It makes no requests, persistence,
  // storage, or product-state changes. Alt+Shift+P toggles this overlay so the
  // operator can capture a proof image and a clean image of one unchanged state.
  const PROBE_VERSION = "P117-PROBE-V1";
  let lastAction = "initial";
  let sequence = 0;
  let visible = true;
  let root;

  function markerColor(value) {
    let hash = 2166136261;
    for (let index = 0; index < value.length; index += 1) {
      hash ^= value.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    const channel = (shift) => 56 + ((hash >>> shift) & 0x8f);
    const hex = (channel) => channel.toString(16).padStart(2, "0");
    return "#" + hex(channel(0)) + hex(channel(8)) + hex(channel(16));
  }

  function pageLabel() {
    const current = document.querySelector(".rail-button[aria-current='page']");
    return current ? current.getAttribute("aria-label") : "Today";
  }

  function stateLabel() {
    const today = document.querySelector(".today-mode-switch [aria-pressed='true']");
    const contextTab = document.querySelector(".tabs [aria-selected='true']");
    const modal = document.querySelector(".modal-backdrop.open .modal h2");
    const ai = document.querySelector(".ai-panel.open") ? "open" : "closed";
    const health = document.querySelector(".context-diff") ? "health-removed" : "health-included";
    const motion = document.body.classList.contains("reduced-motion") ? "reduced" : "standard";
    return [
      "page=" + pageLabel(),
      "today=" + (today ? today.textContent.trim() : "-"),
      "context=" + (contextTab ? contextTab.textContent.trim() : "-"),
      "modal=" + (modal ? modal.textContent.trim() : "-"),
      "ai=" + ai,
      "health=" + health,
      "motion=" + motion,
    ].join(";");
  }

  function signature() {
    return lastAction + "|" + stateLabel();
  }

  function render() {
    if (!root) return;
    const current = signature();
    root.hidden = !visible;
    root.dataset.signature = current;
    root.dataset.marker = markerColor(current);
    root.querySelector("[data-probe-marker]").style.background = markerColor(current);
    root.querySelector("[data-probe-capture]").textContent = "capture " + String(sequence).padStart(3, "0");
    root.querySelector("[data-probe-action]").textContent = "action " + lastAction;
    root.querySelector("[data-probe-state]").textContent = stateLabel();
    root.querySelector("[data-probe-viewport]").textContent =
      location.protocol + " | " + window.innerWidth + "x" + window.innerHeight + " | dpr " + window.devicePixelRatio;
  }

  function record(action) {
    lastAction = action;
    sequence += 1;
    requestAnimationFrame(() => requestAnimationFrame(render));
  }

  function attach() {
    root = document.createElement("aside");
    root.id = "p117-evidence-probe";
    root.setAttribute("aria-label", "P3-117 evidence probe");
    root.setAttribute("aria-live", "off");
    root.style.cssText = [
      "position:fixed",
      "right:14px",
      "bottom:14px",
      "z-index:2147483647",
      "display:grid",
      "grid-template-columns:26px 1fr",
      "gap:8px 10px",
      "width:340px",
      "padding:10px",
      "border:2px solid #111827",
      "border-radius:10px",
      "background:#ffffff",
      "box-shadow:0 8px 24px rgba(15,23,42,.26)",
      "color:#111827",
      "font:600 11px/1.35 -apple-system,BlinkMacSystemFont,sans-serif",
      "letter-spacing:.01em",
    ].join(";");
    root.innerHTML =
      '<span data-probe-marker style="grid-row:1 / span 4;width:26px;height:26px;border-radius:4px;box-shadow:inset 0 0 0 2px #fff"></span>' +
      '<span style="font-weight:800">P3-117 Evidence Probe ' + PROBE_VERSION + '</span>' +
      '<span data-probe-capture></span>' +
      '<span data-probe-action></span>' +
      '<span data-probe-state></span>' +
      '<span data-probe-viewport style="grid-column:1 / -1;color:#334155"></span>';
    document.body.appendChild(root);
    render();
  }

  document.addEventListener("click", (event) => {
    const target = event.target.closest("[data-action]");
    if (target && !target.closest("#p117-evidence-probe")) record(target.dataset.action);
  }, true);

  document.addEventListener("keydown", (event) => {
    if (event.altKey && event.shiftKey && event.key.toLowerCase() === "p") {
      event.preventDefault();
      visible = !visible;
      render();
      return;
    }
    if (event.key === "Tab") record(event.shiftKey ? "key:Shift+Tab" : "key:Tab");
    if (event.key === "Escape") record("key:Escape");
    if (event.key === "Enter" && !event.target.closest("[data-action]")) record("key:Enter");
  }, true);

  window.addEventListener("resize", () => requestAnimationFrame(render));
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", attach, { once: true });
  else attach();
})();
