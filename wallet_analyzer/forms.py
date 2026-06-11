"""
Django Forms for wallet analysis 
"""

from django import forms
import re


class WalletAddressForm(forms.Form):
    """
    Form for wallet address submission
    """

    wallet_address = forms.CharField(
        max_length=64,
        min_length=26,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '1A1zP1eP5QGefi...',
            'autocomplete': 'off',

        }),
        help_text='Bitcoin P2PKH address (starts with 1), P2SH address (starts with 3), or Bech32 address(starts with bc1)'
    )

    def clean_wallet_address(self):
        """Validate Bitcoin address format"""
        address = self.cleaned_data.get('wallet address', '').strip()

        if not address:
            raise forms.ValidationError('Please enter a wallet address')
        
        # Valid Bitcoin address patterns
        # P2PKH: 26-35 characters, starts with 1
        # P2SH: 26-35 characters, starts with 3
        # Bech32: 42-62 characters, starts with bc1

        patterns = [
            r'^1[1-9A-HJ-N-P-Z]{25, 34}$', #P2PKH
            r'^3[1-9A-HJ-NP-Z]{25, 34}$',  #P2SH
            r'^bc1[a-z0-9]{39, 59}$',      #Bech32
        ]

        is_valid = any(re.match(pattern, address) for pattern in patterns)

        if not is_valid:
            raise forms.ValidationError(
                'Invalid Bitcoin address format. Please enter a valid P2PKH (1...),' \
                'P2SH (3...), or Bech32 (bc1...) address.'
            )
        
        return address