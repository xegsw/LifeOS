import AppKit
import CoreGraphics
import Foundation

guard CommandLine.arguments.count == 4, let pid = Int32(CommandLine.arguments[1]) else {
            fputs("usage: capture_exact_pid_window <pid> <expected-title> <output.png>\n", stderr)
            exit(64)
}
let expectedTitle = CommandLine.arguments[2]
let output = URL(fileURLWithPath: CommandLine.arguments[3])
let windows = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]] ?? []
guard let matched = windows.first(where: { item in
    (item[kCGWindowOwnerPID as String] as? NSNumber)?.intValue == Int(pid)
        && (item[kCGWindowName as String] as? String) == expectedTitle
}), let windowNumber = matched[kCGWindowNumber as String] as? NSNumber else {
    fputs("exact PID/title CG window not found\n", stderr)
    exit(1)
}
guard let image = CGWindowListCreateImage(.null, .optionIncludingWindow, CGWindowID(windowNumber.uint32Value), [.boundsIgnoreFraming, .bestResolution]),
      let png = NSBitmapImageRep(cgImage: image).representation(using: .png, properties: [:]) else {
    fputs("target-only window capture unavailable\n", stderr)
    exit(1)
}
try png.write(to: output, options: [.atomic])
let bounds = matched[kCGWindowBounds as String] as? [String: Any] ?? [:]
let receipt: [String: Any] = [
    "schema": "lifeos.p3-144.independent-review.target-window-capture.v1",
    "pid": Int(pid),
    "expected_title": expectedTitle,
    "window_number": windowNumber,
    "bounds": bounds,
    "output": output.path,
    "capture_scope": "CGWindow exact PID/title only; desktop excluded"
]
let json = try JSONSerialization.data(withJSONObject: receipt, options: [.prettyPrinted, .sortedKeys])
FileHandle.standardOutput.write(json)
FileHandle.standardOutput.write(Data("\n".utf8))
