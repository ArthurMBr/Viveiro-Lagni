# clientes_fornecedores/forms.py
from django import forms
from .models import Cliente
from .models import Cliente, Fornecedor

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adiciona a classe CSS 'form-control' a todos os campos
        for field_name, field in self.fields.items():
            if field_name == 'tipo_cliente':
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
                
        # Personaliza o campo de observações com as novas classes e atributos
        self.fields['observacoes'].widget.attrs.update({
            'class': 'form-control observacoes-field',
            'placeholder': 'Ex: Cliente prefere contato por e-mail...',
            'rows': 4,
        })

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'produtos_fornecidos':
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})