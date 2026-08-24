# LIFEOS-P3-085 PM Evidence Manifest

## 范围与可重放性

- PM 在隔离临时副本 `/private/tmp/lifeos-p3-085-pm.vn0H9U/app` 使用 Google Chrome 直接打开 `file:` 页面；未启动 HTTP 服务、未使用网络、CDP 或浏览器策略绕过。
- 验证只使用固定非敏感文本；不写入工程资产、历史 Evidence 或任何真实数据。
- 执行侧的 `browser_blocker.md` 保持原样。本 PM Evidence 补足可用合规图形浏览器中的动态复验，不覆盖执行侧自检的 `Not Pass` 事实。

## 文件与 SHA-256

| 文件 | SHA-256 |
|---|---|
| `verification.json` | `62ad09b122dc82e85ca3eba6fd005d93e334ee3b7776680465c108514040a30b` |
| `lifeos/engineering/LIFEOS-P3-085/evidence/static_check_results.json` | `88e91cf533adef872a53f213f70a9ac676d3f0d5b3f22b7ba8bdf0984051d561` |
| `lifeos/engineering/LIFEOS-P3-085/evidence/MANIFEST.md` | `8443cfa83b0cbd30db6c73e55d0ab9e16fb43bc7dee0f3bbfc70c26e60243ae5` |
| `lifeos/engineering/LIFEOS-P3-082/index.html` | `eb4217b35e42ec0783e3bdf9d614bd79094c7925309b16c746cbc7a6b34d4722` |
| `lifeos/engineering/LIFEOS-P3-082/app.js` | `784523e44f1eb9f8f8363aa1af4c424ce6e15bb730cd597763b3dfeab28efb5d` |
| `lifeos/engineering/LIFEOS-P3-082/styles.css` | `7138a99ee427707846c7c08c59829918c6ee2b22c28839d51e8a4d18fb27d3a2` |

## 结论边界

此 Manifest 只支持 P3-085 的 PM 验收；不构成独立复评、资产冻结、工程基线恢复、真实能力启用、风险关闭或 Stage 4 准入。
