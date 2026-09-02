import { lstat, rm } from "node:fs/promises";
import path from "node:path";

const review = "/private/tmp/lifeos-p3-144-closure4-review-worktree/lifeos/reviews/LIFEOS-P3-144/closure-4-independent-review";
const target = path.join(review, ".build-cache");
if (path.dirname(target) !== review || path.basename(target) !== ".build-cache") throw new Error("build_cache_literal_rejected");
await rm(target, { recursive: true, force: false, maxRetries: 0 });
try { await lstat(target); throw new Error("build_cache_cleanup_failed"); } catch (error) { if (error.code !== "ENOENT") throw error; }
console.log(JSON.stringify({ target, absence: true }));
