import Cocoa
import ApplicationServices
let a=CommandLine.arguments;guard a.count==2,let pid=pid_t(a[1]) else{exit(2)}
func attr(_ e:AXUIElement,_ k:String)->AnyObject?{var v:CFTypeRef?;return AXUIElementCopyAttributeValue(e,k as CFString,&v) == .success ? v:nil}
let app=AXUIElementCreateApplication(pid);guard let ws=attr(app,kAXWindowsAttribute) as? [AXUIElement],ws.count==1,attr(ws[0],kAXTitleAttribute) as? String == "LifeOS P3-148 - Synthetic Offline" else{exit(3)}
func nodes(_ e:AXUIElement)->[AXUIElement]{[e]+(attr(e,kAXChildrenAttribute) as? [AXUIElement] ?? []).flatMap{nodes($0)}}
var rows=[[String:Any]]()
for n in nodes(ws[0]){let role=attr(n,kAXRoleAttribute) as? String ?? "";let title=attr(n,kAXTitleAttribute) as? String ?? attr(n,kAXDescriptionAttribute) as? String ?? ""
 if role=="AXTextArea" || ["发送","确认发送","取消","返回对话"].contains(title){var row:[String:Any]=["role":role,"title":title];if let v=attr(n,kAXPositionAttribute){var p=CGPoint.zero;AXValueGetValue(v as! AXValue,.cgPoint,&p);row["x"]=p.x;row["y"]=p.y};if let v=attr(n,kAXSizeAttribute){var s=CGSize.zero;AXValueGetValue(v as! AXValue,.cgSize,&s);row["width"]=s.width;row["height"]=s.height};if role=="AXTextArea"{row["value"]=attr(n,kAXValueAttribute) as? String ?? "";if let v=attr(n,kAXSelectedTextRangeAttribute){var r=CFRange();AXValueGetValue(v as! AXValue,.cfRange,&r);row["selectionStart"]=r.location;row["selectionLength"]=r.length}};rows.append(row)}
}
let result:[String:Any]=["pid":pid,"window":"LifeOS P3-148 - Synthetic Offline","controls":rows]
print(String(data:try! JSONSerialization.data(withJSONObject:result,options:[.sortedKeys]),encoding:.utf8)!)
