# Held sections: help wanted

Each file here is one section of a translation that is held from publication:
automated checkers and a Claude review could not settle it. Most sit on a
corrupt or ambiguous Greek or Latin source, or need a judgment a careful reader
should make.

How to fix one (people and AI assistants alike):
1. Pick a file (or its GitHub issue, labelled `held-section`).
2. Read `source` (the locked Greek or Latin) and `english` (the current text),
   then `findings`: what the checkers objected to and the reviewer's note.
3. Edit only the `english` list in that file. Faithful AND readable modern
   English: every claim, negation and Scripture reference kept, nothing added.
   Where the source is corrupt, translate what is there and mark a guess with
   square brackets, e.g. "[perhaps: set them free]".
4. Explain your reading in the pull request (cite the source words).
Do not edit `source`, and do not copy any existing English translation.

After a maintainer merges the pull request, the pipeline imports the new
English, checks it, and re-reads the whole work before anything is published.
