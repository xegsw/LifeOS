import AppKit
import ApplicationServices
import CoreGraphics
import Foundation

let title = "LifeOS · 模型设置（安全凭据验证）"

struct Frame: Codable { let x: CGFloat; let y: CGFloat; let width: CGFloat; let height: CGFloat }
struct ViewRecord: Codable {
    let name: String
    let requested: Frame?
    let axFrame: Frame?
    let cgWindowId: UInt32?
    let cgFrame: Frame?
    let screenshot: String?
    let result: String
    let failure: String?
}
struct Record: Codable {
    let schema: String
    let mode: String
    let directPid: Int32
    let bundlePath: String
    let exactTitle: String
    let axTrusted: Bool
    let titleMatched: Bool
    let windowRole: String?
    let webRoles: [String]
    let views: [ViewRecord]
    let result: String
    let failure: String?
    let boundaryNote: String
}

func raw(_ element: AXUIElement, _ attribute: String) -> CFTypeRef? {
    var value: CFTypeRef?
    return AXUIElementCopyAttributeValue(element, attribute as CFString, &value) == .success ? value : nil
}
func text(_ element: AXUIElement, _ attribute: String) -> String? { raw(element, attribute) as? String }
func elements(_ value: CFTypeRef?) -> [AXUIElement] {
    guard let value, CFGetTypeID(value) == CFArrayGetTypeID() else { return [] }
    let values = unsafeBitCast(value, to: CFArray.self)
    return (0..<CFArrayGetCount(values)).map { unsafeBitCast(CFArrayGetValueAtIndex(values, $0), to: AXUIElement.self) }
}
func windowFor(_ pid: Int32) -> AXUIElement? {
    elements(raw(AXUIElementCreateApplication(pid), kAXWindowsAttribute as String)).first { text($0, kAXTitleAttribute as String) == title }
}
func frame(_ window: AXUIElement) -> Frame? {
    guard let positionRaw = raw(window, kAXPositionAttribute as String), let sizeRaw = raw(window, kAXSizeAttribute as String) else { return nil }
    let position = unsafeBitCast(positionRaw, to: AXValue.self)
    let size = unsafeBitCast(sizeRaw, to: AXValue.self)
    var point = CGPoint.zero; var dimensions = CGSize.zero
    guard AXValueGetValue(position, .cgPoint, &point), AXValueGetValue(size, .cgSize, &dimensions) else { return nil }
    return Frame(x: point.x, y: point.y, width: dimensions.width, height: dimensions.height)
}
func webRoles(_ element: AXUIElement, _ depth: Int = 0) -> [String] {
    guard depth < 8 else { return [] }
    return elements(raw(element, kAXChildrenAttribute as String)).flatMap { child in
        let role = text(child, kAXRoleAttribute as String)
        return ((role == "AXWebArea" || role == "AXWebView") ? [role!] : []) + webRoles(child, depth + 1)
    }
}
func cgMatch(_ pid: Int32) -> (UInt32, Frame)? {
    let windows = (CGWindowListCopyWindowInfo(.optionOnScreenOnly, kCGNullWindowID) as? [[String: Any]]) ?? []
    guard let info = windows.first(where: { item in
        let owner = (item[kCGWindowOwnerPID as String] as? NSNumber)?.int32Value
        let layer = (item[kCGWindowLayer as String] as? NSNumber)?.intValue
        let name = item[kCGWindowName as String] as? String
        return owner == pid && layer == 0 && name == title
    }), let number = (info[kCGWindowNumber as String] as? NSNumber)?.uint32Value,
      let bounds = info[kCGWindowBounds as String] as? [String: NSNumber],
      let x = bounds["X"]?.doubleValue, let y = bounds["Y"]?.doubleValue,
      let width = bounds["Width"]?.doubleValue, let height = bounds["Height"]?.doubleValue else { return nil }
    return (number, Frame(x: x, y: y, width: width, height: height))
}
func capture(_ pid: Int32, _ name: String, _ requested: Frame?, _ outputDirectory: String) -> ViewRecord {
    guard let initial = windowFor(pid) else {
        return ViewRecord(name: name, requested: requested, axFrame: nil, cgWindowId: nil, cgFrame: nil, screenshot: nil, result: "PAUSED_RESUMABLE", failure: "exact-title AXWindow unavailable")
    }
    if let requested {
        var value = CGSize(width: requested.width, height: requested.height)
        guard let axValue = AXValueCreate(.cgSize, &value), AXUIElementSetAttributeValue(initial, kAXSizeAttribute as CFString, axValue) == .success else {
            return ViewRecord(name: name, requested: requested, axFrame: frame(initial), cgWindowId: nil, cgFrame: nil, screenshot: nil, result: "PAUSED_RESUMABLE", failure: "exact AX resize unavailable")
        }
        Thread.sleep(forTimeInterval: 0.8)
    }
    guard let target = windowFor(pid), let match = cgMatch(pid) else {
        return ViewRecord(name: name, requested: requested, axFrame: frame(initial), cgWindowId: nil, cgFrame: nil, screenshot: nil, result: "PAUSED_RESUMABLE", failure: "exact-PID CG target unavailable")
    }
    let image = URL(fileURLWithPath: outputDirectory).appendingPathComponent("native_\(name)_target_only.png").path
    let process = Process(); process.executableURL = URL(fileURLWithPath: "/usr/sbin/screencapture"); process.arguments = ["-x", "-l\(match.0)", image]
    do { try process.run(); process.waitUntilExit() } catch {
        return ViewRecord(name: name, requested: requested, axFrame: frame(target), cgWindowId: match.0, cgFrame: match.1, screenshot: nil, result: "PAUSED_RESUMABLE", failure: "target-only screenshot service unavailable")
    }
    let pass = process.terminationStatus == 0 && FileManager.default.fileExists(atPath: image)
    return ViewRecord(name: name, requested: requested, axFrame: frame(target), cgWindowId: match.0, cgFrame: match.1, screenshot: pass ? image : nil, result: pass ? "PASS" : "PAUSED_RESUMABLE", failure: pass ? nil : "target-only screenshot write failed")
}
func write(_ record: Record, _ path: String) { let encoder = JSONEncoder(); encoder.outputFormatting = [.prettyPrinted, .sortedKeys]; try! encoder.encode(record).write(to: URL(fileURLWithPath: path), options: .atomic) }

guard CommandLine.arguments.count == 4 else { fputs("usage: native_pid_ax_capture <bundle.app> <record.json> <output-dir>\n", stderr); exit(64) }
let bundle = CommandLine.arguments[1]; let recordPath = CommandLine.arguments[2]; let output = CommandLine.arguments[3]
let configuration = NSWorkspace.OpenConfiguration(); configuration.createsNewApplicationInstance = true; configuration.activates = true
let semaphore = DispatchSemaphore(value: 0); var launched: NSRunningApplication?; var launchError: Error?
NSWorkspace.shared.openApplication(at: URL(fileURLWithPath: bundle), configuration: configuration) { application, error in launched = application; launchError = error; semaphore.signal() }
guard semaphore.wait(timeout: .now() + 15) == .success, let application = launched else {
    write(Record(schema: "lifeos.p3-143.independent-rereview4.native.v1", mode: "synthetic_offline", directPid: -1, bundlePath: bundle, exactTitle: title, axTrusted: AXIsProcessTrusted(), titleMatched: false, windowRole: nil, webRoles: [], views: [], result: "PAUSED_RESUMABLE", failure: "NSWorkspace direct launch failed: \(launchError?.localizedDescription ?? "timeout")", boundaryNote: "Only direct PID, exact title, AX roles, geometry, and exact-PID target screenshots are queried; no page text, credential, Provider, network, or personal data is read."), recordPath); exit(2)
}
let pid = application.processIdentifier; Thread.sleep(forTimeInterval: 2.0)
guard let window = windowFor(pid) else {
    write(Record(schema: "lifeos.p3-143.independent-rereview4.native.v1", mode: "synthetic_offline", directPid: pid, bundlePath: bundle, exactTitle: title, axTrusted: AXIsProcessTrusted(), titleMatched: false, windowRole: nil, webRoles: [], views: [], result: "PAUSED_RESUMABLE", failure: "exact-title AXWindow unavailable for direct PID", boundaryNote: "Only direct PID, exact title, AX roles, geometry, and exact-PID target screenshots are queried; no page text, credential, Provider, network, or personal data is read."), recordPath); exit(3)
}
let desktop = capture(pid, "desktop", nil, output)
let compact = capture(pid, "compact", Frame(x: 0, y: 0, width: 1160, height: 768), output)
let narrow = capture(pid, "narrow", Frame(x: 0, y: 0, width: 700, height: 760), output)
let views = [desktop, compact, narrow]; let roles = Array(Set(webRoles(window))).sorted()
let pass = text(window, kAXRoleAttribute as String) == "AXWindow" && !roles.isEmpty && views.allSatisfy { $0.result == "PASS" }
write(Record(schema: "lifeos.p3-143.independent-rereview4.native.v1", mode: "synthetic_offline", directPid: pid, bundlePath: bundle, exactTitle: title, axTrusted: AXIsProcessTrusted(), titleMatched: true, windowRole: text(window, kAXRoleAttribute as String), webRoles: roles, views: views, result: pass ? "PASS" : "PAUSED_RESUMABLE", failure: pass ? nil : "native AX/geometry/screenshot Evidence gap", boundaryNote: "Only direct PID, exact title, AX roles, geometry, and exact-PID target screenshots are queried; no page text, credential, Provider, network, or personal data is read."), recordPath)
exit(pass ? 0 : 4)
