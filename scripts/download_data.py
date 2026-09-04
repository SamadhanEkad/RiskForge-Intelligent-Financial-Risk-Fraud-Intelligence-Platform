"""
RiskForge - Kaggle Data Downloader
Downloads the full IEEE-CIS Fraud Detection dataset from Kaggle.
Requires: pip install kaggle and ~/.kaggle/kaggle.json
"""

import os
import sys
import zipfile
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def download_ieee_cis_dataset():
    """Downloads and extracts the IEEE-CIS Fraud Detection dataset."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"[*] Target directory: {RAW_DATA_DIR}")
    
    # Check for kaggle.json credentials
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if not kaggle_json.exists():
        print("\n[!] WARNING: Kaggle API token not found at ~/.kaggle/kaggle.json")
        print("    To download the full 1.5GB dataset automatically:")
        print("    1. Go to https://www.kaggle.com/settings -> Create New Token")
        print(f"    2. Place kaggle.json into {Path.home() / '.kaggle'}")
        print("    Alternatively, generate the realistic sample data using:")
        print("    python scripts/generate_sample_data.py\n")
        return False

    try:
        import kaggle
        print("[*] Kaggle credentials detected. Downloading ieee-fraud-detection...")
        kaggle.api.competition_download_files('ieee-fraud-detection', path=RAW_DATA_DIR)
        
        # Extract any downloaded zip files
        for zip_file in RAW_DATA_DIR.glob("*.zip"):
            print(f"[*] Extracting {zip_file.name}...")
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(RAW_DATA_DIR)
            zip_file.unlink() # remove zip after extraction
            
        print("[+] Download and extraction complete!")
        return True
    except Exception as e:
        print(f"[!] Error during download: {e}")
        return False


if __name__ == "__main__":
    download_ieee_cis_dataset()
