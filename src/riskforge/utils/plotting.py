"""
RiskForge - Corporate Visual Styling & Plotting Utilities
Provides publication-grade plotting themes and figure export helpers.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

from riskforge.utils.config import get_project_root


# Enterprise Risk Palette: Legitimate = Slate Blue, Fraud = Crimson Red
PALETTE = {
    "legit": "#1E3A8A",    # Dark Slate Navy
    "fraud": "#DC2626",    # Vivid Crimson Red
    "accent": "#F59E0B",   # Warning Amber
    "neutral": "#64748B",  # Slate Gray
}


def set_corporate_style():
    """Applies a clean, modern corporate aesthetic to all plots."""
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.size"] = 11
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["axes.labelweight"] = "semibold"
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["figure.titlesize"] = 16
    plt.rcParams["figure.titleweight"] = "bold"
    plt.rcParams["figure.autolayout"] = True


def save_figure(fig, filename: str, dpi: int = 300):
    """Saves a figure to reports/figures/ at publication resolution."""
    root = get_project_root()
    figures_dir = root / "reports" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    out_path = figures_dir / filename
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    print(f"[+] Saved high-impact visual: {out_path}")