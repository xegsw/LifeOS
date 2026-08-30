import ApplicationServices
import Foundation

func value(_ element: AXUIElement, _ attribute: String) -> AnyObject? { var raw: CFTypeRef?; guard AXUIElementCopyAttributeValue(element, attribute as CFString, &raw) == .success else { return nil }; return raw }
func text(_ element: AXUIElement, _ attribute: String) -> String { value(element, attribute) as? String ?? "" }
func children(_ element: AXUIElement) -> [AXUIElement] { value(element, kAXChildrenAttribute) as? [AXUIElement] ?? [] }
func find(_ element: AXUIElement, _ wantedRole: String, _ wantedTitle: String, _ depth: Int = 0) -> AXUIElement? {
  if depth > 16 { return nil }
  if text(element, kAXRoleAttribute) == wantedRole && text(element, kAXTitleAttribute) == wantedTitle { return element }
  for child in children(element) { if let match = find(child, wantedRole, wantedTitle, depth + 1) { return match } }
  return nil
}
guard CommandLine.arguments.count >= 5, let pid = pid_t(CommandLine.arguments[2]) else { fputs("usage: pid_ax_interact <press|set> <pid> <role> <title> [value]\n", stderr); exit(64) }
let action = CommandLine.arguments[1], wantedRole = CommandLine.arguments[3], wantedTitle = CommandLine.arguments[4]
let app = AXUIElementCreateApplication(pid)
guard let target = find(app, wantedRole, wantedTitle) else { fputs("target_not_found\n", stderr); exit(2) }
let result: AXError
if action == "press" { result = AXUIElementPerformAction(target, kAXPressAction as CFString) }
else if action == "set", CommandLine.arguments.count == 6 { result = AXUIElementSetAttributeValue(target, kAXValueAttribute as CFString, CommandLine.arguments[5] as CFString) }
else { fputs("invalid_action\n", stderr); exit(64) }
let payload: [String: Any] = ["schema": "lifeos.p3-141.pid-ax-interact.v1", "action": action, "pid": pid, "role": wantedRole, "title": wantedTitle, "result": result.rawValue, "success": result == .success]
let data = try JSONSerialization.data(withJSONObject: payload, options: [.sortedKeys]); FileHandle.standardOutput.write(data); FileHandle.standardOutput.write("\n".data(using: .utf8)!)
if result != .success { exit(3) }
