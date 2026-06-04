"""
Blockchain.com API Integration
Simple module to fetch Bitcoin transaction and wallet data 
"""

import requests
import json
import time 
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class BlockchainAPI:
    """
    Simple wrapper for Blockchain.com API
    Includes file-based caching for better performance
    """
    
    BASE_URL = "https://blockchain.info"
    CACHE_DIR = Path("data/cache/transactions")
    CACHE_DURATION = timedelta(hours=24)

    def __init__(self):
        self.session = requests.Session()
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def get_transaction(self, tx_hash: str) -> Optional[Dict]:
        """
        Fetch a single Bitcoin transaction data from Blockchain.com by its hash

        Args: 
            tx_hash: Transaction hash(64 character hex string)

        Returns:
            Dictionary with transaction data, or None if error
            """
        
        url = f"{self.BASE_URL}/rawtx/{tx_hash}"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching transaction data for {tx_hash}: {e}")
            return None

    def get_address(self, address: str, limit: int = 50) -> Optional[Dict]:
        """
        Fetch transactions for a Bitcoin address
        Includes simple file-based caching
        
        Args:
            address : Bitcoin address
            limit: Maximum number of transactions to fetch (default 50, max 100)
        
        Returns:
            Dictionary with address data including transactions
        """

        # Check cache first
        cache_file = self.CACHE_DIR / f"{address}.json"
        if cache_file.exists():
            file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if datetime.now() - file_time < self.CACHE_DURATION:
                print(f"Using cached data for {address[:8]}...")
                with open(cache_file, 'r') as f:
                    return json.load(f)
            else:
                print(f"Cache expired for {address[:8]}..., fetching fresh data.")

        # Fetch from API
        url = f"{self.BASE_URL}/rawaddr/{address}?limit={limit}"

        try:
            print(f"Fetching from Blockchain.com API...")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()

            with open(cache_file, 'w') as f:
                json.dump(data, f)
            
            print(f"Data fetched an cached for {address[:8]}...")
            return data

        except requests.exceptions.RequestException as e:
            print(f"Error fetching address: {e}")
            return None
        
    def get_address_balance(self, address: str) -> Optional[int]:
        """
        Get the current balance of a Bitcoin address in satoshis

        Args: 
            address: Bitcoin address
        
        Returns:
            Balance in satoshis (1 BTC = 100,000,000 satoshis), or None if error
        """
        url = f"{self.BASE_URL}/q/addressbalance/{address}"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return int(response.text)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching balance: {e}")
            return None

def test_api():
    """
    Test the API with known Bitcoin transactions and addresses
    """

    print("=" * 60)
    print(" " * 15 + "BLOCKCHAIN API TEST")
    print("=" * 60)

    api = BlockchainAPI()

    # Test 1: Fetch a famous transaction (Bitcoin Pizza - first real-world BTC purchase)
    print("\n🧪 TEST 1: Fetch Single Transaction")
    print("-"*60)
    tx_hash = "a1075db55d416d3ca199f55b6084e2115b9345e16c5cf302fc80e9d5fbf5d48d"
    print(f"Transaction: {tx_hash[:16]}...")

    tx_data = api.get_transaction(tx_hash)

    if tx_data:
        print("\n✅ SUCCESS! Transaction data received:")
        print(f"    - Block Height: {tx_data.get('block_height', 'N/A')}")
        print(f"    - Time:{datetime.fromtimestamp(tx_data.get('time', 0)).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"    - Inputs: {len(tx_data.get('inputs', []))}")
        print(f"    - Outputs: {len(tx_data.get('out', []))}")
        print(f"    - Size: {tx_data.get('size', 'N/A')} bytes")

        # Calculate values (UTXO - Unspent Transaction Outout model)
        total_input = sum(inp.get('prev_out', {}).get('value', 0) for inp in tx_data.get('inputs', []))
        total_output = sum(out.get('value', 0) for out in tx_data.get('out', []))
        fee = total_input - total_output
        print(f"   - Input Value: {total_input / 1e8:.8f} BTC")
        print(f"   - Output Value: {total_output / 1e8:.8f} BTC")
        print(f"   - Fee: {fee / 1e8:.8f} BTC")
    
    else:
        print("\n❌ Failed to fetch transaction")
        return False

    # Test 2 Fetch wallet address
    print("\n\n🧪 TEST 2: Fetch Wallet Address")
    print("-"*60)
    # This is a known address with some activity (not too many transactions)
    address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"  # Satoshi's address (first BTC address)
    print(f"Address: {address}")

    addr_data = api.get_address(address, limit=10)

    if addr_data:
        print("\n✅ SUCCESS! Address data received:")
        print(f"   - Total Received: {addr_data.get('total_received', 0) / 1e8:.8f} BTC")
        print(f"   - Total Sent: {addr_data.get('total_sent', 0) / 1e8:.8f} BTC")
        print(f"   - Final Balance: {addr_data.get('final_balance', 0) / 1e8:.8f} BTC")
        print(f"   - Number of Transactions: {addr_data.get('n_tx', 0)}")
        print(f"   - Transactions fetched: {len(addr_data.get('txs', []))}")
    else:
        print("\n❌ Failed to fetch address")
        return False

     # Test 3: Get balance
    print("\n\n🧪 TEST 3: Get Address Balance")
    print("-"*60)
    balance = api.get_address_balance(address)
    
    if balance is not None:
        print(f"\n✅ SUCCESS! Balance: {balance / 1e8:.8f} BTC")
    else:
        print("\n❌ Failed to fetch balance")
        return False
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    return True


if __name__ == "__main__":
    test_api()
