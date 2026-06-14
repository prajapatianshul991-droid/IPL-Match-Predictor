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

team1 = st.selectbox("Team 1 select karo", teams)
team2 = st.selectbox("Team 2 select karo", teams)
toss_winner = st.selectbox("Toss kisne jeeta?", [team1, team2])
toss_decision = st.selectbox("Toss decision?", ['bat', 'field'])
venue = st.selectbox("Venue select karo", venues)
season = st.number_input("Season (Year)", min_value=2008, max_value=2026, value=2026)

if st.button("Predict Winner! 🏆"):
    team1_enc = le_team.transform([team1])[0]
    team2_enc = le_team.transform([team2])[0]
    toss_enc = le_team.transform([toss_winner])[0]
    venue_enc = le_venue.transform([venue])[0]
    bat_first = 1 if toss_decision == 'bat' else 0

    prediction = model.predict([[team1_enc, team2_enc, venue_enc, toss_enc, bat_first, season]])
    winner = le_team.inverse_transform(prediction)[0]
    
    st.success(f"🏆 Predicted Winner: {winner}")