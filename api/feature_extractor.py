"""
Feature Extraction from Blockchain Transactions

Extracts features from blockchain API data to match Elliptic dataset format
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple

class FeatureExtractor:
    """
    Extracts features from blockchain transaction data

    Maps blockchain data to Elliptic-compatible features
    We can't replicate exact Elliptic features (proprietary), but we can 
    extract meaningful transaction characteristics for ML prediction
    """

    def __init__(self):
        """Initialize feature extraction"""
        self.feature_names = self._get_feature_names()

    def _get_feature_names(self) -> Dict[int, str]:
        """
        Map feature indices to human-readable names
        We approximate Elliptic features with blockchain data
        """
        features = {
            0: 'time_step', # Would be 1-49 in Elliptic, estimate 
            1: 'tx_amount_btc',
            2: 'num_inputs',
            3: 'num_outputs',
            4: 'tx_fee_btc',
            5: 'tx_size_bytes',
            6: 'input_output_ratio',
            7: 'average_input_value',
            8: 'average_output_value',
            9: 'min_input_value',
            10: 'max_input_value',
            11: 'min_output_value',
            12: 'max_output_value',
        }

        return features

    def extract_transaction_features(self, tx_data: Dict, blockchain_api_client=None) -> np.ndarray:
        """
        Extract features from a single transaction

        Args:
            tx_data: Transaction data from Blockchain.com API
            blockchain_api_client: Optional API client for enhanced features

        Returns:
            Feature vector as numpy array (should be 166 elements for Elliptic compatibility)
        """

        features = np.zeros(166)

        try: 
            # Feature 0: Time step(estimate based on block height)
            # Block ~57000 is from May 2010, so we estimate era
            block_height = tx_data.get('block_height', 0)
            features[0] = self._estimate_time_step(block_height)

            # Feature 1: Transaction amount in BTC
            total_output = sum(
                out.get('value', 0) for out in tx_data.get('out', [])
            )
            features[1] = total_output / 1e8 # Convert satoshi to BTC
            
            # Feature 2: Number of inputs
            num_inputs = len(tx_data.get('inputs', []))
            features[2] = num_inputs

            # Feature 3: Number of outputs
            num_outputs = len(tx_data.get('out', []))
            features[3] = num_outputs

            # Feature 4: Transaction fee in BTC
            total_input = sum(
                inp.get('prev_out', {}).get('value', 0) for inp in tx_data.get('inputs', [])
            )
            fee_satoshi = total_input - total_output
            features[4] = fee_satoshi / 1e8 # Convert to BTC

            # Feature 5: Transaction size in bytes
            features[5] = tx_data.get('size', 0)

            # Feature 6: Input-output ratio
            if num_outputs > 0:
                features[6] = num_inputs / num_outputs
            else:
                features[6] = 0

            # Feature 7: Avergae input value
            if num_inputs > 0:
                features[7] = (total_input / num_inputs) / 1e8
            else:
                features[7] = 0
            
            # Feature 8: Average output value
            if num_outputs > 0:
                features[8] = (total_output / num_outputs) / 1e8

            # Feature 9-12: Min/Max input/output values
            if tx_data.get('inputs'):
                input_values = [
                    inp.get('prev_out', {}).get('value', 0) for inp in tx_data.get('inputs', [])
                ]
                features[9] = min(input_values) / 1e8 # Min input
                features[10] = max(input_values) / 1e8 # Max input
            
            if tx_data.get('out'): 
                output_values = [out.get('value', 0) for out in tx_data.get('out', [])]
                features[11] = min(output_values) / 1e8 # Min output
                features[12] = max(output_values) / 1e8 # Max output

            # remaining features will be filled with normalized values for now
            # In production, these would be sophisticated aggregate/temporal features
            # Features 13-166: Placeholder (zeros or computed from available data)

            return features
        
        except Exception as e:
            print(f"Error extracting features: {e}")
            return features
        
    def _estimate_time_step(self, block_height: int) -> int:
        """
        Estimate Elliptic time step (1-49) based on block height

        Elliptic dataset: ~49 time steps over 3 years
        Bitcoin: ~6 blocks per hour, ~144 per day
        """
        # Very rough estimation
        # Block 57,043 (May 2010) = time step ~1
        # Block 1,000,000 (Jan 2021) would be time step ~49

        if block_height < 50000: 
            return 1
        
        elif block_height < 500000:
            return  int((block_height - 50000) / 11250) + 1
        
        else:
            return 49
        
    def extract_wallet_features(self, address_data: Dict) -> Dict:
        """
        Extract aggregate features from wallet address data

        Useful for wallet-level risk assessment

        Args:
            address_data: Address data from Blockchain.com API

        Returns:
            Dictionary of aggregate wallet features
        """
        try:
            transactions = address_data.get('txs', [])

            wallet_features = {
                'total_transactions': address_data.get('n_tx', 0),
                'total_received_btc': address_data.get('total_received', 0) / 1e8,
                'total_sent_btc': address_data.get('total_sent', 0) / 1e8,
                'final_balance_btc': address_data.get('final_balance', 0) / 1e8,

                # Transaction characteristics
                'avg_tx_value': np.mean([tx.get('result', 0) for tx in transactions]) / 1e8,
                'max_tx_value': max([abs(tx.get('result', 0))for tx in transactions]) / 1e8,
                'min_tx_value': min([abs(tx.get('result', 0)) for tx in transactions]) / 1e8,

                # Temporal characteristics
                'tx_dates': [tx.get('time', 0) for tx in transactions],
            }

            return wallet_features
        
        except Exception as e:
            print(f"Error extracting wallet features: {e}")
            return {}
        