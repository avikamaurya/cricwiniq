# CricWinIQ - IPL Win Probability & Match Intelligence Platform

CricWinIQ is a full-stack IPL win probability and match intelligence platform that predicts team-wise winning chances before and after the toss using machine learning, historical IPL data, FastAPI, and React.

The system provides not only win probability but also explainable cricket analytics such as head-to-head record, venue performance, recent form, winning streaks, team strength, team weaknesses, individual player contribution, and toss/pitch/weather-based post-toss insights.

---

## Live Links

**Live Demo:** https://cricwiniq.vercel.app
**Backend API:** https://cricwiniq.onrender.com
**API Documentation:** https://cricwiniq.onrender.com/docs

---

## Features

* Pre-toss win probability prediction
* Post-toss win probability prediction
* Team-wise winning percentage
* Head-to-head comparison
* Venue-based team performance
* Recent form analysis
* Winning streak analysis
* Past few years performance analysis
* Team batting, bowling, and overall strength
* Team weakness detection
* Individual player contribution analysis
* Toss winner and toss decision impact
* Weather and pitch-based post-toss insights
* FastAPI backend with Swagger documentation
* React-based interactive frontend dashboard
* Fully deployed using Render and Vercel

---

## Tech Stack

### Machine Learning and Backend

* Python
* Pandas
* NumPy
* Scikit-learn
* Random Forest Classifier
* Joblib
* FastAPI
* Uvicorn
* Pydantic

### Frontend

* React
* Vite
* JavaScript
* CSS
* Axios

### Deployment

* GitHub
* Render
* Vercel

---

## Project Overview

CricWinIQ is built as an end-to-end machine learning deployment project. The project starts with IPL historical match data and ball-by-ball delivery data, performs data cleaning and feature engineering, trains machine learning models, exposes the models through FastAPI endpoints, and displays predictions through a React frontend.

The project uses two separate prediction models:

1. **Pre-Toss Model**
   Predicts win probability before the toss using team, venue, season, stage, recent form, head-to-head record, venue record, and team strength features.

2. **Post-Toss Model**
   Predicts win probability after the toss using all pre-toss features along with toss winner, toss decision, chasing strength, defending strength, weather condition, and pitch type.

---

## Dataset Used

The project uses IPL-related datasets including:

* `matches.csv`
* `deliveries.csv`
* `players.csv`
* `seasons.csv`

These datasets are used to calculate match-level, team-level, venue-level, and player-level features.

---

## Machine Learning Approach

The raw IPL data is transformed into meaningful cricket-based features before training the model.

Some important features include:

* Team 1 and Team 2
* Venue
* Season
* Match stage
* Day/night match status
* Head-to-head win percentage
* Venue win percentage
* Recent form
* Winning streak
* Past 3-year win rate
* Batting strength
* Bowling strength
* Overall team strength
* Toss winner
* Toss decision
* Chasing strength
* Defending strength
* Venue chasing/defending success rate
* Weather condition
* Pitch type

The model predicts the probability of Team 1 winning the match. Team 2 probability is calculated as:

`Team 2 Win Probability = 100 - Team 1 Win Probability`

---

## Model Evaluation

The models were evaluated using multiple classification metrics, including:

* Accuracy
* Precision
* Recall
* F1 Score
* ROC-AUC
* Log Loss
* Brier Score
* Confusion Matrix

The frontend displays a professional model evaluation note instead of focusing only on raw accuracy, because cricket match prediction naturally involves uncertainty due to player form, toss impact, pitch behavior, and match-day conditions.

---

## Backend API Endpoints

The backend is built using FastAPI.

### Health Check

```http
GET /health
```

Returns backend health status.

### Teams

```http
GET /teams
```

Returns all available IPL teams.

### Venues

```http
GET /venues
```

Returns all available venues.

### Model Performance

```http
GET /model-performance
```

Returns model evaluation metrics.

### Pre-Toss Prediction

```http
POST /predict/pre-toss
```

Predicts win probability before toss.

Example input:

```json
{
  "team1": "Mumbai Indians",
  "team2": "Chennai Super Kings",
  "venue": "Wankhede Stadium",
  "season": 2025,
  "stage": "League",
  "is_day_night": true
}
```

### Post-Toss Prediction

```http
POST /predict/post-toss
```

Predicts win probability after toss.

Example input:

```json
{
  "team1": "Mumbai Indians",
  "team2": "Chennai Super Kings",
  "venue": "Wankhede Stadium",
  "season": 2025,
  "stage": "League",
  "is_day_night": true,
  "toss_winner": "Mumbai Indians",
  "toss_decision": "field",
  "weather": "humid",
  "pitch_type": "batting"
}
```

---

## Project Structure

```text
cricwiniq/
│
├── data/
│   ├── matches.csv
│   ├── deliveries.csv
│   ├── players.csv
│   └── seasons.csv
│
├── models/
│   ├── pre_toss_model.pkl
│   └── post_toss_model.pkl
│
├── metrics/
│   ├── pre_toss_metrics.json
│   └── post_toss_metrics.json
│
├── src/
│   ├── data_loader.py
│   ├── data_cleaning.py
│   ├── team_analytics.py
│   ├── player_analytics.py
│   ├── feature_engineering.py
│   ├── evaluate_model.py
│   ├── train_pre_toss_model.py
│   ├── train_post_toss_model.py
│   └── prediction_service.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   └── package.json
│
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## How to Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/avikamaurya/cricwiniq.git
cd cricwiniq
```

### 2. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Backend

```bash
python -m uvicorn main:app --reload
```

Backend will run on:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

### 4. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on:

```text
http://localhost:5173
```

---

## Deployment

The project is deployed using:

* **Render** for the FastAPI backend
* **Vercel** for the React frontend

The deployed frontend connects to the deployed backend using the Vite environment variable:

```text
VITE_API_BASE_URL=https://cricwiniq.onrender.com
```

Live deployed links:

```text
Frontend: https://cricwiniq.vercel.app
Backend: https://cricwiniq.onrender.com
API Docs: https://cricwiniq.onrender.com/docs
```

---

## Why This Project Is Useful

Most cricket prediction projects only give a direct winner prediction. CricWinIQ goes beyond that by providing:

* Probability-based prediction instead of only winner name
* Separate pre-toss and post-toss prediction
* Explainable cricket analytics
* Team strength and weakness analysis
* Player contribution insights
* Full-stack deployment with working frontend and backend

This makes it a complete machine learning product rather than just a notebook-based model.

---

## Future Improvements

* Add live match data integration
* Add player availability and playing XI-based prediction
* Add real-time score-based win probability
* Improve weather and pitch data using live APIs
* Add more advanced models such as XGBoost or LightGBM
* Add authentication and user prediction history
* Add visual charts for team trends and player impact

---

## Author

**Avika Maurya**
B.Tech CSE, KIIT University

GitHub: https://github.com/avikamaurya

