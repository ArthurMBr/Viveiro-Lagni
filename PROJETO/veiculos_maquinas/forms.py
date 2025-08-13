# viveiro_lagni/PROJETO/veiculos_maquinas/forms.py

from django import forms
from .models import Veiculo, Maquina, Manutencao

class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = '__all__' # Inclui todos os campos do modelo
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

class MaquinaForm(forms.ModelForm):
    class Meta:
        model = Maquina
        fields = '__all__'
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

class ManutencaoForm(forms.ModelForm):
    class Meta:
        model = Manutencao
        fields = '__all__'
        widgets = {
            'data_manutencao': forms.DateInput(attrs={'type': 'date'}),
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }