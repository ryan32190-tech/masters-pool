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
# Updated June 15, 2026 from DraftKings odds.

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
    "Tiers 12-14": 3,   # Combined longshot pool — pick any 3
}

# Player lists — from DraftKings odds (June 15, 2026).
TIERS = {
    # ── Tier 1: Elite Contenders ──────────────────────────────────────────────
    "Tier 1": [
        "Scottie Scheffler",   # +455
        "Rory McIlroy",        # +940
        "Jon Rahm",            # +1025
    ],
    # ── Tier 2: Top-5 Group ───────────────────────────────────────────────────
    "Tier 2": [
        "Xander Schauffele",   # +1850
        "Cameron Young",       # +2000
        "Matthew Fitzpatrick", # +2500
        "Tommy Fleetwood",     # +2500
        "Ludvig Aberg",        # +2600
    ],
    # ── Tier 3: Major Winners Lurking ─────────────────────────────────────────
    "Tier 3": [
        "Bryson DeChambeau",   # +2700
        "Brooks Koepka",       # +2900
        "Collin Morikawa",     # +3300
    ],
    # ── Tier 4: Strong Value ──────────────────────────────────────────────────
    "Tier 4": [
        "Sam Burns",           # +3700
        "Russell Henley",      # +3700
        "Si Woo Kim",          # +3900
        "Justin Rose",         # +4200
        "Wyndham Clark",       # +4200
    ],
    # ── Tier 5: Mid-Tier Names ────────────────────────────────────────────────
    "Tier 5": [
        "Christopher Gotterup", # +4400
        "Justin Thomas",       # +4400
        "Tyrrell Hatton",      # +4500
        "Patrick Cantlay",     # +4500
        "Patrick Reed",        # +4800
    ],
    # ── Tier 6: Dark Horses ───────────────────────────────────────────────────
    "Tier 6": [
        "Viktor Hovland",      # +5300
        "J.J. Spaun",          # +6000
        "Hideki Matsuyama",    # +6400
        "Jordan Spieth",       # +6800
        "Joaquin Niemann",     # +6800
    ],
    # ── Tier 7: Sleepers ──────────────────────────────────────────────────────
    "Tier 7": [
        "Ben Griffin",         # +7200
        "Min Woo Lee",         # +7200
        "Maverick McNealy",    # +7400
        "Adam Scott",          # +7400
        "Shane Lowry",         # +7400
        "Kurt Kitayama",       # +7800
        "Robert MacIntyre",    # +7800
    ],
    # ── Tier 8: Long-Odds Names ───────────────────────────────────────────────
    "Tier 8": [
        "Harris English",      # +8600
        "Kristoffer Reitan",   # +8800
        "Jake Knapp",          # +9400
        "David Puig",          # +9400
        "Nicolai Hojgaard",    # +9600
        "Alex Smalley",        # +10000
        "Alexander Noren",     # +10000
        "Aaron Rai",           # +10000
    ],
    # ── Tier 9: Longshots ─────────────────────────────────────────────────────
    "Tier 9": [
        "Sepp Straka",         # +10500
        "Ryan Gerard",         # +11000
        "Rickie Fowler",       # +11000
        "Gary Woodland",       # +11500
        "Alex Fitzpatrick",    # +12000
        "Jason Day",           # +13000
        "Akshay Bhatia",       # +13500
        "Keegan Bradley",      # +14000
    ],
    # ── Tier 10: Big Swing ────────────────────────────────────────────────────
    "Tier 10": [
        "Keith Mitchell",      # +15000
        "Jacob Bridgeman",     # +15500
        "Jackson Koivun",      # +15500
        "Dustin Johnson",      # +16000
        "Cameron Smith",       # +16000
        "Sahith Theegala",     # +16000
        "Harry Hall",          # +16500
        "Nick Taylor",         # +16500
        "Corey Conners",       # +18000
        "Pierceson Coody",     # +18500
        "Sudarshan Yellamaraju", # +19000
    ],
    # ── Tier 11: 20k–28k ──────────────────────────────────────────────────────
    "Tier 11": [
        "Daniel Berger",       # +20000
        "Sungjae Im",          # +20000
        "Benjamin James",      # +21000
        "Davis Thompson",      # +23000
        "Brian Harman",        # +23000
        "Tom Kim",             # +23000
        "Ryo Hisatsune",       # +23000
        "Max Greyserman",      # +25000
        "Lucas Herbert",       # +25000
        "Jayden Schaper",      # +25000
        "Ryan Fox",            # +25000
        "Jackson Suber",       # +27000
        "Sam Stevens",         # +27000
        "Michael Brennan",     # +27000
        "Matt McCarty",        # +28000
        "Carlos Ortiz",        # +28000
    ],
    # ── Tiers 12–14: The Field (pick any 3) ──────────────────────────────────
    "Tiers 12-14": [
        "Andrew Putnam", "Andrew Novak", "Michael Kim",
        "Adrien Dumont de Chassart", "John Keefer", "Preston Stout",
        "Patrick Rodgers", "John Parry", "Nico Echavarria", "Max McGreevy",
        "Matthias Schmid", "Chris Kirk", "William Mouw", "Nathan Kimsey",
        "Kevin Roy", "Cooper Dossey", "Emiliano Grillo", "Neal Shipley",
        "Billy Horschel", "Ben Kohles", "Laurie Canter", "Adrien Saddier",
        "Ugo Coussaud", "Chandler Phillips", "Matthew Jordan", "Caleb Surratt",
        "Zac Blair", "Cole Hammer", "Padraig Harrington", "Taylor Montgomery",
        "Niklas Norgaard", "Dylan Wu", "Alejandro Tosti", "Carl Yuan",
        "Ben Silverman", "Peter Uihlein", "Nick Hardy", "Arni Sveinsson",
        "Jimmy Stanger", "Ethan Fang", "Eric Lee", "James Nicholas",
        "Graeme McDowell", "Taihei Sato", "Ryder Cowan", "Jackson Herrington",
        "Greyson Leach", "Jackson Ormond", "Rocco Repetto", "Logan Reilly",
        "Mateo Pulcini", "Chase Kyes", "Marcelo Rozo", "Kaito Onishi",
        "Jake Peacock", "Jackson Van Paris", "J.B. Holmes", "Filippo Celli",
        "Manav Shah", "Jake Sollon", "Brandon Wu", "Brandon Holtz",
        "Ryuichi Oiwa", "Robbie Higgins", "Vaughn Harber", "Taek Soo Kim",
        "Matt Robles", "Marek Fleming", "Hamilton Coleman",
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
