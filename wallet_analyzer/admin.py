"""
Django Admin Configuration for AML Monitoring
"""

from django.contrib import admin
from .models import WalletAnalysis, TransactionAnalysis

@admin.register(WalletAnalysis)
class WalletAnalysisAdmin(admin.ModelAdmin):
    """Admin interface for wallet analyses"""

    list_display = [
        'wallet_address_short',
        'risk_score',
        'risk_level',
        'total_transactions_analyzed',
        'analyzed_at'
    ]

    list_filter = ['risk_level', 'analyzed_at']
    search_fields = ['wallet_address']
    readonly_fields = ['analyzed_at', 'updated_at']
    fieldsets = (
        ('Wallet Information', {
            'fields': ('wallet_address',)
        }),
        ('Risk Assessment', {
            'fields': ('risk_score', 'risk_level')
        }),
        ('Transaction Statistics', {
            'fields': (
                'total_transactions_analyzed',
                'high_risk_transaction_count',
                'high_risk_transaction_ratio'
            )
        }),
        ('Patterns & Connections', {
            'fields': (
                'patterns_detected',
                'illicit_connection_count'
            )
        }),
        ('Timestamps', {
            'fields': ('analyzed_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def wallet_address_short(self, obj):
        """Display shortened wallet address"""
        return f"{obj.wallet_address[:8]}...{obj.wallet_address[-4:]}"
    
    wallet_address_short.short_description = "Wallet Address"

@admin.register(TransactionAnalysis)
class TransactionAnalysisAdmin(admin.ModelAdmin):
    """Admin interface for transaction analyses"""
    list_display = [
        'tx_hash_short',
        'ensemble_risk_score',
        'risk_level',
        'tx_timestamp',
        'is_connected_to_illicit'
    ]

    list_filter = ['risk_level', 'is_connected_to_illicit', 'tx_timestamp']
    search_fields = ['tx_hash']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Transaction Information', {
            'fields': ('wallet_analysis', 'tx_hash', 'tx_timestamp', 'tx_amount_btc')
        }),
        ('ML Model Scores', {
            'fields': (
                'isolation_forest_score',
                'local_outlier_factor_score',
                'random_forest_score',
                'ensemble_risk_score'
            )
        }),
        ('Risk assessment', {
            'fields': ('risk_level',)
        }),
        ('Illicit Connections', {
            'fields': (
                'is_connected_to_illicit', 
                'connected_illicit_addresses', 
            ),
            'classes': ('collapse',)
        })
    )

    def tx_hash_short(self, obj):
        """Display shortened tx hash"""
        return f"{obj.tx_hash[:8]}...{tx_hash[-4:]}"

    tx_hash_short.short_description = 'Transaction Hash'