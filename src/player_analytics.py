import pandas as pd


def get_legal_balls(df):
    if "extra_type" in df.columns:
        return df[~df["extra_type"].isin(["wides"])]
    return df


def get_top_batters(deliveries, team, top_n=5):
    team_batting = deliveries[deliveries["batting_team"] == team].copy()

    if team_batting.empty:
        return []

    legal_balls = get_legal_balls(team_batting)

    runs = team_batting.groupby("striker")["batsman_runs"].sum()
    balls = legal_balls.groupby("striker").size()

    batting_df = pd.DataFrame({
        "runs": runs,
        "balls": balls
    }).fillna(0)

    batting_df["strike_rate"] = batting_df.apply(
        lambda x: (x["runs"] / x["balls"]) * 100 if x["balls"] > 0 else 0,
        axis=1
    )

    batting_df["batting_score"] = (
        batting_df["runs"] * 0.6 +
        batting_df["strike_rate"] * 0.4
    )

    top_batters = batting_df.sort_values(
        "batting_score",
        ascending=False
    ).head(top_n)

    return [
        {
            "player": player,
            "runs": int(row["runs"]),
            "balls": int(row["balls"]),
            "strike_rate": round(row["strike_rate"], 2),
            "batting_score": round(row["batting_score"], 2)
        }
        for player, row in top_batters.iterrows()
    ]


def get_bowler_wickets(deliveries):
    non_bowler_wickets = [
        "run out",
        "retired hurt",
        "retired out",
        "obstructing the field"
    ]

    if "dismissal_type" in deliveries.columns:
        wicket_df = deliveries[
            (deliveries["is_wicket"] == 1) &
            (~deliveries["dismissal_type"].isin(non_bowler_wickets))
        ]
    else:
        wicket_df = deliveries[deliveries["is_wicket"] == 1]

    return wicket_df


def get_top_bowlers(deliveries, team, top_n=5):
    team_bowling = deliveries[deliveries["bowling_team"] == team].copy()

    if team_bowling.empty:
        return []

    legal_balls = get_legal_balls(team_bowling)
    wicket_df = get_bowler_wickets(team_bowling)

    balls = legal_balls.groupby("bowler").size()
    runs = team_bowling.groupby("bowler")["total_runs"].sum()
    wickets = wicket_df.groupby("bowler").size()

    bowling_df = pd.DataFrame({
        "balls": balls,
        "runs_conceded": runs,
        "wickets": wickets
    }).fillna(0)

    bowling_df["overs"] = bowling_df["balls"] / 6

    bowling_df["economy"] = bowling_df.apply(
        lambda x: x["runs_conceded"] / x["overs"] if x["overs"] > 0 else 0,
        axis=1
    )

    bowling_df["bowling_score"] = (
        bowling_df["wickets"] * 25 -
        bowling_df["economy"] * 2 +
        bowling_df["balls"] * 0.05
    )

    top_bowlers = bowling_df.sort_values(
        "bowling_score",
        ascending=False
    ).head(top_n)

    return [
        {
            "player": player,
            "wickets": int(row["wickets"]),
            "runs_conceded": int(row["runs_conceded"]),
            "balls": int(row["balls"]),
            "economy": round(row["economy"], 2),
            "bowling_score": round(row["bowling_score"], 2)
        }
        for player, row in top_bowlers.iterrows()
    ]


def get_team_batting_strength(deliveries, team):
    team_batting = deliveries[deliveries["batting_team"] == team].copy()

    if team_batting.empty:
        return 50.0

    legal_balls = get_legal_balls(team_batting)

    total_runs = team_batting["batsman_runs"].sum()
    balls = len(legal_balls)
    overs = balls / 6 if balls > 0 else 0

    run_rate = total_runs / overs if overs > 0 else 0
    strike_rate = (total_runs / balls) * 100 if balls > 0 else 0

    boundaries = team_batting[
        team_batting["batsman_runs"].isin([4, 6])
    ].shape[0]

    boundary_percentage = (boundaries / balls) * 100 if balls > 0 else 0

    death_overs = team_batting[team_batting["over"] >= 16]
    death_legal_balls = get_legal_balls(death_overs)

    death_runs = death_overs["batsman_runs"].sum()
    death_balls = len(death_legal_balls)
    death_overs_count = death_balls / 6 if death_balls > 0 else 0
    death_run_rate = death_runs / death_overs_count if death_overs_count > 0 else 0

    batting_score = (
        run_rate * 4 +
        strike_rate * 0.25 +
        boundary_percentage * 1.5 +
        death_run_rate * 3
    )

    return round(min(batting_score, 100), 2)


def get_team_bowling_strength(deliveries, team):
    team_bowling = deliveries[deliveries["bowling_team"] == team].copy()

    if team_bowling.empty:
        return 50.0

    legal_balls = get_legal_balls(team_bowling)
    wicket_df = get_bowler_wickets(team_bowling)

    balls = len(legal_balls)
    overs = balls / 6 if balls > 0 else 0

    runs_conceded = team_bowling["total_runs"].sum()
    wickets = len(wicket_df)

    economy = runs_conceded / overs if overs > 0 else 0
    wicket_rate = wickets / overs if overs > 0 else 0

    dot_balls = team_bowling[team_bowling["total_runs"] == 0].shape[0]
    dot_ball_percentage = (dot_balls / balls) * 100 if balls > 0 else 0

    death_overs = team_bowling[team_bowling["over"] >= 16]
    death_legal_balls = get_legal_balls(death_overs)

    death_runs = death_overs["total_runs"].sum()
    death_balls = len(death_legal_balls)
    death_overs_count = death_balls / 6 if death_balls > 0 else 0
    death_economy = death_runs / death_overs_count if death_overs_count > 0 else economy

    bowling_score = (
        wicket_rate * 35 +
        dot_ball_percentage * 0.8 +
        max(0, 12 - economy) * 4 +
        max(0, 14 - death_economy) * 2
    )

    return round(min(bowling_score, 100), 2)


def get_team_overall_strength(deliveries, team):
    batting_strength = get_team_batting_strength(deliveries, team)
    bowling_strength = get_team_bowling_strength(deliveries, team)

    overall_strength = (batting_strength * 0.55) + (bowling_strength * 0.45)

    return {
        "team": team,
        "batting_strength": round(batting_strength, 2),
        "bowling_strength": round(bowling_strength, 2),
        "overall_strength": round(overall_strength, 2)
    }


def get_individual_contribution(deliveries, team, top_n=5):
    return {
        "team": team,
        "top_batters": get_top_batters(deliveries, team, top_n),
        "top_bowlers": get_top_bowlers(deliveries, team, top_n)
    }