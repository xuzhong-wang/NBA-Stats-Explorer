"""Streamlit entry point for the NBA Stats Explorer app.

This module loads the cleaned player statistics and presents three views:
1. Metric trends for multiple players across seasons.
2. Summary comparison of regular-season MVP vs. Finals MVP for a season.
3. Advanced detail view for an individual player.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

import altair as alt
import pandas as pd
import streamlit as st


# ---------------------------------------------------------------------------
# Page setup and configuration
# ---------------------------------------------------------------------------


def configure_page() -> None:
    """Configure Streamlit page defaults and base styling."""

    st.set_page_config(
        page_title="NBA Player Stats Explorer",
        layout="wide",
        page_icon="🏀",
    )

    st.title("NBA Stats Explorer: 2016–2025")
    st.markdown(
        """
        Explore top NBA players across recent seasons using traditional and advanced metrics.
        Use the sidebar to navigate between trend, summary, and detail views.
        """
    )


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load the cleaned player statistics produced by the scraping notebook."""

    return pd.read_csv("output/nba_selected_stats.csv")


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------


MetricNameMap = Dict[str, str]


def get_metric_names() -> MetricNameMap:
    """Readable labels for each metric column used in charts and tables."""

    return {
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
        "WS": "Win Shares",
    }


def get_award_lookup() -> Dict[str, Tuple[Optional[str], Optional[str]]]:
    """Map each season to its regular-season MVP and Finals MVP.

    Names must match the `Player` column so that statistics can be shown.
    Missing data is represented by ``None`` and handled gracefully in the UI.
    """

    return {
        "2015-16": ("Stephen Curry", "LeBron James"),
        "2016-17": ("Russell Westbrook", "Kevin Durant"),
        "2017-18": ("James Harden", "Kevin Durant"),
        "2018-19": ("Giannis Antetokounmpo", "Kawhi Leonard"),
        "2019-20": ("Giannis Antetokounmpo", "LeBron James"),
        "2020-21": ("Nikola Jokić", "Giannis Antetokounmpo"),
        "2021-22": ("Nikola Jokić", "Stephen Curry"),
        "2022-23": ("Joel Embiid", "Nikola Jokić"),
        "2023-24": ("Nikola Jokić", "Jaylen Brown"),
        "2024-25": (None, None),
    }


# ---------------------------------------------------------------------------
# Sidebar and layout helpers
# ---------------------------------------------------------------------------


@dataclass
class SidebarSelections:
    """Container for all sidebar-controlled state."""

    view: str
    season: str
    trend_players: List[str]
    trend_metric: str
    chart_theme: str
    detail_player: str


def render_sidebar(df: pd.DataFrame, metric_names: MetricNameMap) -> SidebarSelections:
    """Render sidebar controls used across the three main views."""

    seasons = sorted(df["Season"].unique())
    players = sorted(df["Player"].unique())
    default_players = ["LeBron James", "Stephen Curry", "Kevin Durant"]

    with st.sidebar:
        st.header("Navigation")
        view = st.radio(
            "Select view",
            ["Metric trends", "MVP vs. Finals MVP", "Player detail"],
            index=0,
        )

        st.subheader("Filters")
        season = st.selectbox("Season", seasons, index=len(seasons) - 1)

        st.subheader("Chart options")
        chart_theme = st.selectbox("Theme", ["Streamlit", "Dark"], index=0)

        st.divider()
        st.subheader("Player selection")
        trend_players = st.multiselect(
            "Compare players",
            players,
            default=[p for p in default_players if p in players],
            help="Used in the metric trend view",
        )
        detail_player = st.selectbox("Detail view player", players)
        trend_metric = st.selectbox("Metric for trend view", list(metric_names.keys()))

    return SidebarSelections(
        view=view,
        season=season,
        trend_players=trend_players,
        trend_metric=trend_metric,
        chart_theme=chart_theme,
        detail_player=detail_player,
    )


# ---------------------------------------------------------------------------
# View renderers
# ---------------------------------------------------------------------------


def render_metric_trends(
    df: pd.DataFrame,
    players: Iterable[str],
    metric: str,
    metric_names: MetricNameMap,
    theme: str,
) -> None:
    """Display a multi-player line chart for the selected metric across seasons."""

    if not players:
        st.warning("Please select at least one player to see the trend chart.")
        return

    filtered = df[df["Player"].isin(players)]
    if filtered.empty:
        st.info("No data available for the selected players.")
        return

    color_scheme = "category10" if theme == "Streamlit" else "dark2"

    chart = (
        alt.Chart(filtered)
        .mark_line(point=True)
        .encode(
            x=alt.X("Season:N", sort=sorted(df["Season"].unique()), title="Season"),
            y=alt.Y(metric, title=metric_names.get(metric, metric), scale=alt.Scale(zero=False)),
            color=alt.Color("Player:N", title="Player", scale=alt.Scale(scheme=color_scheme)),
            tooltip=["Player", "Season", alt.Tooltip(metric, format=".2f")],
        )
        .properties(
            title=f"{metric_names.get(metric, metric)} by Season",
            height=400,
        )
    )

    st.subheader("Metric trends")
    st.altair_chart(chart, use_container_width=True)


def render_award_summary(
    df: pd.DataFrame,
    season: str,
    awards: Dict[str, Tuple[Optional[str], Optional[str]]],
    metric_names: MetricNameMap,
) -> None:
    """Show a side-by-side comparison of MVP and Finals MVP for the chosen season."""

    st.subheader("Season summary: MVP vs. Finals MVP")
    mvp, fmvp = awards.get(season, (None, None))

    cols_to_show = ["PTS", "TRB", "AST", "TS%", "BPM", "WS", "PER"]
    summary_labels = [metric_names[col] for col in cols_to_show]

    def _player_row(player: Optional[str]) -> Optional[pd.Series]:
        if not player:
            return None
        row = df[(df["Season"] == season) & (df["Player"] == player)]
        return row.iloc[0] if not row.empty else None

    mvp_row = _player_row(mvp)
    fmvp_row = _player_row(fmvp)

    col1, col2 = st.columns(2)
    with col1:
        _render_player_snapshot("Regular Season MVP", mvp, mvp_row, cols_to_show, summary_labels)
    with col2:
        _render_player_snapshot("Finals MVP", fmvp, fmvp_row, cols_to_show, summary_labels)

    st.caption(
        "Awards are mapped manually for each season. If a player is missing, it means the season's data"
        " is not available in the dataset."
    )


def _render_player_snapshot(
    title: str,
    player: Optional[str],
    row: Optional[pd.Series],
    cols_to_show: List[str],
    labels: List[str],
) -> None:
    """Render a card-like snapshot of player stats used in the summary view."""

    st.markdown(f"### {title}")
    if not player:
        st.info("Award data not available for this season yet.")
        return
    if row is None:
        st.warning(f"{player}'s stats for this season are not in the dataset.")
        return

    st.markdown(f"**{player}**")
    metrics_df = pd.DataFrame({"Metric": labels, "Value": row[cols_to_show].values})
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)


def render_player_detail(
    df: pd.DataFrame, player: str, season: str, metric_names: MetricNameMap
) -> None:
    """Show advanced metrics for a single player with focus on the selected season."""

    st.subheader("Player detail and advanced stats")
    player_df = df[df["Player"] == player].sort_values("Season")

    if player_df.empty:
        st.warning("No data available for the selected player.")
        return

    season_row = player_df[player_df["Season"] == season]
    selected_row = season_row.iloc[0] if not season_row.empty else None

    if selected_row is None:
        st.info("Selected season is not available for this player. Showing all seasons instead.")

    columns_to_display = ["Season", "Team", "Position", "PTS", "TRB", "AST", "TS%", "BPM", "OBPM", "DBPM", "PER", "WS"]
    st.dataframe(
        player_df[columns_to_display],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Advanced metrics for selected season")
    if selected_row is None:
        st.info("No advanced metrics available for this season.")
        return

    advanced_cols = ["TS%", "BPM", "OBPM", "DBPM", "PER", "WS"]
    advanced_labels = [metric_names[col] for col in advanced_cols]
    adv_df = pd.DataFrame(
        {
            "Metric": advanced_labels,
            "Value": [selected_row[col] for col in advanced_cols],
        }
    )

    bar_chart = (
        alt.Chart(adv_df)
        .mark_bar()
        .encode(
            x=alt.X("Metric", sort=None),
            y=alt.Y("Value", title="Value"),
            tooltip=["Metric", alt.Tooltip("Value", format=".2f")],
        )
        .properties(height=350)
    )

    st.altair_chart(bar_chart, use_container_width=True)


def render_metric_explanations() -> None:
    """Expandable section explaining advanced metrics for new users."""

    with st.expander("📘 Advanced Metrics Explained"):
        st.markdown("#### 🧮 True Shooting Percentage (TS%)")
        st.markdown(
            """
            TS% accounts for a player's efficiency on field goals, 3-point shots, and free throws.
            It improves upon FG% by incorporating the value of 3-point shots and the impact of free throws.
            """
        )
        st.latex(r"\text{TS\%} = \frac{\text{Points}}{2 \times (\text{FGA} + 0.44 \times \text{FTA})}")

        st.markdown("#### 📦 Box Plus/Minus (BPM)")
        st.markdown(
            """
            BPM estimates a player's overall impact per 100 possessions relative to an average player.
            It uses box score stats and team performance while the player is on the court.
            """
        )

        st.markdown("#### ⚔️ Offensive Box Plus/Minus (OBPM)")
        st.markdown(
            """
            OBPM isolates a player's offensive contribution, measuring how many more (or fewer) points
            they generate per 100 possessions compared to the league average.
            """
        )

        st.markdown("#### 🛡️ Defensive Box Plus/Minus (DBPM)")
        st.markdown(
            """
            DBPM does the same as OBPM but focuses on defensive impact, estimating points saved
            per 100 possessions.
            """
        )

        st.markdown("#### 🧠 Player Efficiency Rating (PER)")
        st.markdown(
            """
            PER is a per-minute rating developed by John Hollinger to summarize all box score contributions
            into a single number. The league average is always set to 15.0.
            """
        )

        st.markdown("#### 🏆 Win Shares (WS)")
        st.markdown(
            """
            WS estimates how many team wins a player contributed to based on their offensive and
            defensive statistics.
            """
        )


# ---------------------------------------------------------------------------
# Main app orchestration
# ---------------------------------------------------------------------------


def main() -> None:
    """Load data, collect sidebar input, and route to the active view."""

    configure_page()
    df = load_data()
    metric_names = get_metric_names()
    selections = render_sidebar(df, metric_names)
    award_lookup = get_award_lookup()

    if selections.view == "Metric trends":
        render_metric_trends(
            df=df,
            players=selections.trend_players,
            metric=selections.trend_metric,
            metric_names=metric_names,
            theme=selections.chart_theme,
        )
    elif selections.view == "MVP vs. Finals MVP":
        render_award_summary(
            df=df,
            season=selections.season,
            awards=award_lookup,
            metric_names=metric_names,
        )
    elif selections.view == "Player detail":
        render_player_detail(
            df=df,
            player=selections.detail_player,
            season=selections.season,
            metric_names=metric_names,
        )

    st.divider()
    render_metric_explanations()


if __name__ == "__main__":
    main()
