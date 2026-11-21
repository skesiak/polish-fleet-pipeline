"""Generate charts for README from the analytical tables."""

from pathlib import Path

import pandas as pd
import duckdb
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

DB = "fleet.duckdb"
CHARTS_DIR = Path("charts")
SQL_DIR = Path("sql/analysis")

CHARTS_DIR.mkdir(exist_ok=True)
con = duckdb.connect(DB, read_only=True)

def run_sql_file(name):
    """Execute a .sql file from sql/analysis and return the result as a DataFrame."""
    query = (SQL_DIR / name).read_text(encoding="utf-8")
    return con.execute(query).df()


df = run_sql_file("vehicle_age_by_region.sql")
df = df.sort_values("median_age")

fig, ax = plt.subplots(figsize=(8, 6))

ax.barh(df["voivodeship_name"], df["median_age"], color="#4878a8")

ax.set_xlabel("Median age at first registration (years)")
ax.set_title("Vehicles entering the market are oldest in eastern regions")

fig.tight_layout()
fig.savefig(CHARTS_DIR / "median_age_by_region.png", dpi=150)
plt.close(fig)


df = run_sql_file("vehicle_age_by_region.sql")

rho, p = spearmanr(df["median_age"], df["pct_used_import"])

p_text = "p < 0.001" if p < 0.001 else f"p = {p:.3f}"

fig, ax = plt.subplots(figsize=(7, 6))

ax.scatter(df["pct_used_import"], df["median_age"], s=60, color="#4878a8")

for _, row in df.iterrows():
    if row["voivodeship_name"] in ("mazowieckie", "lubelskie", "wielkopolskie"):
        ax.annotate(row["voivodeship_name"],
                    (row["pct_used_import"], row["median_age"]),
                    xytext=(5, 5), textcoords="offset points", fontsize=9)

ax.set_xlabel("Share of used imports (%)")
ax.set_ylabel("Median age at first registration (years)")
ax.set_title(f"Regions importing more used cars register older vehicles\n"
             f"Spearman rho = {rho:.2f}, p = {p_text}, n = {len(df)}")

fig.tight_layout()
fig.savefig(CHARTS_DIR / "age_vs_import.png", dpi=150)
plt.close(fig)



df = run_sql_file("fuel_mix_trend.sql")
df["date"] = pd.to_datetime(df["period"], format="%Y%m")

fig, ax = plt.subplots(figsize=(10, 6))

for category in ["petrol", "diesel", "hybrid_petrol", "lpg", "electric", "hybrid_diesel"]:
    subset = df[df["fuel_category"] == category].sort_values("date")
    ax.plot(subset["date"], subset["share_pct"], label=category, linewidth=2)

ax.set_ylabel("Share of first registrations (%)")
ax.set_title("Petrol holds flat while diesel and LPG give way to hybrids")
ax.legend()
ax.grid(axis="y", alpha=0.3)

fig.tight_layout()
fig.savefig(CHARTS_DIR / "fuel_mix_trend.png", dpi=150)
plt.close(fig)