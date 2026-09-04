"""
RiskForge - Data Schema & Validation Definitions
Defines column groups, expected data types, and data contracts
for the IEEE-CIS Fraud Detection dataset.
"""

from typing import List, Dict

# Core Identifiers and Target
ID_COLUMN: str = "TransactionID"
TARGET_COLUMN: str = "isFraud"
TIME_COLUMN: str = "TransactionDT"
AMOUNT_COLUMN: str = "TransactionAmt"

# Primary Categorical Columns
CATEGORICAL_COLUMNS: List[str] = [
    "ProductCD",
    "card4",
    "card6",
    "P_emaildomain",
    "R_emaildomain",
    "DeviceType",
    "DeviceInfo",
]

# Card Metadata Columns (BIN, bank, country, network, type)
CARD_COLUMNS: List[str] = [
    "card1",
    "card2",
    "card3",
    "card4",
    "card5",
    "card6",
]

# Address & Location Columns
ADDRESS_COLUMNS: List[str] = [
    "addr1",
    "addr2",
    "dist1",
]

# Identity Metadata Columns
IDENTITY_COLUMNS: List[str] = [
    "id_01", "id_02", "id_12", "id_15", "id_16",
    "id_30", "id_31", "id_33", "DeviceType", "DeviceInfo"
]

def get_expected_columns() -> Dict[str, List[str]]:
    """Returns the dictionary of expected column groupings."""
    return {
        "id": [ID_COLUMN],
        "target": [TARGET_COLUMN],
        "time": [TIME_COLUMN],
        "amount": [AMOUNT_COLUMN],
        "card": CARD_COLUMNS,
        "address": ADDRESS_COLUMNS,
        "categorical": CATEGORICAL_COLUMNS,
        "identity": IDENTITY_COLUMNS,
    }