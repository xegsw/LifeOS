import Foundation
let name=CommandLine.arguments[1]
guard name.range(of:"^[a-z0-9-]+$",options:.regularExpression) != nil else {exit(2)}
let root=URL(fileURLWithPath:"/private/tmp/lifeos-p3-147-obsidian-source-v1/fixtures/").appendingPathComponent(name,isDirectory:true)
for (target,alias) in [("target.txt","file.alias"),("folder","dir.alias")] {
 let source=root.appendingPathComponent(target)
 let data=try source.bookmarkData(options:.suitableForBookmarkFile,includingResourceValuesForKeys:[.pathKey],relativeTo:nil)
 try data.write(to:root.appendingPathComponent(alias),options:.withoutOverwriting)
}
