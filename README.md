# AML Blockchain Monitoring System

Source code for the engineering thesis *"Anti-Money Laundering Blockchain Monitoring System: A Comparative Analysis of Machine Learning Algorithms for Illicit Transaction Detection"* (Yaroslav Oleskevych, WSB Merito University in Wrocław, 2026).

The project has two parts:

1. **Experiments** – a comparison of Random Forest (supervised), Isolation Forest and Local Outlier Factor (unsupervised) for detecting illicit Bitcoin transactions on the Elliptic Bitcoin Dataset, evaluated under a random label holdout split and a temporal split.
2. **Web application** – a Django prototype that fetches the transactions of a Bitcoin address from the Blockchain.com API, scores each transaction with the trained Random Forest model and aggregates the scores into a wallet-level risk assessment.

## Repository structure

| Path | Contents |
|---|---|
| `notebooks/` | Jupyter notebooks with data exploration, preprocessing, training and evaluation |
| `notebooks/models/` | Serialized models (`.joblib`) and hyperparameter search results |
| `data/elliptic/` | Compressed Elliptic Bitcoin Dataset (three `.zip` archives) |
| `ml/` | Feature extraction, prediction and wallet-level risk aggregation |
| `api/` | Blockchain.com API wrapper with local caching |
| `wallet_analyzer/` | Django app: models, views, templates |
| `config/` | Django project settings and URL configuration |
| `scripts/setup_env.sh` | Environment setup script |
| `docs/SETUP.md` | Detailed setup instructions (Windows, Linux, macOS) |

## Requirements

- Python 3.12+
- PostgreSQL 16+
- [uv](https://docs.astral.sh/uv/) package manager

## Running the web application

```bash
# 1. First run creates .env from .env.example and stops
bash scripts/setup_env.sh

# 2. Edit .env: set DB_PASSWORD and SECRET_KEY
#    (create the PostgreSQL database and user first, see docs/SETUP.md)

# 3. Second run installs dependencies, tests the database connection,
#    applies migrations and collects static files
bash scripts/setup_env.sh

# 4. Start the development server
uv run python manage.py runserver
```

Open http://127.0.0.1:8000/ and enter a Bitcoin address. The application analyses up to 50 of the address's transactions.

## Reproducing the experiments

1. Extract the three archives in `data/elliptic/` into the same folder, so that it contains `elliptic_txs_features.csv`, `elliptic_txs_classes.csv` and `elliptic_txs_edgelist.csv`.
2. Start Jupyter with `uv run jupyter lab`.
3. Run the notebooks in one kernel, in this order:

| Notebook | Purpose |
|---|---|
| `01_explore_elliptic_dataset.ipynb` | Class distribution, time steps and features |
| `02_preprocessing.ipynb` | Merging, renaming (`txId`, `time_step`, `f2`–`f166`), label encoding, random and temporal splits |
| `03_training.ipynb` | Random-split Random Forest (RandomizedSearchCV + SMOTE); temporal Isolation Forest and LOF |
| `random_split_unsupervised.ipynb` | Isolation Forest and LOF trained on unlabeled transactions, evaluated on labeled ones |
| `rf_exp2.ipynb` | Temporal Random Forest configuration search (train 1–34, validation 35–41) |
| `rf_exp2_training.ipynb` | Experiments 2A–2C; final Experiment 2B model retrained on time steps 1–41 |
| `rf_exp2_post_training_research.ipynb` | Per-time-step recall and probability analysis |
| `04_evaluation.ipynb` | Final evaluation, comparison table, ROC/PR curves, threshold analysis |

## Main findings

- Random Forest reaches a ROC-AUC of 0.997 on the random split and 0.960 on the temporal split; the random split hides the concept drift that appears after the dark market shutdown at time step 43.
- Isolation Forest and Local Outlier Factor score below random chance (ROC-AUC < 0.5): on this dataset, illicit transactions are not statistical outliers in feature space.
- Live features computed from the Blockchain.com API only approximate the Elliptic features, so the web application is a research prototype, not a production AML tool.

## Data source

Elliptic Bitcoin Dataset: M. Weber et al., *Anti-Money Laundering in Bitcoin: Experimenting with Graph Convolutional Networks for Financial Forensics*, KDD '19 Workshop on Anomaly Detection in Finance, arXiv:1908.02591, 2019. Public copy: https://www.kaggle.com/datasets/ellipticco/elliptic-data-set
