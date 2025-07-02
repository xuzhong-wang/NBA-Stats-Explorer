# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.style as style

st.set_page_config(page_title="NBA Player Stats Explorer", layout="centered")

# Page title and description with CSS styling
st.markdown(
    """
    <style>
    @media (prefers-color-scheme: dark) {
        .big-title {
            font-size: 40px !important;
            font-weight: 800;
            color: white;
            text-align: center;
            margin-bottom: 0.5rem;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .description {
            font-size: 18px;
            color: #CCCCCC;
            max-width: 700px;
            line-height: 1.6;
            text-align: justify;
            margin-left: 0;
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
    }

    @media (prefers-color-scheme: light) {
        .big-title {
            font-size: 40px !important;
            font-weight: 800;
            color: black;
            text-align: center;
            margin-bottom: 0.5rem;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .description {
            font-size: 18px;
            color: #333333;
            max-width: 700px;
            line-height: 1.6;
            text-align: justify;
            margin-left: 0;
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown('<div class="big-title">🏀 NBA Stats Explorer: 2016–2025</div>', unsafe_allow_html=True)
st.markdown('<div class="description">This app explores and compares the performance of top NBA players across multiple seasons using a comprehensive blend of traditional and advanced metrics, which provides a fuller picture of player impact and contribution.</div>', unsafe_allow_html=True)

# Load data
df = pd.read_csv("output/nba_selected_stats.csv")

# Add horizontal line
st.markdown("---")

# Select players
players = sorted(df["Player"].unique())
default_players = ["LeBron James", "Stephen Curry", "Kevin Durant"]
selected_players = st.multiselect("👤 Select players to compare:", players, default=default_players)

# Metric mapping dictionary (basic + shooting percentages + advanced)
metric_names = {
    "PTS": "Points Per Game",
    "TRB": "Total Rebounds",
    "AST": "Assists",
    "STL": "Steals",
    "BLK": "Blocks",
    "TOV": "Turnovers",
    "FT": "Free Throws",
    "FG%": "Field Goal %",
    "3P%": "3-Point %",
    "2P%": "2-Point %",
    "FT%": "Free Throw %",
    "TS%": "True Shooting %",
    "BPM": "Box Plus/Minus",
    "OBPM": "Offensive Box Plus/Minus",
    "DBPM": "Defensive Box Plus/Minus",
    "PER": "Player Efficiency Rating",
    "WS": "Win Shares"
}
metrics = list(metric_names.keys())
selected_metric = st.selectbox("📈 Select a metric to visualize:", metrics)

# Set dark style for matplotlib plots
style.use('dark_background')

# Visualization
if selected_players and selected_metric:
    fig, ax = plt.subplots(figsize=(8, 4))
    
    for player in selected_players:
        sub = df[df["Player"] == player]
        ax.plot(sub["Season"], sub[selected_metric], marker="o", label=player)

    ax.set_title(f"{metric_names[selected_metric]} by Season", fontsize=16, color='white')
    ax.set_xlabel("Season", fontsize=12, color='white')
    ax.set_ylabel(metric_names[selected_metric], fontsize=12, color='white')
    ax.legend(title="Player", loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5, color='gray')
    plt.xticks(rotation=45, color='white')
    plt.yticks(color='white')
    st.pyplot(fig)
else:
    st.warning("Please select at least one player and one metric.")