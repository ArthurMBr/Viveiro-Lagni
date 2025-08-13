# produtores/admin.py
from django.contrib import admin
from .models import ProdutorRural, ResponsavelTecnico, CertificadoDigitalResponsavel
from .forms import ProdutorRuralForm, ResponsavelTecnicoForm, CertificadoDigitalResponsavelForm

class CertificadoDigitalResponsavelInline(admin.TabularInline):
    model = CertificadoDigitalResponsavel
    form = CertificadoDigitalResponsavelForm
    extra = 0
    fields = ('nome_arquivo', 'arquivo_pfx', 'senha_pfx', 'data_validade', 'observacoes')
    readonly_fields = ('data_cadastro',)

class ResponsavelTecnicoInline(admin.TabularInline):
    model = ResponsavelTecnico
    form = ResponsavelTecnicoForm
    extra = 1
    fields = ('nome', 'cpf', 'registro_profissional', 'telefone', 'email', 'observacoes')
    inlines = [CertificadoDigitalResponsavelInline]

@admin.register(ProdutorRural)
class ProdutorRuralAdmin(admin.ModelAdmin):
    form = ProdutorRuralForm
    inlines = [ResponsavelTecnicoInline]

    list_display = (
        'nome_fantasia', 'razao_social', 'cpf_cnpj', 'telefone_principal',
        'cidade', 'estado', 'renasem', 'funrural_recolhimento_tipo' # 'email' removed from here
    )
    list_filter = (
        'estado', 'cidade', 'funrural_recolhimento_tipo',
        'data_cadastro', 'data_atualizacao'
    )
    search_fields = ('nome_fantasia', 'razao_social', 'cpf_cnpj', 'cidade', 'estado', 'renasem')
    ordering = ('nome_fantasia',)
    readonly_fields = ('data_cadastro', 'data_atualizacao')
    date_hierarchy = 'data_cadastro'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)