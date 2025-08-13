# produtos/admin.py
from django.contrib import admin
from django.db import models # Importe models para usar nos formfield_overrides
from .models import Produto, NCM, CFOP # Lote foi removido daqui
from .forms import ProdutoForm # Importe o ProdutoForm
from django_select2.forms import Select2Widget # Importe Select2Widget

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    form = ProdutoForm # Use o ProdutoForm personalizado
    list_display = (
        'cod', 'unidade', 'qtd_unid', 'tipo',
        'variedade', 'especie', 'cod_especie',
        'cultivar_info', 'estoque', 'preco', 'status_display', 'valor_total',
        'ncm', 'cfop', 'get_imagem_preview'
    )
    list_filter = ('status', 'tipo', 'unidade')
    search_fields = ('cod', 'variedade', 'especie', 'cod_especie', 'cultivar_info', 'ncm__codigo', 'ncm__descricao', 'cfop__codigo', 'cfop__descricao')

    fieldsets = (
        (None, {
            'fields': (
                'cod',
                ('unidade', 'qtd_unid'),
                ('tipo', 'variedade'),
                ('especie', 'cod_especie'),
                'cultivar_info',
                'preco',
                'status',
                'ncm',
                'cfop',
                'imagem',
            )
        }),
    )

    # Adicionado para usar Select2 em campos ForeignKey (NCM, CFOP) se não estiver no forms.py
    # Se já estiver configurado via NCMSelect2Widget e CFOPSelect2Widget no forms.py, esta parte é opcional.
    formfield_overrides = {
        models.ForeignKey: {'widget': Select2Widget},
    }

    # Calcula o valor total (isto deve estar no admin, não no model)
    def valor_total(self, obj):
        return obj.estoque * obj.preco
    valor_total.short_description = 'Valor Total em Estoque'

    # Exibe o status com cores
    def status_display(self, obj):
        from django.utils.html import format_html # Mova o import para dentro da função para evitar erro de importação circular
        if obj.status == 'Sem Estoque':
            return format_html('<span style="color: red; font-weight: bold;">{}</span>', obj.status)
        elif obj.status == 'Com Estoque':
            return format_html('<span style="color: green;">{}</span>', obj.status)
        return obj.status
    status_display.allow_tags = True
    status_display.short_description = 'Status'

    # Pré-visualização da imagem
    def get_imagem_preview(self, obj):
        if obj.imagem and hasattr(obj.imagem, 'url'):
            from django.utils.html import format_html
            return format_html(f'<img src="{obj.imagem.url}" width="100" height="auto" />')
        return "(Sem imagem)"
    get_imagem_preview.short_description = 'Pré-visualização da Imagem'
    get_imagem_preview.allow_tags = True


@admin.register(NCM)
class NCMAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descricao',)
    search_fields = ('codigo', 'descricao',)
    ordering = ('codigo',)

@admin.register(CFOP)
class CFOPAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descricao',)
    search_fields = ('codigo', 'descricao',)
    ordering = ('codigo',)

# A classe LoteAdmin e seu registro foram REMOVIDOS daqui.
# Eles devem estar no arquivo lotes/admin.py.