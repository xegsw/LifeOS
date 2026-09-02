import AppKit
import ApplicationServices
import Foundation

guard CommandLine.arguments.count == 3, let pid = pid_t(CommandLine.arguments[1]) else {
    fputs("usage: native_pid_ax_capture <pid> <expected-title>\n", stderr)
    exit(64)
}
let expectedTitle = CommandLine.arguments[2]

func value(_ element: AXUIElement, _ attribute: String) -> CFTypeRef? {
    var result: CFTypeRef?
    return AXUIElementCopyAttributeValue(element, attribute as CFString, &result) == .success ? result : nil
}
func string(_ element: AXUIElement, _ attribute: String) -> String? { value(element, attribute) as? String }
func children(_ element: AXUIElement) -> [AXUIElement] {
    [kAXChildrenAttribute, "AXContents", "AXVisibleChildren"].flatMap { attribute -> [AXUIElement] in
        guard let raw = value(element, attribute) else { return [] as [AXUIElement] }
        if CFGetTypeID(raw) == AXUIElementGetTypeID() { return [raw as! AXUIElement] }
        return (raw as? [AXUIElement]) ?? []
    }
}
func walk(_ element: AXUIElement, _ depth: Int, _ visited: inout Set<Int>, _ found: inout [[String: Any]]) {
    guard depth <= 12, visited.insert(Int(CFHash(element))).inserted else { return }
    let role = string(element, kAXRoleAttribute) ?? ""
    if role == "AXWebArea" || role == "AXWebView" {
        found.append(["role": role, "depth": depth, "title": string(element, kAXTitleAttribute) ?? ""])
    }
    for child in children(element) { walk(child, depth + 1, &visited, &found) }
}

let app = AXUIElementCreateApplication(pid)
let windows = (value(app, kAXWindowsAttribute) as? [AXUIElement]) ?? []
let exact = windows.first { string($0, kAXRoleAttribute) == "AXWindow" && string($0, kAXTitleAttribute) == expectedTitle }
var web: [[String: Any]] = []
var visited = Set<Int>()
if let exact { walk(exact, 0, &visited, &web) }
let rawCG = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]] ?? []
let cg = rawCG.compactMap { item -> [String: Any]? in
    guard (item[kCGWindowOwnerPID as String] as? NSNumber)?.intValue == Int(pid) else { return nil }
    return ["window_number": item[kCGWindowNumber as String] as? NSNumber ?? 0,
            "name": item[kCGWindowName as String] as? String ?? "",
            "bounds": item[kCGWindowBounds as String] as? [String: Any] ?? [:]]
}
let result: [String: Any] = [
    "schema": "lifeos.p3-144.closure-4-independent-review.native-pid-ax.v1",
    "pid": Int(pid), "expected_title": expectedTitle, "accessibility_trusted": AXIsProcessTrusted(),
    "exact_title_ax_window": exact != nil, "ax_window_count": windows.count,
    "ax_web_content": web, "cg_windows_for_exact_pid": cg
]
let json = try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys])
FileHandle.standardOutput.write(json); FileHandle.standardOutput.write(Data("\n".utf8))
if !AXIsProcessTrusted() || exact == nil || web.isEmpty { exit(1) }
