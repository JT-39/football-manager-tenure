"""Club names: one spelling for each club, used across the whole project.

Wikipedia and football-data.co.uk spell many clubs differently ("Man United" and
"Manchester United", "Wolves" and "Wolverhampton Wanderers"). Everything in this
project uses the Wikipedia spelling, so the football-data names are translated
here, in one place.

If a new season file contains a name that isn't in FOOTBALL_DATA_TO_WIKIPEDIA,
the pipeline stops with an error that names it, so you can add it here.
"""

# football-data.co.uk name -> Wikipedia name
FOOTBALL_DATA_TO_WIKIPEDIA: dict[str, str] = {
    "Arsenal": "Arsenal",
    "Aston Villa": "Aston Villa",
    "Barnsley": "Barnsley",
    "Birmingham": "Birmingham City",
    "Blackburn": "Blackburn Rovers",
    "Blackpool": "Blackpool",
    "Bolton": "Bolton Wanderers",
    "Bournemouth": "Bournemouth",
    "Bradford": "Bradford City",
    "Brentford": "Brentford",
    "Brighton": "Brighton & Hove Albion",
    "Burnley": "Burnley",
    "Cardiff": "Cardiff City",
    "Charlton": "Charlton Athletic",
    "Chelsea": "Chelsea",
    "Coventry": "Coventry City",
    "Crystal Palace": "Crystal Palace",
    "Derby": "Derby County",
    "Everton": "Everton",
    "Fulham": "Fulham",
    "Huddersfield": "Huddersfield Town",
    "Hull": "Hull City",
    "Ipswich": "Ipswich Town",
    "Leeds": "Leeds United",
    "Leicester": "Leicester City",
    "Liverpool": "Liverpool",
    "Luton": "Luton Town",
    "Man City": "Manchester City",
    "Man United": "Manchester United",
    "Middlesbrough": "Middlesbrough",
    "Newcastle": "Newcastle United",
    "Norwich": "Norwich City",
    "Nott'm Forest": "Nottingham Forest",
    "Oldham": "Oldham Athletic",
    "Portsmouth": "Portsmouth",
    "QPR": "Queens Park Rangers",
    "Reading": "Reading",
    "Sheffield United": "Sheffield United",
    "Sheffield Weds": "Sheffield Wednesday",
    "Southampton": "Southampton",
    "Stoke": "Stoke City",
    "Sunderland": "Sunderland",
    "Swansea": "Swansea City",
    "Swindon": "Swindon Town",
    "Tottenham": "Tottenham Hotspur",
    "Watford": "Watford",
    "West Brom": "West Bromwich Albion",
    "West Ham": "West Ham United",
    "Wigan": "Wigan Athletic",
    "Wimbledon": "Wimbledon",
    "Wolves": "Wolverhampton Wanderers",
}

# The 22 clubs in the first Premier League season, 1992–93. football-data.co.uk
# has no file for that season, so it is entered here. Source: the 1992–93 FA
# Premier League article on Wikipedia.
FOUNDING_CLUBS_1992: list[str] = [
    "Arsenal",
    "Aston Villa",
    "Blackburn Rovers",
    "Chelsea",
    "Coventry City",
    "Crystal Palace",
    "Everton",
    "Ipswich Town",
    "Leeds United",
    "Liverpool",
    "Manchester City",
    "Manchester United",
    "Norwich City",
    "Nottingham Forest",
    "Oldham Athletic",
    "Queens Park Rangers",
    "Sheffield United",
    "Sheffield Wednesday",
    "Southampton",
    "Swindon Town",
    "Tottenham Hotspur",
    "Wimbledon",
]
