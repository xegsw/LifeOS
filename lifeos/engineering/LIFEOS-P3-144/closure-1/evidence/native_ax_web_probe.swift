import ApplicationServices
import Foundation

struct Output: Codable {
    let pid: Int32
    let expectedTitle: String
    let windowCount: Int
    let windowRole: String?
    let descendantRoles: [String]
    let result: String
}

func attribute(_ element: AXUIElement, _ name: String) -> CFTypeRef? {
    var value: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, name as CFString, &value) == .success else { return nil }
    return value
}

func text(_ element: AXUIElement, _ name: String) -> String? {
    attribute(element, name) as? String
}

func descendants(_ element: AXUIElement, depth: Int = 0) -> [String] {
    guard depth < 12 else { return [] }
    var roles: [String] = []
    for attributeName in [kAXChildrenAttribute, kAXContentsAttribute, kAXVisibleChildrenAttribute] {
        let children = attribute(element, attributeName) as? [AXUIElement] ?? []
        for child in children {
            if let role = text(child, kAXRoleAttribute) {
                roles.append(role)
            }
            roles.append(contentsOf: descendants(child, depth: depth + 1))
        }
    }
    return roles
}

guard CommandLine.arguments.count == 3, let pid = Int32(CommandLine.arguments[1]) else {
    exit(64)
}

let expectedTitle = CommandLine.arguments[2]
let app = AXUIElementCreateApplication(pid_t(pid))
let windows = attribute(app, kAXWindowsAttribute) as? [AXUIElement] ?? []
let matches = windows.filter { text($0, kAXTitleAttribute) == expectedTitle }
guard matches.count == 1, let window = matches.first else {
    print(String(data: try! JSONEncoder().encode(Output(pid: pid, expectedTitle: expectedTitle, windowCount: windows.count, windowRole: nil, descendantRoles: [], result: "exact_window_not_unique")), encoding: .utf8)!)
    exit(65)
}
let roles = descendants(window)
let result = roles.contains("AXWebArea") || roles.contains("AXWebView") ? "pass" : "webview_not_found"
print(String(data: try! JSONEncoder().encode(Output(pid: pid, expectedTitle: expectedTitle, windowCount: windows.count, windowRole: text(window, kAXRoleAttribute), descendantRoles: Array(Set(roles)).sorted(), result: result)), encoding: .utf8)!)
