import AppKit
import ApplicationServices
import Foundation

// A fresh, review-owned interaction probe.  It only supplies synthetic
// non-provider placeholder values and never invokes the connection-test,
// enable, or send actions.

struct Arguments { let binary: String; let action: String; let output: String }

func arguments() -> Arguments? {
    let values = Array(CommandLine.arguments.dropFirst())
    guard values.count == 6 else { return nil }
    var fields: [String: String] = [:]
    var index = 0
    while index < values.count { fields[values[index]] = values[index + 1]; index += 2 }
    guard let binary = fields["--binary"], let action = fields["--action"], let output = fields["--output"] else { return nil }
    return Arguments(binary: binary, action: action, output: output)
}

func axValue(_ element: AXUIElement, _ attribute: String) -> CFTypeRef? {
    var value: CFTypeRef?
    return AXUIElementCopyAttributeValue(element, attribute as CFString, &value) == .success ? value : nil
}
func axText(_ element: AXUIElement, _ attribute: String) -> String? { axValue(element, attribute) as? String }
func children(_ element: AXUIElement) -> [AXUIElement] {
    guard let raw = axValue(element, kAXChildrenAttribute as String), CFGetTypeID(raw) == CFArrayGetTypeID() else { return [] }
    return (unsafeBitCast(raw, to: CFArray.self) as [AnyObject]).compactMap { object in
        guard CFGetTypeID(object) == AXUIElementGetTypeID() else { return nil }
        return unsafeBitCast(object, to: AXUIElement.self)
    }
}
func walk(_ element: AXUIElement, depth: Int = 0, _ predicate: (AXUIElement) -> Bool) -> AXUIElement? {
    guard depth <= 12 else { return nil }
    if predicate(element) { return element }
    for child in children(element) { if let found = walk(child, depth: depth + 1, predicate) { return found } }
    return nil
}
func visibleStrings(_ element: AXUIElement, depth: Int = 0, output: inout [String]) {
    guard depth <= 12, output.count < 1000 else { return }
    let role = axText(element, kAXRoleAttribute as String) ?? ""
    let title = axText(element, kAXTitleAttribute as String) ?? ""
    for candidate in [title, axText(element, kAXDescriptionAttribute as String)] {
        if let text = candidate, !text.isEmpty { output.append(text) }
    }
    // Do not read a password text-field's value into review evidence.
    if role != (kAXTextFieldRole as String) || title != "API Key" {
        if let value = axText(element, kAXValueAttribute as String), !value.isEmpty { output.append(value) }
    }
    for child in children(element) { visibleStrings(child, depth: depth + 1, output: &output) }
}
func contains(_ strings: [String], _ needle: String) -> Bool { strings.contains { $0.contains(needle) } }
func button(_ root: AXUIElement, _ title: String) -> AXUIElement? {
    walk(root) { element in
        axText(element, kAXRoleAttribute as String) == (kAXButtonRole as String) && axText(element, kAXTitleAttribute as String) == title
    }
}
func textField(_ root: AXUIElement, _ title: String) -> AXUIElement? {
    walk(root) { element in
        axText(element, kAXRoleAttribute as String) == (kAXTextFieldRole as String) && axText(element, kAXTitleAttribute as String) == title
    }
}
func writeJSON(_ payload: [String: Any], _ path: String) {
    guard let data = try? JSONSerialization.data(withJSONObject: payload, options: [.prettyPrinted, .sortedKeys]) else { exit(2) }
    try? data.write(to: URL(fileURLWithPath: path), options: .atomic)
}

guard let args = arguments() else { fputs("usage error\n", stderr); exit(64) }
var payload: [String: Any] = [
    "schema": "lifeos.p3-141.review-credential-lifecycle-probe.v1",
    "action": args.action,
    "expected_title": "LifeOS · P3-141 Controlled Pilot Candidate",
    "network_actions_invoked": false,
    "timestamp_utc": ISO8601DateFormatter().string(from: Date())
]
let process = Process()
process.executableURL = URL(fileURLWithPath: args.binary)
let standardError = Pipe()
process.standardError = standardError
var env = ProcessInfo.processInfo.environment
env["LIFEOS_INPUT_MODE"] = "synthetic"
env["LIFEOS_P3_141_BUILD_MODE"] = "revision_3_synthetic"
process.environment = env
do { try process.run() } catch {
    payload["status"] = "blocked"; payload["launch_error"] = String(describing: error); writeJSON(payload, args.output); exit(0)
}
let pid = process.processIdentifier
payload["direct_launch_pid"] = Int(pid)
let app = AXUIElementCreateApplication(pid)
var target: AXUIElement?
for _ in 0..<50 {
    if let raw = axValue(app, kAXWindowsAttribute as String), CFGetTypeID(raw) == CFArrayGetTypeID() {
        let windows = unsafeBitCast(raw, to: CFArray.self) as [AnyObject]
        let matches = windows.compactMap { object -> AXUIElement? in
            guard CFGetTypeID(object) == AXUIElementGetTypeID() else { return nil }
            return unsafeBitCast(object, to: AXUIElement.self)
        }.filter { axText($0, kAXTitleAttribute as String) == "LifeOS · P3-141 Controlled Pilot Candidate" }
        if matches.count == 1 { target = matches[0]; break }
    }
    Thread.sleep(forTimeInterval: 0.5)
}
guard let window = target else {
    payload["status"] = "blocked"; payload["block_reason"] = "no unique exact-title AXWindow for direct PID"
    if process.isRunning {
        process.terminate()
        for _ in 0..<20 where process.isRunning { Thread.sleep(forTimeInterval: 0.25) }
    }
    let errorData = standardError.fileHandleForReading.readDataToEndOfFile()
    if let errorText = String(data: errorData, encoding: .utf8), !errorText.isEmpty {
        payload["stderr_excerpt"] = String(errorText.prefix(1000))
    }
    payload["direct_launch_pid_exited"] = !process.isRunning; writeJSON(payload, args.output); exit(0)
}
payload["window_role"] = axText(window, kAXRoleAttribute as String) ?? ""
var starting: [String] = []; visibleStrings(window, output: &starting)
payload["has_native_web_area"] = contains(starting, "LifeOS P3-141 native WebView content")
if let settings = button(window, "Settings") {
    payload["settings_press_result"] = AXUIElementPerformAction(settings, kAXPressAction as CFString).rawValue
    Thread.sleep(forTimeInterval: 0.8)
} else { payload["settings_control_missing"] = true }

func recordState(_ label: String) {
    var strings: [String] = []; visibleStrings(window, output: &strings)
    payload["\(label)_settings_visible"] = contains(strings, "模型设置")
    payload["\(label)_encrypted_mask_message"] = contains(strings, "API Key 已加密保存")
    payload["\(label)_delete_control_present"] = button(window, "删除已保存 API Key") != nil
    payload["\(label)_local_no_key_message"] = contains(strings, "本地模型不需要 API Key")
    payload["\(label)_api_key_field_present"] = textField(window, "API Key") != nil
}

switch args.action {
case "empty-save":
    if let save = button(window, "保存 API Key") {
        payload["credential_action_press_result"] = AXUIElementPerformAction(save, kAXPressAction as CFString).rawValue
        Thread.sleep(forTimeInterval: 0.8)
    } else { payload["credential_action_missing"] = true }
    var strings: [String] = []; visibleStrings(window, output: &strings)
    payload["empty_value_rejected_in_ui"] = contains(strings, "请输入要加密保存的 API Key")
    recordState("after")
case "store", "update":
    let syntheticValue = args.action == "store" ? "review-synthetic-credential-v1-8a2f" : "review-synthetic-credential-v2-6c9d"
    if let field = textField(window, "API Key") {
        payload["credential_field_set_result"] = AXUIElementSetAttributeValue(field, kAXValueAttribute as CFString, syntheticValue as CFTypeRef).rawValue
    } else { payload["credential_field_missing"] = true }
    if let save = button(window, "保存 API Key") {
        payload["credential_action_press_result"] = AXUIElementPerformAction(save, kAXPressAction as CFString).rawValue
        Thread.sleep(forTimeInterval: 1.0)
    } else { payload["credential_action_missing"] = true }
    recordState("after")
case "inspect":
    recordState("after")
case "delete", "cloud-delete":
    if args.action == "cloud-delete" {
        if let cloud = walk(window, { element in
            axText(element, kAXRoleAttribute as String) == (kAXRadioButtonRole as String) && (axText(element, kAXTitleAttribute as String) ?? "").contains("云端模型")
        }) {
            payload["cloud_mode_press_result"] = AXUIElementPerformAction(cloud, kAXPressAction as CFString).rawValue
            Thread.sleep(forTimeInterval: 1.0)
        } else { payload["cloud_mode_control_missing"] = true }
    }
    if let delete = button(window, "删除已保存 API Key") {
        payload["credential_action_press_result"] = AXUIElementPerformAction(delete, kAXPressAction as CFString).rawValue
        Thread.sleep(forTimeInterval: 1.0)
    } else { payload["credential_action_missing"] = true }
    recordState("after")
case "local", "local-save":
    if let local = walk(window, { element in
        axText(element, kAXRoleAttribute as String) == (kAXRadioButtonRole as String) && (axText(element, kAXTitleAttribute as String) ?? "").contains("本地模型")
    }) {
        payload["local_mode_press_result"] = AXUIElementPerformAction(local, kAXPressAction as CFString).rawValue
        Thread.sleep(forTimeInterval: 1.0)
    } else { payload["local_mode_control_missing"] = true }
    if args.action == "local-save" {
        if let save = button(window, "保存配置") {
            payload["local_settings_save_press_result"] = AXUIElementPerformAction(save, kAXPressAction as CFString).rawValue
            // Wait for the asynchronous IPC response and the following render;
            // the persisted backend state, not an optimistic card redraw, is
            // what the separate SQLite probe evaluates.
            Thread.sleep(forTimeInterval: 3.0)
        } else { payload["local_settings_save_missing"] = true }
    }
    recordState("after")
    var strings: [String] = []; visibleStrings(window, output: &strings)
    payload["after_local_provider_set_visible"] = contains(strings, "Ollama") && contains(strings, "LM Studio")
default:
    payload["status"] = "blocked"; payload["block_reason"] = "unsupported review action"
}

if payload["status"] == nil { payload["status"] = "completed" }
if process.isRunning {
    process.terminate()
    for _ in 0..<20 where process.isRunning { Thread.sleep(forTimeInterval: 0.25) }
}
payload["direct_launch_pid_exited"] = !process.isRunning
payload["direct_launch_termination_status"] = process.terminationStatus
payload["completed_utc"] = ISO8601DateFormatter().string(from: Date())
writeJSON(payload, args.output)
