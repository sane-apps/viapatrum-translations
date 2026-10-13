# Fix notes — clause-by-clause reread against the locked Greek (Origen, Homilies on Job)

Date: 2026-10-09. Gate: dual-family clause-aligned review (Workers AI kimi-k2.6 + glm-5.2).
Sections reviewed: 11. Sections with corrections: 10. Corrections applied: 26.
Sections whose remaining flags were adjudicated as false positives (bound to lane response_ids): 10.
Every changed section was re-gated; receipts and adjudications are in reviews/audit/reread_20261009_<section>.*.json.

Scripture references follow the work's convention: LXX numbering first, English numbering in square brackets.
Locked Greek unchanged: the reread only re-chunked the sections (whole-work Greek text verified identical).

## u01-open

- Old: Chapter 13, verse 28: "He grows old like a flower that has bloomed and fallen, or like a shadow that passes away and will not stand."
  New: Chapter 13, verse 28: "He grows old like a wineskin, or like a moth-eaten garment."
  Why: The lemma is Ὃ παλαιοῦται ἴσα ἀσκῷ, ἢ ὥσπερ ἱμάτιον σητόβρωτον (Job 13:28). The English had put in Job 14:2 (flower/shadow), which follows separately as 14:1–2.

## u01-rem-close

- Old: and you caused the dwellers on the earth to be put to sleep.
  New: and you settled those who are on the earth.
  Why: ᾤκισας δὲ τοὺς ἐπὶ τῆς γῆς (Job 22:8) is 'you settled', and the commentary itself treats 'put to sleep' (ἐκοίμησας) as a variant found in some copies.

- Old: “You caused the dwellers on the earth to be put to sleep.” Some copies have “you put to sleep” instead of “you caused to dwell,”
  New: “You settled those who are on the earth.” Some copies have “you put to sleep” instead of “you settled,”
  Why: Ὤικισας δὲ τοὺς ἐπὶ τῆς γῆς is the lemma; ἐκοίμησας is given as the variant.

## u01-rem-early

- Old: By “mountains” there he means the hills,
  New: By “heaps” there he means the hills,
  Why: Θῖνας (θίς, 'heap, dune') is the lemma word being explained; the English had 'mountains', which is not in the Greek.

- Old: and defending me against those responsible,
  New: and punishing those responsible,
  Why: τοὺς αἰτίους ἀμυνόμενος: middle ἀμύνομαι with the guilty as object means 'requiting, punishing', not 'defending me against'.

- Old: then he will see it being transferred to others.
  New: then he will see himself transferred to others.
  Why: τότ' αὑτὸν εἰς ἑτέρους μεταφερόμενον ὄψεται: reflexive αὑτόν, 'himself'.

- Old: “Like nightshade unchewed, undrinkable.”
  New: “Like tough gristle, unchewed, not to be swallowed.”
  Why: Ὥσπερ στρείφνος (στρίφνος, 'tough, hard meat') ἀμάσητος, ἀκατάποτος. It is not nightshade (στρύχνος), and ἀκατάποτος means 'not to be swallowed'.

- Old: and it is not passed on to descendants.
  New: and it is not passed on to descendants [Greek προγόνους, literally 'forebears'].
  Why: εἰς προγόνους οὐ παραπέμπεται: the context requires heirs, but the Greek word is 'forebears', so this is now flagged rather than silently normalised.

- Old: This means: Terrors will come upon him from God and from heaven.
  New: This means: He will undergo terrors from God and from heaven.
  Why: ἐκ Θεοῦ καὶ ἐξ οὐρανοῦ ὑποστήσεται δεινά: the wicked man is the subject; he 'will undergo' terrible things.

## u01-rem-mid

- Old: or the one who is otherwise impious, however he may be impious,
  New: or the one who is impious in some strange way, or however he may be impious,
  Why: εἴτε τοῦ παραδόξου, εἴθ' ὅπως ποτὲ ἀσεβοῦς: παράδοξος is 'strange, unexpected', not 'otherwise'.

## u02-open

- Old: From Severus, from the letter to Juliana the deacon.
  New: From Severus, from the letter to Juliana the deaconess.
  Why: πρὸς Ἰουλιανὴν διάκονον: διάκονος here is feminine (Juliana), so 'deaconess'.

## u02-rem-close

- Old: do not flee from their adversaries, but let the victory come from that abundance.
  New: do not even shun their adversaries but give them free rein, so that the victory may come out of that abundance.
  Why: οὐδὲ φεύγοντες τοὺς ἀντιδίκους, ἀφίασιν, ὥστε ἐκ περιουσίας γενέσθαι τὴν νίκην: ἀφίασιν ('they let them go, give way') was not rendered, and ὥστε is result.

- Old: calling the permission an "utterance"
  New: calling the permission a "dealing"
  Why: χρηματισμὸν τὴν συγχώρησιν λέγων takes up the same χρηματισμός rendered 'dealing' just before (κεχρηματικέναι, 'dealt with you', Job 40:3); this keeps the term consistent.

- Old: He will deliver them" (Psalm 34:7).
  New: He will deliver them" (Psalm 33:8 [34:7]).
  Why: LXX Ps 33:8 = Eng 34:7; Job bracket convention

- Old: "The stone which the builders rejected has become the head of the corner" (Psalm 118:22)
  New: "The stone which they rejected has become the head of the corner" (Psalm 117:22 [118:22])
  Why: Greek ὃν ἀπεδοκίμασαν has no 'builders'; LXX Ps 117:22

- Old: "Why am I still judged," he says, "as a prelude?"
  New: "Why am I still judged," he says, "as a prelude?" And from the beginning he yielded the first place.
  Why: restore omitted καὶ ἐξ ἀρχῆς παρεχώρησε τῶν πρωτείων

## u02-rem-early

- Old: The Lord shattered the jaws of the lions, and it is written in the prophet: “I snatched the prey from their teeth” (Psalm 57:7).
  New: The Lord shattered the jaws of the lions (Psalm 57:7 [58:6]), and it is written in the prophet: “I snatched the prey from their teeth.”
  Why: Ps 57:7 LXX is τὰς μύλας τῶν λεόντων συνέθλασεν κύριος. The reference had been attached to the other quotation (Ἐκ μέσου ὀδόντων αὐτῶν ἅρπαγμα ἐξήρπασα), which is not Ps 57.

- Old: (Job 31:5–6)
  New: (Job 31:6–7)
  Why: The edition marks ΛΑʹ, ʹ, ζʹ: 'I stand in a just balance' is 31:6 and 'if my foot has turned aside' is 31:7.

## u02-rem-mid

- Old: “Look up to heaven” (Job 35:4).
  New: “Look up to heaven” (Job 35:5).
  Why: The edition marks it Κεφ. ΛΕʹ, εʹ, and Ἀνάβλεψον εἰς τὸν οὐρανόν is Job 35:5.

- Old: “If you have sinned, what will you do?” (Job 35:5).
  New: “If you have sinned, what will you do?” (Job 35:6).
  Why: Εἰ ἥμαρτες, τί πράξεις; is Job 35:6, where the verse numeral (ϛʹ) has dropped out of the OCR.

- Old: “I will speak, so that I may rest, opening my lips” (Job 33:3).
  New: “I will speak, so that I may rest, opening my lips” (Job 32:20).
  Why: Λαλήσω, ἵνα ἀναπαύσωμαι ἀνοίξας τὰ χείλη is Job 32:20, marked κʹ in the edition. Job 33:3 is a different verse.

- Old: Since I had become withered and beaten down,
  New: Since I had become hardened and austere,
  Why: κατεσκληκὼς … καὶ κατεστυμμένος: 'dried hard, toughened' and 'made austere, grave', the opposite of the jesting life just mentioned.

- Old: I will not proceed unhindered;
  New: I will not hold back, [but will go on] unhindered;
  Why: Symmachus' οὐχ ἕξω ἀκωλύτως is glossed by the commentator as οὐκ ἐπέχω, ἀλλ' ἀκωλύτως ἐπεξέρχομαι ('I do not hold back, but proceed unhindered'); the English had reversed it to 'I will not proceed unhindered'.

- Old: (Psalm 36:9 (LXX 35:10))
  New: (Psalm 35:10 [36:9])
  Why: LXX numbering first with the English in brackets, as elsewhere in this work (e.g. Psalm 57:7 [58:6]).

## u03-open

- Old: but that I am great, and no one can do what I do.
  New: but that I am great, and he cannot do what I do.
  Why: καὶ οὐ δύναται ἅπερ ἐγώ: 'he cannot (do) what I (can)', not 'no one'.

## u03-rem-mid

- Old: God therefore gave him the same number of children again,
  New: God therefore gave him as many other children,
  Why: ἕτερα τοσοῦτα τέκνα: other children, equal in number.
