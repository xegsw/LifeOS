import AppKit
import Foundation

// Evidence helper: activate only the caller-supplied, already recorded launch PID.
// It performs no app/window discovery and is intentionally unsuitable for global search.
guard CommandLine.arguments.count == 2,
      let rawPid = Int32(CommandLine.arguments[1]), rawPid > 0,
      let application = NSRunningApplication(processIdentifier: rawPid) else {
    FileHandle.standardError.write(Data("usage: focus_direct_pid <positive-direct-pid>\n".utf8))
    exit(64)
}

let activated = application.activate(options: [.activateIgnoringOtherApps])
if !activated {
    FileHandle.standardError.write(Data("failed to activate direct pid\n".utf8))
    exit(65)
}
print("activated_direct_pid=\(rawPid)")
