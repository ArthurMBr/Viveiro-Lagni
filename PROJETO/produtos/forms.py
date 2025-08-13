# produtos/forms.py
from django import forms
from .models import Produto, NCM, CFOP # Importe Produto para acessar as escolhas (choices)
from django_select2.forms import ModelSelect2Widget # Mantenha se estiver usando select2 em outros forms

class NCMSelect2Widget(ModelSelect2Widget):
    model = NCM
    search_fields = ['codigo__icontains', 'descricao__icontains']

class CFOPSelect2Widget(ModelSelect2Widget):
    model = CFOP
    search_fields = ['codigo__icontains', 'descricao__icontains']

class ProdutoForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=Produto.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control select2-basic'}) # Mantenha select2-basic se usado
    )

    class Meta:
        model = Produto
        fields = [
            'cod',
            'unidade',
            'qtd_unid',
            'tipo',
            'variedade',
            'especie',
            'cod_especie',
            'cultivar_info',
            'estoque',
            'preco',
            'status',
            'ncm',
            'cfop',
            'imagem',
        ]
        widgets = {
            'ncm': NCMSelect2Widget,
            'cfop': CFOPSelect2Widget,
            'cod': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: P001'}),
            'unidade': forms.Select(attrs={'class': 'form-control select2-basic'}),
            'qtd_unid': forms.Select(attrs={'class': 'form-control select2-basic'}),
            'tipo': forms.Select(attrs={'class': 'form-control select2-basic'}),
            'variedade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Tomate Cereja'}),
            'especie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Solanum lycopersicum'}),
            'cultivar_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Informações detalhadas sobre a cultivar...'}),
            'estoque': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'cod': 'Código do Produto',
            'unidade': 'Unidade de Medida',
            'qtd_unid': 'Quantidade por Unidade',
            'tipo': 'Tipo de Produto',
            'variedade': 'Variedade',
            'especie': 'Espécie',
            'nome_cientifico': 'Nome Científico', # Adicione se for um novo campo
            'cod_especie': 'Código da Espécie',
            'cultivar_info': 'Informações Cultivar',
            'estoque': 'Estoque',
            'preco': 'Preço Unitário',
            'status': 'Status',
            'ncm': 'NCM',
            'cfop': 'CFOP',
            'imagem': 'Imagem do Produto',
        }

# NOVO FORMULÁRIO: ProdutoFilterForm para a busca e filtro na lista de produtos
class ProdutoFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={
            'placeholder': 'Código, variedade, espécie ou nome científico...',
            'class': 'form-control',
        })
    )

    tipo = forms.ChoiceField(
        required=False,
        label='Tipo',
        choices=[('', 'Todos os Tipos')] + list(Produto.TIPO_CHOICES),
        widget=forms.Select(attrs={
            'class': 'form-select', # Usando form-select para Bootstrap 5
        })
    )

    status = forms.ChoiceField(
        required=False,
        label='Status',
        choices=[('', 'Todos os Status')] + list(Produto.STATUS_CHOICES),
        widget=forms.Select(attrs={
            'class': 'form-select', # Usando form-select para Bootstrap 5
        })
    )