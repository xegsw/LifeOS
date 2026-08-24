# T-UX / T-EXPORT / H9

## 动态状态合同

覆盖 normal、empty、saving_failed、restricted、evidence_gap、confirmed、rejected、corrected、revoked、deleted。每态均提供状态播报、纯键盘路径、焦点返回、无需动画、候选身份及来源/缺口可见。此为无 UI 的语义走查，不宣称冻结或实现最终 UI。

## 导出 / 恢复候选

受控内存测试包保留身份、来源、精确版本、确认状态和排除项；完整、部分失败、控制快照冲突均测试。正式文件格式与路径能力未启用。

## 双 Project 闭包真实断言

- `zero_leak:artifact-b-decision`: actual=`False`, expected=`False`, PASS=`True`
- `zero_leak:artifact-b-unprocessed`: actual=`False`, expected=`False`, PASS=`True`
- `zero_leak:feedback:derivation:next:project-synth-aurora:2cc46dbb909c760f:1`: actual=`False`, expected=`False`, PASS=`True`
- `zero_leak:link-b`: actual=`False`, expected=`False`, PASS=`True`
- `zero_leak:link-cross`: actual=`False`, expected=`False`, PASS=`True`
- `zero_leak:project-synth-aurora`: actual=`False`, expected=`False`, PASS=`True`
- `a_feedback_included`: actual=`True`, expected=`True`, PASS=`True`
- `a_link_included`: actual=`['link-a']`, expected=`['link-a']`, PASS=`True`
- `artifact_versions_closed`: actual=`['artifact-change', 'artifact-decision', 'artifact-stop', 'artifact-unprocessed']`, expected=`['artifact-change', 'artifact-decision', 'artifact-stop', 'artifact-unprocessed']`, PASS=`True`
- `authorizations_closed`: actual=`['artifact-change', 'artifact-decision', 'artifact-stop', 'artifact-unprocessed']`, expected=`['artifact-change', 'artifact-decision', 'artifact-stop', 'artifact-unprocessed']`, PASS=`True`
- `sources_closed`: actual=`['source-change', 'source-decision', 'source-stop', 'source-unprocessed']`, expected=`['source-change', 'source-decision', 'source-stop', 'source-unprocessed']`, PASS=`True`
- `tampered_package_fail_closed`: actual=`package_checksum_invalid`, expected=`package_checksum_invalid`, PASS=`True`

## 所有 state 字段 Project 闭包

- `project-synth-orbit:zero_leak:derivation:mixed:a-b`: actual=`False`, expected=`False`, PASS=`True`
- `project-synth-orbit:zero_leak:feedback:mixed`: actual=`False`, expected=`False`, PASS=`True`
- `project-synth-orbit:zero_leak:SYNTH_MIXED_FEEDBACK`: actual=`False`, expected=`False`, PASS=`True`
- `project-synth-orbit:zero_leak:link-mixed`: actual=`False`, expected=`False`, PASS=`True`
- `project-synth-orbit:zero_leak:artifact-b-unprocessed:v1`: actual=`False`, expected=`False`, PASS=`True`
- `project-synth-aurora:zero_leak:derivation:mixed:a-b`: actual=`False`, expected=`False`, PASS=`True`
- `project-synth-aurora:zero_leak:feedback:mixed`: actual=`False`, expected=`False`, PASS=`True`
- `project-synth-aurora:zero_leak:SYNTH_MIXED_FEEDBACK`: actual=`False`, expected=`False`, PASS=`True`
- `project-synth-aurora:zero_leak:link-mixed`: actual=`False`, expected=`False`, PASS=`True`
- `project-synth-aurora:zero_leak:artifact-decision:v1`: actual=`False`, expected=`False`, PASS=`True`
- `legal_state_present`: actual=`True`, expected=`True`, PASS=`True`
- `legal_feedback_state_present`: actual=`True`, expected=`True`, PASS=`True`

- T-UX：PASS
- T-EXPORT：PASS
- T-EXPORT-PROJECT-CLOSURE：PASS
- T-EXPORT-ALL-STATE-PROJECT-CLOSURE：PASS
