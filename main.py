
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.prediction_service import (
    matches,
    pre_toss_metrics,
    post_toss_metrics,
    predict_pre_toss,
    predict_post_toss
)


app = FastAPI(
    title="CricWinIQ: IPL Win Probability and Match Intelligence API",
    description="Predicts IPL team winning chances before and after toss with analytics.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PreTossInput(BaseModel):
    team1: str
    team2: str
    venue: str
    season: int
    stage: str
    is_day_night: bool


class PostTossInput(BaseModel):
    team1: str
    team2: str
    venue: str
    season: int
    stage: str
    is_day_night: bool
    toss_winner: str
    toss_decision: str
    weather: str
    pitch_type: str


@app.get("/")
def home():
    return {
        "message": "CricWinIQ API is running",
        "docs": "Open /docs to test the API"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/teams")
def get_teams():
    teams = sorted(list(set(matches["team1"]).union(set(matches["team2"]))))
    return {
        "teams": teams
    }


@app.get("/venues")
def get_venues():
    venues = sorted(matches["venue"].dropna().unique().tolist())
    return {
        "venues": venues
    }


@app.get("/model-performance")
def model_performance():
    return {
        "pre_toss_model": {
            "accuracy": pre_toss_metrics.get("accuracy"),
            "precision": pre_toss_metrics.get("precision"),
            "recall": pre_toss_metrics.get("recall"),
            "f1_score": pre_toss_metrics.get("f1_score"),
            "roc_auc": pre_toss_metrics.get("roc_auc"),
            "log_loss": pre_toss_metrics.get("log_loss"),
            "brier_score": pre_toss_metrics.get("brier_score")
        },
        "post_toss_model": {
            "accuracy": post_toss_metrics.get("accuracy"),
            "precision": post_toss_metrics.get("precision"),
            "recall": post_toss_metrics.get("recall"),
            "f1_score": post_toss_metrics.get("f1_score"),
            "roc_auc": post_toss_metrics.get("roc_auc"),
            "log_loss": post_toss_metrics.get("log_loss"),
            "brier_score": post_toss_metrics.get("brier_score")
        }
    }


@app.post("/predict/pre-toss")
def pre_toss_prediction(data: PreTossInput):
    return predict_pre_toss(
        team1=data.team1,
        team2=data.team2,
        venue=data.venue,
        season=data.season,
        stage=data.stage,
        is_day_night=data.is_day_night
    )


@app.post("/predict/post-toss")
def post_toss_prediction(data: PostTossInput):
    return predict_post_toss(
        team1=data.team1,
        team2=data.team2,
        venue=data.venue,
        season=data.season,
        stage=data.stage,
        is_day_night=data.is_day_night,
        toss_winner=data.toss_winner,
        toss_decision=data.toss_decision,
        weather=data.weather,
        pitch_type=data.pitch_type
    )

