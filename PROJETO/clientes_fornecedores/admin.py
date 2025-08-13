# clientes_fornecedores/admin.py

from django.contrib import admin
from .models import Cliente
from .forms import ClienteForm

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    form = ClienteForm
    list_display = ('nome_completo', 'razao_social', 'cpf_cnpj', 'email', 'telefone', 'cidade', 'estado', 'tipo_cliente')
    list_filter = ('tipo_cliente',)
    search_fields = ('nome_completo', 'razao_social', 'cpf_cnpj', 'email')
    ordering = ('nome_completo',)