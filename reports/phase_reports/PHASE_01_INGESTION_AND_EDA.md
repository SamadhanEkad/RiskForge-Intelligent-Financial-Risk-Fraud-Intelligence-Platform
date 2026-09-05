RiskForge — Phase 1 Report (Q&A Format)

Data Ingestion, Memory Optimization, Cleaning, Feature Engineering & Statistical EDA

Document Metadata

Project: RiskForge — Intelligent Financial Risk & Fraud Intelligence Platform

Phase: Phase 1 — Data Ingestion, Data Inspection, Cleaning, Feature Engineering & EDA

Dataset: IEEE-CIS Fraud Detection Dataset

Transactions: 590,540

Identity Records: 144,233

Fraud Rate: ~3.5%

Status: Complete & Verified

Primary Output: data/processed/clean_transactions.parquet

Question 1: What did we do in Phase 1?

Answer: We transformed the raw IEEE-CIS Fraud Detection dataset into a reliable, memory-efficient and analysis-ready dataset for the downstream RiskForge fraud-risk pipeline.

The main activities completed were:

Loaded the complete transaction and identity datasets rather than relying only on a small sample.

Inspected the dataset structure, including columns, data types, missing values and target distribution.

Applied memory optimization and datatype downcasting to reduce unnecessary RAM usage.

Merged transaction and identity information using TransactionID.

Analyzed missingness and identified highly-missing features.

Preserved identity availability as a meaningful signal using has_identity_metadata.

Standardized operating-system and browser values into consistent categories.

Handled numerical and categorical missing values using appropriate strategies.

Created five analytical features for downstream fraud-risk analysis.

Performed statistical EDA covering class imbalance, correlations, transaction amounts, financial exposure, categories and temporal behavior.

Generated eight analytical visualizations for technical and stakeholder interpretation.

Saved the cleaned dataset in Parquet format for efficient downstream processing.

Documented the complete Phase 1 workflow in the Jupyter notebook and this report.

Question 2: Why did we do this?

Answer: Phase 1 establishes the data foundation for the entire RiskForge platform.

To make large-scale processing practical: The IEEE-CIS dataset is high-dimensional. Memory optimization reduces pressure during operations such as merging, grouping, sorting, feature generation and model preparation.

To create a trustworthy downstream dataset: All later feature engineering and modeling phases depend on consistent data types, controlled missing values and a well-defined transaction-level dataset.

To preserve fraud-relevant information: Missing identity information can itself contain useful information. Instead of simply discarding this information, RiskForge explicitly represents identity availability.

To understand fraud before modeling: EDA identifies important patterns, limitations and candidate signals before machine-learning models are trained.

Question 3: What is the Phase 1 data pipeline?

Answer: The complete workflow is:

Raw Transaction Data
        +
Raw Identity Data
        ↓
Data Inspection
        ↓
Memory Optimization
        ↓
TransactionID Left Join
        ↓
Missing-Value Analysis
        ↓
Data Cleaning
        ↓
OS / Browser Standardization
        ↓
Feature Engineering
        ↓
Statistical EDA
        ↓
Business Risk Findings
        ↓
Clean Parquet Dataset
        ↓
Phase 2

Phase 1 prepares the data and identifies useful signals. It does not train the final fraud-detection models.

Question 4: What dataset did we use?

Answer: RiskForge uses the IEEE-CIS Fraud Detection Dataset, which combines transaction-level information with additional identity and device information.

Transaction Data

The transaction table contains information such as:

TransactionID

TransactionDT

TransactionAmt

Product attributes

Card attributes

Address attributes

Email attributes

Numerous anonymized transaction features

Identity Data

The identity table contains additional contextual information such as:

Device information

Operating system

Browser

Device type

Identity/network attributes

The two sources are connected through:

TransactionID

This allows transaction records to be enriched with identity information whenever it is available.

Question 5: How much data was processed?

Answer: Phase 1 used the complete training population:

590,540 transaction records
+
144,233 identity records

Using the full dataset is important because fraud is a minority class. Working with an unnecessarily small sample can hide minority-class patterns and produce misleading conclusions.

Question 6: How did we solve the memory problem?

Answer: We implemented reusable datatype optimization through:

src/riskforge/ingestion/downcast.py

The approximate working memory footprint was:

Before optimization : ~1.85 GB
After optimization  : ~860 MB

This represents a reduction of more than 50% in the working memory footprint.

The optimizer reduces unnecessarily large numeric representations while preserving the information required for analysis.

Why memory optimization matters

590K rows
   ×
Hundreds of columns
   ↓
Large DataFrame
   ↓
High RAM usage
   ↓
Merge / GroupBy / Sorting / Feature Engineering
   ↓
Possible notebook instability

The optimized representation provides a much more practical foundation for subsequent RiskForge phases.

Question 7: What did data inspection reveal?

Answer: The initial inspection showed substantial missingness, particularly in identity-related features.

A major observation was:

54 columns had >50% missing values

Approximately:

65% of records lacked identity metadata

This is important because missing identity information should not automatically be treated as meaningless missing data.

RiskForge therefore preserves identity availability through:

has_identity_metadata

This feature indicates whether useful identity/device metadata is available for a transaction.

Question 8: How were transaction and identity data merged?

Answer: The transaction and identity datasets were combined using a left join on TransactionID.

df = df_txn.merge(
    df_id,
    on="TransactionID",
    how="left"
)

Why LEFT JOIN?

The transaction dataset represents the primary transaction population. Every transaction must remain in the final dataset, even when corresponding identity information is unavailable.

Transaction Records
        │
        │ LEFT JOIN
        ▼
Identity Information
        │
        ▼
All Transactions Preserved
+
Identity Data When Available

This is especially important because identity absence is itself retained as a potential fraud-risk signal.

Question 9: How did we handle missing values?

Answer: Missing values were handled according to the data type and business meaning.

The cleaning workflow included:

Identifying columns with excessive missingness.

Removing columns exceeding the configured high-missingness threshold.

Checking duplicate TransactionID values.

Preserving identity availability before imputation.

Standardizing OS and browser information.

Filling numerical missing values using median values.

Representing remaining categorical missing values as unknown.

The categorical handling was implemented safely for pandas categorical columns by adding the required category before filling missing values.

This prevents errors such as:

TypeError:
Cannot setitem on a Categorical with a new category

Question 10: How did we clean OS and browser information?

Answer: Raw identity fields can contain many inconsistent string representations. We standardized them into meaningful families.

Operating System

Windows
iOS
MacOS
Android
Linux
Other
Unknown

Browser

Chrome
Safari
Firefox
Edge
IE
Other
Unknown

The standardized fields are:

os_clean
browser_clean

This makes the identity information easier to analyze and use in downstream modeling.

Question 11: What features were engineered?

Answer: Five analytical features were created to capture useful fraud-risk information.

Feature

Meaning

has_identity_metadata

Indicates whether identity/device information is available

is_high_value

Identifies transactions above the selected high-value threshold

amt_log

Log-transformed transaction amount for reducing amount skew

hour

Transaction hour derived from transaction time

email_match

Email-domain consistency signal

These features are intentionally interpretable so their behavior can be investigated before advanced modeling.

Question 12: What did the target distribution show?

Answer: Fraud represents approximately:

~3.5% of transactions

This confirms a strong class imbalance.

Therefore, accuracy should not be used as the only model evaluation metric.

Later modeling phases should emphasize:

PR-AUC
Precision
Recall
F1 Score
Confusion Matrix
Financial Cost / Expected Loss

For a fraud-detection system, the cost of missed fraud and unnecessary intervention must also be considered.

Question 13: Why did we analyze financial exposure?

Answer: Fraud risk cannot be understood only by counting fraudulent transactions.

We therefore compared:

Fraud Transaction Count
        vs.
Fraud Dollar Exposure

A relatively small number of fraudulent transactions can still represent substantial financial exposure if transaction values are high.

This establishes an important RiskForge principle:

Financial risk depends on both fraud frequency and the monetary value exposed to fraud.

This principle will become increasingly important when RiskForge moves toward cost-sensitive scoring and decision thresholds.

Question 14: What did temporal analysis contribute?

Answer: Transaction time was transformed into interpretable temporal information, including:

hour
day_of_week

Fraud rates were then examined across time periods using statistical analysis and a temporal heatmap.

This provides an initial understanding of when fraudulent activity is more concentrated.

These temporal signals provide the foundation for Phase 2 features such as:

Transaction velocity
Rolling activity
Behavioral deviation
Time-based risk patterns

Question 15: What did correlation and initial signal analysis show?

Answer: Initial analysis identified:

has_identity_metadata
is_high_value

among the stronger observed signals examined during Phase 1.

The important interpretation is that identity availability and transaction-value behavior appear to contain useful information for distinguishing fraudulent and legitimate transactions.

However, these are EDA associations, not proof of causation.

The signals will be validated rigorously during later model-development phases using proper train/validation/test evaluation.

Question 16: What visualizations were created?

Answer: Phase 1 generated 8 analytical EDA figures covering the major fraud-risk dimensions.

The figures include:

Figure

Analysis

01_missing_value_audit.png

Missing-value structure

02_class_imbalance_donut.png

Fraud vs. legitimate distribution

03_correlation_heatmap.png

Initial feature relationships

04_dollar_asymmetry.png

Transaction count vs. financial exposure

05_temporal_heatmap.png

Fraud behavior across time

06_amount_distribution.png

Transaction amount behavior

07_fraud_rate_by_category.png

Category-level fraud patterns

08_identity_presence_fraud.png

Identity availability vs. fraud

All figures are stored under:

reports/figures/

Question 17: What are the key findings from Phase 1?

Answer: Phase 1 produced six major findings.

Finding 1 — Fraud is highly imbalanced

Approximately:

3.5% of transactions

are fraudulent.

Implication: Accuracy alone is not an appropriate primary metric.

Finding 2 — Identity information is frequently missing

Approximately:

65% of records

lack identity metadata.

Implication: Identity availability should be represented explicitly rather than treated only as a missing-value problem.

Finding 3 — High-missingness features require controlled handling

54 columns >50% missing

were identified during inspection.

Implication: Feature availability and missingness must be considered before model development.

Finding 4 — Financial exposure matters

Fraud must be examined using both:

Number of fraudulent transactions

and:

Financial amount associated with fraud

Implication: Future RiskForge decisions should consider financial cost rather than classification performance alone.

Finding 5 — Time contains behavioral information

Fraud activity varies across time.

Implication: Temporal features can support behavioral baselines and velocity detection in Phase 2.

Finding 6 — Engineered features provide interpretable initial signals

Features such as:

has_identity_metadata
is_high_value
amt_log
hour
email_match

provide useful, interpretable inputs for later modeling.

Question 18: What are the main Phase 1 project artifacts?

Answer: Phase 1 produced the following reusable project components.

File / Directory

Purpose

src/riskforge/ingestion/schema.py

Defines important dataset column groups and schema structure

src/riskforge/ingestion/downcast.py

Performs memory-efficient datatype optimization

src/riskforge/ingestion/cleaner.py

Handles merging, cleaning and missing-value processing

src/riskforge/utils/plotting.py

Provides reusable plotting and figure-export utilities

scripts/download_data.py

Supports dataset acquisition

scripts/generate_sample_data.py

Generates deterministic sample data for lightweight testing

scripts/run_phase1_eda.py

Automates Phase 1 visual EDA generation

notebooks/01_data_ingestion_and_eda.ipynb

Interactive Phase 1 analysis and walkthrough

data/processed/clean_transactions.parquet

Clean downstream-ready dataset

reports/figures/

Phase 1 analytical visualizations

reports/phase_reports/

Phase documentation

Question 19: Why did we save the cleaned dataset as Parquet?

Answer: The cleaned dataset is stored as:

data/processed/clean_transactions.parquet

Parquet is a good format for downstream analytical workloads because it is:

Columnar

Compressed

Type-aware

Efficient for selective column reads

Well suited to repeated analytical processing

This avoids repeatedly rebuilding the cleaned dataset from the original CSV files.

Question 20: What quality checks were completed?

Answer: Phase 1 was considered complete only after validating the main data-processing steps.

The workflow verified:

Transaction and identity datasets loaded successfully.

Transaction and identity records were merged using TransactionID.

Duplicate transaction IDs were checked.

High-missingness columns were controlled.

Identity availability was captured before imputation.

Numerical missing values were handled.

Categorical missing values were handled safely.

OS and browser values were standardized.

Engineered features were generated.

EDA visualizations were exported.

The cleaned dataset was written to Parquet.

The Phase 1 notebook completed successfully.

The final Phase 1 state is therefore:

Complete & Verified

Question 21: What is the Phase 1 architecture?

Answer: The Phase 1 architecture is:

IEEE-CIS Raw Data
        │
        ├────────────────┐
        ▼                ▼
 Transactions        Identity
        │                │
        └───────┬────────┘
                ▼
              Merge
                │
                ▼
        Data Inspection
                │
                ▼
       Memory Optimization
                │
                ▼
         Data Cleaning
                │
        ┌───────┼────────┐
        ▼       ▼        ▼
    Missing    OS      Browser
    Values   Cleaning  Cleaning
        │       │        │
        └───────┼────────┘
                ▼
       Feature Engineering
                │
                ▼
          Statistical EDA
                │
        ┌───────┼───────────────┐
        ▼       ▼               ▼
    Imbalance Financial       Temporal
              Exposure         Patterns
        │       │               │
        └───────┼───────────────┘
                ▼
      Clean Parquet Dataset
                │
                ▼
            Phase 2

Question 22: What is the final output of Phase 1?

Answer: Phase 1 produced a complete data foundation for RiskForge.

The primary downstream dataset is:

data/processed/clean_transactions.parquet

The supporting outputs include:

notebooks/01_data_ingestion_and_eda.ipynb

reports/figures/
    ├── 01_missing_value_audit.png
    ├── 02_class_imbalance_donut.png
    ├── 03_correlation_heatmap.png
    ├── 04_dollar_asymmetry.png
    ├── 05_temporal_heatmap.png
    ├── 06_amount_distribution.png
    ├── 07_fraud_rate_by_category.png
    └── 08_identity_presence_fraud.png

reports/phase_reports/
    └── PHASE_01_INGESTION_AND_EDA.md

Question 23: What is the handoff from Phase 1 to Phase 2?

Answer: Phase 1 provides the clean and structured transaction-level foundation required for behavioral feature engineering.

Phase 2 will build on this foundation by introducing:

SQL / DuckDB Feature Engineering
        ↓
1-Hour Transaction Velocity
        ↓
24-Hour Rolling Spend
        ↓
Customer Behavioral Baselines
        ↓
Amount Z-Scores
        ↓
Historical Deviation Features

The objective is to move from describing individual transactions toward understanding transaction behavior over time.

Final Phase 1 Outcome

Phase 1 is COMPLETE & VERIFIED.

RiskForge now has:

590,540 transaction records processed.

144,233 identity records integrated where available.

50%+ memory reduction through datatype optimization.

A controlled missing-value strategy.

Standardized OS and browser information.

5 interpretable analytical features.

Statistical and visual fraud EDA.

8 Phase 1 analytical figures.

A reusable clean Parquet dataset.

A documented and reproducible Phase 1 pipeline.

Phase 2 → Behavioral Feature Engineering

The next stage of RiskForge will move from data preparation and statistical understanding to behavioral fraud intelligence.

Phase 1
Data Foundation
      ↓
Phase 2
Behavioral & Velocity Features
      ↓
Phase 3
Graph Fraud Intelligence
      ↓
Phase 4
Modeling & Anomaly Detection
      ↓
Phase 5+
Explainability, NLP, Decisioning,
Deployment & MLOps

RiskForge Phase 1 — COMPLETE ✓