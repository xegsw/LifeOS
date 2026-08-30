import AppKit
import Foundation

guard CommandLine.arguments.count == 2, let pid = pid_t(CommandLine.arguments[1]) else {
  fputs("usage: ax_pid_window <pid>\n", stderr)
  exit(64)
}

func stringAttribute(_ element: AXUIElement, _ attribute: CFString) -> String? {
  var value: CFTypeRef?
  guard AXUIElementCopyAttributeValue(element, attribute, &value) == .success else { return nil }
  return value as? String
}

func geometry(_ element: AXUIElement) -> [String: Double]? {
  var positionValue: CFTypeRef?
  var sizeValue: CFTypeRef?
  guard AXUIElementCopyAttributeValue(element, kAXPositionAttribute as CFString, &positionValue) == .success,
        AXUIElementCopyAttributeValue(element, kAXSizeAttribute as CFString, &sizeValue) == .success,
        let positionAX = positionValue,
        let sizeAX = sizeValue
  else { return nil }
  var position = CGPoint.zero
  var size = CGSize.zero
  guard AXValueGetValue(positionAX as! AXValue, .cgPoint, &position),
        AXValueGetValue(sizeAX as! AXValue, .cgSize, &size)
  else { return nil }
  return ["x": position.x, "y": position.y, "width": size.width, "height": size.height]
}

func hasWebViewDescendant(_ element: AXUIElement, _ depth: Int = 0) -> Bool {
  guard depth <= 12 else { return false }
  if let role = stringAttribute(element, kAXRoleAttribute as CFString), role == "AXWebArea" || role == "AXWebView" { return true }
  var value: CFTypeRef?
  guard AXUIElementCopyAttributeValue(element, kAXChildrenAttribute as CFString, &value) == .success,
        let children = value as? [AXUIElement]
  else { return false }
  return children.contains { hasWebViewDescendant($0, depth + 1) }
}

func descendantRoles(_ element: AXUIElement, _ depth: Int = 0) -> [String] {
  guard depth <= 8 else { return [] }
  let role = stringAttribute(element, kAXRoleAttribute as CFString).map { [$0] } ?? []
  var value: CFTypeRef?
  guard AXUIElementCopyAttributeValue(element, kAXChildrenAttribute as CFString, &value) == .success,
        let children = value as? [AXUIElement]
  else { return role }
  return role + children.flatMap { descendantRoles($0, depth + 1) }
}

let application = AXUIElementCreateApplication(pid)
var rawWindows: CFTypeRef?
let status = AXUIElementCopyAttributeValue(application, kAXWindowsAttribute as CFString, &rawWindows)
guard status == .success, let windows = rawWindows as? [AXUIElement] else {
  let output: [String: Any] = ["pid": Int(pid), "ax_status": "windows_unavailable", "status_code": status.rawValue]
  let data = try! JSONSerialization.data(withJSONObject: output, options: [.sortedKeys])
  print(String(data: data, encoding: .utf8)!)
  exit(2)
}

let mapped: [[String: Any]] = windows.map { window in
  var item: [String: Any] = [
    "role": stringAttribute(window, kAXRoleAttribute as CFString) ?? "",
    "title": stringAttribute(window, kAXTitleAttribute as CFString) ?? "",
    "webview_descendant": hasWebViewDescendant(window),
    "descendant_roles": descendantRoles(window),
  ]
  if let frame = geometry(window) { item["frame"] = frame }
  return item
}
let output: [String: Any] = ["pid": Int(pid), "ax_status": "ok", "window_count": mapped.count, "windows": mapped]
let data = try! JSONSerialization.data(withJSONObject: output, options: [.sortedKeys])
print(String(data: data, encoding: .utf8)!)
