"""
FIFA 22 Player Analysis
=======================
Exploratory data analysis of 19,000+ professional footballers from the FIFA 22 dataset.

Analysis Areas:
    1. Age Demographics & Distribution
    2. Peak Performance Age Identification
    3. Top Player Rankings & Comparisons
    4. Nationality Talent Pipeline Analysis
    5. Wage vs Performance Correlation
    6. Position Group Attribute Profiling

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

# Paths (relative to project root)
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
VIZ_DIR = os.path.join(os.path.dirname(__file__), '..', 'visualizations')
DATA_FILE = os.path.join(DATA_DIR, 'players_22.csv')

# Plot style
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
})


def load_data(filepath: str) -> pd.DataFrame:
    """Load the FIFA 22 player dataset from CSV.

    Args:
        filepath: Path to the players_22.csv file.

    Returns:
        DataFrame with all player records.
    """
    df = pd.read_csv(filepath, low_memory=False)
    print(f"✅ Loaded dataset: {df.shape[0]:,} players × {df.shape[1]} attributes")
    return df


# ─────────────────────────────────────────────
# 1. AGE DEMOGRAPHICS
# ─────────────────────────────────────────────

def analyze_age_demographics(df: pd.DataFrame) -> dict:
    """Compute key age statistics across the player population.

    Returns a dict of age metrics for downstream reporting.
    """
    stats = {
        'youngest': df['age'].min(),
        'oldest': df['age'].max(),
        'mean': round(df['age'].mean(), 1),
        'mode': df['age'].mode()[0],
        'under_21': int((df['age'] < 21).sum()),
        'over_33': int((df['age'] > 33).sum()),
    }

    print("\n" + "=" * 45)
    print("  AGE DEMOGRAPHICS")
    print("=" * 45)
    print(f"  Youngest player  : {stats['youngest']} years")
    print(f"  Oldest player    : {stats['oldest']} years")
    print(f"  Average age      : {stats['mean']} years")
    print(f"  Most common age  : {stats['mode']} years")
    print(f"  Players under 21 : {stats['under_21']:,}")
    print(f"  Players over 33  : {stats['over_33']:,}")

    return stats


def plot_age_distribution(df: pd.DataFrame) -> None:
    """Histogram + KDE of player age distribution with mean and mode lines."""
    fig, ax = plt.subplots(figsize=(12, 5))

    sns.histplot(df['age'], bins=range(15, 56), kde=True, color='steelblue', ax=ax)

    ax.axvline(
        df['age'].mean(), color='red', linestyle='--',
        label=f"Mean age: {df['age'].mean():.1f}"
    )
    ax.axvline(
        df['age'].mode()[0], color='orange', linestyle='--',
        label=f"Most common: {df['age'].mode()[0]}"
    )

    ax.set_title("Player Age Distribution in FIFA 22", fontsize=14, fontweight='bold')
    ax.set_xlabel("Age")
    ax.set_ylabel("Number of Players")
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, 'age_distribution.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  📊 Saved: age_distribution.png")


# ─────────────────────────────────────────────
# 2. PEAK PERFORMANCE AGE
# ─────────────────────────────────────────────

def analyze_peak_age(df: pd.DataFrame) -> tuple:
    """Find the age at which players have the highest average overall rating.

    Only considers ages with ≥10 players for statistical robustness.

    Returns:
        Tuple of (peak_age, peak_rating).
    """
    age_stats = df.groupby('age').agg(
        avg_overall=('overall', 'mean'),
        player_count=('overall', 'count')
    ).reset_index()

    # Filter for statistical significance
    age_stats = age_stats[age_stats['player_count'] >= 10]

    peak_age = age_stats.loc[age_stats['avg_overall'].idxmax(), 'age']
    peak_rating = age_stats['avg_overall'].max()

    print(f"\n  🏆 Peak Performance Age : {peak_age}")
    print(f"     Peak Average Rating  : {peak_rating:.2f}")

    return peak_age, peak_rating


def plot_peak_age(df: pd.DataFrame) -> None:
    """Line chart: average rating by age overlaid with player count bars."""
    age_stats = df.groupby('age').agg(
        avg_overall=('overall', 'mean'),
        player_count=('overall', 'count')
    ).reset_index()

    age_stats = age_stats[age_stats['player_count'] >= 10]
    peak_age = age_stats.loc[age_stats['avg_overall'].idxmax(), 'age']
    peak_rating = age_stats['avg_overall'].max()

    fig, ax1 = plt.subplots(figsize=(14, 6))

    # Bar chart: player count
    ax2 = ax1.twinx()
    ax2.bar(age_stats['age'], age_stats['player_count'],
            alpha=0.15, color='steelblue', label='Player Count')
    ax2.set_ylabel('Number of Players', color='steelblue', fontsize=11)

    # Line chart: avg rating
    ax1.plot(age_stats['age'], age_stats['avg_overall'],
             marker='o', color='navy', linewidth=2, markersize=5,
             label='Avg Overall Rating', zorder=5)

    ax1.axvline(peak_age, color='red', linestyle='--', label=f'Peak age: {peak_age}')
    ax1.annotate(f'Peak\n{peak_rating:.1f} avg\nAge {peak_age}',
                 xy=(peak_age, peak_rating),
                 xytext=(peak_age + 2, peak_rating - 2),
                 fontsize=10, fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color='red'))

    ax1.set_xlabel('Age')
    ax1.set_ylabel('Average Overall Rating')
    ax1.set_title('Average Player Rating by Age — FIFA 22\n(Bars show player count at each age)',
                  fontsize=13, fontweight='bold')
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, 'peak_age_analysis.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  📊 Saved: peak_age_analysis.png")


# ─────────────────────────────────────────────
# 3. TOP 10 PLAYERS
# ─────────────────────────────────────────────

def get_top_players(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return the top N players by overall rating."""
    cols = ['short_name', 'overall', 'potential', 'age',
            'nationality_name', 'club_name', 'value_eur', 'wage_eur']
    top = df[cols].sort_values('overall', ascending=False).head(n)

    print(f"\n{'=' * 45}")
    print(f"  TOP {n} HIGHEST RATED PLAYERS")
    print(f"{'=' * 45}")
    print(top[['short_name', 'overall', 'potential', 'age',
               'nationality_name', 'club_name']].to_string(index=False))
    return top


def plot_top_players(top: pd.DataFrame) -> None:
    """Horizontal bar chart of top 10 players by overall rating."""
    # Custom colors: gold for #1, silver for #2, cornflower for rest
    colors = ['#FFD700', '#C0C0C0'] + ['#6495ED'] * (len(top) - 2)

    fig, ax = plt.subplots(figsize=(12, 7))

    bars = ax.barh(top['short_name'][::-1], top['overall'][::-1],
                   color=colors[::-1], height=0.6, edgecolor='white')

    # Annotate with nationality + club
    for bar, (_, row) in zip(bars, top[::-1].iterrows()):
        ax.text(bar.get_x() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"  {row['nationality_name']} | {row['club_name']}",
                va='center', fontsize=9, color='white', fontweight='bold')
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                f"{row['overall']}", va='center', fontsize=11, fontweight='bold')

    ax.set_xlim(83, 95)
    ax.set_title('Top 10 Highest Rated Players — FIFA 22',
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Overall Rating')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, 'top10_players.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  📊 Saved: top10_players.png")


def plot_rating_vs_wage(top: pd.DataFrame) -> None:
    """Side-by-side comparison: rating ranking vs wage ranking for top 10."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    fig.suptitle('Top 10 FIFA 22 Players — Rating & Wages',
                 fontsize=14, fontweight='bold', y=1.02)

    # Left: by overall rating
    axes[0].barh(top['short_name'][::-1], top['overall'][::-1],
                 color='#6495ED', height=0.6, edgecolor='white')
    for bar, val in zip(axes[0].patches, top['overall'][::-1]):
        axes[0].text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                     f"{val}", va='center', fontsize=10, fontweight='bold')
    axes[0].set_xlim(83, 95)
    axes[0].set_title('By Overall Rating', fontsize=12)
    axes[0].spines['top'].set_visible(False)
    axes[0].spines['right'].set_visible(False)

    # Right: by weekly wage
    wage_sorted = top.sort_values('wage_eur', ascending=False)
    axes[1].barh(wage_sorted['short_name'][::-1],
                 wage_sorted['wage_eur'][::-1] / 1000,
                 color='#E8945A', height=0.6, edgecolor='white')
    for bar, val in zip(axes[1].patches, wage_sorted['wage_eur'][::-1]):
        axes[1].text(bar.get_width() + 2, bar.get_y() + bar.get_height() / 2,
                     f"€{val / 1000:.0f}K", va='center', fontsize=10, fontweight='bold')
    axes[1].set_title('By Weekly Wage (€K)', fontsize=12)
    axes[1].spines['top'].set_visible(False)
    axes[1].spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, 'top10_rating_vs_wage.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  📊 Saved: top10_rating_vs_wage.png")


# ─────────────────────────────────────────────
# 4. NATIONALITY ANALYSIS
# ─────────────────────────────────────────────

def analyze_nationalities(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate player statistics by nationality."""
    nation_stats = df.groupby('nationality_name').agg(
        player_count=('overall', 'count'),
        avg_overall=('overall', 'mean'),
        avg_potential=('potential', 'mean'),
        total_value=('value_eur', 'sum')
    ).reset_index()

    nation_stats['total_value_B'] = (nation_stats['total_value'] / 1e9).round(2)

    top15 = nation_stats.sort_values('player_count', ascending=False).head(15)

    print(f"\n{'=' * 45}")
    print("  TOP 15 NATIONS BY PLAYER COUNT")
    print(f"{'=' * 45}")
    print(top15[['nationality_name', 'player_count', 'avg_overall']
               ].round(1).to_string(index=False))

    return nation_stats


def plot_nationality_dominance(df: pd.DataFrame, nation_stats: pd.DataFrame) -> None:
    """Dual chart: most players by nation (left) and highest avg rating by nation (right)."""
    top15_count = nation_stats.sort_values('player_count', ascending=False).head(15)

    # Highest avg rating among nations with ≥50 players
    quality = (nation_stats[nation_stats['player_count'] >= 50]
               .sort_values('avg_overall', ascending=False)
               .head(15))

    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    fig.suptitle('Nationality Dominance in FIFA 22', fontsize=16, fontweight='bold', y=1.02)

    # Left: player count
    colors_left = sns.color_palette('Blues_d', len(top15_count))
    axes[0].barh(top15_count['nationality_name'][::-1],
                 top15_count['player_count'][::-1],
                 color=colors_left[::-1], height=0.7, edgecolor='white')
    for bar, val in zip(axes[0].patches, top15_count['player_count'][::-1]):
        axes[0].text(bar.get_width() + 10, bar.get_y() + bar.get_height() / 2,
                     f"{val:,}", va='center', fontsize=9, fontweight='bold')
    axes[0].set_title('Most Players by Nation', fontsize=12)
    axes[0].set_xlabel('Number of Players')
    axes[0].spines['top'].set_visible(False)
    axes[0].spines['right'].set_visible(False)

    # Right: avg rating
    colors_right = sns.color_palette('Oranges_d', len(quality))
    axes[1].barh(quality['nationality_name'][::-1],
                 quality['avg_overall'][::-1],
                 color=colors_right[::-1], height=0.7, edgecolor='white')
    for bar, val in zip(axes[1].patches, quality['avg_overall'][::-1].round(1)):
        axes[1].text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                     f"{val}", va='center', fontsize=9, fontweight='bold', color='#E8945A')
    axes[1].set_title('Highest Avg Rating by Nation\n(min. 50 players)',
                      fontsize=12, color='#E8945A')
    axes[1].set_xlabel('Average Overall Rating')
    axes[1].spines['top'].set_visible(False)
    axes[1].spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, 'nationality_dominance.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  📊 Saved: nationality_dominance.png")


def plot_nation_bubble(nation_stats: pd.DataFrame) -> None:
    """Bubble chart: quantity (player count) vs quality (avg rating) vs market value."""
    plot_df = (nation_stats[nation_stats['player_count'] >= 100]
               .sort_values('player_count', ascending=False)
               .head(20))

    fig, ax = plt.subplots(figsize=(14, 9))

    scatter = ax.scatter(
        plot_df['player_count'],
        plot_df['avg_overall'],
        s=plot_df['total_value_B'] * 30,
        c=plot_df['avg_overall'],
        cmap='RdYlGn',
        alpha=0.7,
        edgecolors='gray',
        linewidth=0.5,
    )

    for _, row in plot_df.iterrows():
        ax.annotate(row['nationality_name'],
                    (row['player_count'], row['avg_overall']),
                    fontsize=9, fontweight='bold',
                    xytext=(5, 5), textcoords='offset points')

    # Reference lines
    avg_count = plot_df['player_count'].mean()
    avg_rating = plot_df['avg_overall'].mean()
    ax.axhline(avg_rating, color='gray', linestyle='--', alpha=0.4, label=f'Avg rating: {avg_rating:.1f}')
    ax.axvline(avg_count, color='gray', linestyle=':', alpha=0.4, label=f'Avg count: {avg_count:.0f}')

    plt.colorbar(scatter, label='Avg Overall Rating')
    ax.set_xlabel('Number of Players in FIFA 22', fontsize=12)
    ax.set_ylabel('Average Overall Rating', fontsize=12)
    ax.set_title('Nation Comparison: Quantity vs Quality\n(Bubble size = Total Squad Market Value €B)',
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, 'nation_bubble_chart.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  📊 Saved: nation_bubble_chart.png")


# ─────────────────────────────────────────────
# 5. WAGE ANALYSIS
# ─────────────────────────────────────────────

def analyze_wages(df: pd.DataFrame) -> None:
    """Correlation analysis between player wage and overall rating."""
    clean = df[(df['wage_eur'] > 0) & (df['overall'] > 0)].copy()
    corr = clean['wage_eur'].corr(clean['overall'])

    print(f"\n{'=' * 45}")
    print("  WAGE vs PERFORMANCE ANALYSIS")
    print(f"{'=' * 45}")
    print(f"  Correlation (Wage ↔ Overall): {corr:.3f}")

    # Wage stats by rating bracket
    clean['Rating_Band'] = pd.cut(
        clean['overall'],
        bins=[40, 60, 65, 70, 75, 80, 85, 100],
        labels=['40–60', '60–65', '65–70', '70–75', '75–80', '80–85', '85+']
    )

    wage_by_band = clean.groupby('Rating_Band', observed=True)['wage_eur'].agg(
        median_wage='median', mean_wage='mean', player_count='count'
    ).reset_index()

    wage_by_band['median_K'] = (wage_by_band['median_wage'] / 1000).round(1)
    wage_by_band['mean_K'] = (wage_by_band['mean_wage'] / 1000).round(1)

    print("\n  Wage breakdown by rating bracket:\n")
    print(wage_by_band[['Rating_Band', 'player_count', 'median_K', 'mean_K']].to_string(index=False))


def plot_wage_by_position(df: pd.DataFrame) -> None:
    """Strip + bar plot showing wage distribution by position group."""
    pos_map = {
        'GK': 'Goalkeeper',
        'CB': 'Defender', 'LB': 'Defender', 'RB': 'Defender',
        'LWB': 'Defender', 'RWB': 'Defender',
        'CDM': 'Midfielder', 'CM': 'Midfielder', 'CAM': 'Midfielder',
        'LM': 'Midfielder', 'RM': 'Midfielder',
        'LW': 'Forward', 'RW': 'Forward', 'ST': 'Forward',
        'CF': 'Forward', 'LS': 'Forward', 'RS': 'Forward',
        'LF': 'Forward', 'RF': 'Forward', 'SS': 'Forward',
    }

    df_pos = df.copy()
    df_pos['Primary_Position'] = df_pos['player_positions'].str.split(',').str[0].str.strip()
    df_pos['Pos_Group'] = df_pos['Primary_Position'].map(pos_map)
    df_pos = df_pos.dropna(subset=['Pos_Group'])
    df_pos = df_pos[df_pos['wage_eur'] > 0]

    pos_order = ['Forward', 'Midfielder', 'Goalkeeper', 'Defender']
    colors = {'Forward': '#EF4444', 'Midfielder': '#10B981',
              'Goalkeeper': '#F59E0B', 'Defender': '#3B82F6'}

    fig, ax = plt.subplots(figsize=(14, 7))

    # Average wage bars
    avg_wages = df_pos.groupby('Pos_Group')['wage_eur'].mean()
    bar_data = [avg_wages.get(p, 0) for p in pos_order]
    ax.bar(pos_order, bar_data, color=[colors[p] for p in pos_order],
           alpha=0.3, width=0.6, zorder=1)

    # Strip plot overlay (sampled for performance)
    for p in pos_order:
        subset = df_pos[df_pos['Pos_Group'] == p]['wage_eur']
        if len(subset) > 500:
            subset = subset.sample(500, random_state=42)
        x = np.random.normal(pos_order.index(p), 0.15, size=len(subset))
        ax.scatter(x, subset, alpha=0.15, s=8, color=colors[p], zorder=2)

    # Labels
    for i, p in enumerate(pos_order):
        ax.text(i, -3500, f"Avg: €{avg_wages.get(p, 0) / 1000:.1f}K",
                ha='center', fontsize=10, fontweight='bold', color=colors[p])

    ax.set_ylabel('Weekly Wage (€ thousands)', fontsize=12)
    ax.set_xlabel('Position Group', fontsize=12)
    ax.set_title('Wage Distribution by Position — FIFA 22\n(bars = average, dots = individual players)',
                 fontsize=14, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, 'wage_by_position.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  📊 Saved: wage_by_position.png")


# ─────────────────────────────────────────────
# 6. POSITION ATTRIBUTE PROFILING
# ─────────────────────────────────────────────

def plot_position_attributes(df: pd.DataFrame) -> None:
    """Grouped bar chart of average attributes by position group."""
    pos_map = {
        'GK': 'Goalkeeper',
        'CB': 'Defender', 'LB': 'Defender', 'RB': 'Defender',
        'LWB': 'Defender', 'RWB': 'Defender',
        'CDM': 'Midfielder', 'CM': 'Midfielder', 'CAM': 'Midfielder',
        'LM': 'Midfielder', 'RM': 'Midfielder',
        'LW': 'Forward', 'RW': 'Forward', 'ST': 'Forward',
        'CF': 'Forward', 'LS': 'Forward', 'RS': 'Forward',
        'LF': 'Forward', 'RF': 'Forward', 'SS': 'Forward',
    }

    df_pos = df.copy()
    df_pos['Primary_Position'] = df_pos['player_positions'].str.split(',').str[0].str.strip()
    df_pos['Pos_Group'] = df_pos['Primary_Position'].map(pos_map)
    df_pos = df_pos.dropna(subset=['Pos_Group'])

    attr_cols = ['pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']
    pos_stats = df_pos.groupby('Pos_Group')[attr_cols].mean().round(1)

    pos_order = ['Defender', 'Forward', 'Goalkeeper', 'Midfielder']
    colors_p = {'Defender': '#F59E0B', 'Forward': '#6495ED',
                'Goalkeeper': '#10B981', 'Midfielder': '#EF4444'}

    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(attr_cols))
    width = 0.2

    for i, pos in enumerate(pos_order):
        if pos in pos_stats.index:
            vals = pos_stats.loc[pos, attr_cols].values
            ax.bar(x + i * width, vals, width, label=pos, color=colors_p[pos], alpha=0.85)

    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels([c.capitalize() for c in attr_cols], fontsize=11)
    ax.set_ylabel('Average Attribute Score', fontsize=12)
    ax.set_title('Average Player Attributes by Position Group — FIFA 22',
                 fontsize=14, fontweight='bold')
    ax.legend()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, 'position_attributes.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  📊 Saved: position_attributes.png")


# ─────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────

def main():
    """Run the complete player analysis pipeline."""
    print("\n" + "═" * 50)
    print("  ⚽  FIFA 22 PLAYER ANALYSIS")
    print("═" * 50)

    # Ensure output directory exists
    os.makedirs(VIZ_DIR, exist_ok=True)

    # Load data
    df = load_data(DATA_FILE)

    # 1. Age demographics
    analyze_age_demographics(df)
    plot_age_distribution(df)

    # 2. Peak performance age
    analyze_peak_age(df)
    plot_peak_age(df)

    # 3. Top players
    top10 = get_top_players(df, n=10)
    plot_top_players(top10)
    plot_rating_vs_wage(top10)

    # 4. Nationality analysis
    nation_stats = analyze_nationalities(df)
    plot_nationality_dominance(df, nation_stats)
    plot_nation_bubble(nation_stats)

    # 5. Wage analysis
    analyze_wages(df)
    plot_wage_by_position(df)

    # 6. Position attributes
    plot_position_attributes(df)

    print("\n" + "═" * 50)
    print("  ✅ Analysis complete — 8 visualizations saved")
    print(f"     Output: {os.path.abspath(VIZ_DIR)}")
    print("═" * 50 + "\n")


if __name__ == '__main__':
    main()
