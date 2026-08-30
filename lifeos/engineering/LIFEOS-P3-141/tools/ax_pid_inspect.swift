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
    return (direct + contents).reduce(into: []) { output, candidate in
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

func countWebAreas(_ element: AXUIElement, depth: Int = 0) -> Int {
    guard depth < 12 else { return 0 }
    let role = stringAttribute(element, kAXRoleAttribute as CFString)
    let own = (role == "AXWebArea" || role == "AXWebView" || role == "AXHTMLContent") ? 1 : 0
    return own + children(element).reduce(0) { $0 + countWebAreas($1, depth: depth + 1) }
}

guard CommandLine.arguments.count == 2, let rawPid = Int32(CommandLine.arguments[1]), rawPid > 0 else {
    fputs("usage: ax_pid_inspect.swift <direct-pid>\n", stderr)
    exit(64)
}

let application = AXUIElementCreateApplication(pid_t(rawPid))
let windows = (attribute(application, kAXWindowsAttribute as CFString) as? [AXUIElement] ?? [])
    .filter { stringAttribute($0, kAXRoleAttribute as CFString) == "AXWindow" }
let window = windows.first

let record: [String: Any] = [
    "direct_pid": Int(rawPid),
    "ax_window_count": windows.count,
    "ax_windows": windows.map { item in
        ["title": stringAttribute(item, kAXTitleAttribute as CFString) ?? "", "frame": frame(item) ?? [:], "webview_count": countWebAreas(item)]
    },
    "ax_window_title": window.flatMap { stringAttribute($0, kAXTitleAttribute as CFString) } ?? "",
    "ax_window_frame": window.flatMap(frame) ?? [:],
    "ax_window_attribute_names": window.map(attributeNames) ?? [],
    "ax_webview_count": window.map { countWebAreas($0) } ?? 0,
]
let output = try JSONSerialization.data(withJSONObject: record, options: [.prettyPrinted, .sortedKeys])
FileHandle.standardOutput.write(output)
FileHandle.standardOutput.write(Data("\n".utf8))
