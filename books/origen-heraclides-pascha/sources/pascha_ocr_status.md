# On Pascha — OCR status (Witte 1993)

**Verdict (2026-09-11):** first-pass **image transcription** of Witte’s Greek is in `translations/pascha_source.json`. Do **not** treat it as `source_verified`. Do not write English from tesseract. Do not invent papyrus. Do not copy Daly.

Tesseract remains unusable. The recoverable source is still the **page images**.

## What is locked

| File | Role |
|------|------|
| `pascha_witte.pdf` | 262 pp. Bernd Witte, *Die Schrift des Origenes „Über das Passa“* (Altenberge: Oros, 1993). IA: https://archive.org/details/Witte02OrigenesUeberDasPassaK |
| `witte_pages/p-092.png` … `p-160.png` | 300 dpi `pdftoppm` of PDF 92–160 (69 PNGs). Greek is even PDF 92–152. |
| `pascha_witte_greek_ocr.txt` | tesseract `grc+eng` of PDF pp. 92–160. Dirty. Do not translate from this. |
| `pascha_witte_djvu.txt` | IA DJVU text. German + Latin-script garbage. Not a Greek witness. |
| `pascha_witte_pdftotext.txt` | **0 Greek letters** in the running text. Headings extract; body does not. |
| `translations/pascha_source.json` | First-pass transcription: Book I §§1–114 + Book II §§1–35 (**149** records). |

PDF even pages 92–152 are **JPEG XObjects** (~1040×744, ~126 dpi), two per page. 300 dpi render does not add lost letter information; it only makes Witte’s typeset Greek easier to read.

## This pass (2026-09-11)

Transcribed from `witte_pages/` PNGs, not from tesseract and not from Daly.

| Item | Count |
|------|-------|
| Witte numbered paragraphs transcribed | **149 / 149** (`1.1`–`1.114`, `2.1`–`2.35`) |
| Remaining untranscribed numbered §§ | **0** |
| Greek image pages covered | 31 (PDF even 92–152 = Witte print 88–148) |
| `source_verified` | **no** — first pass only |
| Transcribed range | Book I **§§1–114**; Book II **§§1–35** |

Kept as Witte printed them: `[restorations]`, unrestored `[ ... ]` / dotted gaps, `<insertions>`, `{deletions}`, `σ(ωτῆ)ρ(ο)ς` expansions, `||` papyrus page breaks. Apparatus under `P.` stayed out of `greek[]`.

### Hard pages (image-only remnants inside the JSON)

These records exist but the **papyrus** is lost or dotted; the JSON copies Witte’s printed gaps, it does not fill them:

- **1.22, 1.26, 1.29, 1.32, 1.35, 1.39, 1.45, 1.48, 1.53, 1.58–1.62, 1.65–1.66, 1.82, 1.86, 1.95, 1.98–1.99** — printed dots / `L. ca. N Z.`
- **1.94** — Greek lost; Witte prints **Victor of Capua’s Latin**. Left in Latin. Not invented Greek.
- **Witte p.112 / PDF 116** (§§63–67) — lacunose page (`1 L. ca. 15 Z.`, `15–16 L. ca. 11 Z.`)
- **Witte p.116 lower half / PDF 120c** — blank Greek; lemma restorations from catenae/Procopius as Witte bracketed them

A second letter-by-letter pass against the same PNGs is still required before `source_verified`.

## Guéraud–Nautin 1979 vs Witte 1993

Unchanged: charter lock is **Witte’s continuous Greek**. Daly ACW 54 (1992) translates Guéraud–Nautin. Copyrighted. Do not copy.

## Section map (Witte)

Locus: Witte § in the right margin. Book I **§§1–114**; Book II **§§1–35**. JSON `section` ids: `"1.1"` … `"1.114"`, `"2.1"` … `"2.35"`. `witte` is that paragraph number. `head` is the editorial subsection (English labels for the map).

Book I ends Witte p. 132 with `Ὠ(ριγένους) [πε]ρὶ πάσχα ᾱ`. Book II is marked `β` and ends p. 148 with `Ὠριγένους περὶ πάσχα ᾱ β`.

## Next

1. Second pass of `pascha_source.json` against the same page images; then `source_verified`.
2. Then translate. Not before.
