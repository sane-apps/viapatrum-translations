import Foundation
import Vision
import AppKit

guard CommandLine.arguments.count > 1 else {
    fputs("usage: vision_ocr <image>\n", stderr)
    exit(1)
}
let path = CommandLine.arguments[1]
guard let img = NSImage(contentsOfFile: path),
      let tiff = img.tiffRepresentation,
      let ci = CIImage(data: tiff) else {
    fputs("cannot load \(path)\n", stderr)
    exit(2)
}
let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = true
request.recognitionLanguages = ["la", "en", "de"]
let handler = VNImageRequestHandler(ciImage: ci, options: [:])
try handler.perform([request])
let observations = request.results ?? []
for obs in observations {
    if let cand = obs.topCandidates(1).first {
        print(cand.string)
    }
}
