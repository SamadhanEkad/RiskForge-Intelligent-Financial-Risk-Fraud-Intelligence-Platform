"""
RiskForge - Phase 1 Visual Exploratory Data Analysis (EDA)
Generates high-impact figures:
  1. reports/figures/01_dollar_asymmetry.png
  2. reports/figures/02_temporal_fraud_heatmap.png
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

from riskforge.utils.config import get_project_root
from riskforge.utils.plotting import set_corporate_style, save_figure, PALETTE


def generate_phase1_visualizations():
    set_corporate_style()
    root = get_project_root()
    parquet_path = root / "data" / "processed" / "clean_transactions.parquet"
    
    if not parquet_path.exists():
        raise FileNotFoundError(f"Clean data not found at {parquet_path}. Run cleaner.py first!")

    print("[*] Loading clean transactions dataset for visual EDA...")
    # Load core columns needed for Phase 1 plots
    cols = ["TransactionID", "isFraud", "TransactionAmt", "TransactionDT", "card4", "ProductCD", "has_identity_metadata"]
    df = pd.read_parquet(parquet_path, columns=cols)
    print(f"[*] Loaded {len(df):,} transactions.")

    # =========================================================================
    # VISUAL 1: The Dollar Asymmetry of Fraud (01_dollar_asymmetry.png)
    # =========================================================================
    print("[*] Generating Visual 1: Dollar Asymmetry Chart...")
    
    total_txns = len(df)
    total_fraud_txns = df["isFraud"].sum()
    fraud_txn_pct = (total_fraud_txns / total_txns) * 100
    legit_txn_pct = 100 - fraud_txn_pct

    total_dollars = df["TransactionAmt"].sum()
    fraud_dollars = df.loc[df["isFraud"] == 1, "TransactionAmt"].sum()
    fraud_dollar_pct = (fraud_dollars / total_dollars) * 100
    legit_dollar_pct = 100 - fraud_dollar_pct

    fig, ax = plt.subplots(figsize=(9, 5.5))
    categories = ["Transaction Count Volume", "Gross Dollar Volume ($)"]
    
    # Stacked bar plot
    bars_legit = [legit_txn_pct, legit_dollar_pct]
    bars_fraud = [fraud_txn_pct, fraud_dollar_pct]

    bar_width = 0.45
    x = np.arange(len(categories))

    p1 = ax.bar(x, bars_legit, width=bar_width, label="Legitimate", color=PALETTE["legit"], edgecolor="white")
    p2 = ax.bar(x, bars_fraud, width=bar_width, bottom=bars_legit, label="Fraudulent", color=PALETTE["fraud"], edgecolor="white")

    # Annotate percentages
    ax.text(0, legit_txn_pct / 2, f"Legitimate\n{legit_txn_pct:.1f}%\n({total_txns - total_fraud_txns:,} txns)", 
            ha='center', va='center', color='white', fontweight='bold', fontsize=11)
    ax.text(0, legit_txn_pct + (fraud_txn_pct / 2), f"Fraud: {fraud_txn_pct:.1f}%\n({total_fraud_txns:,})", 
            ha='center', va='center', color='white', fontweight='bold', fontsize=10)

    ax.text(1, legit_dollar_pct / 2, f"Legitimate Volume\n{legit_dollar_pct:.1f}%\n(${total_dollars - fraud_dollars:,.0f})", 
            ha='center', va='center', color='white', fontweight='bold', fontsize=11)
    ax.text(1, legit_dollar_pct + (fraud_dollar_pct / 2), f"Fraud Volume\n{fraud_dollar_pct:.1f}%\n(${fraud_dollars:,.0f})", 
            ha='center', va='center', color='white', fontweight='bold', fontsize=10)

    ax.set_ylabel("Percentage of Total (%)")
    ax.set_title("Financial Risk Asymmetry: Transaction Count vs. Dollar Loss Exposure", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=12)
    ax.set_ylim(0, 108)
    ax.legend(loc="upper right", frameon=True)

    save_figure(fig, "01_dollar_asymmetry.png")
    plt.close(fig)

    # =========================================================================
    # VISUAL 2: Temporal Fraud Density Heatmap (02_temporal_fraud_heatmap.png)
    # =========================================================================
    print("[*] Generating Visual 2: Temporal Fraud Heatmap...")
    
    # Decompose seconds into hour of day (0-23) and day of week (0-6)
    df["hour"] = (df["TransactionDT"] // 3600) % 24
    df["day_of_week"] = (df["TransactionDT"] // 86400) % 7

    # Calculate fraud rate (%) per hour x day
    heatmap_data = df.groupby(["day_of_week", "hour"])["isFraud"].mean().unstack() * 100
    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    heatmap_data.index = [day_labels[i] for i in heatmap_data.index]

    fig, ax = plt.subplots(figsize=(12, 5.5))
    sns.heatmap(heatmap_data, cmap="YlOrRd", annot=False, fmt=".1f", linewidths=0.5, cbar_kws={'label': 'Empirical Fraud Rate (%)'}, ax=ax)

    ax.set_title("Temporal Fraud Density: Empirical Fraud Rate by Hour of Day & Day of Week", pad=15)
    ax.set_xlabel("Hour of Day (UTC)", fontsize=11)
    ax.set_ylabel("Day of Week", fontsize=11)

    save_figure(fig, "02_temporal_fraud_heatmap.png")
    plt.close(fig)

    print("[+] Phase 1 Visualizations successfully exported to reports/figures/!")


if __name__ == "__main__":
    generate_phase1_visualizations()