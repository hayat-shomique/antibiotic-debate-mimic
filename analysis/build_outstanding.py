#!/usr/bin/env python3
"""Build OUTSTANDING.md from the swept supervisor asks.

Two copies are produced. The repository copy is redacted; the full copy stays in
the local working directory. Two classes are held back from the repository:

  personal   supervision arrangements, which are nobody's business but his
  personnel  anything naming a third party in connection with conduct, which has
             no place in a research repository whoever the third party is

Everything else, including verbatim instructions from the supervisor about the
science, belongs in the record and is kept.
"""
import json, collections, os, re, sys

SRC = os.environ.get("SWEEP_ASKS") or os.path.expanduser("~/brain_run/_sweep_asks.json")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PERSONAL = re.compile(r"support plan|reasonable adjustment|adhd|disabilit|dyslex|mental health", re.I)
PERSONNEL = re.compile(r"removed .{0,20}from our chat|misconduct|without authoris|without permission|"
                       r"unauthoris|plagiar|Dr\s+[A-Z][a-z]+\s+[A-Z][a-z]+|incident", re.I)


def who_of(a):
    w = (a.get("who") or "?").strip()
    for n in ("Zhu", "Zhikang", "Chen"):
        if w.startswith(n):
            return "Zhikang" if n in ("Zhikang", "Chen") else n
    return "standing orders and protocol"


def build(asks, redact):
    order = {"OUTSTANDING": 0, "PARTIAL": 1}
    sel = [a for a in asks if (a.get("status") or "").strip() in order]
    sel.sort(key=lambda a: (order[(a.get("status") or "").strip()], who_of(a)))
    cnt = collections.Counter((a.get("status") or "?").strip() for a in asks)
    held = 0
    L = ["# Outstanding supervisor asks\n"]
    L.append(
        "Built by sweeping every saved transcript, note file, protocol document and standing-order\n"
        "file for anything Prof. Zhu, Zhikang or the frozen protocol asked for, then checking each\n"
        "one against what is on disk. %d asks were recovered: %d done, %d partial, %d outstanding,\n"
        "%d superseded, %d not actually asks.\n\n"
        "Each entry quotes the ask, says what it requires, and records what was checked.\n"
        % (len(asks), cnt["DONE"], cnt["PARTIAL"], cnt["OUTSTANDING"],
           cnt["SUPERSEDED"], cnt["NOT AN ASK"]))
    for status in ("OUTSTANDING", "PARTIAL"):
        grp = [a for a in sel if (a.get("status") or "").strip() == status]
        kept = []
        for a in grp:
            blob = json.dumps(a)
            if redact and (PERSONAL.search(blob) or PERSONNEL.search(blob)):
                held += 1
                continue
            kept.append(a)
        L.append("\n## %s (%d)\n" % (status.capitalize(), len(kept)))
        for i, a in enumerate(kept, 1):
            v = " ".join((a.get("verbatim") or "").split())
            if len(v) > 420:
                v = v[:420].rstrip() + " [...]"
            req = " ".join((a.get("what_it_requires") or "").split())
            ev = " ".join((a.get("evidence_checked") or "").split())
            e = " ".join((a.get("effort") or "").split())
            L.append("### %s.%d  %s\n" % (status[:4].capitalize(), i, who_of(a)))
            L.append("*%s*\n" % (a.get("date") or "undated").strip())
            if v:
                L.append("> %s\n" % v)
            if req:
                L.append("**What it requires.** %s\n" % req)
            if ev:
                L.append("**Checked.** %s\n" % (ev[:600] + (" [...]" if len(ev) > 600 else "")))
            if e:
                L.append("**Effort.** %s\n" % (e[:400] + (" [...]" if len(e) > 400 else "")))
    if redact and held:
        L.append("\n## Held back from this copy\n")
        L.append("%d entries concern personal supervision arrangements or name a third party in\n"
                 "connection with conduct. They are in the local working copy only.\n" % held)
    s = "\n".join(L)
    s = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", s)
    s = re.sub(r"\s*[–—]\s*", ", ", s)
    return s, held


def main():
    asks = [a for a in json.load(open(SRC)) if isinstance(a, dict)]
    full, _ = build(asks, redact=False)
    pub, held = build(asks, redact=True)
    open(os.path.expanduser("~/brain_run/OUTSTANDING_FULL.md"), "w").write(full)
    open(os.path.join(ROOT, "OUTSTANDING.md"), "w").write(pub)
    print("repo copy written, %d entries held back" % held)


if __name__ == "__main__":
    main()
