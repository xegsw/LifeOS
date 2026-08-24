import AppKit
import ApplicationServices
import CoreGraphics
import Foundation

func rectFromAX(_ element: AXUIElement) -> [String: Double]? {
  var positionValue: CFTypeRef?
  var sizeValue: CFTypeRef?
  guard AXUIElementCopyAttributeValue(element, kAXPositionAttribute as CFString, &positionValue) == .success,
        AXUIElementCopyAttributeValue(element, kAXSizeAttribute as CFString, &sizeValue) == .success,
        let position = positionValue,
        let size = sizeValue else { return nil }
  var point = CGPoint.zero
  var dimension = CGSize.zero
  guard AXValueGetValue(position as! AXValue, .cgPoint, &point),
        AXValueGetValue(size as! AXValue, .cgSize, &dimension) else { return nil }
  return ["x": point.x, "y": point.y, "width": dimension.width, "height": dimension.height]
}

let arguments = CommandLine.arguments
guard arguments.count == 3, let rawPid = Int32(arguments[1]) else {
  fputs("usage: native_geometry <pid> <label>\\n", stderr)
  exit(2)
}
let app = AXUIElementCreateApplication(rawPid)
var windowsValue: CFTypeRef?
let axStatus = AXUIElementCopyAttributeValue(app, kAXWindowsAttribute as CFString, &windowsValue)
var axWindows: [[String: Any]] = []
if axStatus == .success, let windows = windowsValue as? [AXUIElement] {
  for window in windows {
    var titleValue: CFTypeRef?
    _ = AXUIElementCopyAttributeValue(window, kAXTitleAttribute as CFString, &titleValue)
    axWindows.append([
      "title": titleValue as? String ?? "",
      "rect": rectFromAX(window) as Any,
    ])
  }
}

let cgList = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as NSArray? ?? []
let cgWindows: [[String: Any]] = cgList.compactMap { value in
  guard let info = value as? NSDictionary,
        (info[kCGWindowOwnerPID as String] as? NSNumber)?.int32Value == rawPid else { return nil }
  return [
    "title": info[kCGWindowName as String] as? String ?? "",
    "owner": info[kCGWindowOwnerName as String] as? String ?? "",
    "layer": (info[kCGWindowLayer as String] as? NSNumber)?.intValue ?? -1,
    "bounds": info[kCGWindowBounds as String] as? NSDictionary ?? [:],
  ]
}
let cgVisibleWindows: [[String: Any]] = cgList.compactMap { value in
  guard let info = value as? NSDictionary else { return nil }
  return [
    "pid": (info[kCGWindowOwnerPID as String] as? NSNumber)?.intValue as Any,
    "title": info[kCGWindowName as String] as? String ?? "",
    "owner": info[kCGWindowOwnerName as String] as? String ?? "",
    "layer": (info[kCGWindowLayer as String] as? NSNumber)?.intValue ?? -1,
    "bounds": info[kCGWindowBounds as String] as? NSDictionary ?? [:],
  ]
}

let payload: [String: Any] = [
  "label": arguments[2],
  "pid": rawPid,
  "ax_status": axStatus.rawValue,
  "ax_windows": axWindows,
  "cg_window_count": cgList.count,
  "cg_windows": cgWindows,
  "cg_visible_windows": cgVisibleWindows,
]
let data = try JSONSerialization.data(withJSONObject: payload, options: [.prettyPrinted, .sortedKeys])
FileHandle.standardOutput.write(data)
FileHandle.standardOutput.write("\n".data(using: .utf8)!)
