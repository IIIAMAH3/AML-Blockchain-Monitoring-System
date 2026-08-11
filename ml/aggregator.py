"""
Wallet-Level Risk Aggregator

Turns a list of per-transaction ML scores into a single wallet-level
risk summary

Strategy: weight the top-30% worst transactions double so that even a 
small number of highly suspicious transactions elevates the wallet score.
This mirrors real AML practice - one bad actor in the history matters. m 
"""

from __future__ import annotations
from typing import List


def aggregate_wallet_risk(tx_scores: List[dict]) -> dict:
    """
    Parameters
    ----------
    tx_scores : list of dicts, each containing at least:
        risk_score  float  0-100

    Returns
    -------
    dict:
        risk_score      float 0-100
        risk_level      str   LOW | MEDIUM | HIGH
        high_risk_count int 
        high_risk_ratio float 0-1
    """
    if not tx_scores:
        return {
            "risk_score": 0.0,
            "risk_level": "LOW",
            "high_risk_count": 0,
            "high_risk_ratio": 0.0,
        }

    scores = [t["risk_score"] for t in tx_scores]
    n      = len(scores)

    high_risk_count = sum(1 for s in scores if s > 66)
    high_risk_ratio = high_risk_count / n

    # Weighted mean: top 30% worst transactions counted twice
    sorted_scores = sorted(scores, reverse=True)
    top_n         = max(1, int(n * 0.30))
    top_scores    = sorted_scores[:top_n]
    rest_scores   = sorted_scores[top_n:]

    weighted_sum   = sum(top_scores) * 2 + sum(rest_scores)
    weighted_denom = len(top_scores) * 2 + len(rest_scores)
    wallet_score   = round(weighted_sum / weighted_denom, 2)

    return {
        "risk_score":      wallet_score,
        "risk_level":      _risk_level(wallet_score),
        "high_risk_count": high_risk_count,
        "high_risk_ratio": high_risk_ratio
    }

def _risk_level(score: float) -> str:
    if score < 33:
        return "LOW"
    if score < 67:
        return "MEDIUM"
    return "HIGH"