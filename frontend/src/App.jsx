
import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function App() {
  const [mode, setMode] = useState("pre");
  const [teams, setTeams] = useState([]);
  const [venues, setVenues] = useState([]);

  const [formData, setFormData] = useState({
    team1: "",
    team2: "",
    venue: "",
    season: 2026,
    stage: "League",
    is_day_night: true,
    toss_winner: "",
    toss_decision: "field",
    weather: "humid",
    pitch_type: "batting",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchInitialData();
  }, []);

  async function fetchInitialData() {
    try {
      const teamsRes = await fetch(API_BASE_URL + "/teams");
      const teamsData = await teamsRes.json();
      const teamsList = teamsData.teams || [];
      setTeams(teamsList);

      const venuesRes = await fetch(API_BASE_URL + "/venues");
      const venuesData = await venuesRes.json();
      const venuesList = venuesData.venues || [];
      setVenues(venuesList);

      setFormData((prev) => ({
        ...prev,
        team1: teamsList[0] || "",
        team2: teamsList[1] || "",
        toss_winner: teamsList[0] || "",
        venue: venuesList[0] || "",
      }));
    } catch (err) {
      setError("Backend API is not running. Start FastAPI first.");
    }
  }

  function handleChange(e) {
    const { name, value, type, checked } = e.target;

    setFormData((prev) => {
      const updated = {
        ...prev,
        [name]: type === "checkbox" ? checked : value,
      };

      if (name === "team1" || name === "team2") {
        if (
          updated.toss_winner !== updated.team1 &&
          updated.toss_winner !== updated.team2
        ) {
          updated.toss_winner = updated.team1;
        }
      }

      return updated;
    });
  }

  async function handlePredict(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    if (!formData.team1 || !formData.team2 || !formData.venue) {
      setError("Please select both teams and venue.");
      setLoading(false);
      return;
    }

    if (formData.team1 === formData.team2) {
      setError("Team 1 and Team 2 cannot be the same.");
      setLoading(false);
      return;
    }

    try {
      const endpoint =
        mode === "pre" ? "/predict/pre-toss" : "/predict/post-toss";

      const payload =
        mode === "pre"
          ? {
              team1: formData.team1,
              team2: formData.team2,
              venue: formData.venue,
              season: Number(formData.season),
              stage: formData.stage,
              is_day_night: formData.is_day_night,
            }
          : {
              team1: formData.team1,
              team2: formData.team2,
              venue: formData.venue,
              season: Number(formData.season),
              stage: formData.stage,
              is_day_night: formData.is_day_night,
              toss_winner: formData.toss_winner,
              toss_decision: formData.toss_decision,
              weather: formData.weather,
              pitch_type: formData.pitch_type,
            };

      const response = await fetch(API_BASE_URL + endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Prediction failed. Check backend or input values.");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <header className="hero">
        <div>
          <p className="tag">IPL ML + API Project</p>
          <h1>CricWinIQ</h1>
          <p className="subtitle">
            IPL Win Probability & Match Intelligence System
          </p>
        </div>

        <div className="hero-card">
          <p>Prediction Type</p>
          <h2>{mode === "pre" ? "Pre-Toss" : "Post-Toss"}</h2>
        </div>
      </header>

      <main className="container">
        <section className="card form-card">
          <div className="tabs">
            <button
              className={mode === "pre" ? "active" : ""}
              onClick={() => {
                setMode("pre");
                setResult(null);
                setError("");
              }}
              type="button"
            >
              Pre-Toss Prediction
            </button>

            <button
              className={mode === "post" ? "active" : ""}
              onClick={() => {
                setMode("post");
                setResult(null);
                setError("");
              }}
              type="button"
            >
              Post-Toss Prediction
            </button>
          </div>

          {error && <div className="error">{error}</div>}

          <form onSubmit={handlePredict} className="form-grid">
            <div className="field">
              <label>Team 1</label>
              <select name="team1" value={formData.team1} onChange={handleChange}>
                {teams.map((team) => (
                  <option key={team} value={team}>
                    {team}
                  </option>
                ))}
              </select>
            </div>

            <div className="field">
              <label>Team 2</label>
              <select name="team2" value={formData.team2} onChange={handleChange}>
                {teams.map((team) => (
                  <option key={team} value={team}>
                    {team}
                  </option>
                ))}
              </select>
            </div>

            <div className="field">
              <label>Venue</label>
              <select name="venue" value={formData.venue} onChange={handleChange}>
                {venues.map((venue) => (
                  <option key={venue} value={venue}>
                    {venue}
                  </option>
                ))}
              </select>
            </div>

            <div className="field">
              <label>Season</label>
              <input
                name="season"
                type="number"
                value={formData.season}
                onChange={handleChange}
              />
            </div>

            <div className="field">
              <label>Stage</label>
              <select name="stage" value={formData.stage} onChange={handleChange}>
                <option value="League">League</option>
                <option value="Playoffs">Playoffs</option>
                <option value="Qualifier 1">Qualifier 1</option>
                <option value="Qualifier 2">Qualifier 2</option>
                <option value="Eliminator">Eliminator</option>
                <option value="Final">Final</option>
              </select>
            </div>

            <div className="checkbox-field">
              <input
                type="checkbox"
                name="is_day_night"
                checked={formData.is_day_night}
                onChange={handleChange}
              />
              <label>Day/Night Match</label>
            </div>

            {mode === "post" && (
              <>
                <div className="field">
                  <label>Toss Winner</label>
                  <select
                    name="toss_winner"
                    value={formData.toss_winner}
                    onChange={handleChange}
                  >
                    <option value={formData.team1}>{formData.team1}</option>
                    <option value={formData.team2}>{formData.team2}</option>
                  </select>
                </div>

                <div className="field">
                  <label>Toss Decision</label>
                  <select
                    name="toss_decision"
                    value={formData.toss_decision}
                    onChange={handleChange}
                  >
                    <option value="bat">Bat</option>
                    <option value="field">Field</option>
                  </select>
                </div>

                <div className="field">
                  <label>Weather</label>
                  <select
                    name="weather"
                    value={formData.weather}
                    onChange={handleChange}
                  >
                    <option value="clear">Clear</option>
                    <option value="cloudy">Cloudy</option>
                    <option value="humid">Humid</option>
                    <option value="dew">Dew</option>
                    <option value="rainy">Rainy</option>
                    <option value="hot">Hot</option>
                  </select>
                </div>

                <div className="field">
                  <label>Pitch Type</label>
                  <select
                    name="pitch_type"
                    value={formData.pitch_type}
                    onChange={handleChange}
                  >
                    <option value="batting">Batting</option>
                    <option value="bowling">Bowling</option>
                    <option value="balanced">Balanced</option>
                    <option value="spin">Spin</option>
                    <option value="pace">Pace</option>
                    <option value="slow">Slow</option>
                  </select>
                </div>
              </>
            )}

            <button className="predict-btn" type="submit" disabled={loading}>
              {loading ? "Predicting..." : "Predict Winning Chances"}
            </button>
          </form>
        </section>

        {result && <ResultDashboard result={result} />}
      </main>
    </div>
  );
}

function ResultDashboard({ result }) {
  const analysis = result.analysis || {};
  const probabilities = result.win_probability || {};
  const teams = Object.keys(probabilities);

  return (
    <section className="result-section">
      <div className="card result-main">
        <p className="tag">Prediction Result</p>
        <h2>{result.match}</h2>

        {result.venue && (
          <p className="match-meta">
            Venue: {result.venue}
            {result.city && result.city !== "Unknown" ? ", " + result.city : ""}
          </p>
        )}

        <h3 className="winner">Predicted Winner: {result.predicted_winner}</h3>

        <div className="probability-grid">
          {Object.entries(probabilities).map(([team, probability]) => (
            <div className="prob-card" key={team}>
              <p>{team}</p>
              <h2>{probability}</h2>
            </div>
          ))}
        </div>

        {result.weather_pitch_impact && (
          <div className="info-box">
            <h3>Weather & Pitch Impact</h3>
            <ul>
              {result.weather_pitch_impact.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="dashboard-grid">
        <HeadToHeadCard data={analysis.head_to_head} teams={teams} />
        <VenueRecordCard data={analysis.venue_record} teams={teams} />
        <RecentFormCard data={analysis.recent_form} teams={teams} />
        <StreakCard data={analysis.winning_streak} teams={teams} />
        <PastPerformanceCard data={analysis.past_3_year_performance} teams={teams} />
        <TeamStrengthCard data={analysis.team_strength} teams={teams} />
        <WeaknessCard data={analysis.team_weakness} teams={teams} />
        <IndividualContributionCard data={analysis.individual_contribution} teams={teams} />

        {result.chasing_defending_analysis && (
          <ChasingDefendingCard
            data={result.chasing_defending_analysis}
            teams={teams}
          />
        )}
      </div>

      <ModelEvaluationNote />
    </section>
  );
}

function HeadToHeadCard({ data, teams }) {
  if (!data || teams.length < 2) return null;

  const team1 = teams[0];
  const team2 = teams[1];

  return (
    <div className="card stat-card">
      <h3>Head-to-Head</h3>

      <div className="stat-row">
        <span>Matches Played</span>
        <strong>{data.matches_played}</strong>
      </div>

      <div className="team-comparison">
        <MiniTeamStat
          team={team1}
          main={(data[team1 + "_wins"] ?? 0) + " wins"}
          sub={(data[team1 + "_win_percentage"] ?? 0) + "% win rate"}
        />
        <MiniTeamStat
          team={team2}
          main={(data[team2 + "_wins"] ?? 0) + " wins"}
          sub={(data[team2 + "_win_percentage"] ?? 0) + "% win rate"}
        />
      </div>
    </div>
  );
}

function VenueRecordCard({ data, teams }) {
  if (!data || teams.length < 2) return null;

  return (
    <div className="card stat-card">
      <h3>Venue Record</h3>

      <div className="team-comparison">
        {teams.map((team) => {
          const record = data[team] || {};
          return (
            <MiniTeamStat
              key={team}
              team={team}
              main={(record.win_percentage ?? 0) + "%"}
              sub={(record.wins ?? 0) + " wins in " + (record.matches_played ?? 0) + " matches"}
            />
          );
        })}
      </div>
    </div>
  );
}

function RecentFormCard({ data, teams }) {
  if (!data) return null;

  return (
    <div className="card stat-card">
      <h3>Recent Form</h3>

      {teams.map((team) => {
        const form = data[team] || {};
        return (
          <div className="form-row" key={team}>
            <span>{team}</span>
            <div>
              <strong>{form.recent_form || "N/A"}</strong>
              <small>{form.win_percentage ?? 0}% recent win rate</small>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function StreakCard({ data, teams }) {
  if (!data) return null;

  return (
    <div className="card stat-card">
      <h3>Winning Streak</h3>

      <div className="team-comparison">
        {teams.map((team) => (
          <MiniTeamStat
            key={team}
            team={team}
            main={String(data[team] ?? 0)}
            sub="current winning streak"
          />
        ))}
      </div>
    </div>
  );
}

function PastPerformanceCard({ data, teams }) {
  if (!data) return null;

  return (
    <div className="card stat-card">
      <h3>Past 3-Year Performance</h3>

      <div className="team-comparison">
        {teams.map((team) => (
          <MiniTeamStat
            key={team}
            team={team}
            main={(data[team] ?? 0) + "%"}
            sub="win percentage"
          />
        ))}
      </div>
    </div>
  );
}

function TeamStrengthCard({ data, teams }) {
  if (!data) return null;

  return (
    <div className="card stat-card wide-card">
      <h3>Team Strength</h3>

      <div className="strength-grid">
        {teams.map((team) => {
          const strength = data[team] || {};
          return (
            <div className="strength-box" key={team}>
              <h4>{team}</h4>
              <StrengthBar label="Batting" value={strength.batting_strength} />
              <StrengthBar label="Bowling" value={strength.bowling_strength} />
              <StrengthBar label="Overall" value={strength.overall_strength} />
            </div>
          );
        })}
      </div>
    </div>
  );
}

function WeaknessCard({ data, teams }) {
  if (!data) return null;

  return (
    <div className="card stat-card wide-card">
      <h3>Team Weakness</h3>

      <div className="weakness-grid">
        {teams.map((team) => (
          <div className="weakness-box" key={team}>
            <h4>{team}</h4>
            <ul>
              {(data[team] || []).map((weakness, index) => (
                <li key={index}>{weakness}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}

function IndividualContributionCard({ data, teams }) {
  if (!data) return null;

  return (
    <div className="card stat-card wide-card">
      <h3>Individual Contribution</h3>

      <div className="players-grid">
        {teams.map((team) => {
          const teamData = data[team] || {};

          return (
            <div className="players-box" key={team}>
              <h4>{team}</h4>

              <h5>Top Batters</h5>
              {(teamData.top_batters || []).slice(0, 3).map((player) => (
                <div className="player-row" key={player.player}>
                  <span>{player.player}</span>
                  <strong>{Math.round(player.runs)} runs</strong>
                </div>
              ))}

              <h5>Top Bowlers</h5>
              {(teamData.top_bowlers || []).slice(0, 3).map((player) => (
                <div className="player-row" key={player.player}>
                  <span>{player.player}</span>
                  <strong>{Math.round(player.wickets)} wkts</strong>
                </div>
              ))}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ChasingDefendingCard({ data, teams }) {
  if (!data) return null;

  return (
    <div className="card stat-card wide-card">
      <h3>Chasing / Defending Analysis</h3>

      <div className="strength-grid">
        {teams.map((team) => {
          const item = data[team] || {};
          return (
            <div className="strength-box" key={team}>
              <h4>{team}</h4>
              <StrengthBar label="Chasing" value={item.chasing_strength_score} />
              <StrengthBar label="Defending" value={item.defending_strength_score} />
            </div>
          );
        })}
      </div>

      {data.venue && (
        <div className="venue-impact">
          <h4>Venue Trend</h4>
          <p>
            Chasing win rate: <strong>{data.venue.chasing_win_percentage}%</strong>
          </p>
          <p>
            Defending win rate: <strong>{data.venue.defending_win_percentage}%</strong>
          </p>
        </div>
      )}
    </div>
  );
}

function ModelEvaluationNote() {
  return (
    <div className="card model-card">
      <p className="tag">Model Evaluation</p>
      <h2>Evaluation Methodology</h2>

      <p className="evaluation-text">
        The win probability models were evaluated using standard classification
        and probability reliability metrics such as Accuracy, Precision, Recall,
        F1-score, ROC-AUC, Log Loss, and Brier Score. These metrics were used
        during model testing to assess both winner prediction performance and the
        quality of the predicted winning percentages.
      </p>
    </div>
  );
}

function MiniTeamStat({ team, main, sub }) {
  return (
    <div className="mini-team-stat">
      <p>{team}</p>
      <h4>{main}</h4>
      <small>{sub}</small>
    </div>
  );
}

function StrengthBar({ label, value }) {
  const safeValue = Math.min(100, Math.max(0, Number(value || 0)));

  return (
    <div className="strength-row">
      <div className="strength-label">
        <span>{label}</span>
        <strong>{safeValue.toFixed(1)}</strong>
      </div>

      <div className="bar">
        <div className="bar-fill" style={{ width: safeValue + "%" }}></div>
      </div>
    </div>
  );
}

export default App;

