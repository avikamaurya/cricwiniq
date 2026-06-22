import os
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

from src.data_loader import load_all_data
from src.data_cleaning import clean_all_data
from src.feature_engineering import create_pre_toss_features
from src.evaluate_model import evaluate_model


def train_pre_toss_model():
    print("Loading data...")
    matches, deliveries, players, seasons = load_all_data()

    print("Cleaning data...")
    matches, deliveries, players, seasons = clean_all_data(
        matches,
        deliveries,
        players,
        seasons
    )

    print("Creating pre-toss features...")
    df = create_pre_toss_features(matches, deliveries, seasons)

    print("Feature dataset shape:", df.shape)

    X = df.drop("team1_win", axis=1)
    y = df["team1_win"]

    categorical_features = [
        "stage",
        "venue",
        "city",
        "team1",
        "team2"
    ]

    numeric_features = [
        "season",
        "is_day_night",
        "team1_h2h_winrate",
        "team2_h2h_winrate",
        "team1_venue_winrate",
        "team2_venue_winrate",
        "team1_recent_form",
        "team2_recent_form",
        "team1_winning_streak",
        "team2_winning_streak",
        "team1_last_3_year_winrate",
        "team2_last_3_year_winrate",
        "team1_batting_strength",
        "team2_batting_strength",
        "team1_bowling_strength",
        "team2_bowling_strength",
        "team1_overall_strength",
        "team2_overall_strength"
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("numeric", "passthrough", numeric_features)
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(
                n_estimators=300,
                max_depth=12,
                random_state=42,
                class_weight="balanced"
            ))
        ]
    )

    split_index = int(len(X) * 0.8)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    print("Training pre-toss model...")
    model.fit(X_train, y_train)

    print("Evaluating pre-toss model...")
    evaluate_model(
        model,
        X_test,
        y_test,
        model_name="Pre-Toss Win Probability Model",
        save_path="metrics/pre_toss_metrics.json"
    )

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/pre_toss_model.pkl")

    print("\nPre-toss model saved to models/pre_toss_model.pkl")


if __name__ == "__main__":
    train_pre_toss_model()