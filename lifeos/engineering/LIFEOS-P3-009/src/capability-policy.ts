export const CAPABILITIES = Object.freeze({
  real_vault: false,
  tauri_ipc: false,
  filesystem_export: false,
  cloud_or_third_party_model: false,
  vector_index: false,
  sync_or_multi_device: false,
  l3_actions: false,
  external_users: false,
});

export type Capability = keyof typeof CAPABILITIES;

export class DisabledCapability extends Error {}

export function requireCapability(capability: Capability): never {
  throw new DisabledCapability(`${capability} is disabled by P3-009 policy`);
}
