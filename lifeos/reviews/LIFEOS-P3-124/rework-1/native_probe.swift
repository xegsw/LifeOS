import AppKit
import CoreGraphics
import Foundation

struct WindowRecord: Codable {
    let windowNumber: Int
    let ownerPID: Int32
    let ownerName: String
    let layer: Int
    let alpha: Double
    let bounds: [String: Double]
}

struct ProcessRecord: Codable {
    let pid: Int32
    let bundleIdentifier: String?
    let executablePath: String?
    let localizedName: String?
}

struct ProbeResult: Codable {
    let bundleIdentifier: String
    let expectedBundlePath: String
    let bundleIdentifierProcesses: [ProcessRecord]
    let matchingProcesses: [ProcessRecord]
    let matchingWindows: [WindowRecord]
    let exactProcessCount: Int
    let exactWindowCount: Int
    let bindingPass: Bool
    let generatedAt: String
}

guard CommandLine.arguments.count == 3 else {
    fputs("usage: native_probe <bundle-id> <task-local-app-path>\n", stderr)
    exit(64)
}

let targetBundleID = CommandLine.arguments[1]
let expectedBundlePath = URL(fileURLWithPath: CommandLine.arguments[2]).standardizedFileURL.path
let bundleIdentifierApps = NSWorkspace.shared.runningApplications.filter { app in
    app.bundleIdentifier == targetBundleID
}
let matchingApps = bundleIdentifierApps.filter { app in
    app.bundleURL?.standardizedFileURL.path == expectedBundlePath
}

func processRecord(_ app: NSRunningApplication) -> ProcessRecord {
    ProcessRecord(
        pid: app.processIdentifier,
        bundleIdentifier: app.bundleIdentifier,
        executablePath: app.executableURL?.standardizedFileURL.path,
        localizedName: app.localizedName
    )
}
let bundleIdentifierProcessRecords = bundleIdentifierApps.map(processRecord)
let processRecords = matchingApps.map(processRecord)
let matchingPIDs = Set(matchingApps.map { $0.processIdentifier })
let rawWindows = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]] ?? []
let windowRecords = rawWindows.compactMap { info -> WindowRecord? in
    guard
        let ownerPIDNumber = info[kCGWindowOwnerPID as String] as? NSNumber,
        matchingPIDs.contains(ownerPIDNumber.int32Value),
        let windowNumber = info[kCGWindowNumber as String] as? NSNumber,
        let layer = info[kCGWindowLayer as String] as? NSNumber,
        let alpha = info[kCGWindowAlpha as String] as? NSNumber,
        let bounds = info[kCGWindowBounds as String] as? [String: Any],
        let x = bounds["X"] as? NSNumber,
        let y = bounds["Y"] as? NSNumber,
        let width = bounds["Width"] as? NSNumber,
        let height = bounds["Height"] as? NSNumber,
        width.doubleValue > 0,
        height.doubleValue > 0,
        layer.intValue == 0,
        alpha.doubleValue > 0
    else { return nil }

    return WindowRecord(
        windowNumber: windowNumber.intValue,
        ownerPID: ownerPIDNumber.int32Value,
        ownerName: (info[kCGWindowOwnerName as String] as? String) ?? "",
        layer: layer.intValue,
        alpha: alpha.doubleValue,
        bounds: ["x": x.doubleValue, "y": y.doubleValue, "width": width.doubleValue, "height": height.doubleValue]
    )
}

let result = ProbeResult(
    bundleIdentifier: targetBundleID,
    expectedBundlePath: expectedBundlePath,
    bundleIdentifierProcesses: bundleIdentifierProcessRecords,
    matchingProcesses: processRecords,
    matchingWindows: windowRecords,
    exactProcessCount: processRecords.count,
    exactWindowCount: windowRecords.count,
    bindingPass: processRecords.count == 1 && windowRecords.count == 1,
    generatedAt: ISO8601DateFormatter().string(from: Date())
)
let encoder = JSONEncoder()
encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
FileHandle.standardOutput.write(try encoder.encode(result))
FileHandle.standardOutput.write(Data([0x0a]))
