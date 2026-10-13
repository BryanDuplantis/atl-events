#!/usr/bin/env python3
"""
Push events_glide.csv to a Google Sheet.

First run will open a browser for OAuth login.
Subsequent runs reuse the cached token.

Usage:
    python3 push_to_sheets.py                     # creates a new sheet
    python3 push_to_sheets.py --sheet-id <ID>     # updates an existing sheet
"""

import argparse
import csv
from pathlib import Path

import gspread

SCRIPT_DIR = Path(__file__).parent
CREDENTIALS_FILE = SCRIPT_DIR / "credentials.json"
TOKEN_FILE = SCRIPT_DIR / "authorized_user.json"
CSV_FILE = SCRIPT_DIR / "events_glide.csv"
SHEET_TITLE = "ATL Events – Glide Data"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_client() -> gspread.Client:
    """Authenticate via OAuth (browser flow on first run)."""
    if TOKEN_FILE.exists():
        gc = gspread.oauth(
            credentials_filename=str(CREDENTIALS_FILE),
            authorized_user_filename=str(TOKEN_FILE),
            scopes=SCOPES,
        )
    else:
        gc = gspread.oauth(
            credentials_filename=str(CREDENTIALS_FILE),
            authorized_user_filename=str(TOKEN_FILE),
            scopes=SCOPES,
        )
    return gc


def read_csv() -> list[list[str]]:
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


def main():
    parser = argparse.ArgumentParser(description="Push events CSV to Google Sheets")
    parser.add_argument("--sheet-id", help="Existing Google Sheet ID to update")
    args = parser.parse_args()

    print("Authenticating with Google...")
    gc = get_client()

    rows = read_csv()
    print(f"Loaded {len(rows) - 1} events from {CSV_FILE.name}")

    if args.sheet_id:
        sh = gc.open_by_key(args.sheet_id)
        print(f"Opened existing sheet: {sh.title}")
    else:
        sh = gc.create(SHEET_TITLE)
        sh.share(None, perm_type="anyone", role="reader")
        print(f"Created new sheet: {SHEET_TITLE}")

    worksheet = sh.sheet1
    worksheet.clear()
    worksheet.update(rows, value_input_option="RAW")

    # Auto-resize and freeze header
    worksheet.freeze(rows=1)
    worksheet.format("1", {"textFormat": {"bold": True}})

    print(f"\nDone! {len(rows) - 1} events pushed.")
    print(f"Sheet URL: {sh.url}")
    print(f"Sheet ID:  {sh.id}")
    print(f"\nTo update later: python3 push_to_sheets.py --sheet-id {sh.id}")


if __name__ == "__main__":
    main()
