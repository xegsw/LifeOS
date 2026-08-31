import ApplicationServices
import Foundation

struct ResizeResult: Encodable {
  let schema = "lifeos.p3-141.mode-delete.direct-pid-window-size.v1"
  let pid: Int32
  let title: String?
  let requestedWidth: CGFloat
  let requestedHeight: CGFloat
  let observedWidth: CGFloat
  let observedHeight: CGFloat
}

func value(_ element: AXUIElement, _ attribute: String) -> CFTypeRef? {
  var result: CFTypeRef?
  return AXUIElementCopyAttributeValue(element, attribute as CFString, &result) == .success ? result : nil
}
func string(_ element: AXUIElement, _ attribute: String) -> String? { value(element, attribute) as? String }
func size(_ element: AXUIElement) -> CGSize? {
  guard let raw = value(element, kAXSizeAttribute) else { return nil }
  let box = unsafeBitCast(raw, to: AXValue.self)
  var result = CGSize.zero
  return AXValueGetValue(box, .cgSize, &result) ? result : nil
}

guard CommandLine.arguments.count == 4,
      let pid = Int32(CommandLine.arguments[1]),
      let width = Double(CommandLine.arguments[2]),
      let height = Double(CommandLine.arguments[3]) else { exit(64) }

let app = AXUIElementCreateApplication(pid)
guard let windows = value(app, kAXWindowsAttribute) as? [AXUIElement], windows.count == 1 else { exit(2) }
let window = windows[0]
guard string(window, kAXTitleAttribute) == "LifeOS · P3-141 Controlled Pilot Candidate" else { exit(3) }
var requested = CGSize(width: width, height: height)
guard let boxed = AXValueCreate(.cgSize, &requested), AXUIElementSetAttributeValue(window, kAXSizeAttribute as CFString, boxed) == .success else { exit(4) }
usleep(350_000)
guard let observed = size(window) else { exit(5) }
let result = ResizeResult(pid: pid, title: string(window, kAXTitleAttribute), requestedWidth: requested.width, requestedHeight: requested.height, observedWidth: observed.width, observedHeight: observed.height)
let encoder = JSONEncoder(); encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
FileHandle.standardOutput.write(try! encoder.encode(result)); FileHandle.standardOutput.write(Data("\n".utf8))
exit(abs(observed.width - requested.width) < 0.1 && abs(observed.height - requested.height) < 0.1 ? 0 : 6)
