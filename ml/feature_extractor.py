"""
Feature Extractor 

Maps a raw Blockchain.com API transaction dict to the 165-column 
feature vector the RF model expects.

LIMITATION
----------
The Elliptic dataset features are proprietary and anonymised. Only a small
subset can be approximated from public blockchain data. The remaining 154 positions
default to 0 (the dataset's normalised zero). Prediction are 
therefore indicative - this limitation is documented int the thesis.

Feature layout (Elliptic convention)
------------------------------------

f2-f94   : local (per-transaction) features - partially computable here
f95-f166 : aggregated graph-neighbourhood features - set to 0
"""

from datetime import datetime, timezone


# ── Public API ────────────────────────────────────────────────────────────
def extract_features(raw_tx: dict) -> dict:
    """
    Convert a single Blockchain.com raw transaction into a feature dict.

    Parameters
    ----------
    raw_tx: dict - one element from BlockchainAPI.get_address()["txs"]

    Returns
    -------
    dict {f2: float, f3: float, ..., f166: float}
    """
    # Start with all features zeroed (graph features stay 0)
    features = {f"f{i}": 0.0 for i in range(2, 167)}

    # ── Derive local values from raw tx ──────────────────────────────────
    total_input  = _sum_inputs(raw_tx) # satoshis
    total_output = _sum_outputs(raw_tx) # satoshis
    fee          = max(total_input - total_output, 0)
    n_inputs     = len(raw_tx.get("inputs", []))
    n_outputs    = len(raw_tx.get("out", []))
    tx_size      = raw_tx.get("size", 0) or 0

    btc_input = total_input / 1e8
    btc_output = total_output / 1e8
    btc_fee = fee / 1e8
    fee_rate = fee / tx_size if tx_size > 0 else 0.0

    ts   = raw_tx.get("time") or 0
    hour = datetime.fromtimestamp(ts, timezone.utc).hour if ts else 0.0

    # ── Map to feature slots ──────────────────────────────────────────────
    # The exact Elliptic semantics are unknown; these are reasonable proxies.
    features["f2"]  = btc_output                                        # output value (BTC)
    features["f3"]  = btc_input                                         # input value  (BTC)
    features["f4"]  = btc_fee                                           # fee (BTC)
    features["f5"]  = float(n_inputs)                                   # number of inputs
    features["f6"]  = float(n_outputs)                                  # number of outputs
    features["f7"]  = float(tx_size)                                    # tx size (bytes)
    features["f8"]  = fee_rate                                          # fee rate (sat/byte)
    features["f9"]  = float(hour)                                       # UTC hour of day
    features["f10"] = btc_input  / btc_output if btc_output > 0 else 0.0   # input/output ratio
    features["f11"] = float(n_outputs) / float(n_inputs) if n_inputs > 0 else 0.0  # out/in count

    return features


def get_amount_btc(raw_tx: dict) -> float:
    """Total output value of a transaction in BTC."""
    return _sum_outputs(raw_tx) / 1e8


# ── Helpers ───────────────────────────────────────────────────────────────

def _sum_inputs(raw_tx: dict) -> int:
    return sum(
        inp.get("prev_out", {}).get("value", 0)
        for inp in raw_tx.get("inputs", [])
    )

def _sum_outputs(raw_tx: dict) -> int:
    return sum(
        out.get("value", 0)
        for out in raw_tx.get("out", [])
    )
