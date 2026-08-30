const fs = require("node:fs");

const path = require("node:path");
const adapter = fs.readFileSync(path.join(__dirname, "candidate/ui/runtime-adapter.js"), "utf8");
const runtime = fs.readFileSync(path.join(__dirname, "candidate/src/runtime.rs"), "utf8");

const expected = "p3-141-synthetic-capture-001";
if (!adapter.includes(`const SYN_KEY = "${expected}"`)) {
  throw new Error("UI adapter does not use the P3-141 synthetic capture key");
}
if (!runtime.includes(`const SYN_KEY: &str = "${expected}"`)) {
  throw new Error("Runtime does not use the P3-141 synthetic capture key");
}
if (adapter.includes("p3-130-capture-001")) {
  throw new Error("Legacy P3-130 capture key remains in the UI adapter");
}
console.log("ui_runtime_key_contract: PASS");
