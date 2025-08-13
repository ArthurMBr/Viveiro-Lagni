# caixa_pdv/serializers.py
from rest_framework import serializers
from .models import Venda, ItemVenda, Lote, Produto, MovimentoCaixa

# Certifique-se de que o Produto e Lote são importados corretamente
# se você não os tiver na mesma app, ajuste a importação
# from lotes.models import Lote
# from produtos.models import Produto

class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ['id', 'variedade', 'tipo']

class LoteSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer(read_only=True)
    class Meta:
        model = Lote
        fields = ['id', 'codigo', 'produto']

class ItemVendaSerializer(serializers.ModelSerializer):
    lote = LoteSerializer(read_only=True)
    class Meta:
        model = ItemVenda
        fields = ['id', 'lote', 'quantidade', 'preco_unitario_vendido', 'subtotal']
            
class VendaSerializer(serializers.ModelSerializer):
    itens = ItemVendaSerializer(many=True, read_only=True)
    
    # Este campo já estava comentado, o que é o correto
    # cliente_nome = serializers.CharField(source='cliente.nome_completo', read_only=True) 

    class Meta:
        model = Venda
        # O campo 'forma_pagamento' foi removido porque não existe no seu models.py
        fields = ['id', 'data_venda', 'total_venda', 'observacoes', 'itens']

class MovimentoCaixaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimentoCaixa
        fields = [
            'id',
            'data_hora',
            'tipo',
            'valor',
            'descricao',
        ]