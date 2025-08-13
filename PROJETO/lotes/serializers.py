# lotes/serializers.py
from rest_framework import serializers
from .models import Lote
# Importe o modelo Produto da sua aplicação de produtos
from produtos.models import Produto 

# Criação de um Serializer para o modelo Produto
class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ['id', 'variedade', 'tipo', 'unidade']

class LoteSerializer(serializers.ModelSerializer):
    # Usa o serializer de Produto para exibir os dados do produto aninhado
    produto = ProdutoSerializer(read_only=True)
    
    # Adiciona a propriedade 'nome_produto' do modelo como um campo de apenas leitura
    nome_produto = serializers.ReadOnlyField()
    unidade_medida = serializers.ReadOnlyField()

    class Meta:
        model = Lote
        fields = [
            'id',
            'codigo',
            'produto',
            'nome_produto',
            'unidade_medida',
            'data_semeadura',
            'quantidade',
            'preco_unitario',
            'observacoes',
        ]