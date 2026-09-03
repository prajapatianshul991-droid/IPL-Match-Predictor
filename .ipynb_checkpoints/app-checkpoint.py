import os, re, pickle
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ========================= APP =========================
st.set_page_config(page_title="IPL Intelligence Hub", page_icon="🏏", layout="wide")
BASE = Path(__file__).resolve().parent
PLOT_CFG = {"displayModeBar": False, "scrollZoom": False, "displaylogo": False}

st.markdown("""
<style>
:root{--bg:#07111f;--panel:#0d1b2a;--panel2:#12243a;--text:#f7f9fc;--muted:#95a7ba;--accent:#ffb11b;--green:#43d88b;--border:rgba(255,255,255,.09)}
.stApp{background:radial-gradient(circle at 12% 0%,rgba(255,177,27,.09),transparent 28%),linear-gradient(180deg,#07111f,#081522);color:var(--text)}
[data-testid="stSidebar"]{background:#091522;border-right:1px solid var(--border)}
.block-container{max-width:1380px;padding-top:1.6rem;padding-bottom:2.4rem}
.hero{background:linear-gradient(135deg,rgba(18,36,58,.97),rgba(9,24,40,.97));border:1px solid var(--border);border-radius:22px;padding:1.7rem 2rem;margin-bottom:1.1rem;box-shadow:0 18px 50px rgba(0,0,0,.24)}
.eyebrow{color:var(--accent);font-size:.78rem;font-weight:800;letter-spacing:.15em;text-transform:uppercase}.hero h1{font-size:clamp(2rem,4vw,3.2rem);margin:.25rem 0 .4rem;font-weight:900}.hero p{color:#aebed0;max-width:850px;line-height:1.55;margin:0}.badge{display:inline-block;margin:.8rem .35rem 0 0;padding:.35rem .65rem;border-radius:999px;border:1px solid rgba(255,177,27,.28);background:rgba(255,177,27,.08);color:#ffd681;font-size:.75rem;font-weight:700}
.card{background:linear-gradient(145deg,rgba(18,36,58,.88),rgba(10,27,45,.92));border:1px solid var(--border);border-radius:17px;padding:1rem 1.1rem;min-height:110px}.label{color:var(--muted);font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em}.value{font-size:1.55rem;font-weight:900;margin-top:.25rem}.note{color:#8193a8;font-size:.78rem;margin-top:.15rem}.section{font-size:1.18rem;font-weight:850;margin:1.2rem 0 .7rem}
.winner{background:linear-gradient(135deg,rgba(23,68,48,.93),rgba(18,51,39,.93));border:1px solid rgba(67,216,139,.38);border-radius:18px;padding:1.2rem;text-align:center}.winner .name{font-size:1.8rem;font-weight:900}.tiny{color:#7f92a8;font-size:.75rem;line-height:1.45}
div.stButton>button{width:100%;border:0;border-radius:13px;padding:.65rem 1rem;font-weight:850;color:#091321;background:linear-gradient(135deg,#ffb11b,#ff7a00)}
[data-testid="stMetric"]{background:rgba(18,36,58,.72);border:1px solid var(--border);border-radius:15px;padding:.8rem}.footer{text-align:center;color:#62758a;font-size:.72rem;margin-top:2rem}
</style>
""", unsafe_allow_html=True)

TEAM_MAP = {
    "Royal Challengers Bangalore":"Royal Challengers Bengaluru",
    "Kings XI Punjab":"Punjab Kings",
    "Delhi Daredevils":"Delhi Capitals",
    "Rising Pune Supergiants":"Rising Pune Supergiant",
}
ACTIVE = {
    "Chennai Super Kings":[(2008,2015),(2018,2026)], "Deccan Chargers":[(2008,2012)],
    "Delhi Capitals":[(2008,2026)], "Gujarat Lions":[(2016,2017)], "Gujarat Titans":[(2022,2026)],
    "Kochi Tuskers Kerala":[(2011,2011)], "Kolkata Knight Riders":[(2008,2026)], "Lucknow Super Giants":[(2022,2026)],
    "Mumbai Indians":[(2008,2026)], "Pune Warriors":[(2011,2013)], "Punjab Kings":[(2008,2026)],
    "Rajasthan Royals":[(2008,2015),(2018,2026)], "Rising Pune Supergiant":[(2016,2017)],
    "Royal Challengers Bengaluru":[(2008,2026)], "Sunrisers Hyderabad":[(2013,2026)]
}
TEAM_ALIASES = {
    "rcb":"Royal Challengers Bengaluru","royal challengers":"Royal Challengers Bengaluru","royal challengers bengaluru":"Royal Challengers Bengaluru","royal challengers bangalore":"Royal Challengers Bengaluru",
    "mi":"Mumbai Indians","mumbai":"Mumbai Indians","mumbai indians":"Mumbai Indians",
    "csk":"Chennai Super Kings","chennai":"Chennai Super Kings","chennai super kings":"Chennai Super Kings",
    "kkr":"Kolkata Knight Riders","kolkata":"Kolkata Knight Riders","kolkata knight riders":"Kolkata Knight Riders",
    "srh":"Sunrisers Hyderabad","sunrisers":"Sunrisers Hyderabad","sunrisers hyderabad":"Sunrisers Hyderabad",
    "rr":"Rajasthan Royals","rajasthan":"Rajasthan Royals","rajasthan royals":"Rajasthan Royals",
    "pbks":"Punjab Kings","punjab kings":"Punjab Kings","kings xi punjab":"Punjab Kings",
    "dc":"Delhi Capitals","delhi capitals":"Delhi Capitals","delhi daredevils":"Delhi Capitals",
    "gt":"Gujarat Titans","gujarat titans":"Gujarat Titans","lsg":"Lucknow Super Giants","lucknow super giants":"Lucknow Super Giants"
}
FEATURES = ["team1_encoded","team2_encoded","toss_winner_encoded","venue_encoded","h2h_win_rate","team1_recent_avg_runs","team2_recent_avg_runs","team1_recent_runs_conceded","team2_recent_runs_conceded","season"]

def path(name): return BASE / name
def norm_team(x): return TEAM_MAP.get(x, x)
def active(team, year): return any(a <= year <= b for a,b in ACTIVE.get(team, []))
def safe_int(x):
    try: return int(float(x))
    except: return 0

def hero(kicker, title, text, badges=()):
    chips = "".join(f'<span class="badge">{b}</span>' for b in badges)
    st.markdown(f'<div class="hero"><div class="eyebrow">{kicker}</div><h1>{title}</h1><p>{text}</p>{chips}</div>', unsafe_allow_html=True)

def card(label, value, note=""):
    st.markdown(f'<div class="card"><div class="label">{label}</div><div class="value">{value}</div><div class="note">{note}</div></div>', unsafe_allow_html=True)

def section(text): st.markdown(f'<div class="section">{text}</div>', unsafe_allow_html=True)

def lock_plot(fig):
    fig.update_xaxes(fixedrange=True); fig.update_yaxes(fixedrange=True)
    return fig

def show_plot(fig): st.plotly_chart(lock_plot(fig), use_container_width=True, config=PLOT_CFG)

# ========================= LOAD =========================
@st.cache_resource
def load_models():
    with open(path("ipl_model.pkl"),"rb") as f: model = pickle.load(f)
    with open(path("team_encoder.pkl"),"rb") as f: le_team = pickle.load(f)
    with open(path("venue_encoder.pkl"),"rb") as f: le_venue = pickle.load(f)
    fpath = path("selected_features.pkl")
    selected = pickle.load(open(fpath,"rb")) if fpath.exists() else FEATURES
    return model, le_team, le_venue, selected

@st.cache_data
def load_data():
    bat = pd.read_csv(path("batting_stats.csv")); bowl = pd.read_csv(path("bowling_stats.csv")); m = pd.read_csv(path("ipl_final.csv")); balls = pd.read_csv(path("ipl_balls.csv"))
    sp = pd.read_csv(path("season_team_players.csv")); potm = pd.read_csv(path("player_of_match.csv")); oc = pd.read_csv(path("orange_cap.csv")); pc = pd.read_csv(path("purple_cap.csv")); champs = pd.read_csv(path("ipl_champions.csv")); titles = pd.read_csv(path("team_title_counts.csv")); ss = pd.read_csv(path("season_summary.csv"))
    for c in ["team1","team2","toss_winner","winner"]:
        if c in m: m[c] = m[c].replace(TEAM_MAP)
    m["match_id"] = m["match_id"].astype(str); m["date"] = pd.to_datetime(m["date"], errors="coerce")
    if "season" not in m: m["season"] = m["date"].dt.year
    m["season"] = pd.to_numeric(m["season"], errors="coerce").astype("Int64")
    balls["match_id"] = balls["match_id"].astype(str)
    if "batting_team" in balls: balls["batting_team"] = balls["batting_team"].replace(TEAM_MAP)
    for df in [sp,potm,oc,pc,champs,ss]:
        if "season" in df: df["season"] = pd.to_numeric(df["season"], errors="coerce").astype("Int64")
    if "date" in potm: potm["date"] = pd.to_datetime(potm["date"], errors="coerce")
    return bat,bowl,m,balls,sp,potm,oc,pc,champs,titles,ss

@st.cache_data
def build_tables(_balls, _matches):
    season_map = _matches[["match_id","season","date","team1","team2"]].drop_duplicates("match_id")
    sb = _balls.groupby(["match_id","batter"], as_index=False)["runs_batter"].sum().merge(season_map[["match_id","season"]], on="match_id", how="left")
    sb = sb.groupby(["season","batter"], as_index=False)["runs_batter"].sum().rename(columns={"runs_batter":"runs"})
    if "bowler_wicket" in _balls:
        bw = _balls["bowler_wicket"]
    elif "dismissal_kind" in _balls:
        kinds = ["bowled","caught","caught and bowled","hit wicket","lbw","stumped"]
        bw = _balls["dismissal_kind"].isin(kinds).astype(int)
    else: bw = pd.Series(0,index=_balls.index)
    tmp = _balls[["match_id","bowler"]].copy(); tmp["w"] = bw
    sw = tmp.groupby(["match_id","bowler"], as_index=False)["w"].sum().merge(season_map[["match_id","season"]], on="match_id", how="left")
    sw = sw.groupby(["season","bowler"], as_index=False)["w"].sum().rename(columns={"w":"wickets"})
    scores = _balls.groupby(["match_id","batting_team"], as_index=False)["runs_total"].sum().rename(columns={"runs_total":"score"}).merge(season_map,on="match_id",how="left")
    innings = _balls.groupby(["match_id","batting_team","batter"], as_index=False)["runs_batter"].sum().rename(columns={"runs_batter":"runs"}).merge(season_map[["match_id","season","date"]],on="match_id",how="left")
    return sb, sw, scores, innings

model, le_team, le_venue, selected_features = load_models()
batting, bowling, matches, balls, season_players, potm, orange, purple, champions, title_counts, season_summary = load_data()
season_bat, season_bowl, team_scores, innings_scores = build_tables(balls, matches)

# ========================= PREDICTION =========================
def h2h_rate(t1,t2,year):
    h = matches[(matches["season"] < year) & ((((matches.team1==t1)&(matches.team2==t2)))|(((matches.team1==t2)&(matches.team2==t1))))]
    decided = h[h.winner.isin([t1,t2])]
    return .5 if decided.empty else float((decided.winner==t1).mean())

def recent_strength(team, year, n=5):
    hist = matches[(matches["season"] < year) & ((matches.team1==team)|(matches.team2==team))].sort_values("date").tail(n)
    scored, conceded = [], []
    for r in hist.itertuples():
        s = team_scores[team_scores.match_id == str(r.match_id)]
        own = s[s.batting_team == team]["score"]
        opp = s[s.batting_team != team]["score"]
        if len(own): scored.append(float(own.iloc[0]))
        if len(opp): conceded.append(float(opp.iloc[0]))
    return (sum(scored)/len(scored) if scored else 150.0, sum(conceded)/len(conceded) if conceded else 150.0)

def predict_row(t1,t2,toss,venue,year):
    s1,c1 = recent_strength(t1,year); s2,c2 = recent_strength(t2,year)
    vals = {
        "team1_encoded":le_team.transform([t1])[0], "team2_encoded":le_team.transform([t2])[0],
        "toss_winner_encoded":le_team.transform([toss])[0], "venue_encoded":le_venue.transform([venue])[0],
        "h2h_win_rate":h2h_rate(t1,t2,year), "team1_recent_avg_runs":s1, "team2_recent_avg_runs":s2,
        "team1_recent_runs_conceded":c1, "team2_recent_runs_conceded":c2, "season":year,
    }
    X = pd.DataFrame([[vals[f] for f in selected_features]], columns=selected_features)
    return X, vals

# ========================= AI / QUERY ENGINE =========================
def qnorm(q): return re.sub(r"[^a-z0-9]+"," ",q.lower()).strip()
def season_from(q):
    m = re.search(r"\b(200[8-9]|201\d|202[0-6])\b", q); return int(m.group()) if m else None

def teams_from(q):
    s = q.lower(); out=[]
    for alias in sorted(TEAM_ALIASES,key=len,reverse=True):
        if re.search(r"\b"+re.escape(alias)+r"\b",s):
            t=TEAM_ALIASES[alias]
            if t not in out: out.append(t)
    return out

def top_n_from(q, default=1):
    m=re.search(r"\btop\s+(\d+)\b",q.lower()); return min(int(m.group(1)),20) if m else default

def player_alias_match(q, column):
    names = column.dropna().astype(str).unique().tolist(); nq=q.lower()
    exact=[n for n in names if n.lower() in nq]
    if exact: return max(exact,key=len)
    popular={"virat kohli":"V Kohli","rohit sharma":"RG Sharma","shikhar dhawan":"S Dhawan","david warner":"DA Warner","kl rahul":"KL Rahul","ms dhoni":"MS Dhoni","jasprit bumrah":"JJ Bumrah","yuzvendra chahal":"YS Chahal","ravichandran ashwin":"R Ashwin","sunil narine":"SP Narine","bhuvneshwar kumar":"B Kumar"}
    return next((code for full,code in popular.items() if full in nq and code in names), None)

def evidence(text, typ="structured"): return {"documents":[text],"type":typ}

def answer_exact(question):
    q=qnorm(question); year=season_from(question); teams=teams_from(question); n=top_n_from(question)
    rank=any(w in q.split() for w in ["most","highest","maximum","top","leading","best","max"])
    has_runs=any(w in q.split() for w in ["run","runs","score","scored"]); has_wk=any(w in q.split() for w in ["wicket","wickets"])
    seasonish=any(x in q for x in ["season","single season","one season"])

    # highest individual innings score
    if rank and has_runs and any(x in q for x in ["individual","innings","in a match","one match"]):
        d=innings_scores.copy()
        if year is not None: d=d[d.season.astype(int)==year]
        d=d.sort_values("runs",ascending=False).head(n)
        if not d.empty:
            lines=[f"{r.batter} — {int(r.runs)} runs"+(f" ({int(r.season)})" if pd.notna(r.season) else "") for r in d.itertuples()]
            return "Highest individual innings score(s):\n\n"+"\n".join(f"• {x}" for x in lines), evidence("; ".join(lines),"innings_record")

    # single-season runs / season leader
    if has_runs and rank and (seasonish or year is not None):
        d=season_bat.copy();
        if year is not None: d=d[d.season.astype(int)==year]
        d=d.sort_values("runs",ascending=False).head(n)
        if not d.empty:
            lines=[f"{r.batter} — {int(r.runs)} runs"+(f" ({int(r.season)})" if year is None else "") for r in d.itertuples()]
            head=(f"Top {len(d)} run scorer(s) in IPL {year}:" if year else "Highest single-season IPL run total(s):")
            return head+"\n\n"+"\n".join(f"• {x}" for x in lines), evidence("; ".join(lines),"season_runs")

    # single-season wickets / season leader
    if has_wk and rank and (seasonish or year is not None):
        d=season_bowl.copy();
        if year is not None: d=d[d.season.astype(int)==year]
        d=d.sort_values("wickets",ascending=False).head(n)
        if not d.empty:
            lines=[f"{r.bowler} — {int(r.wickets)} wickets"+(f" ({int(r.season)})" if year is None else "") for r in d.itertuples()]
            head=(f"Top {len(d)} wicket-taker(s) in IPL {year}:" if year else "Highest single-season IPL wicket total(s):")
            return head+"\n\n"+"\n".join(f"• {x}" for x in lines), evidence("; ".join(lines),"season_wickets")

    # career runs / wickets
    if rank and has_runs and not seasonish and year is None:
        d=batting.sort_values("total_runs",ascending=False).head(n)
        lines=[f"{r.batter} — {int(r.total_runs)} runs" for r in d.itertuples()]
        return "All-time career run leader(s):\n\n"+"\n".join(f"• {x}" for x in lines), evidence("; ".join(lines),"career_runs")
    if rank and has_wk and not seasonish and year is None:
        d=bowling.sort_values("total_wickets",ascending=False).head(n)
        lines=[f"{r.bowler} — {int(r.total_wickets)} wickets" for r in d.itertuples()]
        return "All-time career wicket leader(s):\n\n"+"\n".join(f"• {x}" for x in lines), evidence("; ".join(lines),"career_wickets")

    # most successful team / most POTM awards
    if rank and any(x in q for x in ["title","titles","trophy","trophies","cups"]) and not teams:
        d=title_counts.sort_values("titles",ascending=False).head(n)
        lines=[f"{r.champion} — {int(r.titles)} titles" for r in d.itertuples()]
        return "Most successful IPL team(s):\n\n"+"\n".join(f"• {x}" for x in lines), evidence("; ".join(lines),"title_leaders")
    if rank and any(x in q for x in ["player of the match","man of the match","potm"]):
        d=potm[potm.player_of_match.notna() & (potm.player_of_match!="Unknown")].player_of_match.value_counts().head(n)
        if len(d):
            lines=[f"{name} — {int(count)} awards" for name,count in d.items()]
            return "Most Player of the Match awards:\n\n"+"\n".join(f"• {x}" for x in lines), evidence("; ".join(lines),"potm_leaders")

    # caps / champion
    if year is not None and "orange cap" in q:
        d=orange[orange.season.astype(int)==year]
        if not d.empty:
            s=d.sort_values("runs",ascending=False).iloc[0]; txt=f"{s.batter} won the Orange Cap in {year} with {int(s.runs)} runs."
            return txt,evidence(txt,"orange_cap")
    if year is not None and "purple cap" in q:
        d=purple[purple.season.astype(int)==year]
        if not d.empty:
            s=d.sort_values("wickets",ascending=False).iloc[0]; txt=f"{s.bowler} won the Purple Cap in {year} with {int(s.wickets)} wickets."
            return txt,evidence(txt,"purple_cap")
    if year is not None and any(x in q for x in ["champion","won ipl","won the ipl","ipl winner","cup winner","title winner"]):
        d=champions[champions.season.astype(int)==year]
        if not d.empty:
            txt=f"{d.iloc[0].champion} won the IPL title in {year}."; return txt,evidence(txt,"champion")

    # titles
    if teams and any(x in q for x in ["title","titles","trophy","trophies","cups"]):
        team=teams[0]; d=title_counts[title_counts.champion==team]
        t=int(d.iloc[0].titles) if not d.empty else 0; txt=f"{team} has won {t} IPL title{'s' if t!=1 else ''} in this dataset."
        return txt,evidence(txt,"team_titles")

    # squad
    if year is not None and teams and any(x in q for x in ["squad","players","player list","who played","played for","player in","player was in"]):
        team=teams[0]; d=season_players[(season_players.season.astype(int)==year)&(season_players.team==team)]
        if not d.empty:
            names=sorted(d.player.dropna().astype(str).unique()); txt=f"IPL {year} squad for {team}:\n\n"+", ".join(names)
            return txt,evidence(", ".join(names),"squad")

    # H2H
    if len(teams)>=2 and any(x in q for x in ["head to head","h2h","record","wins","versus"," vs "]):
        a,b=teams[:2]; d=matches[(((matches.team1==a)&(matches.team2==b))|((matches.team1==b)&(matches.team2==a)))]
        if year is not None: d=d[d.season.astype(int)==year]
        if not d.empty:
            aw=int((d.winner==a).sum()); bw=int((d.winner==b).sum()); nr=len(d)-aw-bw
            txt=f"{a} vs {b}: {len(d)} matches — {a} {aw} wins, {b} {bw} wins, {nr} no-result/other."
            return txt,evidence(txt,"h2h")

    # player career batting/bowling
    bp=player_alias_match(question,batting.batter); wp=player_alias_match(question,bowling.bowler)
    if bp and any(x in q for x in ["batting","runs","strike rate","average","stats","record"]):
        s=batting[batting.batter==bp].iloc[0]; avg="—" if pd.isna(s.average) else f"{s.average:.2f}"
        txt=f"{bp}: {int(s.total_runs)} runs, {int(s.total_balls)} balls, strike rate {s.strike_rate:.2f}, batting average {avg}."
        return txt,evidence(txt,"player_batting")
    if wp and any(x in q for x in ["bowling","wickets","economy","stats","record"]):
        s=bowling[bowling.bowler==wp].iloc[0]; avg="—" if pd.isna(s.bowling_avg) else f"{s.bowling_avg:.2f}"
        txt=f"{wp}: {int(s.total_wickets)} wickets, economy {s.economy:.2f}, bowling average {avg}, {s.overs} overs."
        return txt,evidence(txt,"player_bowling")

    # POTM totals / match-specific with teams + season
    if any(x in q for x in ["player of the match","man of the match","potm"]):
        if year is not None and len(teams)>=2:
            a,b=teams[:2]; d=potm[(potm.season.astype(int)==year)&((((potm.team1==a)&(potm.team2==b)))|(((potm.team1==b)&(potm.team2==a))))]
            if not d.empty:
                rows=[f"{r.date.date() if pd.notna(r.date) else year}: {r.player_of_match}" for r in d.itertuples()]
                return "Player of the Match:\n\n"+"\n".join(f"• {x}" for x in rows), evidence("; ".join(rows),"potm_match")
        p=player_alias_match(question,potm.player_of_match)
        if p:
            cnt=int((potm.player_of_match==p).sum()); txt=f"{p} has {cnt} Player of the Match awards in the dataset."
            return txt,evidence(txt,"potm_total")

    return None, None

@st.cache_resource
def rag_collection():
    try:
        import chromadb
        from chromadb.utils import embedding_functions
        ef=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        client=chromadb.PersistentClient(path=str(path("ipl_chroma_db")))
        return client.get_collection(name="ipl_knowledge_final", embedding_function=ef)
    except Exception: return None

def detect_rag_type(q):
    q=q.lower()
    if "squad" in q or "which players" in q or "players were" in q: return "season_squad"
    if "orange cap" in q or "purple cap" in q or "champion" in q or "won the ipl" in q: return "season_summary"
    if "title" in q or "troph" in q: return "team_titles"
    if "player of the match" in q or "man of the match" in q or "potm" in q: return "match"
    if "wicket" in q or "economy" in q or "bowling" in q: return "career_bowling"
    if "run" in q or "batting" in q or "strike rate" in q: return "career_batting"
    return None

def retrieve(question, n=4):
    c=rag_collection()
    if c is None: return [],[]
    typ=detect_rag_type(question); year=season_from(question); teams=teams_from(question); f=[]
    if typ: f.append({"type":typ})
    if year: f.append({"season":str(year)})
    if teams and typ in ["season_squad","team_titles"]: f.append({"entity":teams[0]})
    where=f[0] if len(f)==1 else ({"$and":f} if f else None)
    args={"query_texts":[question],"n_results":n,"include":["documents","metadatas","distances"]}
    if where: args["where"]=where
    try: r=c.query(**args)
    except Exception: r=c.query(query_texts=[question],n_results=n,include=["documents","metadatas","distances"])
    return r.get("documents",[[]])[0], r.get("distances",[[]])[0]

def gemini_key():
    if st.session_state.get("gemini_api_key"): return st.session_state["gemini_api_key"]
    if os.getenv("GEMINI_API_KEY"): return os.getenv("GEMINI_API_KEY")
    try: return st.secrets.get("GEMINI_API_KEY","")
    except: return ""

def answer_ai(question):
    exact, ev = answer_exact(question)
    if exact: return exact, ev

    docs, dist = retrieve(question)
    # Never turn an arbitrary nearest vector into a factual answer.
    if not docs:
        return "I couldn't find reliable information for that question in the available IPL data.", None

    qtype=detect_rag_type(question)
    # For a recognized fact type, show only filtered evidence; otherwise require Gemini.
    key=gemini_key()
    if not key:
        if qtype and len(docs):
            return "I found related IPL data, but I can't answer this wording confidently without guessing. Try asking with a season, team or player name.", evidence(docs[0],"rag_evidence")
        return "I couldn't map that question confidently. Please make it a little more specific (player/team/season/record).", None

    try:
        from google import genai
        client=genai.Client(api_key=key)
        context="\n".join(f"- {d}" for d in docs)
        prompt=f"""You are IPL Analytics AI. Answer ONLY from the context. If context is insufficient, say so. Never invent statistics.\n\nCONTEXT:\n{context}\n\nQUESTION: {question}\n\nANSWER:"""
        r=client.models.generate_content(model="gemini-3.7-flash",contents=prompt)
        return (r.text.strip() if r.text else "No answer generated."), evidence(context,"rag")
    except Exception:
        return "The IPL data was retrieved, but the AI generation service is temporarily unavailable. I won't guess.", evidence(docs[0],"rag_evidence")

# ========================= SIDEBAR =========================
st.sidebar.markdown("# 🏏 IPL Intelligence")
st.sidebar.caption("Analytics • ML Prediction • Hybrid RAG")
st.sidebar.markdown("---")
page=st.sidebar.radio("Navigate",["🏠 Dashboard","📅 Season Explorer","🤖 IPL AI Assistant","🏆 Match Predictor","📊 Player Comparison","⚔️ Head-to-Head","📈 Run Progression"])
st.sidebar.markdown("---"); st.sidebar.markdown("**Dataset**  \nCricsheet • 2008–2026"); st.sidebar.markdown("**Model**  \nGradient Boosting • 54.62% benchmark"); st.sidebar.markdown('<div class="tiny">AI answers use exact Pandas calculations first, then filtered RAG. Low-confidence questions are not guessed.</div>',unsafe_allow_html=True)

# ========================= PAGES =========================
if page=="🏠 Dashboard":
    hero("IPL DATA LAB","IPL Intelligence Hub","Match history, player records, season archives, ML prediction and a safer hybrid RAG assistant.",["2008–2026","Ball-by-ball","Hybrid RAG"])
    c=st.columns(4)
    vals=[("Matches",f"{len(matches):,}","Historical matches"),("Seasons",matches.season.nunique(),f"{int(matches.season.min())}–{int(matches.season.max())}"),("Venues",matches.venue.nunique(),"Unique grounds"),("Players",len(batting),"Batters tracked")]
    for col,(a,b,d) in zip(c,vals):
        with col: card(a,b,d)
    section("League leaders")
    left,right=st.columns(2)
    for col,df,name,val,title in [(left,batting.nlargest(5,"total_runs"),"batter","total_runs","Top Run Scorers"),(right,bowling.nlargest(5,"total_wickets"),"bowler","total_wickets","Top Wicket Takers")]:
        with col:
            fig=go.Figure(go.Bar(x=df[val],y=df[name],orientation="h",text=df[val],textposition="auto")); fig.update_layout(title=title,yaxis=dict(autorange="reversed"),height=350,margin=dict(l=20,r=20,t=50,b=20),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#eaf1f8")); show_plot(fig)
    section("Recent matches"); st.dataframe(matches.sort_values("date",ascending=False)[["date","team1","team2","winner","venue"]].head(8),use_container_width=True,hide_index=True)

elif page=="📅 Season Explorer":
    hero("SEASON ARCHIVE","IPL Season Explorer","Champion, caps, squads, leaders, match awards and title history for every season.",["2008–2026","Squads","Caps","Champions"])
    years=sorted(season_summary.season.dropna().astype(int).unique()); year=st.selectbox("📅 Select season",years,index=len(years)-1)
    s=season_summary[season_summary.season.astype(int)==year].iloc[0]; pm=potm[potm.season.astype(int)==year]; pm=pm[pm.player_of_match.notna()&(pm.player_of_match!="Unknown")]
    leader=pm.player_of_match.value_counts(); potm_name=leader.index[0] if len(leader) else "—"; potm_n=int(leader.iloc[0]) if len(leader) else 0
    c=st.columns(4); vals=[("🏆 Champion",s.champion,f"IPL {year}"),("🟠 Orange Cap",s.orange_cap,f"{safe_int(s.orange_cap_runs)} runs"),("🟣 Purple Cap",s.purple_cap,f"{safe_int(s.purple_cap_wickets)} wickets"),("⭐ Most POTM",potm_name,f"{potm_n} awards")]
    for col,(a,b,d) in zip(c,vals):
        with col: card(a,b,d)
    tabs=st.tabs(["🔥 Leaders","👥 Squads","⭐ Match Awards","🏆 Titles"])
    with tabs[0]:
        a,b=st.columns(2)
        with a: st.dataframe(season_bat[season_bat.season.astype(int)==year].nlargest(10,"runs").rename(columns={"batter":"Player","runs":"Runs"})[["Player","Runs"]],use_container_width=True,hide_index=True)
        with b: st.dataframe(season_bowl[season_bowl.season.astype(int)==year].nlargest(10,"wickets").rename(columns={"bowler":"Player","wickets":"Wickets"})[["Player","Wickets"]],use_container_width=True,hide_index=True)
    with tabs[1]:
        sp=season_players[season_players.season.astype(int)==year]; teams=sorted(sp.team.dropna().unique()); team=st.selectbox("Team",teams); names=sorted(sp[sp.team==team].player.dropna().unique()); st.write(" • ".join(names))
    with tabs[2]: st.dataframe(pm[["date","team1","team2","winner","player_of_match"]].sort_values("date",ascending=False),use_container_width=True,hide_index=True)
    with tabs[3]:
        a,b=st.columns(2)
        with a: st.dataframe(champions[["season","champion"]].sort_values("season",ascending=False),use_container_width=True,hide_index=True)
        with b: st.dataframe(title_counts.rename(columns={"champion":"Team","titles":"Titles"}),use_container_width=True,hide_index=True)

elif page=="🤖 IPL AI Assistant":
    hero("HYBRID RAG","IPL AI Assistant","Ask natural-language IPL questions. Exact record questions are calculated with Pandas; RAG is used only when appropriate.",["No random guessing","Structured data first","ChromaDB"])
    st.caption("Examples: “who scored highest season runs all time”, “top 5 wicket takers in 2024”, “RCB squad in 2016”, “MI titles”, “Virat Kohli batting stats”.")
    with st.expander("⚙️ Optional: Gemini for compare/explain questions"):
        api_key=st.text_input("Gemini API key",type="password",value="",help="Not needed for normal factual questions.")
        if api_key: st.session_state["gemini_api_key"]=api_key.strip()
        st.caption("Exact factual questions work without Gemini. The key is only used for explanation/comparison-style generation.")
    q=st.chat_input("Ask anything about the IPL dataset…")
    if q:
        st.chat_message("user").write(q)
        ans,ev=answer_ai(q); st.chat_message("assistant").markdown(ans)
        if ev:
            with st.expander("🔎 Retrieved evidence"):
                st.write(ev["documents"][0] if isinstance(ev.get("documents"),list) else ev)

elif page=="🏆 Match Predictor":
    hero("ML PREDICTION","Match Predictor","Pre-season style probability estimate using the final selected Gradient Boosting features.",["10 selected features","54.62% benchmark","No future-season leakage"])
    year=st.number_input("Season",2008,2026,2026); teams=sorted([t for t in le_team.classes_ if active(t,int(year))]); a,b=st.columns(2)
    with a: t1=st.selectbox("Team 1",teams); t2=st.selectbox("Team 2",[t for t in teams if t!=t1])
    with b: toss=st.selectbox("Toss winner",[t1,t2]); venue=st.selectbox("Venue",sorted(le_venue.classes_))
    if st.button("⚡ Predict Winner"):
        try:
            X,info=predict_row(t1,t2,toss,venue,int(year)); proba=model.predict_proba(X)[0]; cls=list(model.classes_); e1=le_team.transform([t1])[0]; e2=le_team.transform([t2])[0]; p1=proba[cls.index(e1)] if e1 in cls else 0; p2=proba[cls.index(e2)] if e2 in cls else 0; total=p1+p2; p1,p2=((p1/total,p2/total) if total else (.5,.5)); win=t1 if p1>=p2 else t2
            st.markdown(f'<div class="winner"><div class="label">Predicted winner</div><div class="name">🏆 {win}</div><div class="note">Confidence {max(p1,p2)*100:.1f}%</div></div>',unsafe_allow_html=True)
            c1,c2=st.columns(2); c1.metric(t1,f"{p1*100:.1f}%"); c2.metric(t2,f"{p2*100:.1f}%")
            st.caption("Recent form and H2H are calculated only from seasons before the selected season.")
        except Exception as e: st.error(f"Prediction error: {e}")

elif page=="📊 Player Comparison":
    hero("PLAYER ANALYTICS","Player Comparison","Compare career batting or bowling records side-by-side.",[f"{len(batting)} batters",f"{len(bowling)} bowlers"])
    tab1,tab2=st.tabs(["🏏 Batting","🎯 Bowling"])
    with tab1:
        names=sorted(batting.batter.dropna()); a,b=st.columns(2); p1=a.selectbox("Player 1",names,index=names.index("V Kohli") if "V Kohli" in names else 0); p2=b.selectbox("Player 2",names,index=names.index("RG Sharma") if "RG Sharma" in names else 1); r1=batting[batting.batter==p1].iloc[0]; r2=batting[batting.batter==p2].iloc[0]
        for label,col in [("Runs","total_runs"),("Balls","total_balls"),("Strike Rate","strike_rate"),("Average","average")]:
            x,y=st.columns(2); x.metric(f"{p1} • {label}","—" if pd.isna(r1[col]) else f"{r1[col]:.2f}" if col in ["strike_rate","average"] else int(r1[col])); y.metric(f"{p2} • {label}","—" if pd.isna(r2[col]) else f"{r2[col]:.2f}" if col in ["strike_rate","average"] else int(r2[col]))
    with tab2:
        names=sorted(bowling.bowler.dropna()); a,b=st.columns(2); p1=a.selectbox("Bowler 1",names,index=names.index("JJ Bumrah") if "JJ Bumrah" in names else 0); p2=b.selectbox("Bowler 2",names,index=names.index("YS Chahal") if "YS Chahal" in names else 1); r1=bowling[bowling.bowler==p1].iloc[0]; r2=bowling[bowling.bowler==p2].iloc[0]
        for label,col in [("Wickets","total_wickets"),("Economy","economy"),("Average","bowling_avg"),("Overs","overs")]:
            x,y=st.columns(2); x.metric(f"{p1} • {label}","—" if pd.isna(r1[col]) else r1[col]); y.metric(f"{p2} • {label}","—" if pd.isna(r2[col]) else r2[col])

elif page=="⚔️ Head-to-Head":
    hero("TEAM RIVALRIES","Head-to-Head Analyzer","Historical meetings, win shares and recent results.",["Normalized teams","Exact counts"])
    teams=sorted(set(matches.team1)|set(matches.team2)); a,b=st.columns(2); t1=a.selectbox("Team 1",teams); t2=b.selectbox("Team 2",[t for t in teams if t!=t1]); h=matches[(((matches.team1==t1)&(matches.team2==t2))|((matches.team1==t2)&(matches.team2==t1)))]
    if h.empty: st.warning("No matches found.")
    else:
        w1=int((h.winner==t1).sum()); w2=int((h.winner==t2).sum()); nr=len(h)-w1-w2; c=st.columns(4)
        for col,(a1,b1,d) in zip(c,[("Matches",len(h),"Total"),(f"{t1} wins",w1,"Decided matches"),(f"{t2} wins",w2,"Decided matches"),("No result",nr,"Other")]):
            with col: card(a1,b1,d)
        fig=go.Figure(go.Bar(x=[t1,t2],y=[w1,w2],text=[w1,w2],textposition="auto")); fig.update_layout(height=320,showlegend=False,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#eaf1f8"),margin=dict(l=20,r=20,t=20,b=20)); show_plot(fig)
        st.dataframe(h[["date","venue","team1","team2","winner"]].sort_values("date",ascending=False).head(8),use_container_width=True,hide_index=True)

elif page=="📈 Run Progression":
    hero("MATCH VISUALIZER","Run Progression","Cumulative over-by-over scoring curves with hover details — zoom controls removed.",["Ball-by-ball","No zoom toolbar"])
    year=st.number_input("Season",2008,2026,2026,key="rp_year"); teams=sorted([t for t in set(matches.team1)|set(matches.team2) if active(t,int(year))]); a,b=st.columns(2); t1=a.selectbox("Team 1",teams,key="rp1"); t2=b.selectbox("Team 2",[t for t in teams if t!=t1],key="rp2"); h=matches[(matches.season.astype(int)==int(year))&((((matches.team1==t1)&(matches.team2==t2)))|(((matches.team1==t2)&(matches.team2==t1))))].sort_values("date")
    if h.empty: st.warning("No match found for this pairing in the selected season.")
    else:
        opts=[f"{r.date.date() if pd.notna(r.date) else 'Match'} • {r.team1} vs {r.team2} • {r.venue}" for r in h.itertuples()]; pick=st.selectbox("Select match",opts); r=h.iloc[opts.index(pick)]; mb=balls[balls.match_id==str(r.match_id)]; ov=mb.groupby(["batting_team","over"],as_index=False).runs_total.sum(); fig=go.Figure()
        for team in [r.team1,r.team2]:
            d=ov[ov.batting_team==team].copy(); d["cum"]=d.runs_total.cumsum(); fig.add_trace(go.Scatter(x=d.over+1,y=d.cum,mode="lines+markers",name=team,line=dict(width=3)))
        fig.update_layout(title=f"{r.team1} vs {r.team2}",xaxis_title="Over",yaxis_title="Cumulative runs",height=500,hovermode="x unified",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#eaf1f8"),legend=dict(orientation="h",y=1.08,x=0),margin=dict(l=20,r=20,t=65,b=35)); show_plot(fig); st.success(f"🏆 Winner: {r.winner}")

st.markdown('<div class="footer">IPL Intelligence Hub • Streamlit • pandas • Plotly • scikit-learn • ChromaDB • Hybrid RAG</div>',unsafe_allow_html=True)
