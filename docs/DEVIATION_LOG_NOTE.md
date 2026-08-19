# How to read the deviation logs

`deviation_log.csv` is **generated**, not append-only. It is rebuilt from a Python literal in
`write_dev.py`, with timestamps written by hand. That means it is a summary of decisions rather
than an audit trail, and a row could in principle be altered or removed without trace.

This is stated rather than fixed, because retrofitting a genuine append-only log after the fact
would itself be a reconstruction and would look more authoritative than it deserves to.

`deviation_log_proposed.csv` is append-only in practice from 19 August onward: rows are added at
the end and nothing earlier is rewritten. Every deviation raised after that date carries the
timestamp at which it was added.

**One rewrite is on the record.** On 19 August at 18:35 a scripted find-and-replace changed the
`decided_by` column throughout `deviation_log.csv`. The intent was to remove tool attribution from
a research record; the effect was a retroactive edit of an audit trail. The pre-edit copy is
preserved in `.prepatch/` in the working directory. Both facts belong in the open.

The reliable record of what changed and when is the git history from 19 August onward. Before that
date there is no version control, and `debate_run.py` was modified during the primary run, so 16
of the 400 ordering-runs were produced by a writer that no longer exists on disk.
