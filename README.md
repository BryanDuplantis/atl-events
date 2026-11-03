# ATL Events

A small pipeline that turns a hand-collected list of Atlanta-area events into a ranked, app-ready table. It scores each event by how close it is to home and how well it matches a set of personal interests, then writes a CSV that a Glide app (or a Google Sheet) can use directly.

This is an early prototype from February 2026 (33 sample events). It is kept as a record of the idea and as a worked example of a small, deterministic data-shaping script. The live version of this problem is [concert-bloodhound](https://github.com/BryanDuplantis/concert-bloodhound), which pulls events from real sources instead of a hand-entered file.

## What it does

```
events_raw.csv ──> normalize.py ──> events_glide.csv ──> push_to_sheets.py ──> Google Sheet ──> Glide app
```

`normalize.py` reads each row of `events_raw.csv` and adds:

- **Distance** from a fixed home point, using the haversine formula (miles).
- **Star rating, 1 to 5**, from the rules below.
- **Display columns** for the app: a friendly date range ("Mar 3-30"), a 12-hour time ("7:00 PM", "All Day", "TBD"), a star string, a one-line subtitle, a category color, and a sort key that puts the best and nearest events first.

| Stars | Rule |
|---|---|
| 5 | Niche event whose tag matches a core interest |
| 4 | Niche event within 10 miles |
| 3 | Niche event farther out, or any event within 5 miles |
| 2 | Any other event within 15 miles |
| 1 | Everything else |

On the sample data that gives 4 five-star, 4 four-star, 8 three-star, 6 two-star and 11 one-star events.

`push_to_sheets.py` uploads the finished CSV to a Google Sheet with `gspread`, either creating a new sheet or updating one you name with `--sheet-id`. `GLIDE_SETUP.md` walks through binding the columns to a Glide app.

## Run it

Requires Python 3. The normalizer uses only the standard library.

```bash
python3 normalize.py                      # events_raw.csv -> events_glide.csv, prints a ranked summary
python3 normalize.py in.csv out.csv       # or name the files
```

To push to Google Sheets, install `gspread`, put a Google OAuth client file at `credentials.json` next to the script, and run `python3 push_to_sheets.py`. The first run opens a browser to authorize and caches a token in `authorized_user.json`. Both files are gitignored; neither is ever committed.

## How it was checked

Running `normalize.py` on the committed `events_raw.csv` reproduces the committed `events_glide.csv` byte for byte, so the output is deterministic. There is no automated test suite.

## Limits

- The home point and the interest tags are constants at the top of `normalize.py`, not settings.
- The input is a hand-built CSV with no scraper, so the data goes stale.
- The scoring rules have never been tuned against real use.
- No tests, and no handling for malformed rows beyond the date and time formatters.
