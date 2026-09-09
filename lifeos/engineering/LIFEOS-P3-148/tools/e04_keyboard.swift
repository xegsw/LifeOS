import Cocoa
import ApplicationServices
let a=CommandLine.arguments
guard a.count>=3,let pid=pid_t(a[1]) else{exit(2)}
func attr(_ e:AXUIElement,_ key:String)->AnyObject?{var v:CFTypeRef?;return AXUIElementCopyAttributeValue(e,key as CFString,&v) == .success ? v:nil}
let app=AXUIElementCreateApplication(pid)
guard let w=attr(app,kAXWindowsAttribute) as? [AXUIElement],w.count==1,attr(w[0],kAXTitleAttribute) as? String == "LifeOS P3-148 - Synthetic Offline" else{exit(3)}
NSRunningApplication(processIdentifier:pid)?.activate(options:[.activateIgnoringOtherApps])
if a[2]=="focus" {
 func nodes(_ e:AXUIElement)->[AXUIElement]{[e]+(attr(e,kAXChildrenAttribute) as? [AXUIElement] ?? []).flatMap{nodes($0)}}
 let fields=nodes(w[0]).filter{attr($0,kAXRoleAttribute) as? String == "AXTextArea"}
 guard fields.count==1,let pv=attr(fields[0],kAXPositionAttribute),let sv=attr(fields[0],kAXSizeAttribute) else{exit(6)}
 var point=CGPoint.zero;var size=CGSize.zero;AXValueGetValue(pv as! AXValue,.cgPoint,&point);AXValueGetValue(sv as! AXValue,.cgSize,&size)
 guard NSWorkspace.shared.frontmostApplication?.processIdentifier == pid else{exit(5)}
 let center=CGPoint(x:point.x+size.width/2,y:point.y+size.height/2)
 for type in [CGEventType.leftMouseDown,CGEventType.leftMouseUp]{CGEvent(mouseEventSource:nil,mouseType:type,mouseCursorPosition:center,mouseButton:.left)!.post(tap:.cghidEventTap)}
 print("clicked_bound_textarea");exit(0)
}
let keys:[String:CGKeyCode]=["enter":36,"tab":48,"escape":53,"left":123,"right":124]
guard let key=keys[a[2]] else{exit(4)}
guard NSWorkspace.shared.frontmostApplication?.processIdentifier == pid else{exit(5)}
for down in [true,false]{let event=CGEvent(keyboardEventSource:nil,virtualKey:key,keyDown:down)!;event.post(tap:.cghidEventTap)}
print("posted_to_bound_pid_\(pid)_\(a[2])")
