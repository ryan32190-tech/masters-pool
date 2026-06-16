# ──────────────────────────────────────────────────────────────────────────────
# config.py  –  US Open Pool Configuration
#
# This is the main file you edit each year. Update tiers from Vegas odds,
# adjust the prize structure, and you're done.
# ──────────────────────────────────────────────────────────────────────────────

POOL_NAME = "US Open Pool 2026"

# ── SCORING RULES ─────────────────────────────────────────────────────────────
# Each participant picks 14 players (see TIERS below for how many per tier).
# Only the 8 BEST (lowest) scores among their picks count toward their total.
# If fewer than 8 of their 14 picks make the cut, they are DISQUALIFIED.
TOTAL_PICKS = 14
SCORING_PICKS = 8   # Best N scores count

# ── TIER STRUCTURE ────────────────────────────────────────────────────────────
# Tiers 1–11: pick exactly 1 player from each.
# Tiers 12–14: combined longshot pool — pick any 3 from the list.
#
# Updated June 15, 2026 from FanDuel / CBS Sports odds.

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

# Player lists — updated from FanDuel odds (CBS Sports, June 14 2026).
TIERS = {
    # ── 2026 U.S. Open at Shinnecock Hills — tiered by Vegas odds ─────────────
    "Tier 1": [
        "Scottie Scheffler",   # +550
        "Rory McIlroy",        # +1200
    ],
    "Tier 2": [
        "Jon Rahm",            # +1300
        "Tommy Fleetwood",     # +2000
        "Xander Schauffele",   # +2000
    ],
    "Tier 3": [
        "Ludvig Aberg",        # +2200
        "Bryson DeChambeau",   # +2200
        "Cameron Young",       # +2200
        "Brooks Koepka",       # +2500  ⚠ hand injury — monitor status
    ],
    "Tier 4": [
        "Matthew Fitzpatrick", # +2700
        "Collin Morikawa",     # +3500
        "Sam Burns",           # +3500
    ],
    "Tier 5": [
        "Justin Rose",         # +4000
        "Tyrrell Hatton",      # +4000
        "Russell Henley",      # +4000
        "Wyndham Clark",       # +4000
        "Justin Thomas",       # +4000
    ],
    "Tier 6": [
        "Si Woo Kim",          # +4500
        "Christopher Gotterup", # +5000
        "Viktor Hovland",      # +5000
        "Patrick Cantlay",     # +5500
        "Patrick Reed",        # +5500
        "Hideki Matsuyama",    # +5500
    ],
    "Tier 7": [
        "Robert MacIntyre",    # +6000
        "Shane Lowry",         # +6000
        "Jordan Spieth",       # +6500
        "J.J. Spaun",          # +6500  (defending champion)
        "Joaquin Niemann",     # +7000
    ],
    "Tier 8": [
        "Min Woo Lee",         # +8000
        "Ben Griffin",         # +8000
    ],
    "Tier 9": [
        "Jake Knapp",          # +10000
        "Akshay Bhatia",       # +10000
        "Aaron Rai",           # +10000  (2026 PGA Championship winner)
        "Harris English",      # +10000
        "Alex Fitzpatrick",    # +10000
    ],
    "Tier 10": [
        "Maverick McNealy",    # +10000
        "Cameron Smith",       # +10000
        "Gary Woodland",       # +10000
        "Ryan Gerard",         # +10000
        "Nicolai Hojgaard",    # +10000
    ],
    "Tier 11": [
        "Adam Scott",          # +10000
        "Jackson Koivun",      # +10000
        "Kristoffer Reitan",   # +10000
        "Sepp Straka",         # +10000
        "Kurt Kitayama",       # +10000
        "Alexander Noren",     # +10000
    ],
    "Tiers 12-14": [
        # Pick any 3 from this longshot pool
        "Sam Stevens", "Ryan Fox", "Sergio Garcia", "Max Greyserman",
        "Dustin Johnson", "Casey Jarvis", "Carlos Ortiz", "Tom McKibbin",
        "Haotong Li", "Nico Echavarria", "Rasmus Neergaard-Petersen",
        "Michael Kim", "Andrew Novak", "Aldrich Potgieter", "Michael Brennan",
        "Sami Valimaki", "Davis Riley", "Charl Schwartzel", "Ben Campbell",
        "Ethan Fang", "Danny Willett", "Mason Howell", "Mateo Pulcini",
        "Jackson Herrington", "Naoyuki Kataoka", "Brandon Wu",
        "Sungjae Im", "Keegan Bradley", "Daniel Berger", "Corey Conners",
        "Jacob Bridgeman", "Rasmus Hojgaard",
    ],
}

# ── PRIZE STRUCTURE ───────────────────────────────────────────────────────────
BUY_IN = 100   # Per person (displayed for reference)

PRIZES = {
    "1st Round Leader": 200,
    "2nd Round Leader": 200,
    "3rd Round Leader": 200,
    "Champion":        1500,
    "Runner Up":        500,
    "3rd Overall":      200,
}

# ── LEADERBOARD API ───────────────────────────────────────────────────────────
ESPN_URL = "https://site.api.espn.com/apis/site/v2/sports/golf/leaderboard?league=pga"
REFRESH_INTERVAL_SECONDS = 60

# ── ODDS API ──────────────────────────────────────────────────────────────────
ODDS_API_URL = (
    "https://api.the-odds-api.com/v4/sports/golf_us_open_championship_winner/odds"
    "?regions=us&markets=outrights&oddsFormat=american"
)
ODDS_PREFERRED_BOOK = "draftkings"

# ── GOOGLE SHEETS ─────────────────────────────────────────────────────────────
PICKS_SHEET_TAB = "Picks"
CHAT_SHEET_TAB  = "Chat"

# ── TOURNAMENT DATES ──────────────────────────────────────────────────────────
# Picks lock automatically at midnight ET on June 18 (start of tournament day).
# Set LOCK_PICKS_ON_START = True to force-lock immediately (use morning of R1).
FIRST_ROUND_START = "2026-06-18 00:01"   # Eastern Time
LOCK_PICKS_ON_START = False              # ← False = open for picks until June 18

# ── PSA / ANNOUNCEMENT BANNER ─────────────────────────────────────────────────
# Displayed at the top of the Pool Standings page. Set to "" to hide it.
PSA_MESSAGE = "US Open Pool is OPEN! Submit your picks before June 18. Good luck at Shinnecock! 🏌️"
