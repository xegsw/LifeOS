import { lstat, readFile, rm } from "node:fs/promises";
import { resolve } from "node:path";

const root = "/private/tmp/lifeos-p3-143-real-ai-secure-activation-v1";
const marker = `${root}/.lifeos-p3-143-owner.json`;
const candidate = resolve(import.meta.dirname, "..");
const target = resolve(candidate, "target");
if (target !== `${candidate}/target`) throw new Error("candidate_target_literal_rejected");
const markerStats = await lstat(marker);
if (!markerStats.isFile() || markerStats.isSymbolicLink() || Number(markerStats.mode & 0o777) !== 0o600) throw new Error("marker_type_rejected");
const observed = JSON.parse(await readFile(marker, "utf8"));
if (observed.schema !== "lifeos.p3-143.real-ai-secure-activation-root.v1" || observed.task !== "LIFEOS-P3-143" || observed.owner !== "lifeos-p3-143-real-ai-secure-activation-v1") throw new Error("marker_payload_rejected");
const stats = await lstat(target);
if (!stats.isDirectory() || stats.isSymbolicLink()) throw new Error("candidate_target_type_rejected");
await rm(target, { recursive: true, force: false, maxRetries: 0 });
console.log(JSON.stringify({ result: "PASS", removed: "candidate/target", marker_bound: true }));
