import { createHash } from "node:crypto";
import { mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import { dirname, join, relative, resolve } from "node:path";

const workspace = resolve(process.cwd());
const reviewBase = "lifeos/reviews/LIFEOS-P3-144/independent-re-review-1";
const reviewAbsolute = join(workspace, reviewBase);
const output = join(reviewAbsolute, "FINAL_MANIFEST.json");

const sha256 = async (path) => createHash("sha256").update(await readFile(path)).digest("hex");
async function walk(directory) {
  const paths = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const absolute = join(directory, entry.name);
    if (entry.isDirectory()) paths.push(...await walk(absolute));
    else if (entry.isFile()) paths.push(relative(workspace, absolute));
    else throw new Error(`unsupported review artifact: ${relative(workspace, absolute)}`);
  }
  return paths;
}
async function entries(paths) {
  return Promise.all(paths.sort().map(async (path) => ({ path, sha256: await sha256(join(workspace, path)) })));
}

const excluded = [
  `${reviewBase}/FINAL_MANIFEST.json`,
  `${reviewBase}/evidence/review_manifest_verification.json`,
  `${reviewBase}/excluded/**`,
];
const manifest = {
  schema: "lifeos.p3-144.independent-re-review-1.final-manifest.v1",
  task: "LIFEOS-P3-144",
  phase: "B",
  candidate_commit: "4115f2958d8fa08fa30fccc90217bdc404769363",
  self_exclusion: true,
  excluded_from_manifest: excluded,
  categories: {
    precontact: await entries(await walk(join(reviewAbsolute, "precontact"))),
    review_tools: await entries(await walk(join(reviewAbsolute, "review_tools"))),
    evidence: await entries(await walk(join(reviewAbsolute, "evidence"))),
    review_report: await entries([`${reviewBase}/independent_review.md`]),
  },
};
await mkdir(dirname(output), { recursive: true });
await writeFile(output, `${JSON.stringify(manifest, null, 2)}\n`, { mode: 0o600 });
console.log(JSON.stringify({ result: "PASS", output: relative(workspace, output) }));
