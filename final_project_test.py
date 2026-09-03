import os
import sys
import pickle
import py_compile
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
PASS = 0
WARN = 0
FAIL = 0

def ok(msg):
    global PASS
    PASS += 1
    print(f"✅ PASS  {msg}")

def warn(msg):
    global WARN
    WARN += 1
    print(f"⚠️ WARN  {msg}")

def fail(msg):
    global FAIL
    FAIL += 1
    print(f"❌ FAIL  {msg}")

def load_csv(name):
    p = BASE / name
    if not p.exists():
        fail(f"Missing file: {name}")
        return None
    try:
        df = pd.read_csv(p)
        ok(f"{name} loaded ({len(df):,} rows)")
        return df
    except Exception as e:
        fail(f"{name} could not be read: {e}")
        return None

print("=" * 72)
print("IPL INTELLIGENCE HUB — FINAL PROJECT TEST")
print("=" * 72)
print(f"Project folder: {BASE}\n")

# ------------------------------------------------------------------
# 1) REQUIRED FILES
# ------------------------------------------------------------------
required = [
    "app.py",
    "ipl_model.pkl",
    "team_encoder.pkl",
    "venue_encoder.pkl",
    "selected_features.pkl",
    "batting_stats.csv",
    "bowling_stats.csv",
    "ipl_final.csv",
    "ipl_balls.csv",
    "season_team_players.csv",
    "player_of_match.csv",
    "orange_cap.csv",
    "purple_cap.csv",
    "ipl_champions.csv",
    "team_title_counts.csv",
    "season_summary.csv",
    "ipl_rag_knowledge_final.csv",
]

print("\n[1] REQUIRED FILES")
for name in required:
    if (BASE / name).exists():
        ok(f"Found {name}")
    else:
        fail(f"Missing {name}")

if (BASE / "ipl_chroma_db").exists():
    ok("Found ipl_chroma_db folder")
else:
    fail("Missing ipl_chroma_db folder")

# ------------------------------------------------------------------
# 2) APP SYNTAX + UI LOCK
# ------------------------------------------------------------------
print("\n[2] APP SYNTAX / UI")
app_path = BASE / "app.py"

if app_path.exists():
    try:
        py_compile.compile(str(app_path), doraise=True)
        ok("app.py syntax compiles successfully")
    except Exception as e:
        fail(f"app.py syntax error: {e}")

    try:
        app_text = app_path.read_text(encoding="utf-8")
        if '"displayModeBar": False' in app_text or "'displayModeBar': False" in app_text:
            ok("Plotly toolbar is disabled")
        else:
            warn("Could not confirm Plotly toolbar is disabled")

        if "fixedrange=True" in app_text:
            ok("Plot zoom/pan ranges are locked")
        else:
            warn("Could not confirm axes are locked")
    except Exception as e:
        warn(f"Could not inspect app.py UI config: {e}")

# ------------------------------------------------------------------
# 3) LOAD DATA
# ------------------------------------------------------------------
print("\n[3] DATA LOAD")
batting = load_csv("batting_stats.csv")
bowling = load_csv("bowling_stats.csv")
matches = load_csv("ipl_final.csv")
balls = load_csv("ipl_balls.csv")
orange = load_csv("orange_cap.csv")
purple = load_csv("purple_cap.csv")
champions = load_csv("ipl_champions.csv")
titles = load_csv("team_title_counts.csv")
summary = load_csv("season_summary.csv")
rag = load_csv("ipl_rag_knowledge_final.csv")

# ------------------------------------------------------------------
# 4) CORE DATA SANITY
# ------------------------------------------------------------------
print("\n[4] CORE DATA SANITY")

if balls is not None:
    expected_cols = {"match_id", "over", "delivery_number", "batting_team"}
    if expected_cols.issubset(balls.columns):
        dupes = balls.duplicated(
            subset=["match_id", "over", "delivery_number", "batting_team"]
        ).sum()
        if dupes == 0:
            ok("Ball-by-ball true duplicate count = 0")
        else:
            fail(f"Ball-by-ball true duplicates found: {dupes}")
    else:
        warn("Could not run true-duplicate test; required columns missing")

    if len(balls) == 295557:
        ok("Ball count matches cleaned dataset: 295,557")
    else:
        warn(f"Ball count is {len(balls):,}; expected 295,557 for current cleaned dataset")

if summary is not None and "season" in summary.columns:
    seasons = sorted(pd.to_numeric(summary["season"], errors="coerce").dropna().astype(int).unique())
    expected = list(range(2008, 2027))
    if seasons == expected:
        ok("All seasons 2008–2026 are present")
    else:
        fail(f"Season coverage mismatch: {seasons}")

# ------------------------------------------------------------------
# 5) KNOWN RECORD CHECKS
# ------------------------------------------------------------------
print("\n[5] KNOWN RECORD CHECKS")

if batting is not None:
    top = batting.sort_values("total_runs", ascending=False).iloc[0]
    if str(top["batter"]) == "V Kohli" and int(top["total_runs"]) == 9336:
        ok("Career run leader = V Kohli, 9,336 runs")
    else:
        fail(f"Unexpected career run leader: {top['batter']} — {top['total_runs']}")

if bowling is not None:
    top = bowling.sort_values("total_wickets", ascending=False).iloc[0]
    if str(top["bowler"]) == "YS Chahal" and int(top["total_wickets"]) == 233:
        ok("Career wicket leader = YS Chahal, 233 wickets")
    else:
        fail(f"Unexpected career wicket leader: {top['bowler']} — {top['total_wickets']}")

if orange is not None:
    orange["season"] = pd.to_numeric(orange["season"], errors="coerce")
    d = orange[orange["season"] == 2024]
    if not d.empty and str(d.iloc[0]["batter"]) == "V Kohli" and int(d.iloc[0]["runs"]) == 741:
        ok("2024 Orange Cap = V Kohli, 741 runs")
    else:
        fail("2024 Orange Cap check failed")

    alltime = orange.sort_values("runs", ascending=False).iloc[0]
    if str(alltime["batter"]) == "V Kohli" and int(alltime["runs"]) == 973 and int(alltime["season"]) == 2016:
        ok("Highest single-season runs = V Kohli, 973 (2016)")
    else:
        fail(
            f"Highest single-season run check failed: "
            f"{alltime['batter']} — {alltime['runs']} ({alltime['season']})"
        )

if purple is not None:
    purple["season"] = pd.to_numeric(purple["season"], errors="coerce")
    d = purple[purple["season"] == 2024]
    if not d.empty and str(d.iloc[0]["bowler"]) == "HV Patel" and int(d.iloc[0]["wickets"]) == 24:
        ok("2024 Purple Cap = HV Patel, 24 wickets")
    else:
        fail("2024 Purple Cap check failed")

if champions is not None:
    champions["season"] = pd.to_numeric(champions["season"], errors="coerce")
    d = champions[champions["season"] == 2016]
    if not d.empty and str(d.iloc[0]["champion"]) == "Sunrisers Hyderabad":
        ok("2016 IPL champion = Sunrisers Hyderabad")
    else:
        fail("2016 champion check failed")

if titles is not None:
    d = titles[titles["champion"] == "Mumbai Indians"]
    if not d.empty and int(d.iloc[0]["titles"]) == 5:
        ok("Mumbai Indians title count = 5")
    else:
        fail("Mumbai Indians title-count check failed")

if rag is not None:
    if len(rag) == 3072:
        ok("Final RAG knowledge base has 3,072 documents")
    else:
        warn(f"RAG document count is {len(rag):,}; current expected count is 3,072")

# ------------------------------------------------------------------
# 6) MODEL / FEATURE CHECKS
# ------------------------------------------------------------------
print("\n[6] MODEL / FEATURES")

expected_features = [
    "team1_encoded",
    "team2_encoded",
    "toss_winner_encoded",
    "venue_encoded",
    "h2h_win_rate",
    "team1_recent_avg_runs",
    "team2_recent_avg_runs",
    "team1_recent_runs_conceded",
    "team2_recent_runs_conceded",
    "season",
]

try:
    with open(BASE / "selected_features.pkl", "rb") as f:
        features = pickle.load(f)
    if list(features) == expected_features:
        ok("Selected feature list matches final 10-feature model")
    else:
        fail(f"Selected features differ:\n{features}")
except Exception as e:
    fail(f"Could not load selected_features.pkl: {e}")

try:
    with open(BASE / "ipl_model.pkl", "rb") as f:
        model = pickle.load(f)
    n = getattr(model, "n_features_in_", None)
    if n == 10:
        ok("Saved ML model expects 10 input features")
    elif n is None:
        warn("Saved model loaded, but n_features_in_ is unavailable")
    else:
        fail(f"Saved model expects {n} features, not 10")
except Exception as e:
    fail(f"Could not load ipl_model.pkl: {e}")

# ------------------------------------------------------------------
# 7) CHROMA VECTOR DB
# ------------------------------------------------------------------
print("\n[7] CHROMA VECTOR DATABASE")

try:
    import chromadb
    from chromadb.utils import embedding_functions

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    client = chromadb.PersistentClient(path=str(BASE / "ipl_chroma_db"))
    collection = client.get_collection(
        name="ipl_knowledge_final",
        embedding_function=ef
    )
    count = collection.count()
    if count == 3072:
        ok("Chroma collection ipl_knowledge_final contains 3,072 vectors")
    else:
        warn(f"Chroma vector count is {count:,}; expected 3,072")

    result = collection.query(
        query_texts=["Who won IPL 2016?"],
        n_results=1,
        where={"$and": [{"type": "season_summary"}, {"season": "2016"}]},
        include=["documents"]
    )
    docs = result.get("documents", [[]])[0]
    if docs and "Sunrisers Hyderabad" in docs[0]:
        ok("Filtered RAG retrieval test: IPL 2016 → Sunrisers Hyderabad")
    else:
        fail("Filtered RAG retrieval test did not return the expected 2016 summary")

except ImportError:
    warn("chromadb/sentence-transformers not available in this Python environment")
except Exception as e:
    fail(f"Chroma DB test failed: {e}")

# ------------------------------------------------------------------
# FINAL SUMMARY
# ------------------------------------------------------------------
print("\n" + "=" * 72)
print("FINAL TEST SUMMARY")
print("=" * 72)
print(f"✅ Passed : {PASS}")
print(f"⚠️ Warnings: {WARN}")
print(f"❌ Failed : {FAIL}")

if FAIL == 0:
    print("\n🎉 CORE PROJECT TESTS PASSED.")
    print("Now open Streamlit and run the manual UI/AI smoke tests.")
else:
    print("\n🛠️ Fix the failed checks before calling the project final.")

print("\nManual Streamlit smoke-test questions:")
print("1. who scored highest season runs all time")
print("2. who has scored most career IPL runs")
print("3. top 5 run scorers in 2024")
print("4. who took most wickets in a season")
print("5. which team has won most IPL titles")
print("6. which players were in RCB in 2016")
print("7. who won the Orange Cap in 2024")
print("8. tell me Virat Kohli batting stats")
print("9. RCB vs MI head to head")
print("10. who won IPL 2016")
