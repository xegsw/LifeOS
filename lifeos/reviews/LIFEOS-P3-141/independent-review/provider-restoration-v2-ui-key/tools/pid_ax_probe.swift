import ApplicationServices
import Foundation

struct Probe: Encodable {
    let pid: Int32
    let windows_ax_error: Int32
    let windows_count: Int?
    let window_roles: [String]
    let webview_like_descendants: Int
}

func value(_ element: AXUIElement, _ attribute: String) -> CFTypeRef? {
    var output: CFTypeRef?
    return AXUIElementCopyAttributeValue(element, attribute as CFString, &output) == .success ? output : nil
}

func text(_ element: AXUIElement, _ attribute: String) -> String {
    guard let output = value(element, attribute) else { return "" }
    return output as? String ?? ""
}

func descendants(_ element: AXUIElement) -> Int {
    let role = text(element, kAXRoleAttribute)
    let subrole = text(element, kAXSubroleAttribute)
    let current = (role == "AXWebArea" || subrole.lowercased().contains("web")) ? 1 : 0
    guard let children = value(element, kAXChildrenAttribute) as? [AXUIElement] else { return current }
    return current + children.reduce(0) { $0 + descendants($1) }
}

guard CommandLine.arguments.count == 2, let raw = Int32(CommandLine.arguments[1]) else {
    fputs("usage: pid_ax_probe <pid>\n", stderr)
    exit(64)
}

let app = AXUIElementCreateApplication(raw)
var output: CFTypeRef?
let error = AXUIElementCopyAttributeValue(app, kAXWindowsAttribute as CFString, &output)
var roles: [String] = []
var webviews = 0
if error == .success, let windows = output as? [AXUIElement] {
    for window in windows {
        roles.append([text(window, kAXRoleAttribute), text(window, kAXTitleAttribute)].joined(separator: ":"))
        webviews += descendants(window)
    }
}
let result = Probe(pid: raw, windows_ax_error: error.rawValue, windows_count: error == .success ? roles.count : nil, window_roles: roles, webview_like_descendants: webviews)
let encoded = try JSONEncoder().encode(result)
print(String(data: encoded, encoding: .utf8)!)
