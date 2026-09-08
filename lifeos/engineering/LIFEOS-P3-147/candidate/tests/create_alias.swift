import Foundation
let name=CommandLine.arguments[1]
guard name.range(of:"^[a-z0-9-]+$",options:.regularExpression) != nil else {exit(2)}
let profilesURL=URL(fileURLWithPath:#filePath).deletingLastPathComponent().deletingLastPathComponent().appendingPathComponent("root_profiles.json")
guard let profile=ProcessInfo.processInfo.environment["LIFEOS_P3_147_BUILD_PROFILE"], ["engineering","independent-review"].contains(profile) else {exit(2)}
let profiles=try JSONSerialization.jsonObject(with:Data(contentsOf:profilesURL)) as! [String:[String:Any]]
let spec=profiles[profile]!
let base=URL(fileURLWithPath:spec["root"] as! String,isDirectory:true)
let marker=try JSONSerialization.jsonObject(with:Data(contentsOf:base.appendingPathComponent(".lifeos-p3-147-owner.json"))) as! NSDictionary
guard marker.isEqual(to:spec["marker"] as! [AnyHashable:Any]) else {exit(2)}
let root=base.appendingPathComponent("fixtures",isDirectory:true).appendingPathComponent(name,isDirectory:true)
for (target,alias) in [("target.txt","file.alias"),("folder","dir.alias")] {
 let source=root.appendingPathComponent(target)
 let data=try source.bookmarkData(options:.suitableForBookmarkFile,includingResourceValuesForKeys:[.pathKey],relativeTo:nil)
 try data.write(to:root.appendingPathComponent(alias),options:.withoutOverwriting)
}
