// Decode only archived bookmark metadata. Do not resolve, mount, or open its target.
import Foundation
let data=FileHandle.standardInput.readDataToEndOfFile()
guard data.count<=1024*1024,
      let values=NSURL.resourceValues(forKeys:[.pathKey],fromBookmarkData:data),
      let path=values[URLResourceKey.pathKey] as? String else {exit(2)}
FileHandle.standardOutput.write(Data(path.utf8))
