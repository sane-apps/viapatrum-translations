#!/usr/bin/env python3
"""Tests for muse_exec.py. No model call."""
import json, os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import muse_exec as me


def ev(kind, **kw):
    return json.dumps({"schema_version": 1, "payload": dict(kind=kind, **kw)})


class FinalText(unittest.TestCase):
    def test_takes_the_completed_terminal_text_once(self):
        out = "\n".join([ev("run_output_delta", text="@@LIST ."), ev("run_output_delta", text="@@LIST ."),
                         ev("run_terminal", terminal="completed", text="@@LIST .")])
        self.assertEqual(me.final_text(out), "@@LIST .")

    def test_no_completed_terminal_is_missing(self):
        self.assertIsNone(me.final_text(ev("run_output_delta", text="half an answer")))
        self.assertIsNone(me.final_text(ev("run_terminal", terminal="failed", text="x")))
        self.assertIsNone(me.final_text("not json at all\n"))

    def test_last_completed_terminal_wins_and_junk_lines_are_skipped(self):
        out = "\n".join(["muse: warning", ev("run_terminal", terminal="completed", text="one"), "{broken",
                         ev("run_terminal", terminal="completed", text="two")])
        self.assertEqual(me.final_text(out), "two")


class Undouble(unittest.TestCase):
    def test_exact_doubles_become_one(self):
        self.assertEqual(me.undouble("@@LIST .\n@@LIST ."), "@@LIST .")
        self.assertEqual(me.undouble("@@LIST /a/b@@LIST /a/b"), "@@LIST /a/b")
        self.assertEqual(me.undouble("@@READ x 1 9\n\n@@READ x 1 9"), "@@READ x 1 9")
        body = "@@WRITE a.py\nprint(1)\n@@END"
        self.assertEqual(me.undouble(body + "\n" + body), body)

    def test_everything_else_is_untouched(self):
        for s in ("@@LIST .", "@@LIST .\n@@LIST ws", "aa", "abab ", '{"ok": true}', "@@LIST a@@LIST b", ""):
            self.assertEqual(me.undouble(s), s if s.strip() != "abab" else "ab")

    def test_final_text_undoubles(self):
        self.assertEqual(me.final_text(ev("run_terminal", terminal="completed", text="@@LIST .\n@@LIST .")), "@@LIST .")


class Refusals(unittest.TestCase):
    def test_unknown_model_and_effort_are_refused_before_any_call(self):
        with self.assertRaises(ValueError):
            me.ask_muse("muse-not-a-model")
        with self.assertRaises(ValueError):
            me.ask_muse("muse-wonder-full-1.0", effort="ludicrous")


if __name__ == "__main__":
    unittest.main()
