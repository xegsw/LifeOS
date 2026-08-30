import ApplicationServices
import CoreGraphics
import Foundation

func jsonString(_ value: Any) -> String {
  let data = try! JSONSerialization.data(withJSONObject: value, options: [.sortedKeys])
  return String(data: data, encoding: .utf8)!
}

func axString(_ element: AXUIElement, _ attribute: CFString) -> String? {
  var value: CFTypeRef?
  guard AXUIElementCopyAttributeValue(element, attribute, &value) == .success else { return nil }
  return value as? String
}

func axChildren(_ element: AXUIElement) -> [AXUIElement] {
  var value: CFTypeRef?
  guard AXUIElementCopyAttributeValue(element, kAXChildrenAttribute as CFString, &value) == .success else { return [] }
  return value as? [AXUIElement] ?? []
}

func axFrame(_ element: AXUIElement) -> [String: Double]? {
  var positionValue: CFTypeRef?
  var sizeValue: CFTypeRef?
  guard AXUIElementCopyAttributeValue(element, kAXPositionAttribute as CFString, &positionValue) == .success,
        AXUIElementCopyAttributeValue(element, kAXSizeAttribute as CFString, &sizeValue) == .success,
        let positionValue, let sizeValue else { return nil }
  let positionAX = positionValue as! AXValue
  let sizeAX = sizeValue as! AXValue
  var point = CGPoint.zero
  var size = CGSize.zero
  guard AXValueGetValue(positionAX, .cgPoint, &point), AXValueGetValue(sizeAX, .cgSize, &size) else { return nil }
  return ["x": Double(point.x), "y": Double(point.y), "width": Double(size.width), "height": Double(size.height)]
}

func axErrorName(_ error: AXError) -> String {
  switch error {
  case .success: return "success"
  case .failure: return "failure"
  case .illegalArgument: return "illegalArgument"
  case .invalidUIElement: return "invalidUIElement"
  case .invalidUIElementObserver: return "invalidUIElementObserver"
  case .cannotComplete: return "cannotComplete"
  case .attributeUnsupported: return "attributeUnsupported"
  case .actionUnsupported: return "actionUnsupported"
  case .notificationUnsupported: return "notificationUnsupported"
  case .notImplemented: return "notImplemented"
  case .notificationAlreadyRegistered: return "notificationAlreadyRegistered"
  case .notificationNotRegistered: return "notificationNotRegistered"
  case .apiDisabled: return "apiDisabled"
  case .noValue: return "noValue"
  case .parameterizedAttributeUnsupported: return "parameterizedAttributeUnsupported"
  case .notEnoughPrecision: return "notEnoughPrecision"
  @unknown default: return "unknown"
  }
}

func visit(
  _ element: AXUIElement,
  depth: Int,
  path: String,
  discovered: inout [[String: Any]],
  visited: inout Int
) {
  guard depth <= 14, visited < 1200 else { return }
  visited += 1
  let role = axString(element, kAXRoleAttribute as CFString) ?? "<missing>"
  if role == "AXWebArea" || role == "AXWebView" {
    var entry: [String: Any] = [
      "accessibility_role": role,
      "path": path,
      "title": axString(element, kAXTitleAttribute as CFString) ?? "",
      "description": axString(element, kAXDescriptionAttribute as CFString) ?? ""
    ]
    if let frame = axFrame(element) { entry["frame"] = frame }
    discovered.append(entry)
  }
  let children = axChildren(element)
  for (index, child) in children.enumerated() {
    visit(child, depth: depth + 1, path: "\(path)/\(role)[\(index)]", discovered: &discovered, visited: &visited)
  }
}

guard CommandLine.arguments.count == 2, let requested = Int32(CommandLine.arguments[1]), requested > 0 else {
  let record: [String: Any] = ["status": "invalid_argument", "usage": "direct_pid_ax_probe <pid>"]
  print(jsonString(record))
  exit(64)
}

let pid = pid_t(requested)
let application = AXUIElementCreateApplication(pid)
var observedPid: pid_t = 0
let pidError = AXUIElementGetPid(application, &observedPid)
var windowsValue: CFTypeRef?
let windowsError = AXUIElementCopyAttributeValue(application, kAXWindowsAttribute as CFString, &windowsValue)
let windows = (windowsValue as? [AXUIElement]) ?? []

var nativeWindows: [[String: Any]] = []
for (index, window) in windows.enumerated() {
  var webBranches: [[String: Any]] = []
  var visited = 0
  visit(window, depth: 0, path: "AXApplication(pid=\(requested))/AXWindow[\(index)]", discovered: &webBranches, visited: &visited)
  var entry: [String: Any] = [
    "index": index,
    "role": axString(window, kAXRoleAttribute as CFString) ?? "<missing>",
    "title": axString(window, kAXTitleAttribute as CFString) ?? "",
    "visited_descendants": visited,
    "webview_descendants": webBranches
  ]
  if let frame = axFrame(window) { entry["frame"] = frame }
  nativeWindows.append(entry)
}

let cgRaw = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]] ?? []
let cgWindows = cgRaw.compactMap { info -> [String: Any]? in
  guard let ownerPid = info[kCGWindowOwnerPID as String] as? Int, ownerPid == Int(requested) else { return nil }
  var entry: [String: Any] = [
    "owner_pid": ownerPid,
    "window_number": info[kCGWindowNumber as String] as? Int ?? -1,
    "owner_name": info[kCGWindowOwnerName as String] as? String ?? "",
    "title": info[kCGWindowName as String] as? String ?? "",
    "layer": info[kCGWindowLayer as String] as? Int ?? -1
  ]
  if let bounds = info[kCGWindowBounds as String] as? [String: Any] { entry["bounds"] = bounds }
  return entry
}

let webviewCount = nativeWindows.reduce(0) { partial, window in
  partial + ((window["webview_descendants"] as? [[String: Any]])?.count ?? 0)
}
let bindingEstablished = pidError == .success && observedPid == pid && windowsError == .success && !nativeWindows.isEmpty && webviewCount > 0
let record: [String: Any] = [
  "schema": "lifeos.p3-141.direct-pid-ax-binding.v1",
  "requested_pid": Int(requested),
  "ax_application_pid": Int(observedPid),
  "ax_application_pid_error": ["code": Int(pidError.rawValue), "name": axErrorName(pidError)],
  "ax_windows_error": ["code": Int(windowsError.rawValue), "name": axErrorName(windowsError)],
  "native_ax_windows": nativeWindows,
  "core_graphics_windows_for_exact_pid": cgWindows,
  "binding_established": bindingEstablished,
  "binding_rule": "exact PID -> AXApplication(same PID) -> AXWindow -> AXWebArea or AXWebView; no bundle, app-name, frontmost-window, or ambient-window lookup"
]
print(jsonString(record))
exit(bindingEstablished ? 0 : 3)
