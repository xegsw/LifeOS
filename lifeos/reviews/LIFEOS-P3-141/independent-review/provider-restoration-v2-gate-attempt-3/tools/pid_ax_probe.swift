import ApplicationServices
import CoreGraphics
import Foundation

func value(_ element: AXUIElement, _ attribute: String) -> AnyObject? {
  var raw: CFTypeRef?
  guard AXUIElementCopyAttributeValue(element, attribute as CFString, &raw) == .success else { return nil }
  return raw
}

func string(_ element: AXUIElement, _ attribute: String) -> String? {
  value(element, attribute) as? String
}

func children(_ element: AXUIElement) -> [AXUIElement] {
  value(element, kAXChildrenAttribute) as? [AXUIElement] ?? []
}

func countRole(_ element: AXUIElement, _ wanted: String, _ depth: Int = 0) -> Int {
  if depth > 24 { return 0 }
  let own = string(element, kAXRoleAttribute) == wanted ? 1 : 0
  return own + children(element).reduce(0) { $0 + countRole($1, wanted, depth + 1) }
}

func tree(_ element: AXUIElement, _ depth: Int = 0) -> [[String: Any]] {
  if depth > 10 { return [] }
  let entry: [String: Any] = [
    "depth": depth,
    "role": string(element, kAXRoleAttribute) ?? "",
    "subrole": string(element, kAXSubroleAttribute) ?? "",
    "title": string(element, kAXTitleAttribute) ?? "",
    "description": string(element, kAXDescriptionAttribute) ?? "",
    "value": string(element, kAXValueAttribute) ?? "",
    "identifier": string(element, kAXIdentifierAttribute) ?? ""
  ]
  return [entry] + children(element).flatMap { tree($0, depth + 1) }
}

guard CommandLine.arguments.count == 2, let pid = pid_t(CommandLine.arguments[1]) else {
  fputs("usage: pid_ax_probe <pid>\n", stderr); exit(64)
}

let application = AXUIElementCreateApplication(pid)
let windows = value(application, kAXWindowsAttribute) as? [AXUIElement] ?? []
var processPath = [CChar](repeating: 0, count: 4096)
let pathLength = proc_pidpath(pid, &processPath, UInt32(processPath.count))
let executable = pathLength > 0 ? String(cString: processPath) : ""
let cgWindows = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]] ?? []

let windowDetails: [[String: Any]] = windows.map { window in
  var position = CGPoint.zero
  var size = CGSize.zero
  var positionRef: CFTypeRef?
  var sizeRef: CFTypeRef?
  _ = AXUIElementCopyAttributeValue(window, kAXPositionAttribute as CFString, &positionRef)
  _ = AXUIElementCopyAttributeValue(window, kAXSizeAttribute as CFString, &sizeRef)
  if let positionRef { AXValueGetValue(positionRef as! AXValue, .cgPoint, &position) }
  if let sizeRef { AXValueGetValue(sizeRef as! AXValue, .cgSize, &size) }
  return [
    "role": string(window, kAXRoleAttribute) ?? "",
    "subrole": string(window, kAXSubroleAttribute) ?? "",
    "title": string(window, kAXTitleAttribute) ?? "",
    "position": ["x": position.x, "y": position.y],
    "size": ["width": size.width, "height": size.height],
    "ax_web_area_count": countRole(window, "AXWebArea")
  ]
}

let matchingCG = cgWindows.compactMap { info -> [String: Any]? in
  guard (info[kCGWindowOwnerPID as String] as? Int32) == pid else { return nil }
  return [
    "window_number": info[kCGWindowNumber as String] as? Int ?? -1,
    "owner": info[kCGWindowOwnerName as String] as? String ?? "",
    "title": info[kCGWindowName as String] as? String ?? "",
    "bounds": info[kCGWindowBounds as String] as? [String: Any] ?? [:],
    "layer": info[kCGWindowLayer as String] as? Int ?? -1
  ]
}

let result: [String: Any] = [
  "schema": "lifeos.p3-141.pid-ax-probe.v1",
  "pid": pid,
  "executable": executable,
  "application_role": string(application, kAXRoleAttribute) ?? "",
  "window_count": windows.count,
  "windows": windowDetails,
  "ax_tree": windows.flatMap { tree($0) },
  "cg_windows_for_pid": matchingCG
]
let data = try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys])
FileHandle.standardOutput.write(data)
FileHandle.standardOutput.write("\n".data(using: .utf8)!)
