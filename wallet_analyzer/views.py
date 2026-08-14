"""
Wallet Analyzer Views

index   GET /              Wallet address input form
analyze POST /analyze/     Fetch -> predict -> save -> redirect
results GET /results/<pk>/ Display saved wallet analysis
"""

import logging
from datetime import datetime, timezone

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from api.blockchain_api import BlockchainAPI
from ml.aggregator import aggregate_wallet_risk
from ml.feature_extractor import extract_features, get_amount_btc
from ml.predictor import predict_transaction
from .models import TransactionAnalysis, WalletAnalysis

logger = logging.getLogger(__name__)

MAX_TRANSACTIONS = 50 # cap to keep response time acceptable

# ── Views ─────────────────────────────────────────────────────────────────

def index(request):
    """Landing page with wallet address input form."""
    return render(request, "wallet_analyzer/index.html")


def analyze(request):
    """POST - fetch wallet -> run ML -> persist -> redirect to results."""
    if request.method != "POST":
        return redirect("index")

    wallet_address = request.POST.get("wallet_address", "").strip()

    if not wallet_address:
        messages.error(request, "Please enter a Bitcoin wallet adress.")
        return redirect("index")

     # ── 1. Fetch from Blockchain.com API ──────────────────────────────────
    api = BlockchainAPI()
    wallet_data = api.get_address(wallet_address, limit=MAX_TRANSACTIONS)

    if wallet_data is None:
        messages.error(
            request, 
            "Could not fetch wallet data."
            "Check the address or try again later."
        )
        return redirect("index")

    raw_txs = wallet_data.get("txs", [])

    if not raw_txs:
        messages.error(
            request, 
            "No transactions found for this wallet address."
        )
        return redirect("index")

    # ── 2. Score each transaction ─────────────────────────────────────────
    tx_results = []
    for raw_tx in raw_txs[:MAX_TRANSACTIONS]:
        try:
            features = extract_features(raw_tx)
            prediction = predict_transaction(features)
            tx_results.append({
                "tx_hash": raw_tx.get("hash", ""),
                "tx_timestamp": _parse_timestamp(raw_tx.get("time")),
                "tx_amount_btc": get_amount_btc(raw_tx),
                **prediction,
            })
        except Exception:
            logger.exception(
                "Failed to score transaction %s", raw_tx.get("hash", "?")
            )

    if not tx_results:
        messages.error(request, "Failed to analyse any transactions.")
        return redirect("index")

     # ── 3. Aggregate to wallet level ──────────────────────────────────────
    wallet_risk = aggregate_wallet_risk(tx_results)
    
    # ── 4. Persist wallet analysis ────────────────────────────────────────
    wallet_analysis = WalletAnalysis.objects.create(
        wallet_address=wallet_address,
        risk_score=wallet_risk["risk_score"],
        risk_level=wallet_risk["risk_level"],
        total_transactions_analyzed=len(tx_results),
        high_risk_transaction_count=wallet_risk["high_risk_count"],
        high_risk_transaction_ratio=wallet_risk["high_risk_ratio"],
        patterns_detected=[],
        illicit_connection_count=0,
    )

    # ── 5. Persist transactions (bulk for efficiency) ─────────────────
    TransactionAnalysis.objects.bulk_create([
        TransactionAnalysis(
            wallet_analysis=wallet_analysis,
            tx_hash=tx["tx_hash"],
            tx_timestamp=tx["tx_timestamp"],
            tx_amount_btc=tx["tx_amount_btc"],
            isolation_forest_score=0.0,     # not used in MVP
            local_outlier_factor_score=0.0, # not used in MVP
            random_forest_score=tx["risk_score"],
            ensemble_risk_score=tx["risk_score"],
            risk_level=tx["risk_level"],
            is_connected_to_illicit=False,
            connected_illicit_addresses=[],
        )
        for tx in tx_results
    ])

    return redirect("results", pk=wallet_analysis.pk)


def results(request, pk: int): 
    """GET - display a saved wallet analysis."""
    wallet_analysis = get_object_or_404(WalletAnalysis, pk=pk)
    transactions = wallet_analysis.transactions.all() # type: ignore

    context = {
        "wallet": wallet_analysis,
        "transactions": transactions,
        "high_risk_pct": round(wallet_analysis.high_risk_transaction_ratio * 100, 1),
    }

    return render(request, "wallet_analyzer/results.html", context=context)

    # ── Helpers ───────────────────────────────────────────────────────────────

def _parse_timestamp(ts) -> datetime:
    if ts:
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    return datetime.now(tz=timezone.utc)
