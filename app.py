import streamlit as st
import requests
import pandas as pd

# --- API SETUP ---
API_KEY = st.secrets["FOOTBALL_API_KEY"]
BASE_URL = "https://v3.football.api-sports.io/"
HEADERS = {
    'x-rapidapi-host': "v3.football.api-sports.io",
    'x-rapidapi-key': API_KEY
}

# --- DATA FETCHING FUNCTIONS ---
def get_leagues():
    # Major Leagues IDs for 2026: EPL=39, LaLiga=140, Bundesliga=78
    return {"Premier League": 39, "La Liga": 140, "Bundesliga": 78, "Serie A": 135}

def get_standings(league_id):
    url = f"{BASE_URL}standings?league={league_id}&season=2025" # Update to 2026 when season starts
    response = requests.get(url, headers=HEADERS).json()
    return response['response'][0]['league']['standings'][0]

def get_top_scorers(league_id):
    url = f"{BASE_URL}players/topscorers?league={league_id}&season=2025"
    response = requests.get(url, headers=HEADERS).json()
    return response['response']

# --- DASHBOARD UI ---
st.title("🏆 AI Football Intelligence 2026")

leagues = get_leagues()
selected_league = st.selectbox("Select League", list(leagues.keys()))
league_id = leagues[selected_league]

tab1, tab2 = st.tabs(["📊 Live Standings", "🔥 Top Players (xG/xA)"])

with tab1:
    if st.button("Load Standings"):
        data = get_standings(league_id)
        # Convert API data to a readable Table
        table = []
        for team in data:
            table.append({
                "Rank": team['rank'],
                "Team": team['team']['name'],
                "Played": team['all']['played'],
                "GD": team['goalsDiff'],
                "Points": team['points'],
                "Form": team['form']
            })
        st.table(pd.DataFrame(table))

with tab2:
    if st.button("Load Top Players"):
        players = get_top_scorers(league_id)
        player_list = []
        for p in players:
            player_list.append({
                "Name": p['player']['name'],
                "Goals": p['statistics'][0]['goals']['total'],
                "Assists": p['statistics'][0]['goals']['assists'],
                "Rating": p['statistics'][0]['games']['rating']
            })
        st.dataframe(pd.DataFrame(player_list))
