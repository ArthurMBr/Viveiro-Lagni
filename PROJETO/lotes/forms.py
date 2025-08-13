# lotes/forms.py

from django import forms
from .models import Lote

class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['produto', 'quantidade', 'data_semeadura'] # REMOVIDO: 'variedade'
        widgets = {
            'data_semeadura': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'produto': 'Produto',
            # REMOVIDO: 'variedade': 'Variedade',
            'quantidade': 'Quantidade',
            'data_semeadura': 'Data de Semeadura',
        }