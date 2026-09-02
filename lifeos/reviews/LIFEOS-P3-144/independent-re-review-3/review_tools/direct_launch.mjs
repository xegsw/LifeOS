import { mkdir, open, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { spawn } from "node:child_process";

const root = process.cwd();
const review = "lifeos/reviews/LIFEOS-P3-144/independent-re-review-3";
const viewport = process.argv.find((arg) => arg.startsWith("--viewport="))?.slice(11);
const label = process.argv.find((arg) => arg.startsWith("--label="))?.slice(8) ?? viewport;
if (!["desktop", "compact", "narrow"].includes(viewport)) {
  throw new Error("--viewport must be desktop, compact, or narrow");
}
if (!/^[a-z0-9_-]+$/.test(label)) throw new Error("--label must contain only lowercase letters, digits, _ or -");
const binary = resolve(root, review, "work/cargo-target/debug/lifeos-p3-144");
const work = resolve(root, review, "work");
await mkdir(work, { recursive: true, mode: 0o700 });
const logPath = resolve(work, `app_${label}.log`);
const log = await open(logPath, "w", 0o600);
const child = spawn(binary, [], {
  detached: true,
  stdio: ["ignore", log.fd, log.fd],
  env: {
    ...process.env,
    LIFEOS_P3_144_VIEWPORT: viewport,
  },
});
log.close();
child.unref();
const launch = {
  schema: "lifeos.p3-144.independent-review.direct-launch.v1",
  viewport,
  binary,
  pid: child.pid,
  root_profile: "independent-review",
  compiled_root: "/private/tmp/lifeos-p3-144-independent-review-v1",
  exact_title: "LifeOS · Work 与健康状态",
  stdout_stderr_log: `work/app_${label}.log`,
  synthetic_only: true,
  network_access: false,
};
await writeFile(resolve(work, `launch_${label}.json`), `${JSON.stringify(launch, null, 2)}\n`, { mode: 0o600 });
console.log(JSON.stringify(launch));
