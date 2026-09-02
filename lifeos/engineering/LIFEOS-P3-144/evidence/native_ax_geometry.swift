import ApplicationServices
import Foundation

struct Rect: Codable {
    let x: Double
    let y: Double
    let width: Double
    let height: Double
}

struct Output: Codable {
    let pid: Int32
    let expectedTitle: String
    let appTrusted: Bool
    let windowCount: Int
    let title: String?
    let role: String?
    let frame: Rect?
    let webRole: String?
    let webFrame: Rect?
    let windowNumber: Int?
    let result: String
}

func attribute(_ element: AXUIElement, _ name: String) -> CFTypeRef? {
    var value: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, name as CFString, &value) == .success else { return nil }
    return value
}

func stringAttribute(_ element: AXUIElement, _ name: String) -> String? {
    attribute(element, name) as? String
}

func rectAttribute(_ element: AXUIElement) -> Rect? {
    guard let positionValue = attribute(element, kAXPositionAttribute),
          let sizeValue = attribute(element, kAXSizeAttribute),
          CFGetTypeID(positionValue) == AXValueGetTypeID(),
          CFGetTypeID(sizeValue) == AXValueGetTypeID() else { return nil }
    var point = CGPoint.zero
    var size = CGSize.zero
    guard AXValueGetValue(positionValue as! AXValue, .cgPoint, &point),
          AXValueGetValue(sizeValue as! AXValue, .cgSize, &size) else { return nil }
    return Rect(x: point.x, y: point.y, width: size.width, height: size.height)
}

func children(_ element: AXUIElement) -> [AXUIElement] {
    attribute(element, kAXChildrenAttribute) as? [AXUIElement] ?? []
}

func webDescendant(_ element: AXUIElement, depth: Int = 0) -> AXUIElement? {
    guard depth <= 20 else { return nil }
    let role = stringAttribute(element, kAXRoleAttribute)
    if role == "AXWebArea" || role == "AXWebView" { return element }
    for child in children(element) {
        if let match = webDescendant(child, depth: depth + 1) { return match }
    }
    return nil
}

// This is deliberately invoked only after the AX lookup has bound the supplied
// direct PID to exactly one window bearing the supplied title. The returned ID
// is used solely with `screencapture -l` to capture that target window; no
// content or metadata for windows owned by other PIDs is emitted.
func targetWindowNumber(pid: Int32, title: String) -> Int? {
    let options: CGWindowListOption = [.optionOnScreenOnly, .excludeDesktopElements]
    let infos = CGWindowListCopyWindowInfo(options, kCGNullWindowID) as? [[String: Any]] ?? []
    let matches = infos.filter { info in
        let ownerPID = (info[kCGWindowOwnerPID as String] as? NSNumber)?.int32Value
        let name = info[kCGWindowName as String] as? String
        let layer = (info[kCGWindowLayer as String] as? NSNumber)?.intValue
        return ownerPID == pid && name == title && layer == 0
    }
    guard matches.count == 1 else { return nil }
    return (matches[0][kCGWindowNumber as String] as? NSNumber)?.intValue
}

guard CommandLine.arguments.count == 3,
      let pid = Int32(CommandLine.arguments[1]) else {
    FileHandle.standardError.write(Data("usage: native_ax_geometry <pid> <exact-title>\n".utf8))
    exit(64)
}

let expectedTitle = CommandLine.arguments[2]
let app = AXUIElementCreateApplication(pid_t(pid))
let windows = attribute(app, kAXWindowsAttribute) as? [AXUIElement] ?? []
let matching = windows.filter { stringAttribute($0, kAXTitleAttribute) == expectedTitle }
guard matching.count == 1, let window = matching.first else {
    let output = Output(pid: pid, expectedTitle: expectedTitle, appTrusted: AXIsProcessTrusted(), windowCount: windows.count, title: nil, role: nil, frame: nil, webRole: nil, webFrame: nil, windowNumber: nil, result: "exact_window_not_unique")
    print(String(data: try! JSONEncoder().encode(output), encoding: .utf8)!)
    exit(65)
}

let web = webDescendant(window)
let number = (attribute(window, "AXWindowNumber") as? NSNumber)?.intValue
    ?? targetWindowNumber(pid: pid, title: expectedTitle)
let output = Output(
    pid: pid,
    expectedTitle: expectedTitle,
    appTrusted: AXIsProcessTrusted(),
    windowCount: windows.count,
    title: stringAttribute(window, kAXTitleAttribute),
    role: stringAttribute(window, kAXRoleAttribute),
    frame: rectAttribute(window),
    webRole: web.flatMap { stringAttribute($0, kAXRoleAttribute) },
    webFrame: web.flatMap { rectAttribute($0) },
    windowNumber: number,
    result: web == nil ? "webview_not_found" : "pass"
)
print(String(data: try! JSONEncoder().encode(output), encoding: .utf8)!)
