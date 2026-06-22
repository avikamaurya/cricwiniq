import pandas as pd


def get_team_matches(matches, team):
    return matches[
        (matches["team1"] == team) | (matches["team2"] == team)
    ].copy()


def get_other_team(row, team):
    if row["team1"] == team:
        return row["team2"]
    return row["team1"]


def get_head_to_head(matches, team1, team2):
    h2h = matches[
        ((matches["team1"] == team1) & (matches["team2"] == team2)) |
        ((matches["team1"] == team2) & (matches["team2"] == team1))
    ]

    total = len(h2h)
    team1_wins = len(h2h[h2h["winner"] == team1])
    team2_wins = len(h2h[h2h["winner"] == team2])

    return {
        "matches_played": total,
        f"{team1}_wins": team1_wins,
        f"{team2}_wins": team2_wins,
        f"{team1}_win_percentage": round((team1_wins / total) * 100, 2) if total > 0 else 50.0,
        f"{team2}_win_percentage": round((team2_wins / total) * 100, 2) if total > 0 else 50.0
    }


def get_team_venue_record(matches, team, venue):
    team_matches = matches[
        (((matches["team1"] == team) | (matches["team2"] == team)) &
         (matches["venue"] == venue))
    ]

    total = len(team_matches)
    wins = len(team_matches[team_matches["winner"] == team])

    return {
        "team": team,
        "venue": venue,
        "matches_played": total,
        "wins": wins,
        "win_percentage": round((wins / total) * 100, 2) if total > 0 else 50.0
    }


def get_recent_form(matches, team, n=5):
    team_matches = get_team_matches(matches, team).sort_values("date")

    recent = team_matches.tail(n)

    form = []
    for _, row in recent.iterrows():
        if row["winner"] == team:
            form.append("W")
        else:
            form.append("L")

    wins = form.count("W")

    return {
        "team": team,
        "recent_form": " ".join(form),
        "matches_considered": len(form),
        "wins": wins,
        "win_percentage": round((wins / len(form)) * 100, 2) if len(form) > 0 else 50.0
    }


def get_winning_streak(matches, team):
    team_matches = get_team_matches(matches, team).sort_values("date", ascending=False)

    streak = 0

    for _, row in team_matches.iterrows():
        if row["winner"] == team:
            streak += 1
        else:
            break

    return streak


def get_last_n_season_winrate(matches, team, current_season, n=3):
    start_season = current_season - n

    recent_matches = matches[
        (matches["season"] >= start_season) &
        (matches["season"] < current_season) &
        ((matches["team1"] == team) | (matches["team2"] == team))
    ]

    total = len(recent_matches)
    wins = len(recent_matches[recent_matches["winner"] == team])

    return round((wins / total) * 100, 2) if total > 0 else 50.0


def get_batting_first_and_chasing_team(row):
    team1 = row["team1"]
    team2 = row["team2"]
    toss_winner = row["toss_winner"]
    toss_decision = str(row["toss_decision"]).lower()

    if toss_winner not in [team1, team2]:
        return None, None

    toss_loser = team2 if toss_winner == team1 else team1

    if toss_decision == "bat":
        batting_first_team = toss_winner
        chasing_team = toss_loser
    else:
        batting_first_team = toss_loser
        chasing_team = toss_winner

    return batting_first_team, chasing_team


def get_chasing_defending_strength(matches, team):
    chasing_matches = 0
    chasing_wins = 0

    defending_matches = 0
    defending_wins = 0

    team_matches = get_team_matches(matches, team)

    for _, row in team_matches.iterrows():
        batting_first_team, chasing_team = get_batting_first_and_chasing_team(row)

        if batting_first_team is None or chasing_team is None:
            continue

        if chasing_team == team:
            chasing_matches += 1
            if row["winner"] == team:
                chasing_wins += 1

        if batting_first_team == team:
            defending_matches += 1
            if row["winner"] == team:
                defending_wins += 1

    chasing_winrate = chasing_wins / chasing_matches if chasing_matches > 0 else 0.5
    defending_winrate = defending_wins / defending_matches if defending_matches > 0 else 0.5

    return {
        "team": team,
        "chasing_matches": chasing_matches,
        "chasing_wins": chasing_wins,
        "chasing_win_percentage": round(chasing_winrate * 100, 2),
        "defending_matches": defending_matches,
        "defending_wins": defending_wins,
        "defending_win_percentage": round(defending_winrate * 100, 2),
        "chasing_strength_score": round(chasing_winrate * 100, 2),
        "defending_strength_score": round(defending_winrate * 100, 2)
    }


def get_venue_chasing_defending_record(matches, venue):
    venue_matches = matches[matches["venue"] == venue]

    chasing_matches = 0
    chasing_wins = 0

    defending_matches = 0
    defending_wins = 0

    for _, row in venue_matches.iterrows():
        batting_first_team, chasing_team = get_batting_first_and_chasing_team(row)

        if batting_first_team is None or chasing_team is None:
            continue

        chasing_matches += 1
        defending_matches += 1

        if row["winner"] == chasing_team:
            chasing_wins += 1

        if row["winner"] == batting_first_team:
            defending_wins += 1

    chasing_success = chasing_wins / chasing_matches if chasing_matches > 0 else 0.5
    defending_success = defending_wins / defending_matches if defending_matches > 0 else 0.5

    return {
        "venue": venue,
        "matches_played": len(venue_matches),
        "chasing_win_percentage": round(chasing_success * 100, 2),
        "defending_win_percentage": round(defending_success * 100, 2)
    }


def get_team_overall_winrate(matches, team):
    team_matches = get_team_matches(matches, team)

    total = len(team_matches)
    wins = len(team_matches[team_matches["winner"] == team])

    return round((wins / total) * 100, 2) if total > 0 else 50.0


def get_team_weakness(matches, deliveries, team, venue=None):
    weaknesses = []

    recent_form = get_recent_form(matches, team, n=5)
    chasing_defending = get_chasing_defending_strength(matches, team)

    if recent_form["win_percentage"] < 40:
        weaknesses.append("Poor recent form")

    if chasing_defending["chasing_win_percentage"] < 40:
        weaknesses.append("Weak chasing record")

    if chasing_defending["defending_win_percentage"] < 40:
        weaknesses.append("Weak defending record")

    if venue:
        venue_record = get_team_venue_record(matches, team, venue)
        if venue_record["matches_played"] >= 3 and venue_record["win_percentage"] < 40:
            weaknesses.append("Poor record at this venue")

    if deliveries is not None and not deliveries.empty:
        bowling_data = deliveries[deliveries["bowling_team"] == team]

        if not bowling_data.empty:
            death_overs = bowling_data[bowling_data["over"] >= 16]

            if not death_overs.empty:
                balls = len(death_overs)
                runs = death_overs["total_runs"].sum()
                overs = balls / 6
                death_economy = runs / overs if overs > 0 else 0

                if death_economy > 10:
                    weaknesses.append("High death-over bowling economy")

        batting_data = deliveries[deliveries["batting_team"] == team]

        if not batting_data.empty:
            total_runs = batting_data["batsman_runs"].sum()
            legal_balls = batting_data[
                ~batting_data["extra_type"].isin(["wides"])
            ] if "extra_type" in batting_data.columns else batting_data

            balls = len(legal_balls)
            strike_rate = (total_runs / balls) * 100 if balls > 0 else 0

            if strike_rate < 120:
                weaknesses.append("Low overall batting strike rate")

    if not weaknesses:
        weaknesses.append("No major weakness detected from available data")

    return weaknesses


def get_team_summary(matches, deliveries, team, venue=None, current_season=None):
    if current_season is None:
        current_season = matches["season"].max()

    return {
        "team": team,
        "overall_win_percentage": get_team_overall_winrate(matches, team),
        "recent_form": get_recent_form(matches, team),
        "winning_streak": get_winning_streak(matches, team),
        "last_3_season_win_percentage": get_last_n_season_winrate(matches, team, current_season, n=3),
        "chasing_defending_strength": get_chasing_defending_strength(matches, team),
        "venue_record": get_team_venue_record(matches, team, venue) if venue else None,
        "weaknesses": get_team_weakness(matches, deliveries, team, venue)
    }