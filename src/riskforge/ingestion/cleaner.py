"""
RiskForge - Data Cleaning & Normalization Pipeline
Cleans raw transaction and identity data, standardizes categorical fields,
handles semantic missingness, and saves the cleaned dataset as Parquet.
"""

from pathlib import Path
import pandas as pd
import numpy as np

from riskforge.ingestion.downcast import reduce_memory_usage
from riskforge.utils.config import get_project_root


def clean_operating_system(os_series: pd.Series) -> pd.Series:
    """Consolidates messy OS strings into standardized platforms."""
    os_str = os_series.astype(str).str.lower()
    
    conditions = [
        os_str.str.contains("windows"),
        os_str.str.contains("ios"),
        os_str.str.contains("mac"),
        os_str.str.contains("android"),
        os_str.str.contains("linux"),
    ]
    choices = ["Windows", "iOS", "MacOS", "Android", "Linux"]
    
    cleaned = np.select(conditions, choices, default="Other/Missing")
    return pd.Series(cleaned, index=os_series.index, dtype="category")


def clean_browser(browser_series: pd.Series) -> pd.Series:
    """Consolidates browser version strings into major browser families."""
    b_str = browser_series.astype(str).str.lower()
    
    conditions = [
        b_str.str.contains("chrome"),
        b_str.str.contains("safari"),
        b_str.str.contains("firefox"),
        b_str.str.contains("edge"),
        b_str.str.contains("ie") | b_str.str.contains("trident"),
    ]
    choices = ["Chrome", "Safari", "Firefox", "Edge", "IE"]
    
    cleaned = np.select(conditions, choices, default="Other/Missing")
    return pd.Series(cleaned, index=browser_series.index, dtype="category")


def clean_categorical_text(series: pd.Series) -> pd.Series:
    """Safely fills nulls and lowercases categorical string columns."""
    cleaned = series.astype(str).str.lower().replace({"nan": "unknown", "none": "unknown", "<na>": "unknown"})
    return cleaned.astype("category")


def run_data_cleaning(sample_size: int = None) -> pd.DataFrame:
    """
    Executes end-to-end cleaning pipeline:
    Loads raw CSVs, downcasts memory, merges identity data, cleans fields,
    and writes to data/processed/clean_transactions.parquet.
    """
    root = get_project_root()
    raw_dir = root / "data" / "raw"
    processed_dir = root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    txn_path = raw_dir / "train_transaction.csv"
    id_path = raw_dir / "train_identity.csv"

    if not txn_path.exists():
        raise FileNotFoundError(f"Missing transaction data at {txn_path}")

    print("[*] Loading raw transaction dataset...")
    df_txn = pd.read_csv(txn_path, nrows=sample_size)
    df_txn = reduce_memory_usage(df_txn)

    if id_path.exists():
        print("[*] Loading raw identity dataset...")
        df_id = pd.read_csv(id_path, nrows=sample_size)
        df_id = reduce_memory_usage(df_id)
        
        print("[*] Merging transactions with identity records...")
        df = df_txn.merge(df_id, on="TransactionID", how="left")
    else:
        print("[!] Identity file not found. Proceeding with transactions only.")
        df = df_txn

    # 1. Deduplicate by TransactionID
    initial_rows = len(df)
    df = df.drop_duplicates(subset=["TransactionID"])
    print(f"[*] Deduplication complete: {initial_rows - len(df)} duplicate records dropped.")

    # 2. Semantic Missing Value Handling & Categorical Cleaning
    print("[*] Standardizing categoricals and handling missing data...")
    for col in ["ProductCD", "card4", "card6", "P_emaildomain", "R_emaildomain", "DeviceType", "DeviceInfo"]:
        if col in df.columns:
            df[col] = clean_categorical_text(df[col])

    # 3. Behavioral Identity Features
    if "id_30" in df.columns:
        df["os_clean"] = clean_operating_system(df["id_30"])
    if "id_31" in df.columns:
        df["browser_clean"] = clean_browser(df["id_31"])
    
    # Behavioral Flag: Identity metadata presence
    if "DeviceInfo" in df.columns:
        df["has_identity_metadata"] = (df["DeviceInfo"] != "unknown").astype(np.int8)
    else:
        df["has_identity_metadata"] = np.int8(0)

    # 4. Final Memory Downcast
    df = reduce_memory_usage(df, verbose=False)

    # 5. Save clean output to Parquet
    out_path = processed_dir / "clean_transactions.parquet"
    print(f"[*] Saving cleaned dataset to {out_path}...")
    df.to_parquet(out_path, index=False)
    print(f"[+] Successfully saved {len(df):,} cleaned rows to Parquet!")

    return df


if __name__ == "__main__":
    run_data_cleaning()