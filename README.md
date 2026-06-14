# 🏏 IPL Match Winner Predictor

A complete end-to-end Data Science project that predicts the winner of an IPL match using historical data (2008–2026) and an interactive Streamlit web app.

🔗 **Live App:** [ipl-match-predictor.streamlit.app](https://ipl-match-predictor-fkpwzkyarkopzy86njuzxc.streamlit.app/)

---

## 📌 Project Overview

This project covers the complete data science pipeline — from raw data collection to a deployed, interactive web application:

1. **Data Collection** – Ball-by-ball IPL data (2008–2026, 1200+ matches) sourced from [Cricsheet](https://cricsheet.org/)
2. **Data Cleaning** – Standardized team names across seasons (e.g., Delhi Daredevils → Delhi Capitals), removed "No Result" matches, checked for duplicates
3. **Exploratory Data Analysis (EDA)** – Visualized:
   - Top winning teams (2008–2026)
   - Impact of toss result on match outcome
   - Most-used venues
4. **Feature Engineering** – Created features like toss decision, season, and label-encoded teams/venues
5. **Machine Learning** – Trained a Random Forest Classifier to predict the match winner, with probability-based logic to ensure predictions are always one of the two competing teams
6. **Deployment** – Built and deployed an interactive web app using Streamlit, with season-aware team filtering (handles renamed, banned, and discontinued teams)

---

## 🧠 Key Challenge Solved

IPL has a complex history — teams have been renamed, banned for seasons, or discontinued entirely:
- Delhi Daredevils → Delhi Capitals
- Kings XI Punjab → Punjab Kings
- Chennai Super Kings banned in 2016–17
- Royal Challengers Bangalore → Royal Challengers Bengaluru

The app uses **season-aware logic** so that only historically valid teams appear for a selected year, keeping predictions logically consistent.

---

## 🛠️ Tech Stack

- **Python**
- **Pandas** – data cleaning and manipulation
- **Matplotlib / Seaborn** – exploratory data analysis
- **Scikit-learn** – Random Forest model, Label Encoding
- **Streamlit** – web app and deployment
- **Pickle** – model and encoder serialization

---

## 📂 Repository Structure

```
├── app.py                  # Streamlit web app
├── IPL.ipynb               # Data cleaning, EDA, feature engineering & model training
├── ipl_final.csv           # Final processed dataset
├── ipl_model.pkl           # Trained Random Forest model
├── team_encoder.pkl        # Label encoder for teams
├── venue_encoder.pkl       # Label encoder for venues
├── requirements.txt        # Project dependencies
└── README.md
```

---

## 🚀 How It Works

1. Select the season (year)
2. Choose Team 1 and Team 2 (only historically valid teams for that season are shown)
3. Select toss winner and toss decision
4. Choose the venue
5. Click **"Predict Winner!"** to get the predicted winner along with the model's confidence score

---

## 📊 Model Performance

- **Model:** Random Forest Classifier
- **Accuracy:** ~49%

Cricket is highly unpredictable, and this model uses only match-level features (teams, venue, toss, season). Accuracy can be improved with player-level and ball-by-ball data — which is planned for future versions.

---

## 🔮 Future Scope (v2)

This is **version 1** of the project. Planned upgrades include:
- Ball-by-ball and player-level analysis
- Live, over-by-over win probability prediction
- Best XI / Dream11-style team suggestions
- Head-to-head team analyzer

---

## 🙏 Acknowledgements

This is a personal learning project, built with guidance and code assistance from **Claude (Anthropic AI)** — used to learn concepts, debug errors, and understand the end-to-end ML workflow step by step.

---

## 👤 Author

**Anshul Prajapati**
B.Tech CSE (Data Science), AKTU
GitHub: [@prajapatianshul991-droid](https://github.com/prajapatianshul991-droid)
