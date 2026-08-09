"""
ML Prediction Engine

Loads the trained Random Forest model once at import time and exposes
a single predict_transaction() function for use by Django views.
"""

import logging
from pathlib import Path

import joblib
import pandas as pd

logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────
# Resolve relative to this file so it works regardless of CWD.
_BASE_DIR   = Path(__file__).resolve().parent.parent
_MODEL_PATH = _BASE_DIR / "notebooks" / "models" / "random_forest" / "random_forest_exp2b.joblib"

# ── Feature layout ────────────────────────────────────────────────────────
# 165 columns: f2 … f166  (f2–f94 = local tx features; f95–f166 = graph)
# Must match the column names used during training.
FEATURE_COLUMNS = [f"f{i}" for i in range(2, 167)]

_model = None

def _get_model():
    global _model
    if _model is None:
        logger.info("Loading RF model from %s", _MODEL_PATH)
        _model = joblib.load(_MODEL_PATH)

    return _model

def _risk_level(score: float) -> str:
    if score < 33:
        return "LOW"
    if score < 67:
        return "MEDIUM"
    return "HIGH"

def predict_transaction(features: dict) -> dict:
    """
    Score a single transaction

    Parameters
    ----------
    features: dict
        Keys are feature names (f2...f166). Missing keys default to 0.
        Values should be in the same scale as the Elliptic dataset.
        For real-world API data these are approximate - see feature_extractor.py.

    Returns
    -------
    dict:
        risk_score          float 0-100
        illicit_probability float 0-1
        risk_level          str   LOW | MEDIUM | HIGH
        prediction          int   0 (licit) | 1 (illicit)   
    """

    model = _get_model()

    # Build a single-row DataFrame with the correct column order.
    # Missing features default to 0 (neutral / unseen value).

    row = {col: float(features.get(col, 0.0)) for col in FEATURE_COLUMNS}
    X = pd.DataFrame([row], columns=FEATURE_COLUMNS)

    #ImbPipeline: SMOTE is skipped at interference - only the RF estimator runs
    prob = float(model.predict_proba(X)[0, 1])
    prediction = int(model.predict(X)[0])
    risk_score = round(prob * 100, 2)

    return {
        "illicit_probability": prob,
        "risk_score": risk_score,
        "risk_level": _risk_level(risk_score),
        "prediction": prediction,
    }
