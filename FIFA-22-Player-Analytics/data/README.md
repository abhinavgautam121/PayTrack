# 📂 Data Source

## FIFA 22 Complete Player Dataset

This project uses the **FIFA 22 Complete Player Dataset** from Kaggle, which contains detailed attributes for every player registered in FIFA 22.

### 📥 Download Instructions

1. Visit the Kaggle dataset page:  
   🔗 [FIFA 22 Complete Player Dataset](https://www.kaggle.com/datasets/stefanoleone992/fifa-22-complete-player-dataset)

2. Download `players_22.csv` and place it in this `data/` directory.

3. (Optional) For historical trend analysis, also download:
   - `players_15.csv` through `players_21.csv`

### 📊 Dataset Overview

| Property | Value |
|---|---|
| **Source** | EA Sports FIFA 22 |
| **Records** | ~19,000+ players |
| **Features** | 100+ attributes per player |
| **File Size** | ~13 MB (players_22.csv) |
| **Format** | CSV (comma-separated) |

### 🔑 Key Columns Used in This Analysis

| Column | Description | Example |
|---|---|---|
| `short_name` | Player display name | L. Messi |
| `overall` | Current overall rating (0–99) | 93 |
| `potential` | Maximum potential rating | 93 |
| `age` | Player age in years | 34 |
| `nationality_name` | Country of origin | Argentina |
| `club_name` | Current club | Paris Saint-Germain |
| `league_name` | League of current club | French Ligue 1 |
| `value_eur` | Estimated market value (€) | 78,000,000 |
| `wage_eur` | Weekly wage (€) | 320,000 |
| `player_positions` | Playing positions | RW, ST, CF |
| `pace` | Pace attribute (0–99) | 85 |
| `shooting` | Shooting attribute (0–99) | 92 |
| `passing` | Passing attribute (0–99) | 91 |
| `dribbling` | Dribbling attribute (0–99) | 95 |
| `defending` | Defending attribute (0–99) | 34 |
| `physic` | Physical attribute (0–99) | 65 |

### ⚠️ Note

The CSV files are excluded from version control (`.gitignore`) due to their size. You must download them manually from Kaggle before running the analysis scripts.
