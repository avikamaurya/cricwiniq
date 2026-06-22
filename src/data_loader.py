import pandas as pd


def load_matches(path="data/matches.csv"):
    return pd.read_csv(path)


def load_deliveries(path="data/deliveries.csv"):
    return pd.read_csv(path)


def load_players(path="data/players.csv"):
    return pd.read_csv(path)


def load_seasons(path="data/seasons.csv"):
    return pd.read_csv(path)


def load_all_data():
    matches = load_matches()
    deliveries = load_deliveries()
    players = load_players()
    seasons = load_seasons()

    return matches, deliveries, players, seasons