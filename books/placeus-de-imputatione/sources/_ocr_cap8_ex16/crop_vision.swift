import Foundation
import AppKit
import Vision
let args = CommandLine.arguments
guard args.count >= 6 else { fputs("usage: crop_vision in.png out.txt x y w h\n", stderr); exit(1) }
let img = NSImage(contentsOf: URL(fileURLWithPath: args[1]))!
let tiff = img.tiffRepresentation!
let rep = NSBitmapImageRep(data: tiff)!
let cg = rep.cgImage!
let x = Int(args[3])!, y = Int(args[4])!, w = Int(args[5])!, h = Int(args[6])!
let cropped = cg.cropping(to: CGRect(x: x, y: y, width: w, height: h))!
let req = VNRecognizeTextRequest(); req.recognitionLevel = .accurate; req.usesLanguageCorrection = true
req.recognitionLanguages = ["la","en","el"]
try! VNImageRequestHandler(cgImage: cropped, options: [:]).perform([req])
let lines = (req.results ?? []).compactMap { $0.topCandidates(1).first?.string }
try! (lines.joined(separator: "\n")+"\n").write(to: URL(fileURLWithPath: args[2]), atomically: true, encoding: .utf8)
print("wrote", args[2], "lines", lines.count)
