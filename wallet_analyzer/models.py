"""
Database models for AML Monitoring System

Models:
 - WalletAnalysis: Results of analyzing a Bitcoin wallet
 - TransactionAnalysis: Per-transaction risk scores
"""


from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class WalletAnalysis(models.Model):
    """
    Stores the results of analyzing a Bitcoin wallet
    """

    # Wallet information
    wallet_address = models.CharField(
        max_length=64,
        db_index=True,
        help_text='Bitcoin wallet address'
    )

    # Analysis results
    risk_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text='Overall wallet risk score (0-100)'
    )

    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('LOW', 'Low risk (0-33)'),
            ('MEDIUM', 'Medium risk (34-66)'),
            ('HIGH', 'High Risk (67-100)'),
        ],
        help_text='Risk classification'
    )

    # Transaction statistics
    total_transactions_analyzed = models.IntegerField(
        help_text='Number of transactions analyzed'
    )

    high_risk_transaction_count = models.IntegerField(
        default=0,
        help_text='Number of transactions flagges as high risk' 
    )

    high_risk_transaction_ratio = models.FloatField(
        default = 0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='Ratio of high-risk transaction (0-1)'
    )

    # Patterns detected
    patterns_detected = models.JSONField(
        default=list, 
        help_text='List of suspicious patterns detected'
    )

    # Illicit connections
    illicit_connection_count = models.IntegerField(
        default=0,
        help_text='Number of connections to known illicit addresses.'
    )

    # Metadata
    analyzed_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When this analysis was created'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When this analysis was last updated'
    )

    notes = models.TextField(
        blank=True,
        default="",
        help_text="Additional notes about this analysis"
    )

    class Meta:
        ordering = ['-analyzed_at']
        indexes = [
            models.Index(fields=['wallet_address', '-analyzed_at'])
        ]

    def __str__(self):
        return f"{self.wallet_address[:8]}...(Risk {self.risk_score:.1f})"
    
    def get_risk_level_color(self):
        """
        Return color for risk level visualization
        """
        if self.risk_level == 'LOW':
            return '#28a745'
        elif self.risk_level == 'MEDIUM':
            return '#ffc107'
        else:
            return '#dc3545'


class TransactionAnalysis(models.Model):
    """
    Stores per-transaction risk analysis for a wallet
    Linked to WalletAnalysis
    """
    # Foreign key to wallet analysis
    wallet_analysis = models.ForeignKey(
        WalletAnalysis,
        on_delete=models.CASCADE,
        related_name='transactions',
        help_text='Parent wallet analysis'
     )

     # Transaction information
    tx_hash = models.CharField(
        max_length=64,
        db_index=True,
        help_text='Bitcoin transaction hash'
    )

    tx_timestamp = models.DateTimeField(
        help_text='When the transaction occurred on blockchain'
    )

    tx_amount_btc = models.DecimalField(
        max_digits=16,
        decimal_places=8,
        help_text='Transaction amount in BTC'
    )

    # ML Model Predictions (per model)
    isolation_forest_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text='Isolation Forest anomaly score (0-100)'
    )

    local_outlier_factor_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text='LOF anomaly score (0-100)'
    )

    random_forest_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text='Random Forest probability of illicit score (0-100)'
    )

    # Ensemble score (combination of all three)
    ensemble_risk_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text='Ensemble risk score combining all models (0-100)'
    )

    # Risk classification
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('LOW', 'Low risk (0-33)'),
            ('MEDIUM', 'Medium risk (34-66)'),
            ('HIGH', 'High Risk (67-100)'),
        ],
        help_text='Risk classification for this transaction'
    )

    # Connected addresses
    is_connected_to_illicit = models.BooleanField(
        default=False,
        help_text='Is this transaction connected to known illicit address?'
    )

    connected_illicit_addresses = models.JSONField(
        default=list,
        help_text="List of known illicit addresses this tx connects to"
    )

     # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this analysis was created"
    )

    class Meta:
        ordering = ['-ensemble_risk_score']
        indexes = [
            models.Index(fields=['wallet_analysis', '-ensemble_risk_score']),
            models.Index(fields=['tx_hash']),
        ]
    
    def __str__(self):
        return f"TX {self.tx_hash[:8]}... (Risk: {self.ensemble_risk_score:.1f})"
    

class AnalysisFeatures(models.Model):
    """
    Stores extracted features for debugging and analysis
    Optional: Can be deleted if storage becomes an issue
    """

    transaction_analysis = models.OneToOneField(
        TransactionAnalysis,
        on_delete=models.CASCADE,
        related_name='features',
        help_text='Associated transaction analysis'
    )

    # Store the 166 features as JSON (space efficient)
    feature_vector = models.JSONField(
        help_text='Dictionary of {feature_number: value} for all 166 features'
    )

    # Time step (Feature 1)
    time_step = models.IntegerField(
        help_text='Time step in ELliptic daataset(1-49)'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    class Meta:
        verbose_name_plural = "Analysis Features"
    
    def __str__(self):
        return f"Features for {self.transaction_analysis.tx_hash[:8]}..."
