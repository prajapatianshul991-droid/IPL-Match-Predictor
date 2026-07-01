import streamlit as st
import pandas as pd
import pickle
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="IPL Analytics Hub",
    page_icon="🏏",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stApp { background-color: #0f1117; color: #f0f0f0; }
    [data-testid="stSidebar"] { background-color: #1a1d2e; border-right: 2px solid #f5a623; }
    .main-title { font-size: 2.8rem; font-weight: 800; color: #f5a623; text-align: center; letter-spacing: 2px; margin-bottom: 0.2rem; }
    .sub-title { font-size: 1rem; color: #aaaaaa; text-align: center; margin-bottom: 2rem; }
    .stat-card { background: linear-gradient(135deg, #1a1d2e, #252840); border: 1px solid #f5a623; border-radius: 12px; padding: 1.2rem; text-align: center; margin: 0.5rem 0; }
    .stat-value { font-size: 2rem; font-weight: 700; color: #f5a623; }
    .stat-label { font-size: 0.85rem; color: #aaaaaa; margin-top: 0.2rem; }
    .section-header { font-size: 1.4rem; font-weight: 700; color: #f5a623; border-bottom: 2px solid #f5a623; padding-bottom: 0.4rem; margin-bottom: 1rem; }
    .stButton > button { background: linear-gradient(135deg, #f5a623, #e8890a); color: #0f1117; font-weight: 700; font-size: 1.1rem; border: none; border-radius: 8px; padding: 0.6rem 2rem; width: 100%; transition: opacity 0.2s; }
    .stButton > button:hover { opacity: 0.85; }
    .winner-box { background: linear-gradient(135deg, #1a3a1a, #1e4a1e); border: 2px solid #4caf50; border-radius: 12px; padding: 1.5rem; text-align: center; margin-top: 1rem; }
    .winner-text { font-size: 1.8rem; font-weight: 800; color: #4caf50; }
    .confidence-text { font-size: 1rem; color: #aaaaaa; margin-top: 0.5rem; }
    hr { border-color: #2a2d3e; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_models():
    with open('ipl_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('team_encoder.pkl', 'rb') as f:
        le_team = pickle.load(f)
    with open('venue_encoder.pkl', 'rb') as f:
        le_venue = pickle.load(f)
    return model, le_team, le_venue

@st.cache_data
def load_stats():
    batting = pd.read_csv('batting_stats.csv')
    bowling = pd.read_csv('bowling_stats.csv')
    matches = pd.read_csv('ipl_final.csv')
    return batting, bowling, matches

@st.cache_data
def load_balls():
    return pd.read_csv('ipl_balls.csv')

model, le_team, le_venue = load_models()
batting_stats, bowling_stats, matches_df = load_stats()

team_active_years = {
    'Chennai Super Kings': [(2008, 2015), (2018, 2026)],
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
        return any(start <= season <= end for start, end in team_active_years[team])
    return True

st.sidebar.markdown("## 🏏 IPL Analytics Hub")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", [
    "🏆 Match Predictor",
    "📊 Player Comparison",
    "⚔️ Head-to-Head",
    "📈 Run Progression"
])
st.sidebar.markdown("---")
st.sidebar.markdown("<small style='color:#aaa'>Data: Cricsheet 2008–2026</small>", unsafe_allow_html=True)

# PAGE 1: MATCH PREDICTOR
if page == "🏆 Match Predictor":
    st.markdown('<div class="main-title">🏆 IPL Match Predictor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Predict the winner based on teams, venue, toss & season</div>', unsafe_allow_html=True)

    teams = sorted(le_team.classes_.tolist())
    venues = sorted(le_venue.classes_.tolist())

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">⚙️ Match Details</div>', unsafe_allow_html=True)
        season = st.number_input("Season (Year)", min_value=2008, max_value=2026, value=2026)
        active_teams = [t for t in teams if is_active(t, season)]
        team1 = st.selectbox("🔵 Team 1", active_teams)
        team2 = st.selectbox("🔴 Team 2", [t for t in active_teams if t != team1])
    with col2:
        st.markdown('<div class="section-header">🪙 Toss Details</div>', unsafe_allow_html=True)
        toss_winner = st.selectbox("Toss Winner", [team1, team2])
        toss_decision = st.selectbox("Toss Decision", ['bat', 'field'])
        venue = st.selectbox("🏟️ Venue", venues)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚡ Predict Winner!"):
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

        st.markdown(f"""
        <div class="winner-box">
            <div class="winner-text">🏆 {winner}</div>
            <div class="confidence-text">Model Confidence: {confidence:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">📊 Win Probability</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.metric(team1, f"{team1_prob*100:.1f}%")
            st.progress(team1_prob)
        with col2:
            st.metric(team2, f"{team2_prob*100:.1f}%")
            st.progress(team2_prob)

# PAGE 2: PLAYER COMPARISON
elif page == "📊 Player Comparison":
    st.markdown('<div class="main-title">📊 Player Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Compare batting & bowling stats of any two IPL players</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏏 Batting", "🎯 Bowling"])

    with tab1:
        all_batters = sorted(batting_stats['batter'].tolist())
        col1, col2 = st.columns(2)
        with col1:
            p1 = st.selectbox("Player 1", all_batters, index=all_batters.index('V Kohli') if 'V Kohli' in all_batters else 0)
        with col2:
            p2 = st.selectbox("Player 2", all_batters, index=all_batters.index('RG Sharma') if 'RG Sharma' in all_batters else 1)

        p1_stats = batting_stats[batting_stats['batter'] == p1].iloc[0]
        p2_stats = batting_stats[batting_stats['batter'] == p2].iloc[0]

        st.markdown("<br>", unsafe_allow_html=True)
        metrics = [
            ('Total Runs', 'total_runs'),
            ('Total Balls', 'total_balls'),
            ('Dismissals', 'dismissals'),
            ('Strike Rate', 'strike_rate'),
            ('Average', 'average'),
        ]
        for label, col in metrics:
            c1, c2, c3 = st.columns([2, 1, 2])
            with c1:
                st.markdown(f'<div class="stat-card"><div class="stat-value">{p1_stats[col]}</div><div class="stat-label">{p1}</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div style="text-align:center; color:#f5a623; font-weight:700; padding-top:1.2rem;">{label}</div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="stat-card"><div class="stat-value">{p2_stats[col]}</div><div class="stat-label">{p2}</div></div>', unsafe_allow_html=True)

    with tab2:
        all_bowlers = sorted(bowling_stats['bowler'].tolist())
        col1, col2 = st.columns(2)
        with col1:
            b1 = st.selectbox("Bowler 1", all_bowlers, index=all_bowlers.index('JJ Bumrah') if 'JJ Bumrah' in all_bowlers else 0)
        with col2:
            b2 = st.selectbox("Bowler 2", all_bowlers, index=all_bowlers.index('YS Chahal') if 'YS Chahal' in all_bowlers else 1)

        b1_stats = bowling_stats[bowling_stats['bowler'] == b1].iloc[0]
        b2_stats = bowling_stats[bowling_stats['bowler'] == b2].iloc[0]

        st.markdown("<br>", unsafe_allow_html=True)
        bowl_metrics = [
            ('Total Wickets', 'total_wickets'),
            ('Overs Bowled', 'overs'),
            ('Runs Given', 'total_runs'),
            ('Economy', 'economy'),
            ('Bowling Avg', 'bowling_avg'),
        ]
        for label, col in bowl_metrics:
            c1, c2, c3 = st.columns([2, 1, 2])
            with c1:
                st.markdown(f'<div class="stat-card"><div class="stat-value">{b1_stats[col]}</div><div class="stat-label">{b1}</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div style="text-align:center; color:#f5a623; font-weight:700; padding-top:1.2rem;">{label}</div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="stat-card"><div class="stat-value">{b2_stats[col]}</div><div class="stat-label">{b2}</div></div>', unsafe_allow_html=True)

# PAGE 3: HEAD-TO-HEAD
elif page == "⚔️ Head-to-Head":
    st.markdown('<div class="main-title">⚔️ Head-to-Head Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Historical record between any two IPL teams</div>', unsafe_allow_html=True)

    teams_list = sorted(matches_df['team1'].unique().tolist())
    col1, col2 = st.columns(2)
    with col1:
        h2h_team1 = st.selectbox("Team 1", teams_list, key='h2h1')
    with col2:
        h2h_team2 = st.selectbox("Team 2", [t for t in teams_list if t != h2h_team1], key='h2h2')

    h2h_matches = matches_df[
        ((matches_df['team1'] == h2h_team1) & (matches_df['team2'] == h2h_team2)) |
        ((matches_df['team1'] == h2h_team2) & (matches_df['team2'] == h2h_team1))
    ]

    if len(h2h_matches) == 0:
        st.warning("Koi match nahi mila in dono teams ke beech!")
    else:
        total = len(h2h_matches)
        team1_wins = len(h2h_matches[h2h_matches['winner'] == h2h_team1])
        team2_wins = len(h2h_matches[h2h_matches['winner'] == h2h_team2])
        no_result = total - team1_wins - team2_wins

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{total}</div><div class="stat-label">Total Matches</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{team1_wins}</div><div class="stat-label">{h2h_team1} Wins</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{team2_wins}</div><div class="stat-label">{h2h_team2} Wins</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{no_result}</div><div class="stat-label">No Result</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">🏆 Win Percentage</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            pct1 = team1_wins / total
            st.metric(h2h_team1, f"{pct1*100:.1f}%")
            st.progress(pct1)
        with col2:
            pct2 = team2_wins / total
            st.metric(h2h_team2, f"{pct2*100:.1f}%")
            st.progress(pct2)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">📅 Recent Matches</div>', unsafe_allow_html=True)
        recent = h2h_matches[['date', 'venue', 'winner']].sort_values('date', ascending=False).head(5)
        st.dataframe(recent.reset_index(drop=True), use_container_width=True)

# PAGE 4: RUN PROGRESSION
elif page == "📈 Run Progression":
    st.markdown('<div class="main-title">📈 Run Progression</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Over-by-over run progression for any IPL match</div>', unsafe_allow_html=True)

    balls_data = load_balls()
    teams_list = sorted(matches_df['team1'].unique().tolist())

    col1, col2 = st.columns(2)
    with col1:
        rp_season = st.number_input("Season (Year)", min_value=2008, max_value=2026, value=2026, key='rp_season')
        active_teams_rp = [t for t in teams_list if is_active(t, rp_season)]
        rp_team1 = st.selectbox("Team 1", active_teams_rp, key='rp_team1')
    with col2:
        rp_team2 = st.selectbox("Team 2", [t for t in active_teams_rp if t != rp_team1], key='rp_team2')

    h2h = matches_df[
        ((matches_df['team1'] == rp_team1) & (matches_df['team2'] == rp_team2) |
        (matches_df['team1'] == rp_team2) & (matches_df['team2'] == rp_team1)) &
        (matches_df['season'] == rp_season)
    ]

    if len(h2h) == 0:
        st.warning("Koi match nahi mila in dono teams ke beech is season mein!")
    else:
        match_options = [f"Match {i+1}: {row['team1']} vs {row['team2']} ({row['venue']})"
                        for i, (_, row) in enumerate(h2h.iterrows())]
        selected_match = st.selectbox("Match select karo", match_options)
        match_idx = match_options.index(selected_match)
        match_info = h2h.iloc[match_idx]

        match_balls = balls_data[balls_data['match_id'] == match_info['match_id']]
        over_scores = match_balls.groupby(['batting_team', 'over'])['runs_total'].sum().reset_index()

        team1_scores = over_scores[over_scores['batting_team'] == match_info['team1']].copy()
        team2_scores = over_scores[over_scores['batting_team'] == match_info['team2']].copy()

        team1_scores['cumulative'] = team1_scores['runs_total'].cumsum()
        team2_scores['cumulative'] = team2_scores['runs_total'].cumsum()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=team1_scores['over'], y=team1_scores['cumulative'],
            mode='lines+markers', name=match_info['team1'],
            line=dict(color='#f5a623', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=team2_scores['over'], y=team2_scores['cumulative'],
            mode='lines+markers', name=match_info['team2'],
            line=dict(color='#4fc3f7', width=3)
        ))

        fig.update_layout(
            title=f"{match_info['team1']} vs {match_info['team2']} — Run Progression",
            xaxis_title="Over",
            yaxis_title="Cumulative Runs",
            plot_bgcolor='#1a1d2e',
            paper_bgcolor='#0f1117',
            font=dict(color='#f0f0f0'),
            legend=dict(bgcolor='#1a1d2e')
        )

        st.plotly_chart(fig, use_container_width=True)
        st.info(f"🏆 Winner: {match_info['winner']}")