import pandas as pd


TEAM_NAME_MAP = {
    "Delhi Daredevils": "Delhi Capitals",
    "Kings XI Punjab": "Punjab Kings",
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru"
}


def standardize_team_name(name):
    if pd.isna(name):
        return name

    name = str(name).strip()
    return TEAM_NAME_MAP.get(name, name)


def clean_matches(matches):
    matches = matches.copy()

    # Remove extra spaces from column names
    matches.columns = matches.columns.str.strip()

    # Convert date column
    matches["date"] = pd.to_datetime(matches["date"], errors="coerce")

    # Keep only normal completed matches with a winner
    matches = matches.dropna(subset=["winner"])
    matches = matches[matches["result"] == "normal"]

    # Standardize team names
    team_columns = ["team1", "team2", "toss_winner", "winner"]

    for col in team_columns:
        if col in matches.columns:
            matches[col] = matches[col].apply(standardize_team_name)

    # Clean text columns
    text_columns = ["stage", "venue", "city", "toss_decision"]

    for col in text_columns:
        if col in matches.columns:
            matches[col] = matches[col].astype(str).str.strip()

    # Convert is_day_night to integer
    matches["is_day_night"] = matches["is_day_night"].astype(int)

    # Sort by date to avoid future data leakage
    matches = matches.sort_values("date").reset_index(drop=True)

    return matches


def clean_deliveries(deliveries):
    deliveries = deliveries.copy()

    deliveries.columns = deliveries.columns.str.strip()

    team_columns = ["batting_team", "bowling_team"]

    for col in team_columns:
        if col in deliveries.columns:
            deliveries[col] = deliveries[col].apply(standardize_team_name)

    text_columns = [
        "striker",
        "non_striker",
        "bowler",
        "extra_type",
        "dismissal_type",
        "dismissed_player",
        "fielder"
    ]

    for col in text_columns:
        if col in deliveries.columns:
            deliveries[col] = deliveries[col].astype(str).str.strip()

    deliveries["is_wicket"] = deliveries["is_wicket"].astype(int)

    numeric_columns = [
        "innings",
        "over",
        "ball",
        "batsman_runs",
        "extra_runs",
        "total_runs"
    ]

    for col in numeric_columns:
        if col in deliveries.columns:
            deliveries[col] = pd.to_numeric(deliveries[col], errors="coerce").fillna(0)

    return deliveries


def clean_players(players):
    players = players.copy()

    players.columns = players.columns.str.strip()

    text_columns = [
        "player_name",
        "nationality",
        "batting_style",
        "bowling_style",
        "playing_role"
    ]

    for col in text_columns:
        if col in players.columns:
            players[col] = players[col].astype(str).str.strip()

    return players


def clean_seasons(seasons):
    seasons = seasons.copy()

    seasons.columns = seasons.columns.str.strip()

    return seasons


def clean_all_data(matches, deliveries, players, seasons):
    matches = clean_matches(matches)
    deliveries = clean_deliveries(deliveries)
    players = clean_players(players)
    seasons = clean_seasons(seasons)

    return matches, deliveries, players, seasons