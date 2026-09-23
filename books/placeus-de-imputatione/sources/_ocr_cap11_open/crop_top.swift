import Foundation
import AppKit
let src = CommandLine.arguments[1]
let dest = CommandLine.arguments[2]
let keep = Double(CommandLine.arguments[3])!
guard let img = NSImage(contentsOfFile: src), let tiff = img.tiffRepresentation,
      let rep = NSBitmapImageRep(data: tiff), let cg = rep.cgImage else { exit(1) }
let w = cg.width, h = cg.height
let hh = Int(Double(h) * keep)
let cropped = cg.cropping(to: CGRect(x: 0, y: 0, width: w, height: hh))!
let out = NSBitmapImageRep(cgImage: cropped)
let png = out.representation(using: .png, properties: [:])!
try! png.write(to: URL(fileURLWithPath: dest))
print("wrote", dest, cropped.width, cropped.height)
