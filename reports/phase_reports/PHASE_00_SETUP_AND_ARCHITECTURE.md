# RiskForge — Phase 0 Report (Q&A Format)
## Project Foundation, Environment Setup & Configuration

---

### Question 1: What did we do in Phase 0?
**Answer:**
We built the complete production foundation for the RiskForge platform:
1. Created the full modular repository skeleton with subpackages for data engineering, graph intelligence, modeling, explainability, NLP, and serving.
2. Initialized Git version control and linked the local project to the official GitHub repository (`SamadhanEkad/RiskForge-Intelligent-Financial-Risk-Fraud-Intelligence-Platform`).
3. Defined all production dependencies in `requirements.txt`.
4. Externalized system paths, model parameters, and financial loss economics into YAML configuration files.
5. Successfully created the first initial commit and pushed it to the `main` branch on GitHub.

---

### Question 2: Why did we do this? (Business & Engineering Rationale)
**Answer:**
* **To Avoid "Notebook Spaghetti Code":** In the real world, machine learning models are not built as 1,000-line single notebooks. Structuring the project into reusable Python subpackages (`src/riskforge/`) ensures that code can be imported by our FastAPI backend, Streamlit dashboard, and automated test suite without rewriting logic.
* **To Anchor ML to Financial Reality from Day 1:** Most data scientists make the mistake of jumping into model training with standard accuracy metrics. By defining the `cost_matrix.yaml` in Phase 0, we established that a missed fraud charges a \$15 fee plus 100% of the amount, while a false alert costs \$5 in customer friction.
* **To Ensure Zero-Data-Leak Git Security:** In financial services, committing customer data or private API keys is a critical compliance violation. Setting up `.gitignore` first ensures raw datasets, large CSVs, and model binaries never get pushed to public GitHub.

---

### Question 3: What files were created, and what does each file do?

| File Path | What It Does | Why It Is Important |
| :--- | :--- | :--- |
| **`.gitignore`** | Tells Git to ignore `data/raw/`, `models/`, `.env`, and virtual environments. | Prevents multi-gigabyte data files and sensitive credentials from leaking to GitHub. |
| **`requirements.txt`** | Lists exact pinned versions for DuckDB, LightGBM, NetworkX, SHAP, FastAPI, Streamlit, etc. | Guarantees reproducible builds so anyone cloning your repo gets the exact same environment. |
| **`configs/config.yaml`** | Stores dataset paths, feature column lists, random seeds, and chronological split ratios (80% train / 20% test). | Externalizes parameters so you never hardcode file paths or numbers inside Python scripts. |
| **`configs/cost_matrix.yaml`** | Defines financial dispute costs (\$15 chargeback fee, \$5 customer friction) and the 4 decision tiers: Approve (<30), Step-Up (30–69), Manual Review (70–89), Decline (90–100). | Bridges the gap between statistical probability and executive business decisions. |
| **`src/riskforge/utils/config.py`** | A Python utility function (`load_config()`) that safely reads YAML files. | Allows any notebook, script, or API endpoint to load system settings cleanly. |
| **`src/riskforge/*/__init__.py`** | Modular package initializers for `ingestion/`, `features/`, `models/`, `explainability/`, `nlp/`, `monitoring/`, and `utils/`. | Converts directories into an importable, testable enterprise Python library. |

---

### Question 4: Key Interview Questions & Answers on Phase 0

#### Q: "Why did you externalize configurations into YAML instead of defining variables in Python?"
**A:** In enterprise production systems, code and configuration must be decoupled (12-Factor App methodology). If risk thresholds, chargeback fees, or file paths change, operations teams can update a YAML file without modifying Python source code, triggering code reviews, or redeploying code.

#### Q: "Why did you choose an 80/20 chronological split instead of random 5-fold cross-validation in config.yaml?"
**A:** Standard random K-Fold cross-validation leaks future information into past transactions, resulting in falsely inflated 0.99 AUC scores that fail in production. Financial transactions have strict temporal dependency, so we train on past months and evaluate on future holdout periods (Out-of-Time validation).

---

### Question 5: What is the final output of Phase 0?
**Answer:**
A fully structured, version-controlled GitHub repository live on `main` branch with clean dependencies, modular folders, and financial business configurations, ready to receive and process real transaction data in Phase 1.
