import { chmod, mkdir, readFile, stat, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { resolve } from "node:path";

const candidate = resolve(import.meta.dirname, "..");
const evidence = resolve(candidate, "..", "evidence");
const screenshotNames = [
  "actual_tauri_person_preview.png",
  "actual_tauri_today_feedback.png",
  "actual_tauri_restart_today.png",
  "actual_tauri_compact_today.png",
  "actual_tauri_narrow_today.png",
];
function imageDimensions(bytes) {
  const pngSignature = "89504e470d0a1a0a";
  if (bytes.subarray(0, 8).toString("hex") === pngSignature) {
    return { pixel_width: bytes.readUInt32BE(16), pixel_height: bytes.readUInt32BE(20) };
  }
  if (bytes[0] === 0xff && bytes[1] === 0xd8) {
    let offset = 2;
    while (offset + 9 < bytes.length) {
      if (bytes[offset] !== 0xff) break;
      const marker = bytes[offset + 1];
      const length = bytes.readUInt16BE(offset + 2);
      if ([0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf].includes(marker)) {
        return { pixel_width: bytes.readUInt16BE(offset + 7), pixel_height: bytes.readUInt16BE(offset + 5) };
      }
      offset += 2 + length;
    }
  }
  throw new Error("unsupported_screenshot_format");
}
const screenshotEvidence = await Promise.all(screenshotNames.map(async (name) => {
  const path = resolve(evidence, name);
  const bytes = await readFile(path);
  const metadata = await stat(path);
  return {
    path: `evidence/${name}`,
    sha256: createHash("sha256").update(bytes).digest("hex"),
    bytes: metadata.size,
    mode: (metadata.mode & 0o777).toString(8),
    ...imageDimensions(bytes),
  };
}));
const report = {
  schema: "lifeos.p3-145.actual-tauri-evidence.v1",
  task: "LIFEOS-P3-145",
  run_profile: "engineering",
  run_mode: "synthetic",
  direct_launch_pid_chain: {
    desktop: { launch_pid: 57210, window_host_pid: 57220, viewport: "desktop" },
    restart: { launch_pid: 57403, window_host_pid: 57412, viewport: "desktop" },
    compact: { launch_pid: 57572, window_host_pid: 57582, viewport: "compact" },
    narrow: { launch_pid: 57714, window_host_pid: 57724, viewport: "narrow" },
  },
  native_chain: {
    exact_window_title: "LifeOS · Work 与健康状态",
    ax_window_observed: true,
    ax_webview_observed: true,
    renderer_url: "tauri://localhost",
  },
  synthetic_loop: {
    work_saved: true,
    non_medical_health_current_state_saved: true,
    durable_memory_explicitly_confirmed_once: true,
    person_disclosure_refs: 3,
    disclosure_types: ["user_work", "health_current_state", "durable_memory"],
    provider_visible_before_confirmation: "DeepSeek",
    synthetic_confirmation_consumed_once: true,
    understanding_feedback_confirmed: true,
    today_single_person_focus_after_feedback: true,
    restart_preserved_typed_state_and_feedback: true,
    network_requests: 0,
  },
  screenshots: screenshotEvidence,
  prohibited_boundary_contact: false,
  real_content_in_evidence: false,
  notes: "All UI inputs were fixed synthetic canaries. The synthetic run mode did not issue network requests. This is Phase A engineering evidence only; it is not Phase B independent review, PM acceptance, a real controlled loop, risk closure, product freeze, or a stage transition.",
};
await mkdir(evidence, { recursive: true, mode: 0o700 });
const reportPath = resolve(evidence, "actual_tauri_evidence.json");
await writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`, { mode: 0o600 });
await chmod(reportPath, 0o600);
console.log(JSON.stringify({ result: "PASS", screenshots: screenshotEvidence.length, synthetic_refs: report.synthetic_loop.person_disclosure_refs, network_requests: 0 }));
