# viveiro_lagni/PROJETO/veiculos_maquinas/admin.py

from django.contrib import admin
from .models import Veiculo, Maquina, Manutencao

@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'placa', 'modelo', 'ano_fabricacao', 'tipo_combustivel', 'data_cadastro')
    search_fields = ('nome', 'placa', 'modelo')
    list_filter = ('tipo_combustivel', 'ano_fabricacao')

@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'identificacao', 'ano_fabricacao', 'data_cadastro')
    search_fields = ('nome', 'tipo', 'identificacao')
    list_filter = ('tipo', 'ano_fabricacao')

@admin.register(Manutencao)
class ManutencaoAdmin(admin.ModelAdmin):
    list_display = ('get_item_manutencao', 'data_manutencao', 'tipo_manutencao', 'custo', 'realizada_por')
    list_filter = ('tipo_manutencao', 'data_manutencao')
    search_fields = ('descricao', 'realizada_por', 'veiculo__nome', 'maquina__nome')
    raw_id_fields = ('veiculo', 'maquina') # Para facilitar a seleção se tiver muitos veículos/máquinas

    def get_item_manutencao(self, obj):
        if obj.veiculo:
            return f"Veículo: {obj.veiculo.nome}"
        elif obj.maquina:
            return f"Máquina: {obj.maquina.nome}"
        return "N/A"
    get_item_manutencao.short_description = "Item"