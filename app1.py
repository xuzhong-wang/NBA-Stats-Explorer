# app1.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.style as style

# Set page config
st.set_page_config(page_title="NBA Player Stats Explorer", layout="centered")

# CSS for page title and description with system theme adaptive color
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

# Display page title and description
st.markdown('<div class="big-title">🏀 NBA Stats Explorer: 2016–2025</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="description">This app explores and compares the performance of top NBA players across multiple seasons using a comprehensive blend of traditional and advanced metrics, which provides a fuller picture of player impact and contribution.</div>', 
    unsafe_allow_html=True
)

# Load player stats data from CSV file
df = pd.read_csv("output/nba_selected_stats.csv")

# Draw a horizontal separator line
st.markdown("---")

# Get unique player list sorted alphabetically
players = sorted(df["Player"].unique())
default_players = ["LeBron James", "Stephen Curry", "Kevin Durant"]

# Multi-select box for choosing players to compare
selected_players = st.multiselect("👤 Select players to compare:", players, default=default_players)

# Dictionary mapping metric codes to human-readable names
metric_names = {
    "PTS": "Points Per Game",
    "TRB": "Total Rebounds Per Game",
    "AST": "Assists Per Game",
    "STL": "Steals Per Game",
    "BLK": "Blocks Per Game",
    "TOV": "Turnovers Per Game",
    "FT": "Free Throws Per Game",
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

# Dropdown for selecting metric to visualize
selected_metric = st.selectbox("📈 Select a metric to visualize:", metrics)

# Allow user to choose chart theme for matplotlib: Light or Dark
theme = st.selectbox("Choose theme for charts:", ["Light", "Dark"])

# Apply matplotlib styles and colors according to chosen theme
if theme == "Dark":
    style.use('dark_background')
    title_color = 'white'
    label_color = 'white'
    grid_color = 'gray'
    tick_color = 'white'
else:
    style.use('default')
    title_color = 'black'
    label_color = 'black'
    grid_color = 'lightgray'
    tick_color = 'black'

# Plot the data with matplotlib and display on Streamlit
if selected_players and selected_metric:
    fig, ax = plt.subplots(figsize=(8, 4))
    for player in selected_players:
        player_data = df[df["Player"] == player]
        ax.plot(player_data["Season"], player_data[selected_metric], marker="o", label=player)

    ax.set_title(f"{metric_names[selected_metric]} by Season", fontsize=16, color=title_color)
    ax.set_xlabel("Season", fontsize=12, color=label_color)
    ax.set_ylabel(metric_names[selected_metric], fontsize=12, color=label_color)
    ax.legend(title="Player", loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5, color=grid_color)
    plt.xticks(rotation=45, color=tick_color)
    plt.yticks(color=tick_color)
    st.pyplot(fig)
else:
    st.warning("Please select at least one player and one metric.")
    
    
# Draw another horizontal line
st.markdown("---")

# Add an expander for advanced metric explanations
with st.expander("📘 Advanced Metrics Explained"):
    st.markdown("#### 🧮 True Shooting Percentage (TS%)")
    st.markdown("""
    TS% accounts for a player's efficiency on **field goals, 3-point shots, and free throws**.  
    It improves upon FG% by incorporating the value of 3-point shots and the impact of free throws.
    """)
    st.markdown("**Formula:**")
    st.latex(r"\text{TS\%} = \frac{\text{Points}}{2 \times (\text{FGA} + 0.44 \times \text{FTA})}")
    st.markdown("""
    **Where:**  
    - **FGA** = Field Goal Attempts  
    - **FTA** = Free Throw Attempts  
    """)
    
    st.markdown("#### 📦 Box Plus/Minus (BPM)")
    st.markdown("""
    BPM estimates a player's **overall impact per 100 possessions** relative to an average player.  
    It uses box score stats and team performance while the player is on the court.
    """)

    st.markdown("#### ⚔️ Offensive Box Plus/Minus (OBPM)")
    st.markdown("""
    OBPM isolates a player's **offensive contribution**, measuring how many more (or fewer) points  
    they generate per 100 possessions compared to the league average.
    """)

    st.markdown("#### 🛡️ Defensive Box Plus/Minus (DBPM)")
    st.markdown("""
    DBPM does the same as OBPM but focuses on **defensive impact**, estimating points saved  
    per 100 possessions.
    """)

    st.markdown("#### 🧠 Player Efficiency Rating (PER)")
    st.markdown("""
    PER is a per-minute rating developed by John Hollinger to summarize **all box score contributions**  
    into a single number. The league average is always set to **15.0**.  
    It's highly correlated with usage and scoring, but may overvalue high-volume shooters.
    """)

    st.markdown("#### 🏆 Win Shares (WS)")
    st.markdown("""
    WS estimates **how many team wins** a player contributed to based on their offensive and  
    defensive statistics.  
    """)
