import { spawn } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const [appPath, viewport, outputPath] = process.argv.slice(2);
if (!appPath || !viewport || !outputPath) throw new Error("usage: node direct_launch.mjs APP VIEWPORT OUTPUT");
const candidate = resolve(process.cwd());
const child = spawn(resolve(appPath), [], {
  cwd: candidate,
  detached: true,
  stdio: "ignore",
  env: { PATH: "/usr/bin:/bin", LIFEOS_P3_144_VIEWPORT: viewport },
});
child.unref();
const receipt = {
  schema: "lifeos.p3-144.independent-review.direct-launch.v1",
  pid: child.pid,
  viewport,
  executable: resolve(appPath),
  launched_at: new Date().toISOString(),
  root_profile: "independent-review",
  run_mode: "synthetic",
  network_permitted: false,
};
const destination = resolve(outputPath);
await mkdir(dirname(destination), { recursive: true });
await writeFile(destination, `${JSON.stringify(receipt, null, 2)}\n`, { mode: 0o600 });
console.log(JSON.stringify(receipt));
