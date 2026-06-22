import pandas as pd

from src.team_analytics import (
    get_head_to_head,
    get_team_venue_record,
    get_recent_form,
    get_winning_streak,
    get_last_n_season_winrate,
    get_chasing_defending_strength,
    get_venue_chasing_defending_record
)

from src.player_analytics import get_team_overall_strength


def build_team_strength_cache(matches, deliveries):
    teams = sorted(list(set(matches["team1"]).union(set(matches["team2"]))))
    strength_cache = {}

    for team in teams:
        strength_cache[team] = get_team_overall_strength(deliveries, team)

    return strength_cache


def _get_h2h_win_percentage(h2h_data, team):
    key = f"{team}_win_percentage"
    return h2h_data.get(key, 50.0)


def _build_base_features(row, historical_matches, strength_cache):
    team1 = row["team1"]
    team2 = row["team2"]
    venue = row["venue"]
    current_season = row["season"]

    h2h = get_head_to_head(historical_matches, team1, team2)

    team1_venue = get_team_venue_record(historical_matches, team1, venue)
    team2_venue = get_team_venue_record(historical_matches, team2, venue)

    team1_recent = get_recent_form(historical_matches, team1, n=5)
    team2_recent = get_recent_form(historical_matches, team2, n=5)

    team1_strength = strength_cache.get(team1, {
        "batting_strength": 50.0,
        "bowling_strength": 50.0,
        "overall_strength": 50.0
    })

    team2_strength = strength_cache.get(team2, {
        "batting_strength": 50.0,
        "bowling_strength": 50.0,
        "overall_strength": 50.0
    })

    return {
        "season": current_season,
        "stage": row["stage"],
        "venue": venue,
        "city": row["city"],
        "team1": team1,
        "team2": team2,
        "is_day_night": int(row["is_day_night"]),

        "team1_h2h_winrate": _get_h2h_win_percentage(h2h, team1),
        "team2_h2h_winrate": _get_h2h_win_percentage(h2h, team2),

        "team1_venue_winrate": team1_venue["win_percentage"],
        "team2_venue_winrate": team2_venue["win_percentage"],

        "team1_recent_form": team1_recent["win_percentage"],
        "team2_recent_form": team2_recent["win_percentage"],

        "team1_winning_streak": get_winning_streak(historical_matches, team1),
        "team2_winning_streak": get_winning_streak(historical_matches, team2),

        "team1_last_3_year_winrate": get_last_n_season_winrate(
            historical_matches, team1, current_season, n=3
        ),
        "team2_last_3_year_winrate": get_last_n_season_winrate(
            historical_matches, team2, current_season, n=3
        ),

        "team1_batting_strength": team1_strength["batting_strength"],
        "team2_batting_strength": team2_strength["batting_strength"],

        "team1_bowling_strength": team1_strength["bowling_strength"],
        "team2_bowling_strength": team2_strength["bowling_strength"],

        "team1_overall_strength": team1_strength["overall_strength"],
        "team2_overall_strength": team2_strength["overall_strength"]
    }


def create_pre_toss_features(matches, deliveries, seasons=None):
    matches = matches.copy().sort_values("date").reset_index(drop=True)

    strength_cache = build_team_strength_cache(matches, deliveries)

    rows = []

    for idx, row in matches.iterrows():
        historical_matches = matches.iloc[:idx]

        if historical_matches.empty:
            continue

        feature_row = _build_base_features(
            row,
            historical_matches,
            strength_cache
        )

        feature_row["team1_win"] = 1 if row["winner"] == row["team1"] else 0

        rows.append(feature_row)

    return pd.DataFrame(rows)


def create_post_toss_features(matches, deliveries, seasons=None):
    matches = matches.copy().sort_values("date").reset_index(drop=True)

    strength_cache = build_team_strength_cache(matches, deliveries)

    rows = []

    for idx, row in matches.iterrows():
        historical_matches = matches.iloc[:idx]

        if historical_matches.empty:
            continue

        feature_row = _build_base_features(
            row,
            historical_matches,
            strength_cache
        )

        team1 = row["team1"]
        team2 = row["team2"]
        venue = row["venue"]

        team1_chase_defend = get_chasing_defending_strength(
            historical_matches,
            team1
        )

        team2_chase_defend = get_chasing_defending_strength(
            historical_matches,
            team2
        )

        venue_chase_defend = get_venue_chasing_defending_record(
            historical_matches,
            venue
        )

        feature_row.update({
            "toss_winner": row["toss_winner"],
            "toss_decision": row["toss_decision"],

            "team1_toss_win": 1 if row["toss_winner"] == team1 else 0,
            "team2_toss_win": 1 if row["toss_winner"] == team2 else 0,

            "team1_chasing_strength": team1_chase_defend["chasing_strength_score"],
            "team2_chasing_strength": team2_chase_defend["chasing_strength_score"],

            "team1_defending_strength": team1_chase_defend["defending_strength_score"],
            "team2_defending_strength": team2_chase_defend["defending_strength_score"],

            "venue_chasing_success_rate": venue_chase_defend["chasing_win_percentage"],
            "venue_defending_success_rate": venue_chase_defend["defending_win_percentage"],

            "weather": "neutral",
            "pitch_type": "balanced",

            "team1_win": 1 if row["winner"] == team1 else 0
        })

        rows.append(feature_row)

    return pd.DataFrame(rows)