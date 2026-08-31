import ApplicationServices
import Foundation

struct Point: Encodable { let x: CGFloat; let y: CGFloat }
struct Size: Encodable { let width: CGFloat; let height: CGFloat }
struct Frame: Encodable { let position: Point?; let size: Size? }
struct Window: Encodable { let role: String?; let title: String?; let frame: Frame }
struct WebNode: Encodable { let role: String?; let frame: Frame }
struct Probe: Encodable {
  let schema = "lifeos.p3-141.mode-delete.direct-pid-ax.v1"
  let pid: Int32
  let manualAccessibilityResult: Int32
  let windows: [Window]
  let webNodes: [WebNode]
}

func value(_ element: AXUIElement, _ attribute: String) -> CFTypeRef? {
  var result: CFTypeRef?
  return AXUIElementCopyAttributeValue(element, attribute as CFString, &result) == .success ? result : nil
}
func string(_ element: AXUIElement, _ attribute: String) -> String? { value(element, attribute) as? String }
func children(_ element: AXUIElement) -> [AXUIElement] { (value(element, kAXChildrenAttribute) as? [AXUIElement]) ?? [] }
func descendants(_ element: AXUIElement) -> [AXUIElement] {
  var queue = children(element), result: [AXUIElement] = []
  while !queue.isEmpty && result.count < 4096 { let next = queue.removeFirst(); result.append(next); queue.append(contentsOf: children(next)) }
  return result
}
func frame(_ element: AXUIElement) -> Frame {
  func point() -> Point? { guard let raw = value(element, kAXPositionAttribute) else { return nil }; let box = unsafeBitCast(raw, to: AXValue.self); var point = CGPoint.zero; return AXValueGetValue(box, .cgPoint, &point) ? Point(x: point.x, y: point.y) : nil }
  func size() -> Size? { guard let raw = value(element, kAXSizeAttribute) else { return nil }; let box = unsafeBitCast(raw, to: AXValue.self); var size = CGSize.zero; return AXValueGetValue(box, .cgSize, &size) ? Size(width: size.width, height: size.height) : nil }
  return Frame(position: point(), size: size())
}

guard CommandLine.arguments.count == 2, let pid = Int32(CommandLine.arguments[1]) else { exit(64) }
let app = AXUIElementCreateApplication(pid)
let expectedTitle = "LifeOS · P3-141 Controlled Pilot Candidate"
let manual = AXUIElementSetAttributeValue(app, "AXManualAccessibility" as CFString, kCFBooleanTrue)
usleep(400_000)
var windows = ((value(app, kAXWindowsAttribute) as? [AXUIElement]) ?? [])
windows.append(contentsOf: descendants(app).filter { string($0, kAXRoleAttribute) == "AXWindow" })
var unique: [AXUIElement] = []
for window in windows where string(window, kAXRoleAttribute) == "AXWindow" && string(window, kAXTitleAttribute) == expectedTitle && !unique.contains(where: { CFEqual($0, window) }) { unique.append(window) }
let webNodes = unique.flatMap { descendants($0).filter { ["AXWebArea", "AXWebView"].contains(string($0, kAXRoleAttribute) ?? "") } }
let output = Probe(pid: pid, manualAccessibilityResult: manual.rawValue, windows: unique.map { Window(role: string($0, kAXRoleAttribute), title: string($0, kAXTitleAttribute), frame: frame($0)) }, webNodes: webNodes.map { WebNode(role: string($0, kAXRoleAttribute), frame: frame($0)) })
let encoder = JSONEncoder(); encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
FileHandle.standardOutput.write(try! encoder.encode(output)); FileHandle.standardOutput.write(Data("\n".utf8))
exit(unique.count == 1 && !webNodes.isEmpty ? 0 : 2)
