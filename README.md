# 🏏 IPL Intelligence Hub

### Machine Learning • Cricket Analytics • RAG • Streamlit

An end-to-end Data Science and Machine Learning project for exploring Indian Premier League data from **2008–2026**.

The application combines **match winner prediction, ball-by-ball analytics, player statistics, season analysis, head-to-head comparisons, interactive visualizations, and an AI-powered IPL assistant using Retrieval-Augmented Generation (RAG).**

🔗 **Live Application:**  
https://ipl-match-predictor-2ffywhpzqtjxydhvc6u2vf.streamlit.app/

---

## 📌 Project Overview

IPL Intelligence Hub was developed as a complete Data Science project covering:

- Data collection
- Data cleaning and preprocessing
- Exploratory Data Analysis
- Feature engineering
- Machine Learning
- Ball-by-ball cricket analytics
- Player-level statistics
- Historical IPL analysis
- Retrieval-Augmented Generation
- Interactive dashboard development
- Cloud deployment

The project uses **1,243 IPL matches** and approximately **295,000+ ball-by-ball deliveries** covering IPL seasons from **2008 to 2026**.

---

## ✨ Key Features

### 🏆 Match Winner Predictor

Predicts the probable winner between two IPL teams using a Machine Learning model trained on historical IPL data.

Prediction features include:

- Team 1
- Team 2
- Toss winner
- Venue
- Historical head-to-head win rate
- Team 1 recent average runs
- Team 2 recent average runs
- Team 1 recent runs conceded
- Team 2 recent runs conceded
- Season

The application also applies **season-aware team validation**, ensuring only teams active during the selected IPL season are available.

---

### 👥 Player Comparison

Compare IPL players using career batting and bowling statistics.

Batting analytics include:

- Total runs
- Balls faced
- Batting average
- Strike rate

Bowling analytics include:

- Total wickets
- Overs
- Economy rate
- Bowling average

---

### 📅 Season Explorer

Explore every IPL season from **2008–2026**.

The Season Explorer provides:

- IPL champion
- Orange Cap winner
- Purple Cap winner
- Player of the Match records
- Teams participating in the season
- Season-wise player squads
- Leading run scorers
- Leading wicket takers
- Historical title counts

---

### ⚔️ Head-to-Head Analysis

Compare two IPL teams using their historical match record.

Displays:

- Total matches played
- Wins by Team 1
- Wins by Team 2
- No-result/other matches
- Historical matchup statistics

---

### 📈 Run Progression Analysis

Visualizes how runs progressed throughout an IPL match using ball-by-ball data.

Interactive Plotly charts are used to provide a clean match progression view.

---

## 🤖 AI-Powered IPL Assistant

The project includes a hybrid IPL question-answering system.

Users can ask questions such as:

- Who scored the most career IPL runs?
- Who scored the highest runs in a single season?
- Who won IPL 2016?
- Who won the Orange Cap in 2024?
- Which team has won the most IPL titles?
- Who were the RCB players in 2016?
- What are Virat Kohli's batting statistics?
- RCB vs MI head-to-head record

---

## 🧠 Hybrid RAG Architecture

The AI assistant combines multiple techniques instead of depending only on an LLM.

### 1. Exact Statistical Queries

Questions involving rankings, totals, maximum values and player statistics are answered directly using **Pandas**.

This helps prevent hallucinated numerical answers.

Examples:

- Highest career runs
- Highest career wickets
- Top N run scorers
- Highest single-season runs
- Orange/Purple Cap winners
- IPL champions
- Team title counts

---

### 2. Vector Retrieval

A dedicated IPL knowledge base is indexed using:

- **ChromaDB**
- **Sentence Transformers**
- **all-MiniLM-L6-v2 embeddings**

The final knowledge base contains approximately **3,072 IPL documents**.

It contains information about:

- Match results
- Career batting statistics
- Career bowling statistics
- Season squads
- IPL champions
- Orange Cap winners
- Purple Cap winners
- Player of the Match records
- Team title history

---

### 3. Gemini Integration

For questions requiring natural-language reasoning, the application can use the **Gemini API** with retrieved IPL context.

If Gemini is unavailable or API quota is exhausted, the application falls back to structured IPL data rather than generating unsupported statistics.

---

## 📊 Dataset

The project uses IPL data provided by **Cricsheet**.

Dataset coverage:

- **Seasons:** 2008–2026
- **Matches:** 1,243
- **Ball-by-ball deliveries:** ~295K+
- **Batters:** 700+
- **Bowlers:** 500+

Raw Cricsheet JSON files were transformed into structured datasets for Machine Learning and analytics.

Source:

https://cricsheet.org/

---

## 🧹 Data Processing

Several preprocessing steps were performed before modelling and analysis.

### Team Name Normalization

Historical team names were standardized.

Examples:

```text
Delhi Daredevils → Delhi Capitals
Kings XI Punjab → Punjab Kings
Royal Challengers Bangalore → Royal Challengers Bengaluru
Rising Pune Supergiants → Rising Pune Supergiant
