"""
setup_sheet.py  –  One-time Google Sheet setup
───────────────────────────────────────────────
Run this once before the pool opens to create the "Picks" tab with the
right column headers.

Usage:
    python setup_sheet.py

Requires .streamlit/secrets.toml to be configured first.
"""

import toml
import gspread
from google.oauth2.service_account import Credentials
from config import TIERS, PICKS_SHEET_TAB

SHEET_COLUMNS = ["Name"] + list(TIERS.keys()) + ["Submitted At"]


def main():
    # Load secrets from .streamlit/secrets.toml
    try:
        secrets = toml.load(".streamlit/secrets.toml")
    except FileNotFoundError:
        print("ERROR: .streamlit/secrets.toml not found.")
        print("Copy .streamlit/secrets.toml.example to .streamlit/secrets.toml and fill it in.")
        return

    spreadsheet_id = secrets.get("SPREADSHEET_ID", "")
    if not spreadsheet_id or spreadsheet_id == "your-google-sheet-id-here":
        print("ERROR: SPREADSHEET_ID not set in secrets.toml")
        return

    sa_info = secrets.get("gcp_service_account", {})
    creds = Credentials.from_service_account_info(
        sa_info,
        scopes=[
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(spreadsheet_id)
    print(f"✅ Opened spreadsheet: {spreadsheet.title}")

    # Check if Picks tab already exists
    existing_sheets = [ws.title for ws in spreadsheet.worksheets()]
    if PICKS_SHEET_TAB in existing_sheets:
        print(f"⚠️  Sheet tab '{PICKS_SHEET_TAB}' already exists — skipping creation.")
        ws = spreadsheet.worksheet(PICKS_SHEET_TAB)
    else:
        ws = spreadsheet.add_worksheet(title=PICKS_SHEET_TAB, rows=200, cols=len(SHEET_COLUMNS))
        print(f"✅ Created tab: {PICKS_SHEET_TAB}")

    # Write header row
    ws.update("A1", [SHEET_COLUMNS])
    print(f"✅ Header row written: {SHEET_COLUMNS}")
    print()
    print("All done! Your Google Sheet is ready.")
    print(f"Share the sheet with your service account email ({sa_info.get('client_email', '?')}) as an Editor.")


if __name__ == "__main__":
    main()
