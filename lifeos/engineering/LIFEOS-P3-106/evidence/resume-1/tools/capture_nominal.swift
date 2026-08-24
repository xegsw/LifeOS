import CoreGraphics
import Darwin
import Foundation
import ImageIO
import UniformTypeIdentifiers

// CGWindowListCreateImage is runtime-available but marked unavailable in the
// current SDK. Calling the system symbol with kCGWindowImageNominalResolution
// captures the real window at logical point resolution; it does not resize,
// pad, composite, or post-process a Retina backing image.
typealias CaptureFunction = @convention(c) (
    CGRect,
    UInt32,
    UInt32,
    UInt32
) -> Unmanaged<CGImage>?

guard CommandLine.arguments.count == 3,
      let windowID = UInt32(CommandLine.arguments[1]) else {
    fatalError("usage: capture_nominal.swift WINDOW_ID OUTPUT.png")
}

guard let handle = dlopen(
    "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics",
    RTLD_LAZY
), let symbol = dlsym(handle, "CGWindowListCreateImage") else {
    fatalError("CGWindowListCreateImage runtime symbol unavailable")
}

let capture = unsafeBitCast(symbol, to: CaptureFunction.self)
let optionIncludingWindow = CGWindowListOption.optionIncludingWindow.rawValue
let imageOptions = CGWindowImageOption.boundsIgnoreFraming.rawValue
    | CGWindowImageOption.nominalResolution.rawValue

guard let unmanaged = capture(.null, optionIncludingWindow, windowID, imageOptions) else {
    fatalError("window capture failed")
}
let image = unmanaged.takeRetainedValue()
guard image.width == 1280, image.height == 1024 else {
    fatalError("unexpected nominal canvas: \(image.width)x\(image.height)")
}

let output = URL(fileURLWithPath: CommandLine.arguments[2]) as CFURL
guard let destination = CGImageDestinationCreateWithURL(
    output,
    UTType.png.identifier as CFString,
    1,
    nil
) else {
    fatalError("cannot create PNG destination")
}
CGImageDestinationAddImage(destination, image, nil)
guard CGImageDestinationFinalize(destination) else {
    fatalError("cannot finalize PNG")
}

print("window_id=\(windowID) width=\(image.width) height=\(image.height) output=\(CommandLine.arguments[2])")
