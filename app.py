import streamlit as st
import pandas as pd
import pickle

# Model aur encoders load karo
with open('ipl_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('team_encoder.pkl', 'rb') as f:
    le_team = pickle.load(f)

with open('venue_encoder.pkl', 'rb') as f:
    le_venue = pickle.load(f)

st.title("🏏 IPL Match Winner Predictor")
st.subheader("2008-2026 Data ke saath!")

teams = sorted(le_team.classes_.tolist())
venues = sorted(le_venue.classes_.tolist())

# Team active years (list of periods - kuch teams 2 baar active rahi hain)
team_active_years = {
    'Chennai Super Kings': [(2008, 2015), (2018, 2026)],  # 2016-17 banned
    'Delhi Daredevils': [(2008, 2018)],
    'Delhi Capitals': [(2019, 2026)],
    'Deccan Chargers': [(2008, 2012)],
    'Sunrisers Hyderabad': [(2013, 2026)],
    'Pune Warriors': [(2011, 2013)],
    'Kochi Tuskers Kerala': [(2011, 2011)],
    'Rising Pune Supergiant': [(2016, 2016)],
    'Rising Pune Supergiants': [(2017, 2017)],
    'Gujarat Lions': [(2016, 2017)],
    'Gujarat Titans': [(2022, 2026)],
    'Kings XI Punjab': [(2008, 2020)],
    'Punjab Kings': [(2021, 2026)],
    'Royal Challengers Bangalore': [(2008, 2023)],
    'Royal Challengers Bengaluru': [(2024, 2026)],
    'Lucknow Super Giants': [(2022, 2026)],
}

def is_active(team, season):
    if team in team_active_years:
        periods = team_active_years[team]
        return any(start <= season <= end for start, end in periods)
    return True

# Season pehle select karo
season = st.number_input("Season (Year)", min_value=2008, max_value=2026, value=2026)

# Season ke according teams filter karo
active_teams = [t for t in teams if is_active(t, season)]

team1 = st.selectbox("Team 1 select karo", active_teams)
team2 = st.selectbox("Team 2 select karo", active_teams)
toss_winner = st.selectbox("Toss kisne jeeta?", [team1, team2])
toss_decision = st.selectbox("Toss decision?", ['bat', 'field'])
venue = st.selectbox("Venue select karo", venues)

if st.button("Predict Winner! 🏆"):
    team1_enc = le_team.transform([team1])[0]
    team2_enc = le_team.transform([team2])[0]
    toss_enc = le_team.transform([toss_winner])[0]
    venue_enc = le_venue.transform([venue])[0]
    bat_first = 1 if toss_decision == 'bat' else 0

    proba = model.predict_proba([[team1_enc, team2_enc, venue_enc, toss_enc, bat_first, season]])[0]
    model_classes = model.classes_

    team1_prob = proba[model_classes == team1_enc][0] if team1_enc in model_classes else 0
    team2_prob = proba[model_classes == team2_enc][0] if team2_enc in model_classes else 0

    winner = team1 if team1_prob > team2_prob else team2
    confidence = max(team1_prob, team2_prob) * 100

    st.success(f"🏆 Predicted Winner: {winner}")
    st.info(f"Confidence: {confidence:.1f}%")