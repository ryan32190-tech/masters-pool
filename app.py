"""
US Open Pool — Streamlit App
────────────────────────────
Live scoring pool app. Pulls leaderboard from ESPN, reads picks from Google
Sheets, and calculates standings using top-8-of-15 scoring with real cut line.

Setup:
  1. Edit config.py with tiers, player lists, and prize amounts
  2. Run setup_sheet.py once to create the Picks tab in your Google Sheet
  3. Fill in .streamlit/secrets.toml
  4. Deploy to Streamlit Community Cloud, share the URL

Local dev:
  pip install -r requirements.txt
  streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components
import re
import requests
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz

from streamlit_autorefresh import st_autorefresh
from config import (
    POOL_NAME, PICKS_PER_TIER, TIERS, TOTAL_PICKS, SCORING_PICKS,
    ESPN_URL, REFRESH_INTERVAL_SECONDS, PICKS_SHEET_TAB, CHAT_SHEET_TAB,
    FIRST_ROUND_START, LOCK_PICKS_ON_START, PRIZES, BUY_IN,
    ODDS_API_URL, ODDS_PREFERRED_BOOK, PSA_MESSAGE,
)

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=POOL_NAME,
    page_icon="https://www.usopen.com/favicon.ico",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Source+Sans+3:wght@300;400;600&display=swap');

/* ── Base ── */
html, body, .stApp {
    background-color: #ffffff !important;
    font-family: 'Source Sans 3', sans-serif !important;
}

/* ── Full-width content, no rounded corners anywhere ── */
*, *::before, *::after {
    border-radius: 0 !important;
}
/* Hide Streamlit's built-in header so our fixed nav sits at the very top */
header[data-testid="stHeader"] { display: none !important; }
[data-testid="stToolbar"]      { display: none !important; }
[data-testid="stDecoration"]   { display: none !important; }

.main .block-container {
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 100% !important;
    padding-top: 70px !important;
}
[data-testid="stSidebar"] { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a3a2a 0%, #0d2419 100%) !important;
    border-right: 3px solid #c9a84c !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] .stMarkdown { color: #e8e4d9 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #c9a84c !important;
    font-family: 'Playfair Display', serif !important;
}
[data-testid="stSidebar"] hr { border-color: #c9a84c55 !important; }
[data-testid="stSidebar"] .stAlert { background-color: #0d2419 !important; border-color: #c9a84c !important; }

/* ── Headers ── */
h1 {
    font-family: 'Playfair Display', serif !important;
    color: #002868 !important;
    font-size: 2.2rem !important;
    letter-spacing: 0.02em !important;
}
h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: #1a3a2a !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background-color: #002868 !important;
    border-radius: 6px 6px 0 0 !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    color: rgba(255,255,255,0.65) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 14px 28px !important;
    border-radius: 0 !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #c9a84c !important;
    background-color: rgba(255,255,255,0.06) !important;
}
.stTabs [aria-selected="true"] {
    color: #c9a84c !important;
    background-color: rgba(255,255,255,0.1) !important;
    border-bottom: 3px solid #c9a84c !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background-color: #ffffff !important;
    border: 1px solid #d6cfbe !important;
    border-top: none !important;
    border-radius: 0 0 6px 6px !important;
    padding: 1.5rem !important;
}

/* ── Buttons ── */
.stButton > button {
    background-color: #002868 !important;
    color: #fff !important;
    border: none !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    font-size: 0.82rem !important;
    border-radius: 3px !important;
    padding: 0.55rem 1.4rem !important;
}
.stButton > button:hover {
    background-color: #004d34 !important;
    color: #c9a84c !important;
}

/* ── Form elements ── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stMultiSelect > div > div {
    border-color: #c9a84c !important;
    border-radius: 3px !important;
    background-color: #ffffff !important;
    color: #1a1a1a !important;
}
.stTextInput > div > div > input::placeholder { color: #888888 !important; }
.stTextInput label, .stMultiSelect label, .stSelectbox label,
.stRadio label, .stCheckbox label, .stNumberInput label {
    color: #1a1a1a !important;
    font-weight: 500 !important;
}

/* Radio button option text */
.stRadio > div > label,
.stRadio > div > label > div,
.stRadio [data-testid="stMarkdownContainer"] p,
div[role="radiogroup"] label,
div[role="radiogroup"] label span,
div[role="radiogroup"] p {
    color: #1a1a1a !important;
}

/* Multiselect tags and options */
.stMultiSelect [data-baseweb="tag"] span,
.stMultiSelect [data-baseweb="select"] span,
.stMultiSelect span { color: #1a1a1a !important; }

/* General markdown and text in forms */
.stForm p, .stForm span, .stForm div,
[data-testid="stForm"] p,
[data-testid="stForm"] label,
[data-testid="stForm"] span { color: #1a1a1a !important; }

/* Password / login input */
[data-testid="stTextInput"] input { color: #1a1a1a !important; }

.stRadio > label { font-weight: 600 !important; color: #1a3a2a !important; }

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    border: 1px solid #d6cfbe !important;
    border-radius: 4px !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] thead tr th {
    background-color: #002868 !important;
    color: #fff !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    font-size: 0.78rem !important;
    text-transform: uppercase !important;
    border: none !important;
}
[data-testid="stDataFrame"] tbody tr:nth-child(even) td {
    background-color: #f0ece3 !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
    background-color: #e8f0eb !important;
}

/* ── Dividers ── */
hr { border-color: #c9a84c88 !important; margin: 1rem 0 !important; }

/* ── Alerts / info boxes ── */
.stAlert { border-radius: 4px !important; }
[data-baseweb="notification"] { border-left: 4px solid #002868 !important; }

/* ── Password screen ── */
.stTextInput label { color: #1a3a2a !important; font-weight: 600 !important; }

/* ── Captions ── */
.stCaption, small { color: #7a7260 !important; font-style: italic; }

/* ── Chat ── */
.chat-container {
    display: flex; flex-direction: column; gap: 0.6rem;
    max-height: 480px; overflow-y: auto;
    padding: 1rem; background: #f9f7f2;
    border: 1px solid #e0ddd5; border-radius: 6px;
    margin-bottom: 1rem;
}
.chat-bubble {
    background: #ffffff; border: 1px solid #e0ddd5;
    border-radius: 8px; padding: 0.6rem 0.9rem;
    max-width: 85%;
}
.chat-bubble-name {
    font-weight: 700; color: #002868; font-size: 0.85rem;
}
.chat-bubble-time {
    font-size: 0.75rem; color: #999; margin-left: 0.5rem;
}
.chat-bubble-text {
    margin-top: 0.2rem; color: #1a1a1a; font-size: 0.95rem;
    white-space: pre-wrap; word-break: break-word;
}

/* ── Expanders ── */
.streamlit-expanderHeader,
[data-testid="stExpander"] summary,
[data-testid="stExpander"] > div:first-child {
    background-color: #002868 !important;
    color: white !important;
    border-radius: 4px !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 600 !important;
}
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
    color: white !important;
}
[data-testid="stExpander"] > div:last-child p,
[data-testid="stExpander"] > div:last-child span,
[data-testid="stExpander"] > div:last-child label,
[data-testid="stExpander"] > div:last-child div {
    color: #1a1a1a !important;
}

/* ── Pick display text (my picks lookup) ── */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] strong {
    color: #1a1a1a !important;
}

/* ── Success / info / warning box text ── */
[data-testid="stAlert"] p,
[data-testid="stAlert"] span {
    color: #1a1a1a !important;
}

/* ── Top Nav Bar — fixed white bar, always at top ── */
.masters-topnav {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 9999;
    background: #ffffff;
    border-bottom: 1px solid #e0ddd5;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2rem;
}
.topnav-left {
    display: flex;
    align-items: center;
    gap: 1.75rem;
    min-width: 180px;
}
.nav-link,
.nav-link:link,
.nav-link:visited {
    font-family: 'Source Sans 3', sans-serif;
    color: #333333 !important;
    font-size: 0.82rem;
    font-weight: 400;
    letter-spacing: 0.06em;
    text-transform: none;
    text-decoration: none !important;
    padding-bottom: 2px;
    border-bottom: 2px solid transparent;
    transition: color 0.15s, border-color 0.15s;
}
.nav-link:hover {
    color: #002868 !important;
    border-bottom: 2px solid #002868;
    text-decoration: none !important;
}
.topnav-center {
    font-family: 'Playfair Display', serif;
    color: #1a3a2a;
    font-size: 1.15rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-align: center;
    flex: 1;
}
.topnav-right {
    font-family: 'Source Sans 3', sans-serif;
    color: #999;
    font-size: 0.75rem;
    letter-spacing: 0.04em;
    text-align: right;
    min-width: 180px;
}


/* ── Hover dropdown menu ── */
.nav-menu-wrapper {
    position: relative;
    height: 56px;
    display: flex;
    align-items: center;
}
.nav-dropdown {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    min-width: 230px;
    background: linear-gradient(160deg, #004d34 0%, #002868 100%);
    border-top: 3px solid #c9a84c;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    z-index: 10000;
}
.nav-menu-wrapper:hover .nav-dropdown {
    display: block;
}
.dropdown-item,
.dropdown-item:link,
.dropdown-item:visited {
    display: block;
    padding: 0.85rem 1.25rem;
    color: #ffffff !important;
    text-decoration: none !important;
    font-family: 'Source Sans 3', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    transition: background 0.15s, color 0.15s;
}
.dropdown-item:last-child { border-bottom: none; }
.dropdown-item:hover {
    background: rgba(255,255,255,0.12);
    color: #c9a84c !important;
}

/* ── Page section titles ── */
.page-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    color: #002868;
    border-bottom: 3px solid #c9a84c;
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem;
}

/* ── Prize cards ── */
.prize-card {
    background: #ffffff;
    border: 1px solid #d6cfbe;
    border-left: 4px solid #c9a84c;
    border-radius: 4px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}
.prize-card-label { font-family: 'Playfair Display', serif; color: #1a3a2a; font-size: 1rem; font-weight: 600; }
.prize-card-amount { font-family: 'Source Sans 3', sans-serif; color: #c9a84c; font-size: 1.3rem; font-weight: 700; }
.prize-card-leader { font-family: 'Source Sans 3', sans-serif; color: #555; font-size: 0.85rem; margin-top: 0.25rem; }

/* ── Standings summary table medals ── */
.medal-row { font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)


# ── AUTH ──────────────────────────────────────────────────────────────────────
def require_auth():
    # Already authenticated in this session
    if st.session_state.get("authenticated"):
        return
    # Auth token carried in query params survives <a href> navigation
    if st.query_params.get("_a") == "1":
        st.session_state.authenticated = True
        return
    st.markdown(f"""
    <div style="text-align:center; padding: 3rem 0 1rem 0;">
        <div style="margin-bottom:1rem;">
            <img src="https://res.cloudinary.com/usga-single-app/image/upload/f_auto,fl_lossy,q_auto/c_fill,dpr_2.0,g_center/v1717591996/championships/logos/USO_Logo_FULL_COLOR_FINAL.png" height="64"
                 style="image-rendering:crisp-edges;">
        </div>
        <div style="font-family:'Playfair Display',serif; font-size:2.8rem; color:#002868; font-weight:700; letter-spacing:0.04em;">
            {POOL_NAME}
        </div>
        <div style="width:80px; height:3px; background:#c9a84c; margin:0.8rem auto 0.4rem auto; border-radius:2px;"></div>
        <div style="font-family:'Source Sans 3',sans-serif; color:#7a7260; font-size:0.95rem; letter-spacing:0.1em; text-transform:uppercase;">
            A Tradition Unlike Any Other
        </div>
    </div>
    """, unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        pw = st.text_input("Pool Password", type="password", placeholder="Enter password to join…")
        if st.button("Enter the Clubhouse", type="primary", use_container_width=True):
            if pw == st.secrets.get("POOL_PASSWORD", "usopen2026"):
                st.session_state.authenticated = True
                st.query_params["_a"] = "1"
                st.rerun()
            else:
                st.error("Wrong password — check with your pool admin.")
    st.stop()

require_auth()


# ── GOOGLE SHEETS ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_sheets_client():
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        return gspread.authorize(creds)
    except Exception:
        return None


def get_worksheet():
    client = get_sheets_client()
    if not client:
        return None
    sid = st.secrets.get("SPREADSHEET_ID", "")
    if not sid:
        return None
    try:
        return client.open_by_key(sid).worksheet(PICKS_SHEET_TAB)
    except Exception as e:
        st.warning(f"⚠️ Could not open Google Sheet: {e}")
        return None


SHEET_COLUMNS = ["Name"] + list(TIERS.keys()) + ["PIN", "Submitted At"]

@st.cache_data(ttl=30)
def load_picks_from_sheet():
    ws = get_worksheet()
    if ws is None:
        return None
    try:
        all_vals = ws.get_all_values()
        if not all_vals:
            return pd.DataFrame()
        # Always use our known column order, ignoring whatever headers are in the sheet
        data_rows = all_vals[1:]  # skip header row
        if not data_rows:
            return pd.DataFrame()
        df = pd.DataFrame(data_rows, columns=SHEET_COLUMNS[:len(all_vals[0])])
        # If sheet has fewer columns than expected (e.g. no PIN column yet), fill missing
        for col in SHEET_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df
    except Exception as e:
        st.warning(f"Could not load picks: {e}")
        return pd.DataFrame()


def load_picks():
    sheet = load_picks_from_sheet()
    if sheet is not None:
        return sheet
    # Local/demo fallback
    if "local_picks" not in st.session_state:
        st.session_state.local_picks = pd.DataFrame()
    return st.session_state.local_picks


def save_picks(name: str, picks_by_tier: dict, pin: str = "") -> bool:
    """Save one participant's picks, overwriting any existing entry for that name."""
    # Flatten picks to one row: Name | Tier 1-2 | Tier 3 | ... | Tiers 13-15 | PIN | Submitted At
    row_vals = [name]
    for tier in TIERS.keys():
        row_vals.append(", ".join(picks_by_tier.get(tier, [])))
    row_vals.append(str(pin).strip())
    row_vals.append(datetime.now().strftime("%Y-%m-%d %H:%M"))

    ws = get_worksheet()
    if ws is not None:
        try:
            all_vals = ws.get_all_values()
            # Always ensure header row matches current structure
            if not all_vals or all_vals[0] != SHEET_COLUMNS:
                ws.update("A1", [SHEET_COLUMNS])
                all_vals = ws.get_all_values()
            data_rows = all_vals[1:]
            names = [r[0] for r in data_rows if r]
            if name in names:
                idx = names.index(name) + 2  # +1 for header, +1 for 1-indexing
                ws.update(f"A{idx}", [row_vals])
            else:
                ws.append_row(row_vals)
            load_picks_from_sheet.clear()
            return True
        except Exception as e:
            st.error(f"Could not save to Google Sheet: {e}")
            return False
    else:
        # Local fallback
        cols = ["Name"] + list(TIERS.keys()) + ["PIN", "Submitted At"]
        new_row = dict(zip(cols, row_vals))
        df = st.session_state.get("local_picks", pd.DataFrame())
        df = df[df["Name"] != name] if not df.empty else df
        st.session_state.local_picks = pd.concat(
            [df, pd.DataFrame([new_row])], ignore_index=True
        )
        return True


# ── CHAT ─────────────────────────────────────────────────────────────────────
CHAT_COLUMNS = ["Name", "Message", "Timestamp"]

def get_chat_worksheet():
    client = get_sheets_client()
    if not client:
        return None
    sid = st.secrets.get("SPREADSHEET_ID", "")
    if not sid:
        return None
    try:
        spreadsheet = client.open_by_key(sid)
        try:
            return spreadsheet.worksheet(CHAT_SHEET_TAB)
        except Exception:
            # Create the Chat tab if it doesn't exist
            ws = spreadsheet.add_worksheet(title=CHAT_SHEET_TAB, rows=1000, cols=3)
            ws.append_row(CHAT_COLUMNS)
            return ws
    except Exception as e:
        return None


@st.cache_data(ttl=15)  # refresh chat more frequently
def load_chat_messages():
    ws = get_chat_worksheet()
    if ws is None:
        return pd.DataFrame(columns=CHAT_COLUMNS)
    try:
        all_vals = ws.get_all_values()
        if len(all_vals) <= 1:
            return pd.DataFrame(columns=CHAT_COLUMNS)
        return pd.DataFrame(all_vals[1:], columns=CHAT_COLUMNS)
    except Exception:
        return pd.DataFrame(columns=CHAT_COLUMNS)


def save_chat_message(name: str, message: str) -> bool:
    ws = get_chat_worksheet()
    if ws is None:
        return False
    try:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        ws.append_row([name.strip(), message.strip(), ts])
        load_chat_messages.clear()
        return True
    except Exception as e:
        st.error(f"Could not send message: {e}")
        return False


# ── ESPN LEADERBOARD ──────────────────────────────────────────────────────────
@st.cache_data(ttl=REFRESH_INTERVAL_SECONDS)
def fetch_leaderboard():
    """
    Returns (data, error). data is a dict with keys:
        tournament  – str
        status      – str  (e.g. "In Progress", "Final", "Scheduled")
        cut_score   – int or None  (score to par at the cut line)
        round       – int  (current round number, 1–4)
        leaderboard – pd.DataFrame with one row per player
    """
    try:
        resp = requests.get(ESPN_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        events = data.get("events", [])
        if not events:
            return None, "No events found in ESPN response."

        # Prefer U.S. Open by name, then any in-progress event, then first available
        def event_priority(e):
            name = e.get("name", "").lower()
            desc = e.get("status", {}).get("type", {}).get("description", "").lower()
            if "u.s. open" in name or "us open" in name or "united states open" in name:
                return 0
            if "in progress" in desc:
                return 1
            if "scheduled" in desc:
                return 2
            return 3

        tournament = sorted(events, key=event_priority)[0]

        t_name = tournament.get("name", "Unknown")
        t_status = tournament.get("status", {}).get("type", {}).get("description", "")

        # Log the tournament name for debugging
        # (Filter prioritises U.S. Open by name; falls back to in-progress event)

        competitions = tournament.get("competitions", [])
        if not competitions:
            return {"tournament": t_name, "status": t_status,
                    "cut_score": None, "round": 1, "leaderboard": pd.DataFrame()}, None

        comp = competitions[0]

        # Cut line — path is event["tournament"]["cutScore"]
        # (in code, `tournament` = the event object; nested "tournament" key holds metadata)
        cut_score = tournament.get("tournament", {}).get("cutScore")
        if cut_score is None:
            cut_score = comp.get("cutScore")
        if cut_score is None:
            cut_data = comp.get("cutLine", {})
            if cut_data:
                cut_score = cut_data.get("score", {}).get("value")
                if cut_score is None:
                    cut_score = cut_data.get("value")
        if cut_score is not None:
            try:
                cut_score = int(cut_score)
            except (ValueError, TypeError):
                cut_score = None

        # Current round
        current_round = comp.get("status", {}).get("period", 1) or 1

        rows = []
        for player in comp.get("competitors", []):
            name = player.get("athlete", {}).get("displayName", "Unknown")

            # Always prefer statistics[].scoreToPar — it's the live running score.
            # score.displayValue only updates after a round is fully complete, so
            # it lags badly mid-round (e.g. showing -2 while player is really -5).
            total_display = None
            for stat in player.get("statistics", []):
                if stat.get("name") == "scoreToPar":
                    val = stat.get("displayValue", "")
                    if val not in ("—", "--", "", None):
                        total_display = val
                    break
            # Fall back to score.displayValue if no live stat found
            if not total_display:
                score_obj = player.get("score", {})
                total_display = (
                    score_obj.get("displayValue", "E")
                    if isinstance(score_obj, dict) else str(score_obj)
                )
            # Normalise blank / dash to "E"
            if total_display in ("—", "--", None, ""):
                total_display = "E"
            total_int = _parse_score(total_display)

            p_status = player.get("status", {})
            position = p_status.get("position", {}).get("displayName", "--")
            thru = str(p_status.get("thru") or "—")
            if thru == "0":
                thru = "—"
            status_name = p_status.get("type", {}).get("name", "").lower()

            made_cut = "cut" not in status_name and "wd" not in status_name and "dq" not in status_name
            status_label = (
                "WD"  if "wd"  in status_name
                else "DQ"  if "dq"  in status_name
                else "CUT" if "cut" in status_name
                else ""
            )

            # Per-round scores from linescores.
            # ESPN stores raw stroke counts in .value (e.g. 68, 72).
            # We prefer .displayValue which is the score-to-par string ("E","-4","+2").
            # If only raw strokes are available, convert: score-to-par = strokes - 70 (Shinnecock par).
            round_scores = {}
            for i, ls in enumerate(player.get("linescores", []), 1):
                dv = str(ls.get("displayValue", "")).strip()
                if dv and dv not in ("—", "--", "", "null"):
                    try:
                        round_scores[f"R{i}"] = _parse_score(dv)
                        continue
                    except Exception:
                        pass
                val = ls.get("value")
                try:
                    if val is not None and not pd.isna(val):
                        v = int(float(val))
                        # Raw strokes are always 50+; score-to-par is rarely outside -15..+20
                        round_scores[f"R{i}"] = (v - 70) if v > 20 else v
                except (ValueError, TypeError):
                    pass

            # Today's score — pass thru so not-started players cleanly show —
            today_display = _extract_today(player, thru)

            rows.append({
                "position":   position,
                "name":       name,
                "score":      total_display,
                "score_int":  total_int,
                "today":      today_display,
                "thru":       thru,
                "status":     status_label,
                "made_cut":   made_cut,
                **round_scores,
            })

        df = pd.DataFrame(rows)

        # Re-derive positions ourselves from score_int so they're always consistent.
        # Sort active players by score, then assign T-positions for ties.
        active_df = df[df["made_cut"]].copy()
        cut_df    = df[~df["made_cut"]].copy()

        active_df = active_df.sort_values("score_int").reset_index(drop=True)
        pos_labels = []
        i = 0
        while i < len(active_df):
            j = i
            while j < len(active_df) - 1 and active_df.loc[j+1, "score_int"] == active_df.loc[i, "score_int"]:
                j += 1
            label = f"T{i+1}" if j > i else str(i+1)
            for _ in range(j - i + 1):
                pos_labels.append(label)
            i = j + 1
        active_df["position"] = pos_labels

        cut_df["position"] = "MC"
        df = pd.concat([active_df, cut_df], ignore_index=True)

        return {
            "tournament": t_name,
            "status": t_status,
            "cut_score": cut_score,
            "round": current_round,
            "leaderboard": df,
        }, None

    except requests.RequestException as e:
        return None, f"Network error: {e}"
    except Exception as e:
        return None, f"Parse error: {e}"


def _extract_today(player: dict, thru: str = "—") -> str:
    """Today's round score-to-par. Returns '—' when player hasn't started."""
    # If player hasn't teed off yet, today's score is always —
    if thru in ("—", "", "0"):
        return "—"
    # ESPN exposes today's round score as "today" stat; "scoreToPar" is the
    # live running score (same as today in R1, total in R2+). Try "today" first,
    # then fall back to "scoreToPar". Never use linescores — those values are
    # raw stroke counts (e.g. 72), not score-to-par.
    for stat in player.get("statistics", []):
        if stat.get("name") in ("today", "scoreToPar"):
            val = stat.get("displayValue", "—")
            if val not in ("—", "--", "", None):
                return val
    return "—"


def _parse_score(s) -> int:
    if s in (None, "E", "--", "—", "N/A", ""):
        return 0
    try:
        return int(str(s).replace("+", ""))
    except ValueError:
        return 0


def _fmt(n: int) -> str:
    if n == 0:
        return "E"
    return f"+{n}" if n > 0 else str(n)


# ── STANDINGS ENGINE ──────────────────────────────────────────────────────────
def get_all_picks_flat(participant_row: pd.Series) -> list[str]:
    """Return a flat list of all player names for one participant."""
    players = []
    for tier in TIERS.keys():
        raw = str(participant_row.get(tier, "") or "")
        players.extend([p.strip() for p in raw.split(",") if p.strip()])
    return players


import unicodedata

def _normalize(s: str) -> str:
    """Lowercase, strip accents, remove dots/hyphens, collapse spaces."""
    # Handle special characters that NFD won't decompose
    _CHAR_MAP = {"ø": "o", "Ø": "o", "æ": "ae", "Æ": "ae", "å": "a", "Å": "a"}
    s = "".join(_CHAR_MAP.get(c, c) for c in s)
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[.\-]", " ", s)   # J.J. → J J,  Neergaard-Petersen → Neergaard Petersen
    s = re.sub(r"\s+", " ", s)     # collapse multiple spaces
    return s.lower().strip()


def build_score_map(lb: pd.DataFrame, cut_score: int | None = None) -> dict:
    """
    Returns a dict: normalized_name -> {score_int, score_display, made_cut, position}
    Includes last-name-only keys for fuzzy matching, but ONLY when that last name
    is unique in the field (prevents e.g. Alex Fitzpatrick / Matt Fitzpatrick collision).
    If cut_score is provided, players scoring worse than the cut are projected
    as missing the cut even if ESPN hasn't officially marked them yet (Round 2).
    """
    # First pass: count how many players share each last name
    last_name_counts: dict[str, int] = {}
    for _, row in lb.iterrows():
        parts = _normalize(row["name"]).split()
        if len(parts) > 1:
            last_name_counts[parts[-1]] = last_name_counts.get(parts[-1], 0) + 1

    score_map = {}
    for _, row in lb.iterrows():
        made_cut = row["made_cut"]
        # Project cut for active players when a cut line is known
        if cut_score is not None and made_cut and row["score_int"] > cut_score:
            made_cut = False
        info = {
            "score_int":     row["score_int"],
            "score_display": row["score"],
            "made_cut":      made_cut,
            "position":      row["position"],
            "status":        row.get("status", ""),
        }
        key = _normalize(row["name"])
        score_map[key] = info
        # Only index by last name if it is unique in the field
        parts = key.split()
        if len(parts) > 1 and last_name_counts.get(parts[-1], 0) == 1:
            score_map[parts[-1]] = info
    return score_map


def lookup_player(name: str, score_map: dict) -> dict | None:
    key = _normalize(name)
    if key in score_map:
        return score_map[key]
    # Substring match on normalized names
    for lb_key, val in score_map.items():
        if key in lb_key or lb_key in key:
            return val
    return None


def score_participant(picks: list[str], score_map: dict) -> dict:
    """
    Given a flat list of 15 player names and the score map, compute:
      - per_player: list of {name, score_int, score_display, made_cut, counted}
      - makers: number of picks who made the cut
      - dq: True if makers < SCORING_PICKS
      - total: sum of best SCORING_PICKS scores (or None if DQ)
      - total_display: formatted string
    """
    per_player = []
    for pick in picks:
        info = lookup_player(pick, score_map)
        if info:
            per_player.append({
                "name":          pick,
                "score_int":     info["score_int"],
                "score_display": info["score_display"],
                "made_cut":      info["made_cut"],
                "position":      info["position"],
                "status":        info["status"],
                "found":         True,
            })
        else:
            per_player.append({
                "name":          pick,
                "score_int":     999,
                "score_display": "N/F",
                "made_cut":      False,  # Not found = not in this field
                "position":      "—",
                "status":        "N/F",
                "found":         False,
            })

    # Players who made the cut, sorted by score (best first)
    # Not-found players are excluded from makers count (name mismatch ≠ missed cut)
    cut_players = sorted(
        [p for p in per_player if p["made_cut"] and p["found"]],
        key=lambda x: x["score_int"],
    )

    makers = len(cut_players)
    # Only DQ if we have confirmed cut players < SCORING_PICKS (ignore not-found)
    found_count = len([p for p in per_player if p["found"]])
    dq = found_count >= SCORING_PICKS and makers < SCORING_PICKS

    if dq:
        total = None
        total_display = "DQ"
        # Mark none as counted
        for p in per_player:
            p["counted"] = False
    else:
        counting = cut_players[:SCORING_PICKS]
        counting_names = {p["name"] for p in counting}
        total = sum(p["score_int"] for p in counting)
        total_display = _fmt(total)
        for p in per_player:
            p["counted"] = p["name"] in counting_names and p["made_cut"]

    return {
        "per_player":    per_player,
        "makers":        makers,
        "dq":            dq,
        "total":         total,
        "total_display": total_display,
    }


def calc_team_strength(per_player: list, odds_map: dict | None) -> float:
    """
    Sum of implied win probabilities for each active (made cut) pick.
    Uses live odds if available, falls back to 0 for unmatched players.
    Returns a value between 0 and 1.
    """
    if not odds_map:
        return 0.0
    total = 0.0
    for p in per_player:
        if not p.get("made_cut"):
            continue
        key  = _normalize(p["name"])
        info = odds_map.get(key)
        if info is None:
            last = key.split()[-1] if key.split() else key
            info = odds_map.get(last)
        if info:
            total += _implied_prob(info["american"])
    return total


def calculate_win_probability(standings: list, odds_map: dict | None) -> list:
    """
    Add a win_prob percentage to each entry in standings.
    Formula (weights): score 50%, active picks 30%, team strength 20%.
    Scores are inverted (lower = better in golf) and normalized across the pool.
    """
    if not standings:
        return standings

    n = len(standings)

    # ── Component 1: Score (lower is better → invert to higher = better) ──
    valid = [e for e in standings if not e["dq"] and e["total"] is not None]
    if valid:
        scores = [e["total"] for e in valid]
        min_s, max_s = min(scores), max(scores)
        rng = max_s - min_s if max_s != min_s else 1
        for e in standings:
            if e["dq"] or e["total"] is None:
                e["_score_norm"] = 0.0
            else:
                e["_score_norm"] = (max_s - e["total"]) / rng  # invert
    else:
        for e in standings:
            e["_score_norm"] = 0.0

    # ── Component 2: Active picks (makers / TOTAL_PICKS) ──
    for e in standings:
        e["_active_norm"] = e["makers"] / TOTAL_PICKS if not e["dq"] else 0.0

    # ── Component 3: Team strength (sum of implied probs of active picks) ──
    strengths = []
    for e in standings:
        ts = calc_team_strength(e["per_player"], odds_map) if not e["dq"] else 0.0
        e["_strength"] = ts
        strengths.append(ts)
    max_ts = max(strengths) if max(strengths) > 0 else 1
    for e in standings:
        e["_strength_norm"] = e["_strength"] / max_ts

    # ── Weighted composite ──
    W_SCORE    = 0.50
    W_ACTIVE   = 0.30
    W_STRENGTH = 0.20

    for e in standings:
        e["_composite"] = (
            W_SCORE    * e["_score_norm"] +
            W_ACTIVE   * e["_active_norm"] +
            W_STRENGTH * e["_strength_norm"]
        )

    # ── Normalize composites to sum to 100% ──
    total_comp = sum(e["_composite"] for e in standings)
    for e in standings:
        if total_comp > 0:
            e["win_prob"] = f"{e['_composite'] / total_comp * 100:.1f}%"
        else:
            e["win_prob"] = "—"

    # Clean up temp keys
    for e in standings:
        for k in ["_score_norm", "_active_norm", "_strength", "_strength_norm", "_composite"]:
            e.pop(k, None)

    return standings


def calculate_standings(picks_df: pd.DataFrame, lb_data: dict | None) -> list:
    if picks_df.empty:
        return []

    results = []
    if lb_data and not lb_data["leaderboard"].empty:
        # Only project cut during Round 2 — Round 1 has no cut yet, and Round 3+
        # the cut is already official in ESPN's made_cut field so don't override it.
        cut_score_for_map = lb_data.get("cut_score") if lb_data.get("round", 1) == 2 else None
        score_map = build_score_map(lb_data["leaderboard"], cut_score_for_map)
    else:
        score_map = {}

    for _, row in picks_df.iterrows():
        name = row.get("Name", "Unknown")
        picks = get_all_picks_flat(row)
        scored = score_participant(picks, score_map)
        results.append({"participant": name, **scored})

    # Sort: DQ last, then by total score ascending
    results.sort(key=lambda x: (x["dq"], x["total"] if x["total"] is not None else 9999))
    return results


# ── ROUND LEADERS (for prize display) ─────────────────────────────────────────
def get_round_leader(picks_df: pd.DataFrame, lb: pd.DataFrame, through_round: int) -> str | None:
    """
    Find the pool leader as of the END of `through_round` (1, 2, or 3).
    Uses CUMULATIVE score through that round — i.e. sum of R1..RN per player —
    which mirrors the live pool standings at the close of that round.
    """
    round_cols = [f"R{i}" for i in range(1, through_round + 1)]
    available = [c for c in round_cols if c in lb.columns]
    if not available:
        return None

    # Build cumulative score map: player_name → sum of R1..RN
    cumulative_map: dict[str, int] = {}
    for _, row in lb.iterrows():
        total = 0
        valid = True
        for col in available:
            val = row.get(col)
            try:
                if val is None or pd.isna(val):
                    valid = False
                    break
                total += int(val)
            except (ValueError, TypeError):
                valid = False
                break
        if valid:
            key = _normalize(str(row["name"]))
            cumulative_map[key] = total
            last = key.split()[-1] if key.split() else key
            cumulative_map.setdefault(last, total)

    if not cumulative_map:
        return None

    bests = []
    for _, row in picks_df.iterrows():
        picks = get_all_picks_flat(row)
        scores = []
        for p in picks:
            key = _normalize(p)
            s = cumulative_map.get(key)
            if s is None:
                last = key.split()[-1] if key.split() else key
                s = cumulative_map.get(last)
            if s is not None:
                scores.append(s)
        if len(scores) >= SCORING_PICKS:
            best_n = sorted(scores)[:SCORING_PICKS]
            bests.append((row["Name"], sum(best_n)))

    if not bests:
        return None
    # Require at least half the pool to have valid data — guards against
    # showing a premature leader when the round isn't fully complete yet.
    if len(bests) < max(2, len(picks_df) // 2):
        return None
    bests.sort(key=lambda x: x[1])
    return f"{bests[0][0]} ({_fmt(bests[0][1])})"


# ── PICKS LOCK ────────────────────────────────────────────────────────────────
def picks_are_locked() -> bool:
    return bool(LOCK_PICKS_ON_START)


# ── ODDS API ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=REFRESH_INTERVAL_SECONDS)
def fetch_odds():
    """
    Returns (odds_map, error).
    odds_map: { normalized_player_name: {"american": int, "book": str} }
    Prefers ODDS_PREFERRED_BOOK; falls back to averaging all available books.
    """
    api_key = st.secrets.get("ODDS_API_KEY", "")
    if not api_key:
        return None, "No ODDS_API_KEY found in secrets — add it to .streamlit/secrets.toml"

    url = f"{ODDS_API_URL}&apiKey={api_key}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 401:
            return None, "Invalid Odds API key — check ODDS_API_KEY in secrets.toml"
        if resp.status_code == 422:
            return None, "U.S. Open odds not yet available from The Odds API (tournament may not be listed yet)"
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return None, str(e)

    if not data:
        return None, "No odds data returned"

    # data is a list of events — we want the first (only U.S. Open outright event)
    event = data[0] if isinstance(data, list) and data else {}
    bookmakers = event.get("bookmakers", [])

    # Build { player_name: [american_odds, ...] } across all books
    player_odds: dict[str, list[int]] = {}
    player_book:  dict[str, str]      = {}

    preferred = next((b for b in bookmakers if b["key"] == ODDS_PREFERRED_BOOK), None)
    books_to_use = [preferred] if preferred else bookmakers

    for book in books_to_use:
        if not book:
            continue
        for market in book.get("markets", []):
            if market.get("key") != "outrights":
                continue
            for outcome in market.get("outcomes", []):
                name  = outcome.get("name", "")
                price = outcome.get("price")
                if name and price is not None:
                    player_odds.setdefault(name, []).append(int(price))
                    player_book[name] = book.get("title", "")

    if not player_odds:
        return None, "No outright odds found in API response"

    # Average across books (usually just one if preferred book matched)
    odds_map: dict[str, dict] = {}
    for name, prices in player_odds.items():
        avg = int(sum(prices) / len(prices))
        odds_map[_normalize(name)] = {
            "american": avg,
            "display":  f"+{avg}" if avg > 0 else str(avg),
            "name":     name,
            "book":     player_book.get(name, ""),
        }

    return odds_map, None


def _implied_prob(american: int) -> float:
    """Convert American odds to implied probability (0–1)."""
    if american > 0:
        return 100 / (american + 100)
    else:
        return abs(american) / (abs(american) + 100)


# ── VIEW RENDERERS ────────────────────────────────────────────────────────────

@st.cache_resource
def _load_scottie_b64():
    """Load Scottie.jpg from the repo root and return as base64 string."""
    import base64, os
    img_path = os.path.join(os.path.dirname(__file__), "Scottie.jpg")
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def render_scottie_header():
    b64 = _load_scottie_b64()
    if not b64:
        return
    st.markdown(f"""
    <div style="display:flex; justify-content:center; margin: -8px 0 -18px 0;">
      <img src="data:image/jpeg;base64,{b64}"
           style="height:180px; mix-blend-mode:multiply;">
    </div>
    """, unsafe_allow_html=True)


def render_standings_view(picks_df, lb_data, lb_error):
    st.markdown('<div class="page-title">Pool Standings</div>', unsafe_allow_html=True)
    st.caption(f"Best {SCORING_PICKS} of {TOTAL_PICKS} picks count · Fewer than {SCORING_PICKS} make cut = DQ")
    if PSA_MESSAGE:
        st.markdown(f"""
        <div style="background:#f0f4ff; border-left:4px solid #002868;
                    padding:10px 16px; border-radius:4px; margin-bottom:0.5rem;
                    color:#1a1a1a; font-size:0.95rem;">
            {PSA_MESSAGE}
        </div>
        """, unsafe_allow_html=True)

    # ── Cut line info bar — only show Round 2 onwards ────────────────────────
    if picks_are_locked() and lb_data and not lb_data["leaderboard"].empty:
        lb = lb_data["leaderboard"]
        round_num  = lb_data.get("round", 1)
        cut_score  = lb_data.get("cut_score")
        status_str = lb_data.get("status", "")

        # No cut line projection during Round 1 — too early to be meaningful
        if round_num >= 2:
            if cut_score is not None:
                cut_label = f"✂️ Cut line: **{_fmt(cut_score)}**"
            else:
                # Project from the worst active score during Round 2
                active_scores = lb[lb["made_cut"]]["score_int"]
                if not active_scores.empty:
                    projected = active_scores.max()
                    cut_label = f"✂️ Projected cut: **{_fmt(projected)}** or better"
                else:
                    cut_label = None

            if cut_label:
                info_parts = [cut_label, f"Round {round_num} of 4"]
                if status_str:
                    info_parts.append(status_str)
                st.info("  ·  ".join(info_parts))
        else:
            # Round 1 — just show round info, no cut line
            st.info(f"Round {round_num} of 4  ·  {status_str}" if status_str else f"Round {round_num} of 4")

    if lb_error:
        st.warning(f"⚠️ Leaderboard unavailable: {lb_error}")

    if picks_df.empty:
        st.info("No picks submitted yet — use **Submit Picks** to enter the pool.")
        return

    standings = calculate_standings(picks_df, lb_data)

    if not lb_data or lb_data["leaderboard"].empty:
        st.info("⏳ Scoring will appear once the tournament begins.")
        for entry in standings:
            st.write(f"• {entry['participant']}")
        return

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    tournament_started = picks_are_locked()
    cut_col_label = "Making Cut"

    # (Win Probability removed — odds API disabled)

    # Summary table
    rows = []
    place = 1
    for entry in standings:
        if tournament_started:
            if entry["dq"]:
                rows.append({"Place": "❌ DQ", "Participant": entry["participant"],
                             "Score": "DQ", cut_col_label: f"{entry['makers']}/{TOTAL_PICKS}"})
            else:
                rows.append({"Place": medals.get(place, str(place)), "Participant": entry["participant"],
                             "Score": entry["total_display"], cut_col_label: f"{entry['makers']}/{TOTAL_PICKS}"})
                place += 1
        else:
            rows.append({"Place": "—", "Participant": entry["participant"],
                         "Score": "n/a", "Making Cut": "-/-"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="page-title" style="font-size:1.3rem">Pick Breakdown</div>', unsafe_allow_html=True)

    # Hide picks until the tournament starts
    if not picks_are_locked():
        st.info("🔒 Pick details are hidden until the U.S. Open begins. Check the **Submit Picks** page to view your own picks.")
        return

    # Build row labels
    pick_labels = []
    for tier, count in PICKS_PER_TIER.items():
        if count == 1:
            pick_labels.append(tier)
        else:
            for i in range(1, count + 1):
                pick_labels.append(f"{tier} — Pick {i}")

    place_map = {}
    p = 1
    for entry in standings:
        if not entry["dq"]:
            place_map[entry["participant"]] = p
            p += 1

    def col_header(entry):
        if entry["dq"]:
            return f"{entry['participant']} ❌ DQ"
        pl = place_map.get(entry["participant"], "")
        return f"{medals.get(pl, str(pl)+'.')} {entry['participant']}  {entry['total_display']}"

    def abbrev(full_name: str) -> str:
        """'Tommy Fleetwood' → 'T. Fleetwood'"""
        parts = full_name.strip().split()
        if len(parts) >= 2:
            return f"{parts[0][0]}. {' '.join(parts[1:])}"
        return full_name

    # Work out the widest abbreviated name in the entire field so every
    # name column is exactly that wide — no truncation.
    all_names = [abbrev(px["name"]) for e in standings for px in e["per_player"]]
    max_name_chars = max((len(n) for n in all_names), default=14)
    name_w  = max(130, max_name_chars * 9)   # ~9px per char
    score_w = 52

    cut_round = lb_data.get("round", 1) if lb_data else 1
    cut_label = "Proj. Making Cut" if (cut_round <= 2 and lb_data and lb_data.get("cut_score") is not None) else "Making Cut"

    # Build column keys: one name col + one score col per participant
    # Score col key must be unique — use a private prefix
    def score_key(i): return f"\u200b{i}"   # zero-width-space + index = invisible header

    table_rows = []
    for slot_idx, label in enumerate(pick_labels):
        row = {"": label}
        for i, entry in enumerate(standings):
            hdr = col_header(entry)
            per = entry["per_player"]
            if slot_idx < len(per):
                px = per[slot_idx]
                short = abbrev(px["name"])
                if not px.get("found", True):
                    name_cell  = f"❓ {short}"
                    sc         = ""
                elif not px["made_cut"]:
                    name_cell  = f"✂️ {short}"
                    sc         = px["score_display"]
                elif px["counted"]:
                    name_cell  = f"✅ {short}"
                    sc         = px["score_display"]
                else:
                    name_cell  = f"➖ {short}"
                    sc         = px["score_display"]
            else:
                name_cell = ""
                sc        = ""
            row[hdr]          = name_cell
            row[score_key(i)] = sc
        table_rows.append(row)

    # Summary rows
    totals  = {"": "TOTAL"}
    cut_row = {"": cut_label}
    for i, entry in enumerate(standings):
        hdr = col_header(entry)
        totals[hdr]           = ""
        totals[score_key(i)]  = entry["total_display"] if not entry["dq"] else "DQ"
        cut_row[hdr]          = ""
        cut_row[score_key(i)] = f"{entry['makers']}/{TOTAL_PICKS}"
    table_rows.append(totals)
    table_rows.append(cut_row)

    breakdown_df = pd.DataFrame(table_rows)

    # Column config
    col_cfg = {"": st.column_config.TextColumn("", width=95)}
    for i, entry in enumerate(standings):
        hdr = col_header(entry)
        col_cfg[hdr]          = st.column_config.TextColumn(hdr,          width=name_w)
        col_cfg[score_key(i)] = st.column_config.TextColumn(" ",          width=score_w)
    n_rows = len(breakdown_df)

    # Style the last two rows green
    def _style_summary(df):
        styles = pd.DataFrame("", index=df.index, columns=df.columns)
        green = "background-color: #002868; color: #ffffff; font-weight: 600;"
        for col in df.columns:
            styles.iloc[-2, df.columns.get_loc(col)] = green
            styles.iloc[-1, df.columns.get_loc(col)] = green
        return styles

    styled = breakdown_df.style.apply(_style_summary, axis=None)
    st.dataframe(styled, use_container_width=True, hide_index=True,
                 column_config=col_cfg, height=35 * n_rows + 38)


def _score_html(val: str, score_int: int | None = None) -> str:
    """Return an HTML span with Masters score coloring.
    Red = under par, black = even, dark grey = over par.
    """
    if val in (None, "", "—", "-"):
        return '<span style="color:#888;">—</span>'
    try:
        n = int(score_int) if score_int is not None else int(val)
    except (ValueError, TypeError):
        n = None
    if n is None:
        return f'<span style="color:#333;">{val}</span>'
    if n < 0:
        color = "#c8102e"   # red for under par
    elif n == 0:
        color = "#1a1a1a"   # near-black for Even
    else:
        color = "#1a1a1a"   # over par stays dark
    display = val if val else (_fmt(n))
    return f'<span style="color:{color}; font-weight:700;">{display}</span>'


def render_leaderboard_view(lb_data, lb_error):
    st.markdown('<div class="page-title">Tournament Leaderboard</div>', unsafe_allow_html=True)

    if lb_error:
        st.warning(lb_error)
        st.info("Live scoring will appear automatically once the tournament starts.")
        return

    if not lb_data or lb_data["leaderboard"].empty:
        st.info("🏌️ No scores yet — the tournament hasn't started.")
        return

    lb         = lb_data["leaderboard"]
    round_num  = lb_data.get("round", 1)
    status_str = lb_data.get("status", "")

    active = lb[lb["made_cut"]].copy()
    cut    = lb[~lb["made_cut"]].copy()

    # Sort active: started players (thru != "—") best score first, not-started last
    active["_started"] = active["thru"].apply(lambda t: 0 if str(t) not in ("—", "", "0") else 1)
    active = active.sort_values(["_started", "score_int"]).drop(columns=["_started"])

    # Which round columns have data?
    round_cols = [r for r in ["R1", "R2", "R3", "R4"]
                  if r in lb.columns and lb[r].notna().any()]

    # ── Cut line info ─────────────────────────────────────────────────────────
    cut_line_html = ""
    if round_num >= 2:
        if lb_data.get("cut_score") is not None:
            cut_line_html = f'<span style="color:#c8102e;font-weight:700;">&#9986; Cut: {_fmt(lb_data["cut_score"])}</span>'
        elif not active.empty:
            worst = int(active["score_int"].max())
            cut_line_html = f'<span style="color:#c8102e;font-weight:700;">&#9986; Proj. Cut: {_fmt(worst)} or better</span>'

    # ── Build rows ────────────────────────────────────────────────────────────
    r_headers = "".join(f'<th style="text-align:center;padding:8px 6px;background:#1a3570;color:#f0f5ff;font-size:0.72rem;font-weight:700;letter-spacing:.10em;border-right:1px solid #2a4a8a;white-space:nowrap;">{r}</th>' for r in round_cols)

    def score_cell(val, score_int=None):
        if val in (None, "", "—", "-", "nan"):
            return '<span style="color:#888;">—</span>'
        try:
            n = int(score_int) if score_int is not None else int(val)
        except (ValueError, TypeError):
            n = None
        color = "#c8102e" if (n is not None and n < 0) else "#1a1a1a"
        return f'<span style="color:{color};font-weight:700;">{val}</span>'

    def build_rows(df, grey=False):
        out = ""
        for i, (_, row) in enumerate(df.iterrows()):
            bg = "#e4edf8" if (i % 2 == 1) else "#f0f5ff"
            if grey:
                bg = "#d8e4f4" if (i % 2 == 1) else "#dce8f4"
            score_int = row.get("score_int", None)
            try:
                score_int = int(score_int)
            except (ValueError, TypeError):
                score_int = None
            today_val = str(row.get("today", "—"))
            try:
                today_int = int(today_val)
            except (ValueError, TypeError):
                today_int = None
            r_cells = ""
            for r in round_cols:
                rv = row.get(r, "—")
                try:
                    rv_int = int(rv)
                except (ValueError, TypeError):
                    rv_int = None
                rv_str = str(rv) if rv not in ("—", "", None) else "—"
                r_cells += f'<td style="text-align:center;padding:7px 6px;border-right:1px solid #c0cce4;">{score_cell(rv_str, rv_int)}</td>'
            opacity = ' opacity:0.7;' if grey else ''
            out += f"""<tr style="background:{bg};border-bottom:1px solid #c0cce4;{opacity}">
              <td style="text-align:center;padding:7px 8px;font-weight:700;color:#444;font-size:0.82rem;border-right:1px solid #c0cce4;min-width:38px;">{row.get("position","—")}</td>
              <td style="text-align:left;padding:7px 12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;font-size:0.85rem;border-right:1px solid #c0cce4;min-width:170px;">{row.get("name","")}</td>
              <td style="text-align:center;padding:7px 6px;border-right:1px solid #c0cce4;">{score_cell(str(row.get("score","—")), score_int)}</td>
              <td style="text-align:center;padding:7px 6px;border-right:1px solid #c0cce4;">{score_cell(today_val, today_int)}</td>
              <td style="text-align:center;padding:7px 6px;border-right:1px solid #c0cce4;">{row.get("thru","—")}</td>
              {r_cells}
            </tr>"""
        return out

    active_rows = build_rows(active)

    cut_section = ""
    if not cut.empty:
        n_cols = 5 + len(round_cols)
        cut_section = f"""
        <tr>
          <td colspan="{n_cols}" style="background:#1a3570;color:#f0f5ff;font-size:0.72rem;font-weight:700;letter-spacing:.10em;text-align:center;padding:6px;">
            &#9986;&nbsp; MISSED CUT / WD / DQ &nbsp;({len(cut)} players)
          </td>
        </tr>
        {build_rows(cut, grey=True)}"""

    refresh_note = f"Round {round_num} of 4 &nbsp;·&nbsp; refreshes every {REFRESH_INTERVAL_SECONDS}s &nbsp;·&nbsp; data via ESPN"
    if status_str:
        refresh_note = f"{status_str} &nbsp;·&nbsp; {refresh_note}"

    cut_bar = f'<div style="text-align:center;padding:5px 0 3px;font-size:0.82rem;background:#f0f5ff;border-bottom:1px solid #c0cce4;">{cut_line_html}</div>' if cut_line_html else ""

    # Sticky-header columns
    th_style = "position:sticky;top:0;z-index:2;background:#1a3570;color:#f0f5ff;font-size:0.72rem;font-weight:700;letter-spacing:.10em;padding:8px 6px;border-right:1px solid #2a4a8a;white-space:nowrap;"
    n_rows     = len(active) + len(cut)
    # Full height — no cap, show every player without internal scrolling
    tbl_height = 34 + n_rows * 34 + (0 if cut.empty else 42)

    full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: linear-gradient(180deg, #c8dff5 0%, #5a9fd4 30%, #1a3a8a 70%, #002868 100%);
    padding: 22px 10px 28px 10px;
    font-family: Arial, Helvetica, sans-serif;
  }}
  .board {{
    max-width: 820px;
    margin: 0 auto;
    background: #f0f5ff;
    border: 6px solid #1a3570;
    border-radius: 4px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    overflow: hidden;
  }}
  .cap {{
    background: #f0f5ff;
    border-bottom: 3px solid #1a3570;
    text-align: center;
    padding: 12px 0 8px 0;
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 1.9rem;
    font-weight: 900;
    letter-spacing: .18em;
    color: #1a1a1a;
  }}
  .badge {{
    display: inline-block;
    background: #002868;
    color: #fff;
    font-family: Arial, sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: .08em;
    padding: 3px 10px;
    border-radius: 12px;
    margin-left: 12px;
    vertical-align: middle;
    position: relative;
    top: -3px;
  }}
  .scroll-wrap {{
    overflow-y: visible;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
  }}
  thead th {{
    position: sticky;
    top: 0;
    z-index: 2;
  }}
  .footer {{
    background: #1a3570;
    color: #b8cce8;
    text-align: center;
    font-size: 0.68rem;
    padding: 6px;
    letter-spacing: .05em;
  }}
</style>
</head>
<body>
<div class="board">
  <div class="cap">U.S. OPEN <span class="badge">ROUND {round_num}</span></div>
  {cut_bar}
  <div class="scroll-wrap">
    <table>
      <thead>
        <tr>
          <th style="{th_style}text-align:center;min-width:38px;">POS</th>
          <th style="{th_style}text-align:left;padding-left:12px;min-width:170px;">PLAYER</th>
          <th style="{th_style}text-align:center;">TOTAL</th>
          <th style="{th_style}text-align:center;">TODAY</th>
          <th style="{th_style}text-align:center;">THRU</th>
          {r_headers}
        </tr>
      </thead>
      <tbody>
        {active_rows}
        {cut_section}
      </tbody>
    </table>
  </div>
  <div class="footer">{refresh_note}</div>
</div>
</body>
</html>"""

    # height = background padding + board header + table content + footer
    iframe_height = 22 + 28 + 58 + tbl_height + 30 + 60
    components.html(full_html, height=iframe_height, scrolling=False)


def render_prizes_view(picks_df, lb_data):
    st.markdown('<div class="page-title">Prize Pool</div>', unsafe_allow_html=True)

    lb = lb_data["leaderboard"] if lb_data else pd.DataFrame()
    current_round = lb_data.get("round", 1) if lb_data else 0

    participants = len(picks_df)
    total_pool   = participants * BUY_IN

    m1, m2 = st.columns(2)
    with m1: st.metric("Participants", participants)
    with m2: st.metric("Total Payout", f"${total_pool:,}")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    round_label_map = {
        "1st Round Leader": 1,
        "2nd Round Leader": 2,
        "3rd Round Leader": 3,
    }

    for label, pct in PRIZES.items():
        amount = int(round(pct * total_pool))
        leader_str = ""
        if label in round_label_map and not picks_df.empty and not lb.empty:
            rnd = round_label_map[label]
            # Only show winner once that round is fully complete (round has advanced past it)
            if current_round > rnd:
                ldr = get_round_leader(picks_df, lb, rnd)
                if ldr:
                    leader_str = f"→ {ldr}"
        elif label in ("Champion", "Runner Up") and not picks_df.empty and lb_data and lb_data.get("status") == "Final":
            stds = calculate_standings(picks_df, lb_data)
            active_s = [s for s in stds if not s["dq"]]
            if label == "Champion" and len(active_s) >= 1:
                leader_str = f"→ 🏆 {active_s[0]['participant']} ({active_s[0]['total_display']})"
            elif label == "Runner Up" and len(active_s) >= 2:
                leader_str = f"→ {active_s[1]['participant']} ({active_s[1]['total_display']})"

        pct_display = f"{int(pct * 100)}%"
        st.markdown(f"""
        <div class="prize-card">
            <div style="display:flex; justify-content:space-between; align-items:baseline;">
                <span class="prize-card-label">{label}</span>
                <span class="prize-card-amount">${amount:,} <span style="font-size:0.85rem; color:#888;">({pct_display})</span></span>
            </div>
            {"<div class='prize-card-leader'>" + leader_str + "</div>" if leader_str else ""}
        </div>
        """, unsafe_allow_html=True)


def render_odds_view():
    st.markdown('<div class="page-title">Player Tiers</div>', unsafe_allow_html=True)
    st.caption("Players grouped by draft tier — each participant picks from every tier.")

    for tier, players in TIERS.items():
        st.markdown(f"**{tier}**")
        df = pd.DataFrame({"Player": players})
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={"Player": st.column_config.TextColumn("Player", width=260)},
            height=35 * len(df) + 38,
        )
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)


def _render_my_picks(name: str, pin: str, picks_df: pd.DataFrame):
    """Show a read-only summary of one participant's picks after verifying their PIN."""
    if picks_df.empty:
        return
    row = picks_df[picks_df["Name"].str.strip().str.lower() == name.strip().lower()]
    if row.empty:
        st.info("No picks found for that name — check the spelling matches what you submitted.")
        return
    row = row.iloc[0]
    stored_pin = str(row.get("PIN", "") or "").strip()
    # If a PIN was set, verify it; if no PIN was stored, allow access freely
    if stored_pin and pin.strip() != stored_pin:
        st.error("❌ Incorrect PIN — please try again.")
        return
    st.success(f"✅ Picks on file for **{name}**")
    for tier in TIERS.keys():
        val = str(row.get(tier, "") or "").strip()
        if val:
            st.markdown(f"**{tier}:** {val}")


def render_submit_view(picks_df):
    st.markdown('<div class="page-title">Submit Your Picks</div>', unsafe_allow_html=True)
    locked = picks_are_locked()

    # ── Locked: picks are hidden, but let people look up their own ────────────
    if locked:
        st.warning("🔒 **Picks are locked** — the U.S. Open has started. Picks are hidden until the tournament ends.")
        st.markdown("#### View Your Picks")
        name_lookup = st.text_input("Your name:", placeholder="First Last")
        pin_lookup  = st.text_input("Your PIN:", placeholder="4 digits", max_chars=4)
        if name_lookup.strip() and pin_lookup.strip():
            _render_my_picks(name_lookup.strip(), pin_lookup.strip(), picks_df)
        return

    # ── Pre-tournament: submit / update picks ─────────────────────────────────
    n_single = sum(1 for t, n in PICKS_PER_TIER.items() if n == 1)
    n_combo  = sum(n for t, n in PICKS_PER_TIER.items() if n > 1)
    combo_tier = next(t for t, n in PICKS_PER_TIER.items() if n > 1)
    st.info(
        f"Pick **1 player from each of Tiers 1–{n_single}**, then "
        f"**{n_combo} players from the {combo_tier} pool**. "
        f"Total: {TOTAL_PICKS} picks. You can resubmit to update before Round 1 starts."
    )

    # ── Load existing picks to pre-fill form ──────────────────────────────────
    with st.expander("👀 Already submitted? Load your picks to edit them", expanded=True):
        if picks_df.empty:
            st.info("No submissions on file yet.")
        else:
            existing_names = sorted(picks_df["Name"].str.strip().dropna().unique().tolist())
            name_check = st.selectbox(
                "Select your name:",
                options=["— select —"] + existing_names,
                key="name_check",
            )
            pin_check = st.text_input("Your PIN:", placeholder="4 digits", max_chars=4, key="pin_check")

            if name_check != "— select —" and pin_check.strip() and not picks_df.empty:
                row_match = picks_df[picks_df["Name"].str.strip() == name_check]
                if row_match.empty:
                    st.info("No picks found — try selecting a different name.")
                else:
                    row_data = row_match.iloc[0]
                    stored_pin = str(row_data.get("PIN", "") or "").strip()
                    if stored_pin and pin_check.strip() != stored_pin:
                        st.error("❌ Incorrect PIN — please try again.")
                    else:
                        st.success(f"✅ Picks found for **{name_check}** — click below to load them into the form.")
                        if st.button("✏️ Load my picks into the form", type="primary"):
                            # Pre-fill session state for each tier widget
                            for tier in TIERS.keys():
                                val = str(row_data.get(tier, "") or "").strip()
                                selections = [v.strip() for v in val.split(",") if v.strip()]
                                n = PICKS_PER_TIER[tier]
                                if n == 1:
                                    st.session_state[f"pick_{tier}"] = selections[0] if selections else "— select —"
                                else:
                                    # Truncate to current max in case picks were saved under old rules
                                    st.session_state[f"pick_{tier}"] = selections[:n]
                            # Pre-fill name and PIN
                            st.session_state["prefill_name"] = name_check
                            st.session_state["prefill_pin"]  = pin_check.strip()
                            st.rerun()

    with st.expander("✏️ First Time Entry", expanded=True):
        st.caption("New to the pool? Fill out your picks below and hit Submit.")

    with st.form("picks_form"):
        participant_name = st.text_input(
            "Your Name *",
            placeholder="First Last",
            value=st.session_state.get("prefill_name", ""),
        )
        participant_pin = st.text_input(
            "Your 4-digit PIN *",
            placeholder="e.g. 1234",
            max_chars=4,
            value=st.session_state.get("prefill_pin", ""),
            help="You'll need this PIN to view or edit your picks later.",
        )

        all_picks: dict[str, list] = {}
        for tier, players in TIERS.items():
            n = PICKS_PER_TIER[tier]
            if n == 1:
                options = ["— select —"] + players
                current = st.session_state.get(f"pick_{tier}", "— select —")
                idx = options.index(current) if current in options else 0
                st.markdown(f"**{tier}**")
                choice = st.radio(tier, options=options, index=idx,
                                  label_visibility="collapsed", key=f"pick_{tier}", horizontal=True)
                all_picks[tier] = [] if choice == "— select —" else [choice]
            else:
                current = st.session_state.get(f"pick_{tier}", [])
                st.markdown(f"**{tier}** — pick any {n}")
                choices = st.multiselect(tier, options=players, default=current, max_selections=n,
                                         label_visibility="collapsed", key=f"pick_{tier}")
                all_picks[tier] = choices

        submitted = st.form_submit_button("🏌️ Submit My Picks", type="primary", use_container_width=True)
        if submitted:
            errors = []
            if not participant_name.strip():
                errors.append("Please enter your name.")
            if not participant_pin.strip().isdigit() or len(participant_pin.strip()) != 4:
                errors.append("Please choose a 4-digit PIN (numbers only).")
            for tier, n in PICKS_PER_TIER.items():
                chosen = len(all_picks.get(tier, []))
                if chosen != n:
                    errors.append(f"**{tier}**: need {n} pick{'s' if n>1 else ''} (you picked {chosen})")
            if errors:
                for err in errors:
                    st.error(err)
            else:
                if save_picks(participant_name.strip(), all_picks, pin=participant_pin.strip()):
                    # Clear prefill state after successful save
                    for key in ["prefill_name", "prefill_pin"] + [f"pick_{t}" for t in TIERS.keys()]:
                        st.session_state.pop(key, None)
                    st.success(f"✅ Picks saved for **{participant_name.strip()}**! Remember your PIN: **{participant_pin.strip()}** 🤞")
                    st.balloons()


def render_distribution_view(picks_df):
    st.markdown('<div class="page-title">Pick Distribution</div>', unsafe_allow_html=True)

    if not picks_are_locked():
        st.info("🔒 Pick distribution will be revealed when the Masters begins.")
        return

    if picks_df.empty:
        st.info("No picks submitted yet.")
        return

    # Count how many times each player was picked across all tiers
    player_counts: dict[str, int] = {}
    total_participants = len(picks_df)

    for tier in TIERS.keys():
        for _, row in picks_df.iterrows():
            val = str(row.get(tier, "") or "").strip()
            players = [p.strip() for p in val.split(",") if p.strip()]
            for player in players:
                player_counts[player] = player_counts.get(player, 0) + 1

    if not player_counts:
        st.info("No pick data found.")
        return

    rows = []
    for player, count in sorted(player_counts.items(), key=lambda x: -x[1]):
        pct = (count / total_participants * 100) if total_participants else 0
        rows.append({
            "Player":      player,
            "# Picked":    count,
            "% of Pool":   f"{pct:.0f}%",
        })

    dist_df = pd.DataFrame(rows)
    st.dataframe(
        dist_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Player":   st.column_config.TextColumn("Player",    width=220),
            "# Picked": st.column_config.NumberColumn("# Picked", width=100),
            "% of Pool": st.column_config.TextColumn("% of Pool", width=100),
        },
        height=35 * len(dist_df) + 38,
    )


def render_chat_view():
    render_scottie_header()
    st.markdown('<div class="page-title">Pool Chat</div>', unsafe_allow_html=True)
    st.caption("Chat with the rest of the pool — messages refresh every 15 seconds.")

    messages = load_chat_messages()

    # ── Message feed ──────────────────────────────────────────────────────────
    if messages.empty:
        st.info("No messages yet — be the first to say something! 👇")
    else:
        # Show oldest → newest, render as bubbles
        bubbles_html = '<div class="chat-container">'
        for _, msg in messages.iterrows():
            name = str(msg.get("Name", "")).strip() or "Anonymous"
            text = str(msg.get("Message", "")).strip()
            time = str(msg.get("Timestamp", "")).strip()
            if not text:
                continue
            # Show just the time portion (HH:MM) for readability
            time_short = time.split(" ")[-1] if " " in time else time
            bubbles_html += f"""
            <div class="chat-bubble">
                <span class="chat-bubble-name">{name}</span>
                <span class="chat-bubble-time">{time_short}</span>
                <div class="chat-bubble-text">{text}</div>
            </div>"""
        bubbles_html += "</div>"
        st.markdown(bubbles_html, unsafe_allow_html=True)

    # ── Send form ─────────────────────────────────────────────────────────────
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([1, 3])
        with col1:
            sender_name = st.text_input("Your name", placeholder="First Last",
                                        value=st.session_state.get("chat_name", ""))
        with col2:
            message_text = st.text_input("Message", placeholder="Type something…", max_chars=300)
        send = st.form_submit_button("Send 💬", type="primary", use_container_width=True)
        if send:
            if not sender_name.strip():
                st.error("Please enter your name.")
            elif not message_text.strip():
                st.error("Message can't be empty.")
            else:
                st.session_state["chat_name"] = sender_name.strip()
                if save_chat_message(sender_name.strip(), message_text.strip()):
                    st.rerun()


# ── MAIN ──────────────────────────────────────────────────────────────────────
st_autorefresh(interval=REFRESH_INTERVAL_SECONDS * 1000, key="auto_refresh")

# ── ROUTING — read view from query params ────────────────────────────────────
view = st.query_params.get("view", "standings")

# Fetch data
lb_data, lb_error = fetch_leaderboard()
picks_df     = load_picks()
using_sheets = get_worksheet() is not None

tournament_name = "Masters Tournament"
status_str  = lb_data["status"] if lb_data else ""
status_icon = {"In Progress": "🟢", "Final": "🏁", "Scheduled": "🕐"}.get(status_str, "")
now_str     = datetime.now(pytz.timezone("America/New_York")).strftime("%I:%M %p ET")

# ── TOP NAV BAR — fixed white bar with real HTML text links ──────────────────
submit_href = "?_a=1&view=submit"

st.markdown(f"""
<div class="masters-topnav">
    <div class="topnav-left">
        <div class="nav-menu-wrapper">
            <a class="nav-link">☰&nbsp; Menu</a>
            <div class="nav-dropdown">
                <a href="?_a=1&view=standings"    class="dropdown-item" target="_self">Pool Standings</a>
                <a href="?_a=1&view=leaderboard" class="dropdown-item" target="_self">Tournament Leaderboard</a>
                <a href="?_a=1&view=prizes"      class="dropdown-item" target="_self">Prize Pool</a>
                <a href="?_a=1&view=odds"        class="dropdown-item" target="_self">Player Tiers</a>
                <a href="?_a=1&view=distribution" class="dropdown-item" target="_self">Pick Distribution</a>
                <a href="?_a=1&view=chat"        class="dropdown-item" target="_self">💬 Pool Chat</a>
            </div>
        </div>
        <a href="{submit_href}" class="nav-link" target="_self">✏️&nbsp; Submit Picks</a>
    </div>
    <div class="topnav-center">
        <img src="https://www.masters.com/favicon.ico" height="20"
             style="vertical-align:middle; margin-right:8px; image-rendering:crisp-edges;">
        {POOL_NAME}
    </div>
    <div class="topnav-right">
        {"" if not status_icon else status_icon + "&nbsp;"}{tournament_name}&nbsp;·&nbsp;{now_str}
    </div>
</div>
""", unsafe_allow_html=True)

if not using_sheets:
    st.warning("⚠️ **Demo mode** — picks stored in session only.")

# ── PAGE ROUTING ──────────────────────────────────────────────────────────────
if   view == "standings":   render_standings_view(picks_df, lb_data, lb_error)
elif view == "leaderboard": render_leaderboard_view(lb_data, lb_error)
elif view == "prizes":      render_prizes_view(picks_df, lb_data)
elif view == "odds":        render_odds_view()
elif view == "distribution": render_distribution_view(picks_df)
elif view == "chat":        render_chat_view()
elif view == "submit":      render_submit_view(picks_df)
