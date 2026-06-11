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
