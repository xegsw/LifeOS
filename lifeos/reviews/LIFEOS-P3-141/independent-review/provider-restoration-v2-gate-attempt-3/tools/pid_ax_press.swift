import ApplicationServices
import Foundation

func value(_ element: AXUIElement, _ attribute: String) -> AnyObject? {
  var raw: CFTypeRef?
  guard AXUIElementCopyAttributeValue(element, attribute as CFString, &raw) == .success else { return nil }
  return raw
}

func title(_ element: AXUIElement) -> String { value(element, kAXTitleAttribute) as? String ?? "" }
func role(_ element: AXUIElement) -> String { value(element, kAXRoleAttribute) as? String ?? "" }
func children(_ element: AXUIElement) -> [AXUIElement] { value(element, kAXChildrenAttribute) as? [AXUIElement] ?? [] }

func find(_ element: AXUIElement, _ wanted: String, _ depth: Int = 0) -> AXUIElement? {
  if depth > 16 { return nil }
  if role(element) == "AXButton" && title(element) == wanted { return element }
  for child in children(element) { if let match = find(child, wanted, depth + 1) { return match } }
  return nil
}

guard CommandLine.arguments.count == 3, let pid = pid_t(CommandLine.arguments[1]) else {
  fputs("usage: pid_ax_press <pid> <exact button title>\n", stderr); exit(64)
}
let wanted = CommandLine.arguments[2]
let application = AXUIElementCreateApplication(pid)
let windows = value(application, kAXWindowsAttribute) as? [AXUIElement] ?? []
guard let button = windows.lazy.compactMap({ find($0, wanted) }).first else {
  let payload: [String: Any] = ["schema": "lifeos.p3-141.pid-ax-press.v1", "pid": pid, "title": wanted, "pressed": false, "reason": "button_not_found"]
  let data = try JSONSerialization.data(withJSONObject: payload, options: [.sortedKeys])
  FileHandle.standardOutput.write(data); FileHandle.standardOutput.write("\n".data(using: .utf8)!); exit(2)
}
let result = AXUIElementPerformAction(button, kAXPressAction as CFString)
let payload: [String: Any] = ["schema": "lifeos.p3-141.pid-ax-press.v1", "pid": pid, "title": wanted, "pressed": result == .success, "ax_result": result.rawValue]
let data = try JSONSerialization.data(withJSONObject: payload, options: [.sortedKeys])
FileHandle.standardOutput.write(data); FileHandle.standardOutput.write("\n".data(using: .utf8)!)
if result != .success { exit(3) }
