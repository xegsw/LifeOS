import CoreGraphics
import Foundation
import ImageIO
import UniformTypeIdentifiers

guard CommandLine.arguments.count == 4 else {
    fatalError("usage: side_by_side.swift REFERENCE ACTUAL OUTPUT.png")
}

func load(_ path: String) -> CGImage {
    let url = URL(fileURLWithPath: path) as CFURL
    guard let source = CGImageSourceCreateWithURL(url, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        fatalError("cannot load \(path)")
    }
    guard image.width == 1280, image.height == 1024 else {
        fatalError("unexpected source size \(image.width)x\(image.height): \(path)")
    }
    return image
}

let reference = load(CommandLine.arguments[1])
let actual = load(CommandLine.arguments[2])
let colorSpace = CGColorSpaceCreateDeviceRGB()
guard let context = CGContext(
    data: nil,
    width: 2560,
    height: 1024,
    bitsPerComponent: 8,
    bytesPerRow: 0,
    space: colorSpace,
    bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
) else {
    fatalError("cannot create comparison context")
}

context.draw(reference, in: CGRect(x: 0, y: 0, width: 1280, height: 1024))
context.draw(actual, in: CGRect(x: 1280, y: 0, width: 1280, height: 1024))
guard let comparison = context.makeImage() else {
    fatalError("cannot create comparison image")
}

let output = URL(fileURLWithPath: CommandLine.arguments[3]) as CFURL
guard let destination = CGImageDestinationCreateWithURL(
    output,
    UTType.png.identifier as CFString,
    1,
    nil
) else {
    fatalError("cannot create output")
}
CGImageDestinationAddImage(destination, comparison, nil)
guard CGImageDestinationFinalize(destination) else {
    fatalError("cannot finalize output")
}
print("reference_left actual_right width=2560 height=1024 output=\(CommandLine.arguments[3])")
