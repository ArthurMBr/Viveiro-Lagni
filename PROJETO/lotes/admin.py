# lotes/admin.py
from django.contrib import admin
from django.db import models # Necessário para formfield_overrides
from .models import Lote
from django_select2.forms import Select2Widget # Mantenha se você usa o Select2

@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        # 'numero_lote', # REMOVIDO: Conforme solicitado
        'produto',
        'quantidade',
        'preco_unitario',
        'data_semeadura',   # Usando o campo do seu models.py
    )
    list_filter = (
        'produto',
        'data_semeadura',   # Usando o campo do seu models.py
    )
    search_fields = (
        'codigo',
        # 'numero_lote', # REMOVIDO: Conforme solicitado
        'produto__cod',
        'produto__variedade',
        # 'observacoes' foi removido, pois não está no seu models.py atual
    )
    ordering = (
        '-data_semeadura', # Ordena pela data de semeadura mais recente
        'codigo',
    )
    # Define campos que não podem ser editados manualmente no admin
    readonly_fields = ('codigo', 'preco_unitario') # 'numero_lote' foi removido daqui também
    # Permite navegar por data na barra lateral do admin
    date_hierarchy = 'data_semeadura' # Usando o campo do seu models.py

    # Se você estiver usando django-select2 para o campo 'produto' no admin
    # formfield_overrides = {
    #     models.ForeignKey: {'widget': Select2Widget}
    # }