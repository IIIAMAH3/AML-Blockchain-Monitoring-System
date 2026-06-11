"""
URL configuration for wallet_analyzer app
"""

from django.urls import path
from . import views

app_name = 'wallet_analyzer'

url_patterns = [
    path('', views.home, name='home'),
    path('analyze/str:address', views.analyze_wallet, name='analyze_wallet'),
    path('transaction/<int:analysis_id>/<int:tx_id>/', views.transaction_detail, name='transaction_detail'),
    path('alerts/', views.alerts, name='alerts'),
    path('recent/', views.recent_analyses, name='recent_analyses'),
    
]