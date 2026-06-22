
import json
import joblib
import pandas as pd
import numpy as np

from src.data_loader import load_all_data
from src.data_cleaning import clean_all_data
from src.team_analytics import (
    get_head_to_head,
    get_team_venue_record,
    get_recent_form,
    get_winning_streak,
    get_last_n_season_winrate,
    get_chasing_defending_strength,
    get_venue_chasing_defending_record,
    get_team_weakness
)
from src.player_analytics import (
    get_team_overall_strength,
    get_individual_contribution
)


pre_toss_model = joblib.load("models/pre_toss_model.pkl")
post_toss_model = joblib.load("models/post_toss_model.pkl")

matches, deliveries, players, seasons = clean_all_data(*load_all_data())


def make_json_safe(value):
    if isinstance(value, dict):
        return {str(k): make_json_safe(v) for k, v in value.items()}

    if isinstance(value, list):
        return [make_json_safe(item) for item in value]

    if isinstance(value, tuple):
        return tuple(make_json_safe(item) for item in value)

    if isinstance(value, (np.integer,)):
        return int(value)

    if isinstance(value, (np.floating,)):
        return float(value)

    if pd.isna(value) if not isinstance(value, (dict, list, tuple)) else False:
        return None

    return value


def load_metrics(path):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


pre_toss_metrics = load_metrics("metrics/pre_toss_metrics.json")
post_toss_metrics = load_metrics("metrics/post_toss_metrics.json")


def get_city_for_venue(venue):
    venue_matches = matches[matches["venue"] == venue]

    if venue_matches.empty:
        return "Unknown"

    city_counts = venue_matches["city"].dropna().value_counts()

    if city_counts.empty:
        return "Unknown"

    return city_counts.index[0]


def get_h2h_percentage(h2h, team):
    return h2h.get(f"{team}_win_percentage", 50.0)


def build_pre_toss_input(team1, team2, venue, city, season, stage, is_day_night):
    h2h = get_head_to_head(matches, team1, team2)

    team1_venue = get_team_venue_record(matches, team1, venue)
    team2_venue = get_team_venue_record(matches, team2, venue)

    team1_recent = get_recent_form(matches, team1)
    team2_recent = get_recent_form(matches, team2)

    team1_strength = get_team_overall_strength(deliveries, team1)
    team2_strength = get_team_overall_strength(deliveries, team2)

    return pd.DataFrame([{
        "season": season,
        "stage": stage,
        "venue": venue,
        "city": city,
        "team1": team1,
        "team2": team2,
        "is_day_night": int(is_day_night),

        "team1_h2h_winrate": get_h2h_percentage(h2h, team1),
        "team2_h2h_winrate": get_h2h_percentage(h2h, team2),

        "team1_venue_winrate": team1_venue["win_percentage"],
        "team2_venue_winrate": team2_venue["win_percentage"],

        "team1_recent_form": team1_recent["win_percentage"],
        "team2_recent_form": team2_recent["win_percentage"],

        "team1_winning_streak": get_winning_streak(matches, team1),
        "team2_winning_streak": get_winning_streak(matches, team2),

        "team1_last_3_year_winrate": get_last_n_season_winrate(
            matches, team1, season, n=3
        ),
        "team2_last_3_year_winrate": get_last_n_season_winrate(
            matches, team2, season, n=3
        ),

        "team1_batting_strength": team1_strength["batting_strength"],
        "team2_batting_strength": team2_strength["batting_strength"],

        "team1_bowling_strength": team1_strength["bowling_strength"],
        "team2_bowling_strength": team2_strength["bowling_strength"],

        "team1_overall_strength": team1_strength["overall_strength"],
        "team2_overall_strength": team2_strength["overall_strength"]
    }])


def build_post_toss_input(
    team1,
    team2,
    venue,
    city,
    season,
    stage,
    is_day_night,
    toss_winner,
    toss_decision,
    weather,
    pitch_type
):
    base_df = build_pre_toss_input(
        team1,
        team2,
        venue,
        city,
        season,
        stage,
        is_day_night
    )

    team1_chase_defend = get_chasing_defending_strength(matches, team1)
    team2_chase_defend = get_chasing_defending_strength(matches, team2)
    venue_chase_defend = get_venue_chasing_defending_record(matches, venue)

    base_df["toss_winner"] = toss_winner
    base_df["toss_decision"] = toss_decision

    base_df["team1_toss_win"] = 1 if toss_winner == team1 else 0
    base_df["team2_toss_win"] = 1 if toss_winner == team2 else 0

    base_df["team1_chasing_strength"] = team1_chase_defend["chasing_strength_score"]
    base_df["team2_chasing_strength"] = team2_chase_defend["chasing_strength_score"]

    base_df["team1_defending_strength"] = team1_chase_defend["defending_strength_score"]
    base_df["team2_defending_strength"] = team2_chase_defend["defending_strength_score"]

    base_df["venue_chasing_success_rate"] = venue_chase_defend["chasing_win_percentage"]
    base_df["venue_defending_success_rate"] = venue_chase_defend["defending_win_percentage"]

    base_df["weather"] = weather
    base_df["pitch_type"] = pitch_type

    return base_df


def apply_weather_pitch_adjustment(
    team1_probability,
    team1,
    team2,
    toss_winner,
    toss_decision,
    weather,
    pitch_type
):
    adjustment = 0.0
    explanation = []

    chasing_team = None
    defending_team = None

    toss_decision = toss_decision.lower()
    weather = weather.lower()
    pitch_type = pitch_type.lower()

    if toss_decision == "field":
        chasing_team = toss_winner
        defending_team = team2 if toss_winner == team1 else team1

    elif toss_decision == "bat":
        defending_team = toss_winner
        chasing_team = team2 if toss_winner == team1 else team1

    if weather in ["humid", "dew"]:
        explanation.append("Humid or dew-like conditions may support the chasing team.")
        if chasing_team == team1:
            adjustment += 0.03
        elif chasing_team == team2:
            adjustment -= 0.03

    if weather == "cloudy":
        explanation.append("Cloudy weather may assist bowlers slightly.")

    if weather == "rainy":
        explanation.append("Rainy conditions may increase match uncertainty.")

    if weather == "hot":
        explanation.append("Hot conditions may increase fatigue and slightly affect fielding intensity.")

    if pitch_type == "batting":
        explanation.append("Batting-friendly pitch may favor the stronger batting or chasing side.")
        if chasing_team == team1:
            adjustment += 0.02
        elif chasing_team == team2:
            adjustment -= 0.02

    if pitch_type in ["slow", "spin"]:
        explanation.append("Slow or spin-friendly pitch may favor teams better at defending.")
        if defending_team == team1:
            adjustment += 0.02
        elif defending_team == team2:
            adjustment -= 0.02

    if pitch_type == "pace":
        explanation.append("Pace-friendly pitch may benefit teams with stronger pace bowling.")

    if pitch_type == "bowling":
        explanation.append("Bowling-friendly pitch may reduce batting advantage.")

    if pitch_type == "balanced":
        explanation.append("Balanced pitch conditions are treated as mostly neutral.")

    adjusted_probability = team1_probability + adjustment
    adjusted_probability = max(0.05, min(0.95, adjusted_probability))

    if not explanation:
        explanation.append("Weather and pitch conditions treated as mostly neutral.")

    return adjusted_probability, explanation


def build_common_analysis(team1, team2, venue, season):
    team1_strength = get_team_overall_strength(deliveries, team1)
    team2_strength = get_team_overall_strength(deliveries, team2)

    analysis = {
        "head_to_head": get_head_to_head(matches, team1, team2),

        "venue_record": {
            team1: get_team_venue_record(matches, team1, venue),
            team2: get_team_venue_record(matches, team2, venue)
        },

        "recent_form": {
            team1: get_recent_form(matches, team1),
            team2: get_recent_form(matches, team2)
        },

        "winning_streak": {
            team1: get_winning_streak(matches, team1),
            team2: get_winning_streak(matches, team2)
        },

        "past_3_year_performance": {
            team1: get_last_n_season_winrate(matches, team1, season, n=3),
            team2: get_last_n_season_winrate(matches, team2, season, n=3)
        },

        "team_strength": {
            team1: team1_strength,
            team2: team2_strength
        },

        "team_weakness": {
            team1: get_team_weakness(matches, deliveries, team1, venue),
            team2: get_team_weakness(matches, deliveries, team2, venue)
        },

        "individual_contribution": {
            team1: get_individual_contribution(deliveries, team1, top_n=3),
            team2: get_individual_contribution(deliveries, team2, top_n=3)
        }
    }

    return make_json_safe(analysis)


def predict_pre_toss(team1, team2, venue, season, stage, is_day_night):
    city = get_city_for_venue(venue)

    input_df = build_pre_toss_input(
        team1,
        team2,
        venue,
        city,
        season,
        stage,
        is_day_night
    )

    team1_probability = float(pre_toss_model.predict_proba(input_df)[0][1])
    team2_probability = 1 - team1_probability

    predicted_winner = team1 if team1_probability >= team2_probability else team2

    result = {
        "match": f"{team1} vs {team2}",
        "prediction_type": "pre_toss",
        "venue": venue,
        "city": city,

        "win_probability": {
            team1: f"{round(team1_probability * 100, 2)}%",
            team2: f"{round(team2_probability * 100, 2)}%"
        },

        "predicted_winner": predicted_winner,

        "model_performance": {
            "accuracy": pre_toss_metrics.get("accuracy"),
            "f1_score": pre_toss_metrics.get("f1_score"),
            "roc_auc": pre_toss_metrics.get("roc_auc")
        },

        "analysis": build_common_analysis(team1, team2, venue, season)
    }

    return make_json_safe(result)


def predict_post_toss(
    team1,
    team2,
    venue,
    season,
    stage,
    is_day_night,
    toss_winner,
    toss_decision,
    weather,
    pitch_type
):
    city = get_city_for_venue(venue)

    input_df = build_post_toss_input(
        team1,
        team2,
        venue,
        city,
        season,
        stage,
        is_day_night,
        toss_winner,
        toss_decision,
        weather,
        pitch_type
    )

    team1_probability = float(post_toss_model.predict_proba(input_df)[0][1])

    team1_probability, condition_explanation = apply_weather_pitch_adjustment(
        team1_probability,
        team1,
        team2,
        toss_winner,
        toss_decision,
        weather,
        pitch_type
    )

    team2_probability = 1 - team1_probability

    predicted_winner = team1 if team1_probability >= team2_probability else team2

    result = {
        "match": f"{team1} vs {team2}",
        "prediction_type": "post_toss",
        "venue": venue,
        "city": city,

        "toss_winner": toss_winner,
        "toss_decision": toss_decision,
        "weather": weather,
        "pitch_type": pitch_type,

        "win_probability": {
            team1: f"{round(team1_probability * 100, 2)}%",
            team2: f"{round(team2_probability * 100, 2)}%"
        },

        "predicted_winner": predicted_winner,

        "model_performance": {
            "accuracy": post_toss_metrics.get("accuracy"),
            "f1_score": post_toss_metrics.get("f1_score"),
            "roc_auc": post_toss_metrics.get("roc_auc")
        },

        "weather_pitch_impact": condition_explanation,

        "chasing_defending_analysis": {
            team1: get_chasing_defending_strength(matches, team1),
            team2: get_chasing_defending_strength(matches, team2),
            "venue": get_venue_chasing_defending_record(matches, venue)
        },

        "analysis": build_common_analysis(team1, team2, venue, season)
    }

    return make_json_safe(result)

