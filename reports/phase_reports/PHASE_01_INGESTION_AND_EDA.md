# RiskForge — Phase 1 Report (Q&A Format)

## Data Ingestion, Memory Optimization, Data Cleaning, Feature Engineering & Statistical EDA

---

### Question 1: What did we do in Phase 1?

**Answer:**

We transformed the raw IEEE-CIS Fraud Detection dataset into a clean, memory-efficient, analysis-ready dataset that can be used by all downstream RiskForge modules.

The major activities completed in Phase 1 were:

1. **Loaded the complete IEEE-CIS Fraud Detection dataset** containing 590,540 transaction records and 144,233 identity records.

2. **Inspected the transaction and identity datasets** to understand their schema, data types, missing-value patterns, target distribution, and relationship between transaction and identity information.

3. **Optimized memory usage through numerical downcasting**, reducing the memory footprint of the raw data substantially while preserving the required numerical information.

4. **Merged transaction and identity data** using `TransactionID` as the joining key and a left join so that every transaction remained in the final dataset.

5. **Performed missing-value analysis** and identified columns with extremely high missingness.

6. **Removed columns with more than 80% missing values** because these columns provide limited reliable information for downstream analysis.

7. **Removed duplicate transactions** using `TransactionID` to maintain one record per transaction.

8. **Created `has_identity_metadata`**, a binary missingness indicator that captures whether identity/device information is available for a transaction.

9. **Standardized operating-system information** into consistent categories such as Windows, iOS, MacOS, Android, Linux, Other, and Unknown.

10. **Standardized browser information** into consistent categories such as Chrome, Safari, Firefox, Edge, IE, Other, and Unknown.

11. **Handled remaining missing numerical values** using median imputation.

12. **Handled categorical missing values** using an appropriate unknown category while preserving pandas categorical data types.

13. **Engineered additional fraud-risk features** including:
    - `has_identity_metadata`
    - `is_high_value`
    - `amt_log`
    - `hour`
    - `email_match`

14. **Performed statistical exploratory data analysis** covering missing values, fraud class imbalance, correlations, transaction amounts, temporal behavior, categorical fraud rates, and identity presence.

15. **Generated eight professional EDA visualizations** and exported them to `reports/figures/`.

16. **Saved the cleaned dataset as Parquet**, creating a reusable data source for Phase 2 feature engineering and behavioral analysis.

---

### Question 2: Why did we do this? (Business & Engineering Rationale)

**Answer:**

* **To Build a Reliable Data Foundation:** Machine learning models are only as reliable as the data pipeline feeding them. Phase 1 converts inconsistent raw transaction and identity data into a standardized dataset that downstream systems can trust.

* **To Reduce Memory Pressure:** The IEEE-CIS dataset contains hundreds of columns and hundreds of thousands of transactions. Loading and processing the complete dataset without memory optimization can create unnecessary RAM pressure and cause notebook or application failures.

* **To Preserve Every Transaction:** We used a left join from transaction data to identity data so that the transaction table remains the authoritative base population. Missing identity information is preserved instead of silently removing transactions.

* **To Treat Missingness as Information:** In fraud detection, missing identity information may itself contain predictive information. Instead of simply treating missing values as a technical problem, we created `has_identity_metadata` to explicitly capture identity-data availability.

* **To Improve Data Consistency:** Raw browser and operating-system fields contain many variations of the same underlying value. Standardizing them into meaningful families reduces unnecessary category fragmentation.

* **To Handle Class Imbalance Correctly:** Fraud represents only a small percentage of all transactions. Therefore, raw accuracy can be misleading. Phase 1 establishes the class-imbalance understanding required for more appropriate evaluation metrics such as PR-AUC in later phases.

* **To Understand Financial Risk:** Fraud analysis should consider transaction value, not only transaction count. A small number of high-value fraudulent transactions can represent significant financial exposure.

* **To Understand Temporal Behavior:** Fraud activity may vary by hour and day. Extracting temporal patterns allows later models to identify unusual transaction timing and behavioral deviations.

* **To Create a Reusable Dataset:** Saving the cleaned data in Parquet provides a consistent input for future SQL analysis, feature engineering, machine learning, explainability, and deployment components.

---

### Question 3: What did the data inspection reveal?

**Answer:**

The initial inspection produced several important findings:

| Finding | Observation | Business / Technical Meaning |
| :--- | :--- | :--- |
| Transaction Records | 590,540 | Large enough for robust fraud modeling |
| Identity Records | 144,233 | Identity information covers only part of the transaction population |
| Fraud Rate | ~3.5% | Strong class imbalance exists |
| High-Missingness Columns | 54 columns with more than 50% missingness | Missing data is a major characteristic of the dataset |
| Identity Availability | Identity metadata is absent for roughly 65% of transactions | Missingness itself can potentially provide fraud-risk information |
| Dataset Width | Hundreds of transaction + identity columns | Memory optimization is important |
| Target Variable | `isFraud` | Binary fraud classification problem |

The most important observation was that **identity information is missing for a large portion of transactions**.

This led directly to the creation of the `has_identity_metadata` feature.

---

### Question 4: How did we optimize memory usage?

**Answer:**

The raw IEEE-CIS dataset contains many numerical columns stored using unnecessarily large data types such as `int64` and `float64`.

We implemented numerical downcasting to use smaller compatible types wherever possible.

For example:

```text
int64  → int32 / int16 / int8
float64 → float32