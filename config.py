# ──────────────────────────────────────────────────────────────────────────────
# config.py  –  Masters Pool Configuration
#
# This is the main file you edit each year. Update tiers from Vegas odds,
# adjust the prize structure, and you're done.
# ──────────────────────────────────────────────────────────────────────────────

POOL_NAME = "Masters Pool 2026"

# ── SCORING RULES ─────────────────────────────────────────────────────────────
# Each participant picks 14 players (see TIERS below for how many per tier).
# Only the 8 BEST (lowest) scores among their picks count toward their total.
# If fewer than 8 of their 15 picks make the cut, they are DISQUALIFIED.
TOTAL_PICKS = 14
SCORING_PICKS = 8   # Best N scores count

# ── TIER STRUCTURE ────────────────────────────────────────────────────────────
# Tiers 1–11: pick exactly 1 player from each.
# Tiers 12–14: combined longshot pool — pick any 4 from the list.
#
# Update player lists each year from Vegas odds (typically 1 week before
# the tournament). Add or remove tiers by editing both TIERS and PICKS_PER_TIER.

PICKS_PER_TIER = {
    "Tier 1":      1,
    "Tier 2":      1,
    "Tier 3":      1,
    "Tier 4":      1,
    "Tier 5":      1,
    "Tier 6":      1,
    "Tier 7":      1,
    "Tier 8":      1,
    "Tier 9":      1,
    "Tier 10":     1,
    "Tier 11":     1,
    "Tiers 12-14": 3,   # Combined longshot tier — pick any 3
}

# Player lists — update these from Vegas odds before the tournament.
TIERS = {
    # ── 2026 Masters — tiered by Vegas odds ──
    "Tier 1": [
        "Scottie Scheffler",   # +410
        "Jon Rahm",            # +850
        "Rory McIlroy",        # +1025
        "Bryson DeChambeau",   # +1100
    ],
    "Tier 2": [
        "Ludvig Aberg",        # +1750
        "Xander Schauffele",   # +1850
    ],
    "Tier 3": [
        "Cameron Young",       # +2350
        "Tommy Fleetwood",     # +2500
        "Matthew Fitzpatrick", # +2600
        "Collin Morikawa",     # +3100
    ],
    "Tier 4": [
        "Justin Rose",         # +3600
        "Jordan Spieth",       # +3800
        "Brooks Koepka",       # +3800
        "Hideki Matsuyama",    # +3900
    ],
    "Tier 5": [
        "Robert MacIntyre",    # +4000
        "Russell Henley",      # +4200
        "Christopher Gotterup", # +4300
        "Patrick Reed",        # +4500
        "Viktor Hovland",      # +4600
    ],
    "Tier 6": [
        "Si Woo Kim",          # +4700
        "Min Woo Lee",         # +5400
        "Justin Thomas",       # +5500
        "Patrick Cantlay",     # +5700
        "Adam Scott",          # +6200
    ],
    "Tier 7": [
        "Akshay Bhatia",       # +6500
        "Sepp Straka",         # +6700
        "Jason Day",           # +6900
        "Jake Knapp",          # +6900
        "Tyrrell Hatton",      # +6900
        "Shane Lowry",         # +7000
    ],
    "Tier 8": [
        "Sam Burns",           # +7200
        "Corey Conners",       # +8200
        "Nicolai Hojgaard",    # +8400
        "Kurt Kitayama",       # +8800
        "Jacob Bridgeman",     # +9400
    ],
    "Tier 9": [
        "Maverick McNealy",    # +9800
        "Cameron Smith",       # +10000
        "Harris English",      # +10500
        "Gary Woodland",       # +11000
        "Ben Griffin",         # +11000
        "Daniel Berger",       # +11000
    ],
    "Tier 10": [
        "Max Homa",            # +11500
        "Sungjae Im",          # +12000
        "J. J. Spaun",         # +12000
        "Rasmus Hojgaard",     # +13000
        "Keegan Bradley",      # +14000
        "Harry Hall",          # +16000
    ],
    "Tier 11": [
        "Marco Penge",         # +16000
        "Alexander Noren",     # +16000
        "Ryan Gerard",         # +17000
        "Nick Taylor",         # +19500
        "Aaron Rai",           # +19500
        "Brian Harman",        # +20000
    ],
    "Tiers 12-14": [
        # Pick any 3 from this longshot pool
        "Sam Stevens", "Ryan Fox", "Sergio Garcia", "Wyndham Clark",
        "Max Greyserman", "Dustin Johnson", "Casey Jarvis", "Carlos Ortiz",
        "Tom McKibbin", "Haotong Li", "Nico Echavarria", "Kristoffer Reitan",
        "Rasmus Neergaard-Petersen", "John Keefer", "Michael Kim", "Andrew Novak",
        "Aldrich Potgieter", "Michael Brennan", "Sami Valimaki", "Davis Riley",
        "Charl Schwartzel", "Bubba Watson", "Zach Johnson", "Ben Campbell",
        "Ethan Fang", "Danny Willett", "Pongsapak Laopakdee", "Vijay Singh",
        "Mason Howell", "Mateo Pulcini", "Jackson Herrington", "Angel Cabrera",
        "Naoyuki Kataoka", "Brandon Wu", "Mike Weir", "Fred Couples",
        "Jose Maria Olazabal",
    ],
}

# ── PRIZE STRUCTURE ───────────────────────────────────────────────────────────
# Edit these dollar amounts each year.
# The app will display the structure and highlight the current leader for each.
#
# Format: { "Label": dollar_amount }
# Add or remove rounds as needed.

BUY_IN = 100   # Per person (displayed for reference)

PRIZES = {
    "1st Round Leader": 200,
    "2nd Round Leader": 200,
    "3rd Round Leader": 200,
    "Champion":        1500,
    "Runner Up":        400,
    "3rd Overall":      200,
}

# ── LEADERBOARD API ───────────────────────────────────────────────────────────
ESPN_URL = "https://site.api.espn.com/apis/site/v2/sports/golf/leaderboard?league=pga"
REFRESH_INTERVAL_SECONDS = 60

# ── ODDS API ──────────────────────────────────────────────────────────────────
# Sign up free at https://the-odds-api.com — add your key to .streamlit/secrets.toml
# as ODDS_API_KEY = "your_key_here"
# Free tier: 500 requests/month (well within limits at 60-second refresh)
ODDS_API_URL = (
    "https://api.the-odds-api.com/v4/sports/golf_masters_tournament_winner/odds"
    "?regions=us&markets=outrights&oddsFormat=american"
)
# Preferred bookmaker key — falls back to averaging all available books
ODDS_PREFERRED_BOOK = "draftkings"

# ── GOOGLE SHEETS ─────────────────────────────────────────────────────────────
PICKS_SHEET_TAB = "Picks"
CHAT_SHEET_TAB  = "Chat"

# ── TOURNAMENT DATES ──────────────────────────────────────────────────────────
# Picks lock when the first round starts.
FIRST_ROUND_START = "2026-04-10 00:01"   # Eastern Time — set to midnight so lock is always active
LOCK_PICKS_ON_START = True

# ── PSA / ANNOUNCEMENT BANNER ─────────────────────────────────────────────────
# Displayed at the top of the Pool Standings page. Set to "" to hide it.
PSA_MESSAGE = "The prize pool is set. Here we go."
