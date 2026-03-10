import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# --- 1. BACKGROUND ENGINE: Strength Calculator ---
def calculate_team_strength(form, home_record, away_record, def_stat, att_stat):
    # Higher form and att_stat = better strength
    # Lower def_stat (goals conceded) = better strength
    base = (form * 0.3) + (att_stat * 0.4) + (home_record * 0.1) + (away_record * 0.1)
    defense_impact = (2 - def_stat) * 0.2  # Inverse: lower goals conceded helps
    return round(base + defense_impact, 2)

# --- 2. PREDICTION LOGIC ---
def predict_match(h_strength, a_strength):
    home_xg = h_strength * 1.2  # Simple multiplier for Home Advantage
    away_xg = a_strength * 0.9
    home_win = poisson.pmf(range(1, 10), home_xg).sum()
    away_win = poisson.pmf(range(1, 10), away_xg).sum()
    return home_xg, away_xg

# --- 3. THE DASHBOARD ---
st.set_page_config(page_title="Elite Football Engine 2026", layout="wide")

# Use "Tabs" to organize the Search and Predictor
tab1, tab2 = st.tabs(["🎯 Match Predictor", "📊 Player Stats Search"])

with tab1:
    st.title("Strategic Match Predictor")
    league = st.selectbox("Select League", ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "Eredivisie"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏠 Home Team")
        h_team = st.text_input("Home Team Name", "Arsenal")
        h_form = st.slider("Recent Form (1-10)", 1, 10, 8, key="h_f")
        h_att = st.slider("Attacking Record (Avg Goals)", 0.5, 4.0, 2.1, key="h_a")
        h_def = st.slider("Defensive Record (Avg Conceded)", 0.5, 4.0, 0.9, key="h_d")
        h_info = st.text_area("Player Info (e.g., 'Saka high fatigue', 'Saliba back')", key="h_p")

    with col2:
        st.subheader("🚀 Away Team")
        a_team = st.text_input("Away Team Name", "Liverpool")
        a_form = st.slider("Recent Form (1-10)", 1, 10, 7, key="a_f")
        a_att = st.slider("Attacking Record (Avg Goals)", 0.5, 4.0, 1.8, key="a_a")
        a_def = st.slider("Defensive Record (Avg Conceded)", 0.5, 4.0, 1.1, key="a_d")
        a_info = st.text_area("Player Info (e.g., 'Salah on bench', 'Midfield rotated')", key="a_p")

    # Background Calculation
    h_strength = calculate_team_strength(h_form, 8, 5, h_def, h_att)
    a_strength = calculate_team_strength(a_form, 6, 7, a_def, a_att)
    
    if st.button("Run Prediction"):
        h_xg, a_xg = predict_match(h_strength, a_strength)
        st.divider()
        m1, m2 = st.columns(2)
        m1.metric(f"{h_team} Calculated Strength", h_strength)
        m2.metric(f"{a_team} Calculated Strength", a_strength)
        st.success(f"Predicted Score: {round(h_xg, 2)} - {round(a_xg, 2)}")

with tab2:
    st.title("League Player Search")
    st.write("Sort players by xG (Expected Goals), xA (Expected Assists), and CS (Clean Sheets).")
    
    # Simulated Data Table
    data = {
        "Player": ["Haaland", "Salah", "Palmer", "Saka", "Watkins", "Foden"],
        "League": ["EPL", "EPL", "EPL", "EPL", "EPL", "EPL"],
        "xG": [24.5, 18.2, 15.1, 12.4, 14.8, 10.2],
        "xA": [3.2, 8.5, 9.1, 10.4, 4.2, 7.8],
        "CS Contribution": [0.1, 0.2, 0.4, 0.5, 0.2, 0.3]
    }
    df = pd.DataFrame(data)
    
    search = st.text_input("Search Player Name")
    sort_by = st.selectbox("Sort By", ["xG", "xA", "CS Contribution"])
    
    filtered_df = df[df['Player'].str.contains(search, case=False)]
    st.dataframe(filtered_df.sort_values(by=sort_by, ascending=False), use_container_width=True)
