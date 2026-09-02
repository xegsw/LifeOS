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

func string(_ element: AXUIElement, _ attribute: String) -> String? {
    value(element, attribute) as? String
}

func relatedElements(_ element: AXUIElement) -> [AXUIElement] {
    let attributes = [kAXChildrenAttribute, "AXContents", "AXVisibleChildren", "AXRows", "AXTabs"]
    return attributes.flatMap { attribute -> [AXUIElement] in
        guard let attributeValue = value(element, attribute) else { return [] }
        if CFGetTypeID(attributeValue) == AXUIElementGetTypeID() { return [attributeValue as! AXUIElement] }
        return (attributeValue as? [AXUIElement]) ?? []
    }
}

func walk(_ element: AXUIElement, _ depth: Int, _ visited: inout Set<Int>, _ records: inout [[String: Any]]) {
    guard depth <= 12 else { return }
    let identity = Int(CFHash(element))
    guard visited.insert(identity).inserted else { return }
    let role = string(element, kAXRoleAttribute) ?? ""
    if role == "AXWebArea" || role == "AXWebView" {
        records.append([
            "role": role,
            "subrole": string(element, kAXSubroleAttribute) ?? "",
            "title": string(element, kAXTitleAttribute) ?? "",
            "depth": depth
        ])
    }
    for child in relatedElements(element) { walk(child, depth + 1, &visited, &records) }
}

let application = AXUIElementCreateApplication(pid)
let windows = (value(application, kAXWindowsAttribute) as? [AXUIElement]) ?? []
var windowRecords: [[String: Any]] = []
var exactWindow: AXUIElement?
for window in windows {
    let title = string(window, kAXTitleAttribute) ?? ""
    let role = string(window, kAXRoleAttribute) ?? ""
    windowRecords.append(["title": title, "role": role])
    if title == expectedTitle && role == "AXWindow" { exactWindow = window }
}
var webRecords: [[String: Any]] = []
var visited = Set<Int>()
if let exactWindow { walk(exactWindow, 0, &visited, &webRecords) }

let rawWindows = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]] ?? []
let cgWindows = rawWindows.compactMap { item -> [String: Any]? in
    guard (item[kCGWindowOwnerPID as String] as? NSNumber)?.intValue == Int(pid) else { return nil }
    return [
        "window_number": item[kCGWindowNumber as String] as? NSNumber ?? 0,
        "name": item[kCGWindowName as String] as? String ?? "",
        "owner": item[kCGWindowOwnerName as String] as? String ?? "",
        "bounds": item[kCGWindowBounds as String] as? [String: Any] ?? [:]
    ]
}
let result: [String: Any] = [
    "schema": "lifeos.p3-144.independent-review.native-pid-ax.v1",
    "pid": Int(pid),
    "expected_title": expectedTitle,
    "accessibility_trusted": AXIsProcessTrusted(),
    "application_title": string(application, kAXTitleAttribute) ?? "",
    "ax_windows": windowRecords,
    "exact_title_ax_window": exactWindow != nil,
    "ax_web_content": webRecords,
    "cg_windows_for_exact_pid": cgWindows
]
let json = try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys])
FileHandle.standardOutput.write(json)
FileHandle.standardOutput.write(Data("\n".utf8))
if !AXIsProcessTrusted() || exactWindow == nil || webRecords.isEmpty { exit(1) }
