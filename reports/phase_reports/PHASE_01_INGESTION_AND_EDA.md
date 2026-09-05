RiskForge — Phase 1 Report

Data Ingestion, Memory Optimization, Cleaning, Feature Engineering & Statistical EDA

1. Phase Overview

Project: RiskForge — Intelligent Financial Risk & Fraud Intelligence Platform
Phase: Phase 1 — Data Ingestion, Data Inspection, Cleaning, Feature Engineering & EDA
Dataset: IEEE-CIS Fraud Detection Dataset
Records: 590,540 transactions + 144,233 identity records
Status: Complete & Verified

Phase Objective

The objective of Phase 1 was to transform the raw IEEE-CIS fraud dataset into a reliable, memory-efficient and analysis-ready dataset that can be used by all downstream RiskForge modules.

The phase establishes the foundation for the complete fraud-risk platform:

Raw Transaction + Identity Data
              ↓
       Data Inspection
              ↓
      Memory Optimization
              ↓
        Data Merging
              ↓
      Missing-Value Analysis
              ↓
       Data Cleaning
              ↓
      Feature Engineering
              ↓
       Statistical EDA
              ↓
     Business Risk Findings
              ↓
 Clean Parquet Dataset + EDA Assets

Phase 1 does not train the final fraud models. It prepares trustworthy data and identifies the signals that will guide Phase 2 and the later modeling stages.

2. Dataset Understanding

The IEEE-CIS dataset contains two complementary sources:

Transaction data

The transaction table contains payment and transaction-level attributes such as:

Transaction ID

Transaction timestamp

Transaction amount

Product information

Card information

Address information

Email information

Numerous anonymized transaction features

Identity data

The identity table contains additional device and identity-related information such as:

Device information

Operating system

Browser

Device type

Identity/network attributes

The two datasets are connected through:

TransactionID

This relationship allows RiskForge to enrich each transaction with available identity context.

3. Data Ingestion

Phase 1 loads the complete training transaction and identity datasets rather than working with a small demonstration subset.

Input

data/raw/
├── train_transaction.csv
├── train_identity.csv
├── test_transaction.csv
├── test_identity.csv
└── sample_submission.csv

The training data contains:

590,540 transactions
144,233 identity records

The raw dataset is high-dimensional and memory-intensive, so memory optimization is performed before expensive downstream processing.

4. Memory Optimization

A major engineering challenge is the size of the IEEE-CIS dataset.

The initial in-memory representation was approximately:

~1.85 GB

After datatype optimization/downcasting, the working memory footprint was reduced to approximately:

~860 MB

This represents a reduction of roughly:

50%+

Why this matters

Without memory optimization:

Large CSV files
      ↓
590K rows × hundreds of columns
      ↓
Large DataFrame
      ↓
High RAM usage
      ↓
Possible notebook instability / crashes

RiskForge therefore implements reusable memory optimization logic in:

src/riskforge/ingestion/downcast.py

The downcaster reduces unnecessarily large numeric representations and uses more efficient categorical representations where appropriate.

Engineering principle

The goal is not simply to make the dataset smaller. The goal is to reduce memory usage while preserving the information required for downstream analytics and modeling.

5. Data Inspection

Before cleaning, missingness and data quality were inspected.

A key finding was:

54 columns had more than 50% missing values

Identity information was also highly incomplete:

~65% of records lacked identity metadata

This is important in fraud detection because missing identity information may itself carry predictive information.

Therefore, missing identity information is not treated only as a nuisance to be filled.

RiskForge explicitly creates:

has_identity_metadata

as a binary feature.

6. Transaction + Identity Merge

The transaction and identity datasets are merged using:

df_txn.merge(
    df_id,
    on="TransactionID",
    how="left"
)

Why LEFT JOIN?

The transaction dataset is the primary analytical population.

A left join ensures that transactions remain in the dataset even when corresponding identity information is unavailable.

Conceptually:

Transaction
    │
    ├── Identity available
    │        ↓
    │   Add identity data
    │
    └── Identity unavailable
             ↓
        Keep transaction

This is especially important because identity absence is itself a potentially useful fraud signal.

7. Missing-Value Strategy

Phase 1 uses a structured missing-value strategy.

Step 1 — High-missing columns

Columns with more than 80% missing values are removed when they are not required for important engineered features.

Step 2 — Numeric variables

Remaining numerical missing values are filled using the median.

Step 3 — Categorical variables

Categorical missing values are represented using an explicit:

unknown

category.

Step 4 — Identity absence

Identity availability is separately represented using:

has_identity_metadata

This preserves information about missingness rather than hiding it through imputation.

Important modeling note: Phase 1 uses dataset-level cleaning for EDA. In the future modeling pipeline, imputation statistics must be fitted on the training split only to prevent data leakage.

8. Data Cleaning

The cleaning pipeline standardizes inconsistent categorical information.

Operating System

Raw identity values are consolidated into meaningful families:

Windows
iOS
MacOS
Android
Linux
Other
Unknown

Browser

Browser strings are standardized into broader families such as:

Chrome
Safari
Firefox
Edge
IE
Other
Unknown

This reduces unnecessary cardinality and makes the variables easier to analyze and model.

9. Feature Engineering

Phase 1 adds five meaningful analytical features.

Feature

Purpose

has_identity_metadata

Indicates whether identity/device metadata is available

is_high_value

Identifies unusually high-value transactions for risk analysis

amt_log

Log-transformed transaction amount for reducing right-skew

hour

Extracts hour-of-day behavior from TransactionDT

email_match

Captures consistency between relevant email-domain information

These features provide a first layer of domain-aware signals before the advanced behavioral and graph features are introduced in Phase 2 and Phase 3.

10. Why Feature Engineering Was Necessary

Raw variables do not always represent the business concept directly.

For example:

TransactionDT

is a relative time representation.

RiskForge transforms it into:

hour

so that temporal fraud patterns can be studied.

Similarly:

TransactionAmt

is useful numerically, but its distribution is highly skewed. Therefore:

amt_log

provides a more stable representation for analysis.

The identity flag converts missingness into an explicit behavioral/data-availability signal.

11. Target Distribution

The target variable is:

isFraud

with:

0 = Legitimate
1 = Fraudulent

The observed fraud rate is approximately:

3.5%

This means the dataset is strongly imbalanced.

A naive classifier that predicts every transaction as legitimate can achieve high accuracy while detecting no fraud.

Therefore:

Accuracy

is not sufficient as the primary evaluation metric.

RiskForge will emphasize metrics such as:

Precision
Recall
PR-AUC
F1
Confusion Matrix
Financial Cost / Expected Loss

in later modeling phases.

12. Financial Risk Asymmetry

One of the most important Phase 1 findings is that fraud should not be evaluated only by transaction count.

The EDA compares:

Fraud transaction percentage
        vs.
Fraud dollar-volume percentage

This answers two different questions:

Question 1

How many transactions are fraudulent?

Question 2

How much financial exposure is associated with those fraudulent transactions?

The second question is particularly important for RiskForge because the platform is designed around financial risk, not merely classification accuracy.

This finding motivates the later:

Cost Matrix
      ↓
Risk Score
      ↓
Decision Threshold
      ↓
Approve / Step-up / Review / Decline

13. Temporal Fraud Analysis

TransactionDT is transformed into temporal variables including:

hour
day_of_week

RiskForge then examines empirical fraud rates across:

Hour of Day × Day of Week

The resulting heatmap helps identify temporal concentration and behavioral patterns in fraudulent activity.

This is useful because fraud risk may vary according to transaction timing.

The temporal analysis becomes the foundation for later behavioral features such as:

transaction velocity
rolling activity
historical behavioral deviation
time-based risk patterns

14. Correlation & Signal Analysis

The Phase 1 analysis found that:

has_identity_metadata
is_high_value

were among the strongest observed signals examined during the initial analysis.

The important interpretation is:

Identity availability and transaction-value behavior appear to contain useful information for distinguishing fraudulent and legitimate transactions.

The result is an association, not proof of causation.

These signals will therefore be carried forward and tested properly in later modeling phases using train/validation/test evaluation.

15. EDA Visualizations

Phase 1 produced 8 EDA figures covering important fraud-risk dimensions.

The visual analysis focuses on:

Financial exposure

Transaction amount behavior

Temporal patterns

Fraud distribution

Category behavior

Identity availability

Behavioral differences between legitimate and fraudulent transactions

The figures are stored under:

reports/figures/

These visuals are designed to support both technical analysis and stakeholder interpretation.

16. Key Phase 1 Findings

Finding 1 — Fraud is highly imbalanced

Approximately:

3.5% of transactions

are fraudulent.

Implication: Accuracy alone is misleading.

Finding 2 — Identity information is frequently missing

Approximately:

65% of records

lack identity metadata.

Implication: Missingness should be treated as information and represented explicitly.

Finding 3 — High-missing features require controlled handling

54 columns >50% missing

were identified during inspection.

Implication: Feature availability and missingness must be considered before modeling.

Finding 4 — Financial exposure matters

Fraud must be examined in terms of both:

number of fraudulent transactions

and:

financial amount associated with fraud

Implication: Later RiskForge decisions should be cost-sensitive rather than based only on classification metrics.

Finding 5 — Time contains behavioral information

Fraud rates vary across time periods.

Implication: Temporal features can support behavioral baselines and velocity detection in Phase 2.

Finding 6 — Engineered features reveal useful initial signals

Features such as:

has_identity_metadata
is_high_value
amt_log
hour
email_match

provide interpretable domain-oriented signals for later modeling.

17. Phase 1 Architecture

IEEE-CIS Raw Data
       │
       ├───────────────┐
       ▼               ▼
Transactions        Identity
       │               │
       └───────┬───────┘
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
   Missing   OS/      Browser
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
   Imbalance  Financial      Temporal
              Exposure        Patterns
       │       │               │
       └───────┼───────────────┘
               ▼
       Clean Parquet Dataset
               │
               ▼
        Phase 2 Input

18. Phase 1 Project Artifacts

File / Directory

Purpose

src/riskforge/ingestion/schema.py

Defines important dataset column groups and schema-related structure

src/riskforge/ingestion/downcast.py

Performs memory-efficient datatype optimization

src/riskforge/ingestion/cleaner.py

Handles merge, cleaning, missing values and feature preparation

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

Exported Phase 1 analytical visualizations

reports/phase_reports/

Phase documentation

19. Why Parquet?

The cleaned dataset is stored as:

data/processed/clean_transactions.parquet

Parquet is preferred for downstream analytical workloads because it is:

Columnar

Compressed

Type-aware

Efficient for selective column reads

Better suited to repeated analytical processing than raw CSV

The Parquet file becomes the single processed-data handoff between Phase 1 and the later RiskForge modules.

20. Quality & Validation Checks

Phase 1 validates important properties of the processed dataset:

✓ Transaction population preserved
✓ TransactionID uniqueness checked
✓ Transaction + identity merge completed
✓ High-missing columns handled
✓ Numeric missing values handled
✓ Categorical missing values handled
✓ Identity availability feature created
✓ OS standardized
✓ Browser standardized
✓ Temporal features created
✓ Fraud distribution inspected
✓ Financial exposure analyzed
✓ EDA figures generated
✓ Clean Parquet artifact created

21. Technical Design Decisions

Decision 1 — Use a modular ingestion package

Instead of placing all logic in one notebook:

src/riskforge/ingestion/

contains reusable ingestion components.

This allows the same logic to be reused by scripts, notebooks, tests and future production pipelines.

Decision 2 — Preserve missingness information

Instead of treating all missing values as meaningless:

missing identity
       ↓
has_identity_metadata

is explicitly represented.

Decision 3 — Separate EDA from future model preprocessing

Phase 1 prepares the analytical dataset.

Later model pipelines will perform train-only fitting of preprocessing components to avoid leakage.

Decision 4 — Think in terms of financial risk

The project measures both:

fraud frequency

and:

financial exposure

This aligns the technical system with the business objective.

22. Limitations of Phase 1

Phase 1 intentionally does not solve the complete fraud-detection problem.

The following are deferred to later phases:

Behavioral velocity features
Graph intelligence
Supervised ML
Anomaly detection
Sequence/deep learning
Probability calibration
Risk scoring
SHAP explainability
Policy engine
NLP investigation
What-if simulation
FastAPI
Streamlit dashboard
Docker deployment
MLflow
Drift monitoring
CI/CD

Phase 1 therefore provides the data foundation, not the final fraud decision engine.

23. Phase 1 Final Outcome

At the end of Phase 1, RiskForge has transformed the raw IEEE-CIS data into a structured analytical foundation.

Final Phase 1 deliverables

590,540 transactions
        +
144,233 identity records
        ↓
Memory-optimized processing
        ↓
Merged and cleaned dataset
        ↓
5 engineered analytical features
        ↓
Statistical + business EDA
        ↓
8 exported EDA figures
        ↓
Clean Parquet dataset
        ↓
Phase 2 ready

Final conclusion

Phase 1 establishes a reliable data foundation for RiskForge.

The most important lessons from the phase are:

Fraud is highly imbalanced, so accuracy is not enough.

Missing identity information can itself be a useful fraud signal.

Financial exposure must be considered alongside fraud frequency.

Temporal behavior provides useful early fraud-risk information.

Memory-efficient data engineering is necessary for large, high-dimensional fraud datasets.

Domain-aware feature engineering creates interpretable signals for later machine-learning models.

The cleaned Parquet dataset provides a consistent handoff into the next phase.

24. Next Phase

Phase 2 — SQL Velocity Features & Behavioral Baseline Deviations

The next phase will extend the Phase 1 foundation with behavioral intelligence.

Planned work includes:

1-hour transaction velocity
24-hour rolling spend
Transaction frequency
Amount deviation
Z-scores against historical card behavior
Behavioral baselines
SQL/DuckDB rolling-window features

The pipeline will become:

Phase 1 Clean Dataset
        ↓
Behavioral Feature Engineering
        ↓
Velocity Features
        ↓
Historical Baselines
        ↓
Deviation / Risk Signals
        ↓
Phase 3 Graph Intelligence

Phase 1 Status: COMPLETE ✓