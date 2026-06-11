"""
Django views for AML Monitoring System
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, Count
from django.contrib import messages
from datetime import datetime, timedelta

from .forms import WalletAddressForm
from .models import WalletAnalysis, TransactionAnalysis
from api.blockchain_api import BlockchainAPI

def home(request):
    """
    Home page - wallet submission form
    """

    if request.method == 'POST':
        form = WalletAddressForm(request.POST)
        if form.is_valid():
            wallet_address = form.cleaned_data['wallet_address']
            # Redirect to analysis page
            return redirect('analyze_wallet', address=wallet_address)
    else:
        form = WalletAddressForm()
        
    # Get statistics for display
    total_analyses = WalletAnalysis.objects.count()
    avg_risk_score = WalletAnalysis.objects.aggregate(avg=Avg('risk_score'))['avg'] or 0

    high_risk_count = WalletAnalysis.objects.filter(risk_level='HIGH').count()

    context = {
        'form': form,
        'total_analyses': total_analyses,
        'avg_risk_score': round(avg_risk_score, 2),
        'high_risk_count': high_risk_count,
    }

    return render(request, 'wallet_analyzer/home.html', context)


def analyze_wallet(request, address):
    """
    Analyze a wallet and display results

    This view:
    1.Checks if specific wallet was recently analyzed (cache)
    2.If not, fetches data from Blockchain API
    3.Extract features
    4.Runs ML models (placeholder for now)
    5.Saves results to database
    6.Displays results 
    """
    # Check cache - has this wallet been analyzed in last 24 hours?
    recent_analysis = WalletAnalysis.objects.filter(
        wallet_address=address,
        analyzed_at__gte=datetime.now() - timedelta(hours=24)).first()
    
    if recent_analysis:
        # Use cached results
        analysis = recent_analysis
        cached = True
    else:
        # Fetch and analyze
        cached = False

        try:
            # Initialize API client
            api = BlockchainAPI()

            # Fetch blockchain data
            address_data, transactions_with_features = api.get_address_with_features(
                address,
                limit=500 # Analyze last 500 transactions
            )
            if not address_data:
                messages.error(request, 'Could not fetch data from blockchain. Please try again')
                return redirect('home')
            
            # For now, create placeholder analysis
            # Week 3 will add actual ML predictions
            analysis = WalletAnalysis.objects.create(
                wallet_address=address,
                risk_score=50.0,
                risk_level='MEDIUM',
                total_transactions_analyzed=len(transactions_with_features),
                high_risk_transaction_count=0,
                high_risk_transaction_ratio=0.0,
                patterns_detected=[],
                illicit_connection_count=0,
                notes='Analysis completed successfully (ML predictions coming later)'
            )

            for tx_info in transactions_with_features[:100]: # Save first 100 for now
                tx_data = tx_info['tx_data']        

                TransactionAnalysis.objects.create(
                    wallet_analysis=analysis,
                    tx_hash=tx_info['tx_hash'],
                    tx_timestamp=datetime.fromtimestamp(tx_data.get('time', 0)),
                    tx_amount_btc=sum(o.get('value', 0) for o in tx_data.get('out', [])),
                    isolation_forest_score=50.0, # Placeholder
                    local_outlier_factor_score=50.0, # Placeholder
                    random_forest_score=50.0, # Placeholder
                    ensemble_risk_score=50.0, # Placeholder
                    risk_level='MEDIUM', # Placeholder,
                    is_connected_to_illicit=False,
                )
        
        except Exception as e:
            messages.error(request, f'Error analyzing wallet: {str(e)}')
            return redirect('home')

    # Get related transactions
    transactions = analysis.transactions.all()[:20] # type: ignore
    
    context = {
        'analysis': analysis,
        'transactions': transactions,
        'cached': cached,
        'wallet_address_display': f"{address[:8]}...{address[-4]}",
    }

    return render(request, 'wallet_analyzer/wallet_analysis.html', context)

def transaction_detail(request, analysis_id, tx_id):
    """
    Detailed view of a single transaction within a wallet analysis
    """
    analysis = get_object_or_404(WalletAnalysis, id=analysis_id)
    transaction = get_object_or_404(
        TransactionAnalysis,
        id=tx_id,
        wallet_analysis=analysis
    )

    context = {
        'analysis': analysis,
        'transaction': transaction
    }

    return render(request, 'wallet_analyzer/transaction_detail.html', context)


def alerts(request):
    """
    Display high-risk wallets and transactions
    """
    # Get high-risk wallets analyzed in last 30 days
    high_risk_analyses = WalletAnalysis.objects.filter(
        risk_level='HIGH',
        analyzed_at__gte=datetime.now() - timedelta(days=30)
    ).order_by('-risk_score')

    # Get high-risk transactions
    high_risk_transactions = TransactionAnalysis.objects.filter(
        risk_level='HIGH'
    ).order_by('-ensemble_risk_score')[:50]

    context = {
        'high_risk_analyses': high_risk_analyses,
        'high_risk_transactions': high_risk_transactions,
    }

    return render(request, 'wallet_analyzer/alerts.html', context)

def recent_analyses(request):
    """
    Display recently analyzed wallets
    """
    analyses = WalletAnalysis.objects.all()[:20]

    context = {
        'analyses': analyses,
    }

    return render(request, 'wallet_analyzer/recent_analyses.html', context)
