# Open questions and decisions

Questions that need the project owner's decision. Nobody should choose these alone.
Add new ones at the top; when one is decided, note the answer and the date.

## Added 2026-11-23 (milestone 1a)

1. **Which table(s) on the Wikipedia page are "the" spells table?**
   The snapshot has five `wikitable` tables (three `sortable nowrap`, one
   `sortable plainrowheaders`, one plain). The parsing session needs to decide which to
   read, and whether the page splits current and former managers across tables.

2. **One `metadata.json` or one per snapshot?**
   Right now `data/raw/metadata.json` describes the latest snapshot only (it includes the
   file name). If we take a `--refresh` snapshot later, the old snapshot's HTML stays in
   git but its metadata is overwritten (it is still in git history). Alternatives: name
   it `<snapshot>.metadata.json`, or keep a list of snapshots in one file.

3. **Should a refresh delete older snapshots?**
   Currently they are kept, and the pipeline always uses the newest by date. Keeping them
   grows the repo by about 2.4 MB each time.

4. **Should `spells.json` be committed?**
   `data/processed/` is git-ignored for now. The website build could either run the
   Python pipeline in CI, or read a committed `spells.json`. This affects the deploy
   workflow in milestone 6.

5. **User-Agent contact details.**
   Wikipedia's policy asks for a contact URL or email in the User-Agent. The current one
   (in `config.py`) is generic and has no contact details, because personal details were
   not to be added without asking. You may want to add the repo URL.

6. **Branch name.** The task brief asked for a branch called `setup-python-basics`. The
   cloud session was only allowed to push to `claude/milestone-1a-python-basics-q4sxhi`,
   so the work and pull request use that branch instead.

7. **Leftover template code.** `features.py` and `plots.py` are still the CCDS
   placeholders (with a typer CLI). `typer`, `matplotlib`, `numpy` and `python-dotenv`
   are still dependencies. Keep them, or drop what we don't use once the real code
   exists?
