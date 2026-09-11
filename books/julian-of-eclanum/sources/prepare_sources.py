import hashlib
import html
import json
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class Paragraphs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.buf = None
        self.anchor = None
        self.suppress = 0
        self.notes = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'p':
            self.buf = []
            self.notes = []
        if tag == 'a' and attrs.get('name', '').startswith('JL_'):
            self.anchor = attrs['name']
        if tag == 'sup':
            self.suppress += 1
        if tag == 'a' and '_note.htm#' in attrs.get('href', '') and self.buf is not None:
            self.notes.append(attrs['href'])
            self.buf.append(' [n' + attrs['href'].split('#N')[-1] + '] ')

    def handle_endtag(self, tag):
        if tag == 'sup':
            self.suppress = max(0, self.suppress - 1)
        if tag == 'p' and self.buf is not None:
            text = re.sub(r'\s+', ' ', ''.join(self.buf)).strip()
            if self.anchor and text:
                self.rows.append((self.anchor, text, self.notes))
            self.buf = None

    def handle_data(self, data):
        if self.buf is not None and not self.suppress:
            self.buf.append(data)


def fetch(url, path):
    if not path.exists():
        req = urllib.request.Request(url, headers={'User-Agent': 'Personal scholarly reading'})
        path.write_bytes(urllib.request.urlopen(req, timeout=40).read())
    return path.read_bytes().decode('utf-8', errors='replace')


expected = [141, 236, 216, 136, 64, 41]
manifest = []
for book in range(1, 7):
    url = f'https://www.augustinus.it/latino/incompiuta_giuliano/incompiuta_giuliano_{book}_libro.htm'
    path = ROOT / f'ad_florum_{book}.html'
    parser = Paragraphs()
    parser.feed(fetch(url, path))
    notes_url = url.replace('_libro.htm', '_note.htm')
    notes_html = fetch(notes_url, ROOT / f'ad_florum_{book}_notes.html')
    note_map = {}
    for note_id, note_body in re.findall(r'NAME="N(\d+)"[^>]*>\d+</A>(.*?)</P>', notes_html, flags=re.I | re.S):
        note_map[note_id] = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', note_body))).strip(' -\r\n')
    sections = {}
    speaker = None
    for anchor, text, notes in parser.rows:
        section = int(anchor.split('_')[-1])
        entry = sections.setdefault(section, {'book': book, 'section': section, 'source': url+'#'+anchor, 'julian': [], 'augustine': [], 'notes': []})
        text = re.sub(r'^\d+\.\s*', '', text)
        # Latin web edition mislabels Julian's first paragraph at IV.108 as AUG.
        # Its Italian parallel labels GIUL.; the following reply addresses Julian.
        if book == 4 and section == 108 and text.startswith('AUG. Parvulos vero'):
            text = text.replace('AUG.', 'IUL.', 1)
            entry['editorial_note'] = 'Speaker corrected from AUG. to Julian at IV.108; checked against the Italian parallel, which reads GIUL., and the following reply.'
        # Full names inside a sentence are people, not speaker labels (IV.23/104).
        parts = re.split(r'\b(IUL|AUG|^IULIANUS|^AUGUSTINUS)\.\s*', text, flags=re.I)
        if parts[0].strip() and speaker:
            entry[speaker].append(parts[0].strip())
        for label, content in zip(parts[1::2], parts[2::2]):
            speaker = 'julian' if label.upper().startswith('IUL') else 'augustine'
            if content.strip():
                entry[speaker].append(content.strip())
        entry['notes'].extend(notes)
    rows = list(sections.values())
    for row in rows:
        note_ids = re.findall(r'\[n(\d+)\]', ' '.join(row['julian']))
        assert all(n in note_map for n in note_ids), (book, row['section'], note_ids)
        row['julian_source_notes'] = {n: note_map[n] for n in note_ids}
    (ROOT / f'ad_florum_{book}_notes.json').write_text(json.dumps(note_map, ensure_ascii=False, indent=2))
    assert sorted(sections) == list(range(1, expected[book-1]+1)), (book, sorted(sections))
    assert all(r['julian'] for r in rows), (book, [r['section'] for r in rows if not r['julian']])
    (ROOT / f'ad_florum_{book}.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2))
    julian_words = sum(len(' '.join(r['julian']).split()) for r in rows)
    manifest.append({'book':book,'sections':len(rows),'julian_latin_words':julian_words,'url':url,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    print(book, len(rows), julian_words, 'LAST:', rows[-1]['julian'][-1][-90:])
(ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2))
