"""
FIFA 22 Club & League Analysis
================================
Deep-dive into club-level economics, squad demographics, and league comparisons
using the FIFA 22 dataset.

Analysis Areas:
    1. Club Valuation Rankings (Top 10 Most Valuable Squads)
    2. Squad Age Profiling (Youngest vs Oldest Clubs)
    3. League Benchmarking (Top 8 European Leagues)
    4. Underpaid Talent Identification (Market Inefficiency Detection)
    5. Squad Diversity Analysis (International Composition)

Author : Abhinav Gautam
Dataset: Kaggle — FIFA 22 Complete Player Dataset
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
VIZ_DIR = os.path.join(os.path.dirname(__file__), '..', 'visualizations')
DATA_FILE = os.path.join(DATA_DIR, 'players_22.csv')

plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
})

MIN_SQUAD_SIZE = 11  # Minimum players for a club to be included


def load_club_data(filepath: str) -> pd.DataFrame:
    """Load FIFA 22 data and filter to players with valid club assignments.

    Clubs with fewer than MIN_SQUAD_SIZE players are excluded to ensure
    statistically meaningful comparisons.
    """
    df = pd.read_csv(filepath, low_memory=False)
    df_clubs = df.dropna(subset=['club_name']).copy()

    # Filter to clubs with enough players
    club_sizes = df_clubs['club_name'].value_counts()
    valid_clubs = club_sizes[club_sizes >= MIN_SQUAD_SIZE].index
    df_clubs = df_clubs[df_clubs['club_name'].isin(valid_clubs)]

    print(f"✅ Loaded: {len(df_clubs):,} players across "
          f"{df_clubs['club_name'].nunique():,} clubs "
          f"({df_clubs['league_name'].nunique():,} leagues)")

    return df_clubs


def compute_club_stats(df_clubs: pd.DataFrame) -> pd.DataFrame:
    """Aggregate player-level data to club-level statistics.

    Returns a DataFrame with one row per club containing:
        - total_value, avg_overall, avg_age, avg_wage, squad_size
        - num_nations (international diversity metric)
        - top_overall (best player rating)
    """
    club_stats = df_clubs.groupby('club_name').agg(
        total_value=('value_eur', 'sum'),
        avg_overall=('overall', 'mean'),
        avg_age=('age', 'mean'),
        avg_wage=('wage_eur', 'mean'),
        squad_size=('overall', 'count'),
        num_nations=('nationality_name', 'nunique'),
        top_overall=('overall', 'max'),
    ).reset_index()

    club_stats['total_value_M'] = (club_stats['total_value'] / 1e6).round(1)
    club_stats['avg_overall'] = club_stats['avg_overall'].round(1)
    club_stats['avg_age'] = club_stats['avg_age'].round(1)

    return club_stats


# ─────────────────────────────────────────────
# 1. CLUB VALUATION RANKINGS
# ─────────────────────────────────────────────

def show_top_clubs(club_stats: pd.DataFrame, n: int = 10) -> None:
    """Display the top N clubs ranked by total squad market value."""
    top = club_stats.sort_values('total_value', ascending=False).head(n)

    print(f"\n{'=' * 55}")
    print(f"  TOP {n} CLUBS BY TOTAL SQUAD VALUE")
    print(f"{'=' * 55}")
    print(top[['club_name', 'total_value_M', 'avg_overall',
               'squad_size', 'avg_age']].to_string(index=False))


# ─────────────────────────────────────────────
# 2. SQUAD AGE PROFILING
# ─────────────────────────────────────────────

def plot_squad_age_profile(club_stats: pd.DataFrame) -> None:
    """Side-by-side chart: 10 youngest vs 10 oldest squads.

    Business context: 'youngest squads' = future-building strategy;
    'oldest squads' = 'win now' competitive window.
    """
    youngest = club_stats.nsmallest(10, 'avg_age')
    oldest = club_stats.nlargest(10, 'avg_age')

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Squad Age Profile — Youngest vs Oldest Clubs',
                 fontsize=14, fontweight='bold', y=1.02)

    # Youngest Clubs
    axes[0].barh(youngest['club_name'], youngest['avg_age'],
                 color='#10B981', height=0.6, edgecolor='white')
    for bar, row in zip(axes[0].patches, youngest.itertuples()):
        axes[0].text(bar.get_width() + 0.05,
                     bar.get_y() + bar.get_height() / 2,
                     f"{row.avg_age:.1f} yrs (OVR {row.avg_overall:.1f})",
                     va='center', fontsize=9)
    axes[0].set_xlim(18, 28)
    axes[0].set_title('10 Youngest Squads\n(Future Builders)', fontsize=12)
    axes[0].set_xlabel('Average Squad Age')
    axes[0].invert_yaxis()
    axes[0].spines['top'].set_visible(False)
    axes[0].spines['right'].set_visible(False)

    # Oldest Clubs
    axes[1].barh(oldest['club_name'], oldest['avg_age'],
                 color='#EF4444', height=0.6, edgecolor='white')
    for bar, row in zip(axes[1].patches, oldest.itertuples()):
        axes[1].text(bar.get_width() + 0.05,
                     bar.get_y() + bar.get_height() / 2,
                     f"{row.avg_age:.1f} yrs (OVR {row.avg_overall:.1f})",
                     va='center', fontsize=9)
    axes[1].set_xlim(25, 35)
    axes[1].set_title('10 Oldest Squads\n(Win Now Mode)', fontsize=12)
    axes[1].set_xlabel('Average Squad Age')
    axes[1].invert_yaxis()
    axes[1].spines['top'].set_visible(False)
    axes[1].spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, 'squad_age.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  📊 Saved: squad_age.png")


# ─────────────────────────────────────────────
# 3. LEAGUE BENCHMARKING
# ─────────────────────────────────────────────

def benchmark_leagues(df_clubs: pd.DataFrame) -> None:
    """Compare Europe's top 8 leagues across key performance metrics."""
    top_leagues = [
        'English Premier League', 'Spain Primera Division',
        'German 1. Bundesliga', 'Italian Serie A',
        'French Ligue 1', 'Portuguese Liga ZON SAGRES',
        'Dutch Eredivisie', 'Belgian Jupiler Pro League',
    ]

    df_top = df_clubs[df_clubs['league_name'].isin(top_leagues)].copy()

    league_stats = df_top.groupby('league_name').agg(
        avg_overall=('overall', 'mean'),
        avg_wage_k=('wage_eur', 'mean'),
        avg_value_m=('value_eur', 'mean'),
        avg_age=('age', 'mean'),
        num_players=('overall', 'count'),
        top_overall=('overall', 'max'),
    ).round(1).reset_index()

    league_stats['avg_wage_k'] = (league_stats['avg_wage_k'] / 1000).round(1)
    league_stats['avg_value_m'] = (league_stats['avg_value_m'] / 1e6).round(2)

    # Readable league names
    short_names = {
        'English Premier League': 'Premier League',
        'Spain Primera Division': 'La Liga',
        'German 1. Bundesliga': 'Bundesliga',
        'Italian Serie A': 'Serie A',
        'French Ligue 1': 'Ligue 1',
        'Portuguese Liga ZON SAGRES': 'Liga Portugal',
        'Dutch Eredivisie': 'Eredivisie',
        'Belgian Jupiler Pro League': 'Jupiler Pro',
    }
    league_stats['league_name'] = league_stats['league_name'].map(short_names)

    print(f"\n{'=' * 60}")
    print("  LEAGUE BENCHMARKING — TOP 8 EUROPEAN LEAGUES")
    print(f"{'=' * 60}")
    print(league_stats[['league_name', 'avg_overall', 'avg_wage_k',
                         'avg_value_m', 'avg_age']].to_string(index=False))


# ─────────────────────────────────────────────
# 4. UNDERPAID TALENT IDENTIFICATION
# ─────────────────────────────────────────────

def find_underpaid_talent(df_clubs: pd.DataFrame) -> None:
    """Identify quality players (OVR ≥ 75) who are systematically underpaid.

    Uses a simple linear wage model: Expected_Wage = (Overall - 50) × 500
    Players with a negative wage gap exceeding €5K are flagged as 'gems'.

    Business insight: These are players a club could target for
    high-value-per-euro signings.
    """
    df_clubs = df_clubs.copy()
    df_clubs['Expected_Wage'] = (df_clubs['overall'] - 50) * 500
    df_clubs['Wage_Gap'] = df_clubs['wage_eur'] - df_clubs['Expected_Wage']

    underpaid = df_clubs[
        (df_clubs['overall'] >= 75) & (df_clubs['Wage_Gap'] < -5000)
    ]

    print(f"\n{'=' * 55}")
    print("  UNDERPAID TALENT IDENTIFICATION")
    print(f"{'=' * 55}")
    print(f"  Underpaid quality players found: {len(underpaid):,}")

    club_gems = (underpaid.groupby('club_name')
                 .agg(num_gems=('short_name', 'count'),
                      avg_overall=('overall', 'mean'),
                      avg_gap=('Wage_Gap', 'mean'))
                 .sort_values('num_gems', ascending=False)
                 .head(15))

    club_gems['avg_gap_k'] = (club_gems['avg_gap'] / 1000).round(1)
    club_gems['avg_overall'] = club_gems['avg_overall'].round(1)

    print("\n  Top 15 clubs with most underpaid quality players:\n")
    print(club_gems[['num_gems', 'avg_overall', 'avg_gap_k']].to_string())


# ─────────────────────────────────────────────
# 5. SQUAD DIVERSITY ANALYSIS
# ─────────────────────────────────────────────

def plot_squad_diversity(club_stats: pd.DataFrame) -> None:
    """Bar chart of the 15 most internationally diverse club squads."""
    top_diverse = club_stats.sort_values('num_nations', ascending=False).head(15)

    fig, ax = plt.subplots(figsize=(12, 6))

    bars = ax.barh(
        top_diverse['club_name'], top_diverse['num_nations'],
        color=sns.color_palette('Purples_d', len(top_diverse)),
        height=0.6, edgecolor='white',
    )

    for bar, row in zip(bars, top_diverse.itertuples()):
        ax.text(bar.get_width() + 0.2,
                bar.get_y() + bar.get_height() / 2,
                f"{int(row.num_nations)} nations | {row.squad_size} players",
                va='center', fontsize=9, color='gray')

    ax.set_xlabel('Number of Different Nationalities in Squad', fontsize=11)
    ax.set_title('Most Internationally Diverse Squads — FIFA 22',
                 fontsize=13, fontweight='bold', pad=15)
    ax.invert_yaxis()
    ax.set_xlim(0, max(top_diverse['num_nations']) + 2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, 'squad_diversity.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  📊 Saved: squad_diversity.png")


def analyze_league_diversity(df_clubs: pd.DataFrame) -> None:
    """Show average squad diversity by league (top 8)."""
    league_div = (df_clubs
                  .groupby(['league_name', 'club_name'])['nationality_name']
                  .nunique()
                  .reset_index()
                  .groupby('league_name')['nationality_name']
                  .mean()
                  .sort_values(ascending=False)
                  .head(8)
                  .round(1))

    print(f"\n{'=' * 45}")
    print("  AVERAGE SQUAD DIVERSITY BY LEAGUE")
    print(f"{'=' * 45}")
    print(league_div.to_string())


# ─────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────

def main():
    """Run the complete club & league analysis pipeline."""
    print("\n" + "═" * 50)
    print("  🏟️  FIFA 22 CLUB & LEAGUE ANALYSIS")
    print("═" * 50)

    os.makedirs(VIZ_DIR, exist_ok=True)

    # Load and prepare data
    df_clubs = load_club_data(DATA_FILE)
    club_stats = compute_club_stats(df_clubs)

    # 1. Club valuations
    show_top_clubs(club_stats)

    # 2. Squad age profiles
    plot_squad_age_profile(club_stats)

    # 3. League benchmarking
    benchmark_leagues(df_clubs)

    # 4. Underpaid talent
    find_underpaid_talent(df_clubs)

    # 5. Squad diversity
    plot_squad_diversity(club_stats)
    analyze_league_diversity(df_clubs)

    print("\n" + "═" * 50)
    print("  ✅ Club analysis complete — 2 visualizations saved")
    print(f"     Output: {os.path.abspath(VIZ_DIR)}")
    print("═" * 50 + "\n")


if __name__ == '__main__':
    main()
