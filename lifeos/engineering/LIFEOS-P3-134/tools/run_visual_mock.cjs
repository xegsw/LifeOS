"use strict";

const fs = require("fs/promises");
const path = require("path");
const { pathToFileURL } = require("url");
const { chromium } = require("playwright");

const root = "/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-134";
const candidate = path.join(root, "candidate", "ui", "index.html");
const reference = "/Users/xxe/Documents/No.2/lifeos/prototypes/LIFEOS-P3-116/index.html";
const out = path.join(root, "evidence", "visual");
const fixedText = "整理 LifeOS Context Recovery 合成验收记录。";
const contextId = "ctx:project:local-work-self-use";

async function main() {
  await fs.mkdir(out, { recursive: true });
  const browser = await chromium.launch({
    executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    headless: true,
    args: ["--disable-background-networking", "--disable-component-update", "--disable-sync", "--no-first-run"]
  });
  const results = { runner: "P3-134 task-local offline visual mock", network: false, viewports: {}, workflow: {}, reference: null, passed: false };
  try {
    for (const viewport of [{ width: 1280, height: 1024 }, { width: 1160, height: 768 }, { width: 700, height: 760 }]) {
      const context = await browser.newContext({ viewport, deviceScaleFactor: 1, reducedMotion: "reduce" });
      const page = await context.newPage();
      await installRuntime(page);
      await page.goto(pathToFileURL(candidate).href, { waitUntil: "load" });
      await page.waitForSelector(".icon-rail");
      const name = `${viewport.width}x${viewport.height}`;
      await page.screenshot({ path: path.join(out, `candidate-${name}-empty.png`), fullPage: true });
      results.viewports[name] = await signature(page);
      await context.close();
    }

    const visualContext = await browser.newContext({ viewport: { width: 700, height: 760 }, deviceScaleFactor: 1, reducedMotion: "reduce" });
    const visual = await visualContext.newPage();
    await installRuntime(visual);
    await visual.goto(pathToFileURL(candidate).href, { waitUntil: "load" });
    await visual.waitForSelector(".icon-rail");
    results.workflow.empty = await signature(visual);
    await visual.locator("button[data-action='capture']").first().click();
    await visual.waitForTimeout(300);
    const postOpen = await visual.evaluate(() => [...document.querySelectorAll("[data-action]")].map((node) => node.getAttribute("data-action")));
    await fs.writeFile(path.join(out, "post-open-debug.json"), JSON.stringify(postOpen, null, 2) + "\n");
    if (!postOpen.includes("runtime:capture")) throw new Error(`capture modal did not bind: ${JSON.stringify(postOpen)}`);
    await visual.locator("button[data-action='runtime:capture']").click();
    await visual.waitForTimeout(300);
    const postCapture = await visual.evaluate(() => ({
      actions: [...document.querySelectorAll("[data-action]")].map((node) => node.getAttribute("data-action")),
      runtime: document.documentElement.dataset.runtime || null,
      tauri: Boolean(window.__TAURI__?.core?.invoke)
    }));
    await fs.writeFile(path.join(out, "post-capture-debug.json"), JSON.stringify(postCapture, null, 2) + "\n");
    if (!postCapture.actions.includes("runtime:confirm")) throw new Error(`capture did not reach confirm state: ${JSON.stringify(postCapture)}`);
    results.workflow.insufficient = await signature(visual);
    await visual.evaluate(() => document.querySelector("button[data-action='runtime:confirm']")?.click());
    await visual.waitForSelector(".ai-panel.open");
    results.workflow.candidate = await signature(visual);
    await visual.screenshot({ path: path.join(out, "candidate-700-candidate.png"), fullPage: true });
    await visual.evaluate(() => document.querySelector("button[data-action='runtime:accept']")?.click());
    await visual.waitForSelector("button[data-action='runtime:complete']");
    results.workflow.normal = await signature(visual);
    await visual.screenshot({ path: path.join(out, "candidate-700-normal.png"), fullPage: true });
    await visual.locator("button[data-action='nav:me']").click();
    await visual.waitForSelector("#main-content");
    results.workflow.me = await signature(visual);
    await visual.locator("button[data-action='nav:contexts']").first().click();
    await visual.locator("button[data-action='context:launch']").first().click();
    results.workflow.contextDetail = await signature(visual);
    await visual.locator("button[data-action='nav:memory']").first().click();
    await visual.locator("button[data-action='memory:m1']").first().click();
    results.workflow.memoryDetail = await signature(visual);
    await visual.locator("button[data-action='ai']").first().click();
    await visual.waitForSelector("button[data-action='workspace']");
    await visual.locator("button[data-action='workspace']").first().click();
    results.workflow.workspace = await signature(visual);
    await visual.screenshot({ path: path.join(out, "candidate-700-workspace.png"), fullPage: true });
    results.workflow.calls = await visual.evaluate(() => window.__mockCalls || []);
    results.workflow.expectedCommands = ["runtime_status", "get_today", "get_context_recovery", "get_context_next_action", "assemble_global_ai_context", "get_evidence_backed_understanding", "capture_record", "confirm_capture_context", "decide_context_next_action"];
    results.workflow.commandSubsetPass = results.workflow.expectedCommands.every((name) => results.workflow.calls.includes(name));
    await visualContext.close();

    const refContext = await browser.newContext({ viewport: { width: 1280, height: 1024 }, deviceScaleFactor: 1, reducedMotion: "reduce" });
    const ref = await refContext.newPage();
    await ref.goto(pathToFileURL(reference).href, { waitUntil: "load" });
    await ref.waitForSelector(".icon-rail");
    await ref.screenshot({ path: path.join(out, "reference-1280.png"), fullPage: true });
    results.reference = await signature(ref);
    await refContext.close();

    results.passed = Object.values(results.viewports).every((entry) => entry.rail && entry.globalAi && entry.landmarks.main) && results.workflow.commandSubsetPass && results.workflow.candidate.aiOpen && results.workflow.normal.focus && results.workflow.normal.noticedSafe && results.workflow.workspace.workspace;
  } finally {
    await browser.close();
  }
  await fs.writeFile(path.join(out, "visual-mock-results.json"), JSON.stringify(results, null, 2) + "\n");
  if (!results.passed) process.exitCode = 1;
}

async function installRuntime(page) {
  await page.addInitScript(({ fixedText, contextId }) => {
    const calls = [];
    let record = null;
    let linked = false;
    let action = null;
    const candidate = { candidate_id: "candidate:p3-131:fixed", text: fixedText, identity: "candidate_action", derivation_id: "derivation:synthetic:fixed", processor: "offline_synthetic_model:p3-132-v1", processor_version: "p3-132-v1", basis_refs: ["capture:p3-131:fixed"], evidence_state: "sufficient", why: "固定合成 Evidence。" };
    const today = () => ({ status: record ? "ready" : "empty", records: record ? [record] : [], source: "local_capture", ai_status: "offline_synthetic_only", audit: { event_count: record ? (linked ? 3 : 1) : 0, capture_saved: record ? 1 : 0, capture_repeat: 0, context_feedback: linked ? 1 : 0, candidate_feedback: action ? 1 : 0, action_created: action ? 1 : 0, result_recorded: 0 }, context_recovery: recovery(), confirmed_actions: action ? [action] : [], todays_focus: action ? action.action_id : null, lifeos_noticed: null, memory_provenance: { derivation_refs: [], candidate_refs: [], feedback_refs: [], action_refs: action ? [action.action_id] : [], result_refs: [], original_copy_created: false } });
    const recovery = () => ({ context_id: contextId, project_id: "local-work-self-use", person_id: "person:local-owner", project_title: "LifeOS 产品开发", state: linked ? "active" : "watching", reliable_suggestion: linked, evidence_gap: linked ? null : "尚未确认 Context。", source_ref: "SRC-SYN-WORK-001", artifact_ref: "ART-SYN-CONTEXT-RECOVERY-001@v1", typed_link_ref: linked ? "link:confirmed" : null, feedback_ref: null, audit_ref: linked ? "audit:context" : null, memory_copy_created: false });
    window.__mockCalls = calls;
    window.__TAURI__ = { core: { invoke: async (name, { request }) => {
      calls.push(name);
      if (name === "runtime_status") return { status: "ready", offline: true, ai_enabled: true, ipc_allowlist: ["capture_record", "get_today", "runtime_status", "confirm_capture_context", "get_context_recovery", "get_context_next_action", "decide_context_next_action", "record_action_result", "assemble_global_ai_context", "get_evidence_backed_understanding", "decide_understanding_feedback"], filesystem: false, raw_database: false, generic_path_api: false, shell: false, process_spawn: false, network: false, vault: false, export: false, sync: false, model_port: "offline_synthetic_only", model_adapter: "offline_synthetic_model:p3-132-v1" };
      if (name === "get_today") return today();
      if (name === "get_context_recovery") return recovery();
      if (name === "get_context_next_action") return { status: linked && !action ? "ready" : "insufficient", context_id: contextId, candidates: linked && !action ? [candidate] : [], disclosure: null, evidence_gap: linked ? null : "尚未确认 Context。" };
      if (name === "assemble_global_ai_context") return { context_id: contextId, page: request.page, selection_ref: request.selection_ref || null, included: [{ kind: "person", reference: "person:local-owner" }, { kind: "page", reference: request.page }, { kind: "selection", reference: request.selection_ref || "capture:p3-131:fixed" }], removed_context_kinds: request.removed_context_kinds || [], request_local: true };
      if (name === "get_evidence_backed_understanding") return { understanding_id: "understanding:synthetic:fixed", observation: "固定合成 Observation。", suggestion: "固定合成 Suggestion。", identity: "ai_observation_and_suggestion", processor: "offline_synthetic_model:p3-132-v1", processor_version: "p3-132-v1", basis_refs: [], why: "无可靠 basis 不显示 noticed。", evidence_state: "sufficient", synthetic_adapter: true, disclosure: null };
      if (name === "capture_record") { if (request.text !== fixedText) throw { code: "synthetic_input_rejected", message: "未写入" }; record = { id: "capture:p3-131:fixed", content: fixedText, created_at_ms: 1, source: "local_capture", source_id: "SRC-SYN-WORK-001", artifact_version: "ART-SYN-CONTEXT-RECOVERY-001@v1", identity: "user_original" }; return { status: "saved", record, record_count: 1, audit_event_count: 1, context_id: contextId, link_status: "candidate" }; }
      if (name === "confirm_capture_context") { linked = request.decision === "confirm"; return { status: "saved", capture_id: record.id, context_id: contextId, decision: request.decision, feedback_count: 1, audit_event_count: 2, recovery: recovery() }; }
      if (name === "decide_context_next_action") { if (request.decision === "accept" || request.decision === "edit_accept") action = { action_id: "action:p3-131:fixed", text: fixedText, state: "open", confirmation_kind: request.decision, candidate_ref: candidate.candidate_id, confirmed_at: 1 }; return { status: "saved", candidate_id: candidate.candidate_id, decision: request.decision, action, feedback_ref: "feedback:fixed", audit_event_count: 3 }; }
      if (name === "record_action_result") { action = null; return { status: "saved", action_id: request.action_id, result: "completed", result_ref: "result:fixed", audit_event_count: 4 }; }
      if (name === "decide_understanding_feedback") throw { code: "understanding_feedback_not_implemented", message: "未写入" };
      throw { code: "unknown_ipc_rejected", message: "未写入" };
    } } };
  }, { fixedText, contextId });
}

async function signature(page) {
  return page.evaluate(() => {
    const rect = (selector) => { const node = document.querySelector(selector); if (!node) return null; const box = node.getBoundingClientRect(); return { x: Math.round(box.x), y: Math.round(box.y), width: Math.round(box.width), height: Math.round(box.height) }; };
    const root = getComputedStyle(document.documentElement);
    return {
      rail: Boolean(document.querySelector(".icon-rail")),
      globalAi: Boolean(document.querySelector(".composer")),
      aiOpen: Boolean(document.querySelector(".ai-panel.open")),
      focus: Boolean(document.querySelector("[data-action='runtime:complete']")),
      noticedSafe: !document.querySelector(".noticed-card") || document.querySelector(".noticed-card")?.dataset.evidence === "no-reliable-basis" || !document.querySelector(".noticed-card .actions:not([hidden])"),
      workspace: Boolean(document.querySelector(".workspace-reference")),
      landmarks: { nav: document.querySelectorAll("nav").length, main: document.querySelectorAll("main").length, dialog: document.querySelectorAll("[role='dialog']").length },
      classes: [...new Set([...document.querySelectorAll("[class]")].flatMap((node) => [...node.classList]))].sort(),
      tokens: { ink: root.getPropertyValue("--ink").trim(), blue: root.getPropertyValue("--blue").trim(), line: root.getPropertyValue("--line").trim() },
      geometry: { rail: rect(".icon-rail"), main: rect("#main-content"), composer: rect(".composer"), panel: rect(".ai-panel") }
    };
  });
}

main().catch((error) => { console.error(error.stack || error); process.exit(1); });
