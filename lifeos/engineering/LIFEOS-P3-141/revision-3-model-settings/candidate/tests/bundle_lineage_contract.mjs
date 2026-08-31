import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const candidate = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const productContracts = [
  "ui/runtime-adapter.js",
  "ui/interaction_contract.md",
  "ui/ia_reconciliation.md",
  "ui/visual_contract.json",
  "ui/state_machine.json",
].map((relative) => ({ relative, text: readFileSync(resolve(candidate, relative), "utf8") }));

const combined = productContracts.map(({ text }) => text).join("\n");
for (const prohibited of [
  "本次会话 API Key",
  "仅保留在本次会话",
  "清除本次会话 API Key",
  "本次会话内存",
  "环境变量名引用",
  "环境变量凭据",
  "session-only API Key",
  "session credential",
]) {
  assert.ok(!combined.includes(prohibited), `forbidden credential product semantics remain: ${prohibited}`);
}

for (const required of [
  "API Key 已加密保存",
  "加密保存到受控本地 SQLite",
  "密钥材料与数据库分离",
  "可更新或删除",
  "跨重启保留",
  "save_ai_provider_credential",
  "store_or_update",
  "删除已保存 API Key",
]) {
  assert.ok(combined.includes(required), `persistent-credential contract is missing: ${required}`);
}

const adapter = productContracts.find(({ relative }) => relative === "ui/runtime-adapter.js").text;
for (const required of [
  'option("openai", "OpenAI")',
  'option("anthropic", "Anthropic")',
  'option("deepseek", "DeepSeek")',
  'option("kimi", "Kimi")',
  'option("cloud_custom_openai_compatible", "自定义 OpenAI-compatible")',
  'option("ollama", "Ollama")',
  'option("lm_studio", "LM Studio")',
  'option("local_custom_compatible", "自定义本地兼容服务")',
  "requirePersistedProviderMode",
]) {
  assert.ok(adapter.includes(required), `provider/mode invariant is missing: ${required}`);
}

console.log("bundle-lineage-contract: PASS");
