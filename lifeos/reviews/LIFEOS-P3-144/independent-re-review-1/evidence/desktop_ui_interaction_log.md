# Desktop App interaction log — review-owned synthetic inputs only

- Direct PID: `19293`; launch receipt: `direct_launch_desktop.json`.
- The actual Tauri UI stated that Work and Health entries are local-only and
  capped at 3 entries / 200 characters. Three synthetic Work entries and three
  synthetic non-medical Health entries were saved. The fourth entry for each
  domain was rejected with `每类最多保存 3 条；未写入。`.
- The Health entry screen stated it does not provide diagnosis, treatment,
  medication, or emergency judgement. No medical scenario or real health data
  was entered.
- A Work-only disclosure preview listed exactly the three synthetic Work
  entries, showed `仅发送到 DeepSeek · https://api.deepseek.com`, a local
  resolver explanation, and a separate confirmation button.
- Before a Provider config existed, confirmation was rejected with `请先保存主
  AI 服务配置。`. After a synthetic-only DeepSeek config, a synthetic credential,
  explicit synthetic model test, selection, and enablement, the UI stated
  `合成模型目录测试完成；未执行网络请求。` and later created an AI Understanding
  only after the separate confirmation action.
- The resulting Understanding exposed all five feedback actions: confirm,
  edit, reject, ignore, correct. `ignore` was selected and the UI reported that
  feedback was saved and the relevant Today projection recomputed.

This is a factual UI transcript summary. The raw visual/PID evidence is kept
separately; the inputs were self-authored, non-sensitive synthetic strings and
no Provider, network, or real credential was contacted.
