"""
RiskForge - High-Fidelity IEEE-CIS Sample Data Generator
Generates a realistic 15,000-row dataset replicating the IEEE-CIS Fraud Detection schema.
Embeds realistic fraud typologies:
  1. Card-testing velocity bursts
  2. Device-sharing fraud syndicates (for NetworkX graph mining)
  3. High-amount behavioral deviation outliers
"""

import numpy as np
import pandas as pd
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
SAMPLE_DATA_DIR = PROJECT_ROOT / "data" / "sample"


def generate_ieee_cis_sample(n_rows: int = 15000, seed: int = 42):
    """Generates authentic train_transaction.csv and train_identity.csv."""
    np.random.seed(seed)
    print(f"[*] Generating {n_rows:,} transactions matching IEEE-CIS schema...")

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Base Transaction Identifiers & Chronological Time
    transaction_ids = np.arange(3000000, 3000000 + n_rows)
    
    # Chronological timestamps (TransactionDT in seconds over a 30-day period)
    time_deltas = np.sort(np.random.exponential(scale=170, size=n_rows))
    transaction_dt = np.cumsum(time_deltas).astype(int) + 86400

    # 2. Card & Identity Attributes
    card1_pool = np.random.randint(1000, 18000, size=1200) # 1200 distinct cards
    card1 = np.random.choice(card1_pool, size=n_rows)
    card2 = np.random.choice([111.0, 174.0, 264.0, 321.0, 399.0, 490.0, 555.0, np.nan], size=n_rows)
    card3 = np.random.choice([150.0, 185.0, np.nan], p=[0.92, 0.05, 0.03], size=n_rows)
    card4 = np.random.choice(['visa', 'mastercard', 'discover', 'american express'], p=[0.65, 0.28, 0.05, 0.02], size=n_rows)
    card5 = np.random.choice([102.0, 117.0, 137.0, 166.0, 226.0, np.nan], size=n_rows)
    card6 = np.random.choice(['debit', 'credit'], p=[0.74, 0.26], size=n_rows)

    addr1 = np.random.choice([126.0, 204.0, 299.0, 315.0, 325.0, 441.0, np.nan], size=n_rows)
    addr2 = np.random.choice([87.0, 96.0, np.nan], p=[0.95, 0.02, 0.03], size=n_rows)
    dist1 = np.random.choice([np.nan, 0.0, 2.0, 5.0, 12.0, 25.0, 150.0], p=[0.60, 0.10, 0.10, 0.08, 0.06, 0.04, 0.02], size=n_rows)

    p_email_pool = ['gmail.com', 'yahoo.com', 'hotmail.com', 'anonymous.com', 'aol.com', 'comcast.net', np.nan]
    p_emaildomain = np.random.choice(p_email_pool, p=[0.42, 0.22, 0.15, 0.08, 0.05, 0.03, 0.05], size=n_rows)
    r_emaildomain = np.random.choice(p_email_pool, p=[0.30, 0.15, 0.10, 0.05, 0.03, 0.02, 0.35], size=n_rows)

    product_cd = np.random.choice(['W', 'C', 'R', 'H', 'S'], p=[0.74, 0.12, 0.06, 0.05, 0.03], size=n_rows)

    # 3. Transaction Amounts (log-normal distribution)
    base_amounts = np.random.lognormal(mean=4.2, sigma=1.1, size=n_rows)
    transaction_amt = np.round(base_amounts, 2)

    # 4. Synthesize Target: isFraud (base ~3.5% rate)
    is_fraud = np.zeros(n_rows, dtype=int)
    base_fraud_indices = np.random.choice(n_rows, size=int(n_rows * 0.025), replace=False)
    is_fraud[base_fraud_indices] = 1

    # 5. Embed Specific Fraud Typologies for our Downstream Modules:
    print("[*] Embedding fraud typologies (Card-testing bursts, Syndicate rings, High-value anomalies)...")
    
    # A. Fraud Syndicate (Device-Sharing Ring)
    # A single device and IP linked to 15 different cards committing fraud
    syndicate_card_ids = np.random.choice(card1_pool, size=15, replace=False)
    syndicate_indices = np.random.choice(n_rows, size=120, replace=False)
    for idx in syndicate_indices:
        card1[idx] = np.random.choice(syndicate_card_ids)
        is_fraud[idx] = 1
        p_emaildomain[idx] = 'anonymous.com'
        product_cd[idx] = 'C'

    # B. High-Amount Outliers
    large_fraud_indices = np.random.choice(np.where(is_fraud == 1)[0], size=40, replace=False)
    transaction_amt[large_fraud_indices] = np.random.uniform(900.0, 3200.0, size=40).round(2)

    # C. Card-testing bursts (Rapid rapid velocity on same card)
    burst_card = card1_pool[0]
    burst_indices = np.sort(np.random.choice(n_rows, size=12, replace=False))
    burst_time = transaction_dt[burst_indices[0]]
    for step, idx in enumerate(burst_indices):
        card1[idx] = burst_card
        transaction_dt[idx] = burst_time + (step * 90) # 90 seconds apart
        transaction_amt[idx] = 1.00 if step < 8 else 750.00 # micro-auth then drain
        is_fraud[idx] = 1

    # Re-sort chronologically after injecting bursts
    sort_order = np.argsort(transaction_dt)
    transaction_ids = transaction_ids[sort_order]
    transaction_dt = transaction_dt[sort_order]
    transaction_amt = transaction_amt[sort_order]
    is_fraud = is_fraud[sort_order]
    card1 = card1[sort_order]
    card2 = card2[sort_order]
    card3 = card3[sort_order]
    card4 = card4[sort_order]
    card5 = card5[sort_order]
    card6 = card6[sort_order]
    addr1 = addr1[sort_order]
    addr2 = addr2[sort_order]
    dist1 = dist1[sort_order]
    product_cd = product_cd[sort_order]
    p_emaildomain = p_emaildomain[sort_order]
    r_emaildomain = r_emaildomain[sort_order]

    # Vesta engineered features subset (V1 - V30)
    v_cols = {}
    for i in range(1, 31):
        v_cols[f"V{i}"] = np.random.choice([0.0, 1.0, 2.0, np.nan], size=n_rows)

    # C features (counts)
    c_cols = {}
    for i in range(1, 15):
        c_cols[f"C{i}"] = np.random.poisson(lam=1.5, size=n_rows)

    # D features (timedeltas)
    d_cols = {}
    for i in range(1, 16):
        d_cols[f"D{i}"] = np.random.choice([0.0, 14.0, 30.0, 120.0, np.nan], size=n_rows)

    # Build Transaction DataFrame
    txn_data = {
        "TransactionID": transaction_ids,
        "isFraud": is_fraud,
        "TransactionDT": transaction_dt,
        "TransactionAmt": transaction_amt,
        "ProductCD": product_cd,
        "card1": card1,
        "card2": card2,
        "card3": card3,
        "card4": card4,
        "card5": card5,
        "card6": card6,
        "addr1": addr1,
        "addr2": addr2,
        "dist1": dist1,
        "P_emaildomain": p_emaildomain,
        "R_emaildomain": r_emaildomain,
        **c_cols,
        **d_cols,
        **v_cols
    }
    df_transaction = pd.DataFrame(txn_data)

    # 6. Generate Identity DataFrame (~35% of transactions have identity metadata)
    identity_indices = np.random.choice(n_rows, size=int(n_rows * 0.35), replace=False)
    # Ensure all syndicate transactions have identity so graph can connect them
    identity_indices = np.unique(np.concatenate([identity_indices, syndicate_indices]))
    
    id_txn_ids = transaction_ids[identity_indices]
    n_id = len(id_txn_ids)

    devices = ['Windows', 'iOS Device', 'MacOS', 'SM-G950F', 'SM-G960N', 'Trident/7.0', 'rv:57.0', np.nan]
    device_info = np.random.choice(devices, size=n_id)
    
    # Assign the syndicate ring to SM-G950F
    syndicate_txn_mask = np.isin(id_txn_ids, transaction_ids[syndicate_indices])
    device_info[syndicate_txn_mask] = 'SM-G950F'

    os_list = ['Windows 10', 'iOS 12.1.0', 'Android 9', 'MacOS 10.14', 'Windows 7', np.nan]
    browsers = ['chrome 70.0', 'safari 12.0', 'firefox 63.0', 'edge 17.0', 'mobile safari 12.0', np.nan]
    
    df_identity = pd.DataFrame({
        "TransactionID": id_txn_ids,
        "id_01": np.random.uniform(-100, 0, size=n_id).round(1),
        "id_02": np.random.randint(10000, 500000, size=n_id),
        "id_12": np.random.choice(['NotFound', 'Found', np.nan], size=n_id),
        "id_15": np.random.choice(['New', 'Found', 'Unknown', np.nan], size=n_id),
        "id_16": np.random.choice(['Found', 'NotFound', np.nan], size=n_id),
        "id_30": np.random.choice(os_list, size=n_id),
        "id_31": np.random.choice(browsers, size=n_id),
        "DeviceType": np.random.choice(['desktop', 'mobile', np.nan], size=n_id),
        "DeviceInfo": device_info
    })

    # Save CSVs to data/raw
    txn_path = RAW_DATA_DIR / "train_transaction.csv"
    id_path = RAW_DATA_DIR / "train_identity.csv"
    df_transaction.to_csv(txn_path, index=False)
    df_identity.to_csv(id_path, index=False)

    # Save Parquet to data/sample for fast local reads
    df_transaction.to_parquet(SAMPLE_DATA_DIR / "train_transaction.parquet", index=False)
    df_identity.to_parquet(SAMPLE_DATA_DIR / "train_identity.parquet", index=False)

    fraud_rate = df_transaction['isFraud'].mean() * 100
    print(f"[+] Successfully generated:")
    print(f"    - Transactions: {len(df_transaction):,} rows -> {txn_path}")
    print(f"    - Identities:   {len(df_identity):,} rows -> {id_path}")
    print(f"    - Fraud Rate:   {fraud_rate:.2f}% (Industry-standard imbalanced baseline)\n")


if __name__ == "__main__":
    generate_ieee_cis_sample()
