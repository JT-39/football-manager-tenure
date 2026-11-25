# Milestone 1b exercises: clean the spells table

You'll write the six functions marked `TODO` in `manager_tenure/features.py`. Each one has tests in `tests/test_features.py`. An exercise is done when its tests pass.

## How to work
```bash
git checkout milestone-1b-clean-spells
uv run pytest tests/test_features.py -k exercise1   # run one exercise's tests
make test                                           # run everything
make lint                                           # check style (make format fixes most of it)
```
- Explore in a notebook first if you like. Name it `notebooks/1.0-jt-explore-spells.ipynb` and start it with `uv run jupyter lab`. Then move the finished code into the function.
- Commit after each exercise, e.g. `Feat(pipeline): Read the spells table from the snapshot`.
- **House style:**
  - Each function takes a DataFrame and returns a **new** one, so start with `spells = spells.copy()`.
  - Write it in plain steps, with no classes and no clever one-liners.
  - Comments explain *why*, especially data quirks.

The hints below get more specific as you go down, so stop reading as soon as you're unblocked. R and tidyverse equivalents are given in brackets.

---

## Exercise 1: `read_spells_table`
Return the spells table as pandas reads it, with 521 rows.
1. `pd.read_html()` returns a **list** of DataFrames, one per `<table>` on the page.
2. It has a `match=` argument: only tables containing that text are returned.
3. `match="Duration"` leaves just one table. Take the first item, `[0]`. (In R this is `rvest::html_table()`.)

## Exercise 2: `tidy_columns`
Return the columns `name, club, from, until, duration_days, nationality`, in that order.
1. You need to drop three columns and rename the rest. (`select(-…)` and `rename()`.)
2. `.drop(columns=[...])` and `.rename(columns={"Old": "new", ...})`.
3. The test puts `nationality` last. If you drop and rename, without reordering, it stays where it was.

## Exercise 3: `flag_caretakers`
Add `is_caretaker`, and remove `† ‡ §` and any extra spaces from names.
1. The `.str` accessor gives string methods on a whole column. (Like `stringr` working on vectors.)
2. `.str.contains(CARETAKER_MARKER, regex=False)` gives True/False.
3. `.str.strip(NAME_MARKERS + " ")` removes any of those characters from both ends. (`str_remove_all()` plus `str_trim()`.)
4. Why does `test_exercise3_does_not_change_the_input` exist? Without `.copy()`, assigning a new column can change the caller's DataFrame too. R copies data when you modify it; pandas doesn't always.

## Exercise 4: `parse_dates`
Turn `from` and `until` into real dates, set ongoing spells to end on `as_of`, and add `is_ongoing`.
1. Do it in three parts:
   - Work out which spells are ongoing.
   - Clean the text.
   - Convert it to dates.
2. Ongoing: `.str.startswith("Present")`.
3. **Data quirk:** some dates have footnotes, e.g. `"30 August 2022[a]"`. Remove them with a regular expression: `.str.replace(r"\[.*?\]", "", regex=True)`. Here `\[` means a literal `[`, and `.*?` means "as little as possible".
4. `pd.to_datetime(text, format="%d %B %Y")` handles "14 May 1986": `%d` is the day, `%B` the full month name, `%Y` the four-digit year. (`lubridate::dmy()`.)
5. Converting "Present*" will fail. Either blank it first with `.where(~is_ongoing)` (`~` means "not"), or convert with `errors="coerce"` so it becomes `NaT`, pandas' "missing date", like `NA`. Then `.fillna(pd.Timestamp(as_of))`.
6. Finish with `.drop(columns=["from", "until"])`.

## Exercise 5: `add_tenure`
Add `tenure_days` (total time in charge) and `pl_tenure_days` (days in Premier League seasons).
1. Subtracting two date columns gives a "timedelta" (a duration) column. `.dt.days` turns it into whole days. (`as.numeric(difftime(..., units = "days"))`.)
2. The Premier League part is harder. `parse_league_seasons` turns the "Years in League" text into date ranges, and `premier_league_days` counts the days of each spell that overlap those ranges. Read both functions before changing `add_tenure`.
3. Note the change from the first version: we no longer cut spells off at 1992. Wikipedia's own season list is more accurate, because clubs were in lower divisions before 1992 and after relegation.

## Exercise 6 (stretch): `read_nationalities`
Return 521 country names, in table order, read from the flag images.
1. pandas can't see images, so read the HTML yourself with `lxml`, which is already installed. (`rvest::read_html()` plus `html_elements()`.)
2. `from lxml import html`, then `doc = html.parse(str(html_path))`.
3. Find the right table: loop over `doc.iter("table")` and keep the one whose `.text_content()` contains `"Duration"`.
4. Its rows are `table.findall(".//tr")`. Skip the first row, which is the header.
5. In each row, the first `<td>` is the nationality cell. Find the `<img>` inside it with `.findall(".//img")` and read `.get("alt")`, which holds e.g. "Scotland".
6. If a row has no flag, use `None` so the list still lines up with the rows.

---

## When all the tests pass: investigate before merging
Your cleaned `tenure_days` can be compared with Wikipedia's own `duration_days` column. Do that comparison in a notebook. Here's a preview:

- About **96%** of finished spells match exactly.
- Most of the rest are **off by one day**. Does Wikipedia count both the first and last day?
- A few differ a lot. For example, **Alex McLeish at Birmingham** shows 1292 vs 1496 days. Is that a Wikipedia error, a date we've misread, or a different definition?
- Ongoing spells differ by about 3 days, because Wikipedia last updated its durations a few days before our snapshot.

**Your call as the analyst:** do we trust our own dates, Wikipedia's durations, or flag disagreements in a pandera check? Write your answer in `open-questions.md`.
