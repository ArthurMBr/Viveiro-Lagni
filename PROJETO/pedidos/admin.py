# pedidos/admin.py
from django.contrib import admin
from .models import Pedido, ItemPedido
from .forms import PedidoForm

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    form = PedidoForm
    inlines = [ItemPedidoInline]
    list_display = ('id', 'data_pedido', 'previsao_entrega', 'status', 'total_pedido')
    search_fields = ('id',)
    list_filter = ('status', 'data_pedido', 'previsao_entrega')

    readonly_fields = ('data_pedido', 'total_pedido')

    fieldsets = (
        (None, {
            'fields': (
                ('status',),
                ('previsao_entrega',),
                'total_pedido',
            )
        }),
    )