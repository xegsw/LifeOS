import AppKit
import ApplicationServices
import CoreGraphics
import Foundation

struct CaptureRecord: Codable {
    let schema: String
    let directPid: Int32
    let bundlePath: String
    let exactTitle: String
    let axTrusted: Bool
    let titleMatched: Bool
    let windowRole: String?
    let windowFrame: [String: CGFloat]?
    let webRoles: [String]
    let screenshotPath: String?
    let screenshotOwnerPid: Int32?
    let screenshotWindowId: UInt32?
    let result: String
    let failure: String?
    let boundaryNote: String
}

func value(_ element: AXUIElement, _ attribute: String) -> CFTypeRef? {
    var result: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, attribute as CFString, &result) == .success else { return nil }
    return result
}

func textValue(_ element: AXUIElement, _ attribute: String) -> String? {
    value(element, attribute) as? String
}

func children(of element: AXUIElement) -> [AXUIElement] {
    value(element, kAXChildrenAttribute as String) as? [AXUIElement] ?? []
}

func descendantWebRoles(_ element: AXUIElement, depth: Int = 0) -> [String] {
    guard depth < 8 else { return [] }
    var roles: [String] = []
    for child in children(of: element) {
        if let role = textValue(child, kAXRoleAttribute as String), role == "AXWebArea" || role == "AXWebView" {
            roles.append(role)
        }
        roles.append(contentsOf: descendantWebRoles(child, depth: depth + 1))
    }
    return roles
}

func frame(of window: AXUIElement) -> [String: CGFloat]? {
    guard let positionRef = value(window, kAXPositionAttribute as String),
          let sizeRef = value(window, kAXSizeAttribute as String) else { return nil }
    let position = unsafeBitCast(positionRef, to: AXValue.self)
    let size = unsafeBitCast(sizeRef, to: AXValue.self)
    var point = CGPoint.zero
    var dimensions = CGSize.zero
    guard AXValueGetValue(position, .cgPoint, &point), AXValueGetValue(size, .cgSize, &dimensions) else { return nil }
    return ["x": point.x, "y": point.y, "width": dimensions.width, "height": dimensions.height]
}

func writeRecord(_ record: CaptureRecord, to path: String) {
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    let data = try! encoder.encode(record)
    try! data.write(to: URL(fileURLWithPath: path), options: .atomic)
}

guard CommandLine.arguments.count == 4 else {
    fputs("usage: native_pid_ax_capture.swift <bundle.app> <record.json> <screenshot.png>\\n", stderr)
    exit(64)
}

let bundlePath = CommandLine.arguments[1]
let recordPath = CommandLine.arguments[2]
let screenshotPath = CommandLine.arguments[3]
let exactTitle = "LifeOS · 模型设置（安全凭据验证）"
let workspace = NSWorkspace.shared
let configuration = NSWorkspace.OpenConfiguration()
configuration.createsNewApplicationInstance = true
configuration.activates = false
let launchSemaphore = DispatchSemaphore(value: 0)
var running: NSRunningApplication?
var launchError: Error?
workspace.openApplication(at: URL(fileURLWithPath: bundlePath), configuration: configuration) { application, error in
    running = application
    launchError = error
    launchSemaphore.signal()
}

guard launchSemaphore.wait(timeout: .now() + 15) == .success, let application = running else {
    let record = CaptureRecord(schema: "lifeos.p3-143.native-pid-ax-capture.v1", directPid: -1, bundlePath: bundlePath, exactTitle: exactTitle, axTrusted: AXIsProcessTrusted(), titleMatched: false, windowRole: nil, windowFrame: nil, webRoles: [], screenshotPath: nil, screenshotOwnerPid: nil, screenshotWindowId: nil, result: "PAUSED_RESUMABLE", failure: "NSWorkspace launch failed: \\(launchError?.localizedDescription ?? \"timeout\")", boundaryNote: "Only bundle identity, exact title, AX roles and exact-PID geometry were queried; no UI content, credential, provider, network or personal data was accessed.")
    writeRecord(record, to: recordPath)
    exit(2)
}

let pid = application.processIdentifier
Thread.sleep(forTimeInterval: 2.0)
let trusted = AXIsProcessTrusted()
let appElement = AXUIElementCreateApplication(pid)
let appWindows = value(appElement, kAXWindowsAttribute as String) as? [AXUIElement] ?? []
let targetWindow = appWindows.first { textValue($0, kAXTitleAttribute as String) == exactTitle }

guard let window = targetWindow else {
    let record = CaptureRecord(schema: "lifeos.p3-143.native-pid-ax-capture.v1", directPid: pid, bundlePath: bundlePath, exactTitle: exactTitle, axTrusted: trusted, titleMatched: false, windowRole: nil, windowFrame: nil, webRoles: [], screenshotPath: nil, screenshotOwnerPid: nil, screenshotWindowId: nil, result: "PAUSED_RESUMABLE", failure: trusted ? "exact-title AXWindow unavailable for direct PID" : "Accessibility API is not trusted for the direct PID", boundaryNote: "Only bundle identity, exact title, AX roles and exact-PID geometry were queried; no UI content, credential, provider, network or personal data was accessed.")
    writeRecord(record, to: recordPath)
    exit(3)
}

let windowRole = textValue(window, kAXRoleAttribute as String)
let windowFrame = frame(of: window)
let webRoles = Array(Set(descendantWebRoles(window))).sorted()
let infos = (CGWindowListCopyWindowInfo(.optionIncludingWindow, kCGNullWindowID) as? [[String: Any]]) ?? []
let matchingInfo = infos.first { info in
    let owner = (info[kCGWindowOwnerPID as String] as? NSNumber)?.int32Value
    let layer = (info[kCGWindowLayer as String] as? NSNumber)?.intValue ?? -1
    return owner == pid && layer == 0
}

guard let info = matchingInfo, let number = (info[kCGWindowNumber as String] as? NSNumber)?.uint32Value else {
    let record = CaptureRecord(schema: "lifeos.p3-143.native-pid-ax-capture.v1", directPid: pid, bundlePath: bundlePath, exactTitle: exactTitle, axTrusted: trusted, titleMatched: true, windowRole: windowRole, windowFrame: windowFrame, webRoles: webRoles, screenshotPath: nil, screenshotOwnerPid: nil, screenshotWindowId: nil, result: "PAUSED_RESUMABLE", failure: "exact-PID CGWindow unavailable for target-only screenshot", boundaryNote: "Only bundle identity, exact title, AX roles and exact-PID geometry were queried; no UI content, credential, provider, network or personal data was accessed.")
    writeRecord(record, to: recordPath)
    exit(4)
}

let screenshot = Process()
screenshot.executableURL = URL(fileURLWithPath: "/usr/sbin/screencapture")
screenshot.arguments = ["-x", "-l\\(number)", screenshotPath]
do {
    try screenshot.run()
    screenshot.waitUntilExit()
} catch {
    let record = CaptureRecord(schema: "lifeos.p3-143.native-pid-ax-capture.v1", directPid: pid, bundlePath: bundlePath, exactTitle: exactTitle, axTrusted: trusted, titleMatched: true, windowRole: windowRole, windowFrame: windowFrame, webRoles: webRoles, screenshotPath: nil, screenshotOwnerPid: pid, screenshotWindowId: number, result: "PAUSED_RESUMABLE", failure: "target-only screenshot API unavailable", boundaryNote: "Only bundle identity, exact title, AX roles and exact-PID geometry were queried; no UI content, credential, provider, network or personal data was accessed.")
    writeRecord(record, to: recordPath)
    exit(5)
}
guard screenshot.terminationStatus == 0, FileManager.default.fileExists(atPath: screenshotPath) else {
    let record = CaptureRecord(schema: "lifeos.p3-143.native-pid-ax-capture.v1", directPid: pid, bundlePath: bundlePath, exactTitle: exactTitle, axTrusted: trusted, titleMatched: true, windowRole: windowRole, windowFrame: windowFrame, webRoles: webRoles, screenshotPath: nil, screenshotOwnerPid: pid, screenshotWindowId: number, result: "PAUSED_RESUMABLE", failure: "target-only screenshot write failed", boundaryNote: "Only bundle identity, exact title, AX roles and exact-PID geometry were queried; no UI content, credential, provider, network or personal data was accessed.")
    writeRecord(record, to: recordPath)
    exit(6)
}

let isPass = windowRole == "AXWindow" && !webRoles.isEmpty
let record = CaptureRecord(schema: "lifeos.p3-143.native-pid-ax-capture.v1", directPid: pid, bundlePath: bundlePath, exactTitle: exactTitle, axTrusted: trusted, titleMatched: true, windowRole: windowRole, windowFrame: windowFrame, webRoles: webRoles, screenshotPath: screenshotPath, screenshotOwnerPid: pid, screenshotWindowId: number, result: isPass ? "PASS" : "PAUSED_RESUMABLE", failure: isPass ? nil : "AXWebView/AXWebArea absent from exact-title window", boundaryNote: "Only bundle identity, exact title, AX roles and exact-PID geometry were queried; no UI content, credential, provider, network or personal data was accessed.")
writeRecord(record, to: recordPath)
exit(isPass ? 0 : 7)
