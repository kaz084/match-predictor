import streamlit as st
import numpy as np
from scipy.stats import poisson

# --- PASTE YOUR MatchPredictor CLASS HERE ---
class MatchPredictor:
    def __init__(self, league_name):
        self.configs = {
            "UCL": {"avg_home": 1.85, "avg_away": 1.59, "draw_mod": 0.95},
            "EPL": {"avg_home": 1.55, "avg_away": 1.22, "draw_mod": 1.10},
            "LaLiga": {"avg_home": 1.48, "avg_away": 1.18, "draw_mod": 1.20},
            "Bundesliga": {"avg_home": 1.72, "avg_away": 1.46, "draw_mod": 0.90}
        }
        self.config = self.configs.get(league_name, self.configs["UCL"])

    def calculate_player_gravity(self, team_xg, players_out, replacements):
        usage_rates = {"Isak": 0.32, "Maddison": 0.28, "Son": 0.30, "Bruno": 0.24, "Kane": 0.40}
        efficiency = {"Ekitike": 0.75, "Solanke": 0.55, "Jackson": 0.85, "Tonali": 0.60}
        total_loss = sum(usage_rates.get(p, 0.10) for p in players_out)
        total_recovery = sum(efficiency.get(r, 0.40) * usage_rates.get(players_out[i], 0.10) 
                             for i, r in enumerate(replacements) if i < len(players_out))
        return team_xg * (1 - total_loss + total_recovery)

    def get_gk_modifier(self, gk_name):
        mods = {"Alisson": 1.15, "Mamardashvili": 0.88, "Vicario": 1.05, "Ramsdale": 0.94, "Oblak": 1.05}
        return mods.get(gk_name, 1.0)

    def predict(self, home_stats, away_stats, home_gk, away_gk):
        home_xg = home_stats['att'] * away_stats['def'] * self.config['avg_home']
        away_xg = away_stats['att'] * home_stats['def'] * self.config['avg_away']
        home_xg = self.calculate_player_gravity(home_xg, home_stats['out'], home_stats['bench'])
        away_xg = self.calculate_player_gravity(away_xg, away_stats['out'], away_stats['bench'])
        home_cs = poisson.pmf(0, away_xg) * self.get_gk_modifier(home_gk)
        away_cs = poisson.pmf(0, home_xg) * self.get_gk_modifier(away_gk)
        return home_xg, away_xg, home_cs, away_cs

# --- STREAMLIT FRONTEND ---
st.set_page_config(page_title="2026 Match Engine", layout="wide")
st.title("⚽ Tactical Predictor Pro (2026 Edition)")

# Sidebar Configuration
league = st.sidebar.selectbox("Select League", ["UCL", "EPL", "LaLiga", "Bundesliga"])
predictor = MatchPredictor(league)

col1, col2 = st.columns(2)

with col1:
    st.header("🏠 Home Team")
    h_att = st.slider("Home Attack Strength", 0.5, 2.0, 1.15)
    h_def = st.slider("Home Defense Liability", 0.5, 2.0, 0.80)
    h_gk = st.selectbox("Home GK", ["Oblak", "Alisson", "Vicario", "Other"])
    h_out = st.multiselect("Key Players Out (Home)", ["Son", "Maddison", "Kane", "Isak"])
    h_bench = st.multiselect("Replacements (Home)", ["Solanke", "Ekitike", "Jackson"])

with col2:
    st.header("🚀 Away Team")
    a_att = st.slider("Away Attack Strength", 0.5, 2.0, 1.30)
    a_def = st.slider("Away Defense Liability", 0.5, 2.0, 1.10)
    a_gk = st.selectbox("Away GK", ["Vicario", "Mamardashvili", "Ramsdale", "Other"])
    a_out = st.multiselect("Key Players Out (Away)", ["Son", "Maddison", "Kane", "Isak"])
    a_bench = st.multiselect("Replacements (Away)", ["Solanke", "Ekitike", "Jackson"])

# Execution
h_xg, a_xg, h_cs, a_cs = predictor.predict(
    {'att': h_att, 'def': h_def, 'out': h_out, 'bench': h_bench},
    {'att': a_att, 'def': a_def, 'out': a_out, 'bench': a_bench},
    h_gk, a_gk
)

# Results Display
st.divider()
m1, m2, m3 = st.columns(3)
m1.metric("Predicted Scoreline", f"{round(h_xg, 2)} - {round(a_xg, 2)}")
m2.metric("Home Clean Sheet Prob", f"{round(h_cs * 100, 1)}%")
m3.metric("Away Clean Sheet Prob", f"{round(a_cs * 100, 1)}%")

# Simulation Visualization
st.subheader("Win/Draw/Loss Distribution")
probs = [poisson.pmf(i, h_xg) for i in range(5)]
st.bar_chart(probs)
