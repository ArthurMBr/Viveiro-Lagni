# pedidos/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Pedido, ItemPedido
from produtos.models import Produto
from lotes.models import Lote

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['status', 'observacoes', 'valor_frete', 'desconto_total', 'previsao_entrega']
        widgets = {
            'previsao_entrega': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'valor_frete': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'desconto_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not field.widget.attrs.get('class'):
                field.widget.attrs.update({'class': 'form-control'})

ItemPedidoFormSet = inlineformset_factory(
    Pedido,
    ItemPedido,
    fields=['produto', 'lote', 'quantidade', 'preco_unitario', 'id'],
    extra=1,
    can_delete=True,
    widgets={
        'produto': forms.Select(attrs={'class': 'form-control select2-item'}),
        'lote': forms.Select(attrs={'class': 'form-control select2-item'}),
        'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        'preco_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
    }
)