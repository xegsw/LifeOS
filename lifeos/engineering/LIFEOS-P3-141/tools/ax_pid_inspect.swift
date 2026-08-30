// Direct, single-PID Accessibility inspection for P3-141 actual-Tauri
// Evidence. It never enumerates applications or windows: the sole input is
// the PID emitted by the corresponding controlled launch.
import ApplicationServices
import Cocoa
import Foundation

func attribute(_ element: AXUIElement, _ name: CFString) -> CFTypeRef? {
    var value: CFTypeRef?
    return AXUIElementCopyAttributeValue(element, name, &value) == .success ? value : nil
}

func stringAttribute(_ element: AXUIElement, _ name: CFString) -> String? {
    attribute(element, name) as? String
}

func children(_ element: AXUIElement) -> [AXUIElement] {
    let direct = attribute(element, kAXChildrenAttribute as CFString) as? [AXUIElement] ?? []
    let contents = attribute(element, kAXContentsAttribute as CFString) as? [AXUIElement] ?? []
    let visible = attribute(element, kAXVisibleChildrenAttribute as CFString) as? [AXUIElement] ?? []
    return (direct + contents + visible).reduce(into: []) { output, candidate in
        if !output.contains(where: { CFEqual($0, candidate) }) { output.append(candidate) }
    }
}

func attributeNames(_ element: AXUIElement) -> [String] {
    var names: CFArray?
    guard AXUIElementCopyAttributeNames(element, &names) == .success, let names else { return [] }
    return names as? [String] ?? []
}

func frame(_ element: AXUIElement) -> [String: Double]? {
    guard let positionRaw = attribute(element, kAXPositionAttribute as CFString),
          let sizeRaw = attribute(element, kAXSizeAttribute as CFString) else { return nil }
    let positionValue = unsafeBitCast(positionRaw, to: AXValue.self)
    let sizeValue = unsafeBitCast(sizeRaw, to: AXValue.self)
    guard AXValueGetType(positionValue) == .cgPoint, AXValueGetType(sizeValue) == .cgSize else { return nil }
    var position = CGPoint.zero
    var size = CGSize.zero
    guard AXValueGetValue(positionValue, .cgPoint, &position), AXValueGetValue(sizeValue, .cgSize, &size) else { return nil }
    return ["x": Double(position.x), "y": Double(position.y), "width": Double(size.width), "height": Double(size.height)]
}

func nativeWebNodes(_ element: AXUIElement, depth: Int = 0) -> [[String: Any]] {
    guard depth < 16 else { return [] }
    let role = stringAttribute(element, kAXRoleAttribute as CFString) ?? ""
    let own: [[String: Any]] = (role == "AXWebArea" || role == "AXWebView")
        ? [["role": role, "title": stringAttribute(element, kAXTitleAttribute as CFString) ?? "", "frame": frame(element) ?? [:]]]
        : []
    return own + children(element).flatMap { nativeWebNodes($0, depth: depth + 1) }
}

func nativeWebNodeEvidencePass(_ roles: [String]) -> Bool {
    roles.contains("AXWebArea") || roles.contains("AXWebView")
}

if CommandLine.arguments.count == 2 && CommandLine.arguments[1] == "--self-test" {
    let controls: [[String: Any]] = [
        ["name": "window_only_rejected", "roles": ["AXWindow", "AXGroup", "AXStaticText"], "passed": !nativeWebNodeEvidencePass(["AXWindow", "AXGroup", "AXStaticText"])],
        ["name": "app_html_only_rejected", "roles": ["AXWindow", "AXHTMLContent"], "passed": !nativeWebNodeEvidencePass(["AXWindow", "AXHTMLContent"])],
        ["name": "native_web_area_accepted", "roles": ["AXWindow", "AXWebArea"], "passed": nativeWebNodeEvidencePass(["AXWindow", "AXWebArea"])],
        ["name": "native_web_view_accepted", "roles": ["AXWindow", "AXWebView"], "passed": nativeWebNodeEvidencePass(["AXWindow", "AXWebView"])],
    ]
    let record: [String: Any] = ["mode": "strict_native_web_node_counterexamples", "all_passed": controls.allSatisfy { $0["passed"] as? Bool == true }, "controls": controls]
    let output = try JSONSerialization.data(withJSONObject: record, options: [.prettyPrinted, .sortedKeys])
    FileHandle.standardOutput.write(output)
    FileHandle.standardOutput.write(Data("\n".utf8))
    exit(0)
}

guard CommandLine.arguments.count == 3, let rawPid = Int32(CommandLine.arguments[1]), rawPid > 0 else {
    fputs("usage: ax_pid_inspect.swift <direct-pid> <exact-window-title> | --self-test\n", stderr)
    exit(64)
}

let expectedTitle = CommandLine.arguments[2]
let application = AXUIElementCreateApplication(pid_t(rawPid))
let windows = (attribute(application, kAXWindowsAttribute as CFString) as? [AXUIElement] ?? [])
    .filter { stringAttribute($0, kAXRoleAttribute as CFString) == "AXWindow" }
let exactWindows = windows.filter { stringAttribute($0, kAXTitleAttribute as CFString) == expectedTitle }
let window = exactWindows.first
let nodes = window.map { nativeWebNodes($0) } ?? []

let record: [String: Any] = [
    "direct_pid": Int(rawPid),
    "expected_window_title": expectedTitle,
    "ax_window_count": windows.count,
    "exact_title_ax_window_count": exactWindows.count,
    "ax_windows": windows.map { item in
        ["title": stringAttribute(item, kAXTitleAttribute as CFString) ?? "", "frame": frame(item) ?? [:], "native_web_node_count": nativeWebNodes(item).count]
    },
    "ax_window_title": window.flatMap { stringAttribute($0, kAXTitleAttribute as CFString) } ?? "",
    "ax_window_frame": window.flatMap(frame) ?? [:],
    "ax_window_attribute_names": window.map(attributeNames) ?? [],
    "native_web_nodes": nodes,
    "native_web_node_count": nodes.count,
    "strict_native_web_node_pass": exactWindows.count == 1 && !nodes.isEmpty,
]
let output = try JSONSerialization.data(withJSONObject: record, options: [.prettyPrinted, .sortedKeys])
FileHandle.standardOutput.write(output)
FileHandle.standardOutput.write(Data("\n".utf8))
