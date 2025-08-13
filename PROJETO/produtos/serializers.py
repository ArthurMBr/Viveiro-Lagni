# produtos/serializers.py
from rest_framework import serializers
from .models import Produto, NCM, CFOP

class NCMSerializer(serializers.ModelSerializer):
    class Meta:
        model = NCM
        fields = ['id', 'codigo', 'descricao']

class CFOPSerializer(serializers.ModelSerializer):
    class Meta:
        model = CFOP
        fields = ['id', 'codigo', 'descricao']

class ProdutoSerializer(serializers.ModelSerializer):
    # Serializers aninhados para exibir os detalhes completos
    ncm = NCMSerializer(read_only=True)
    cfop = CFOPSerializer(read_only=True)

    class Meta:
        model = Produto
        fields = [
            'id',
            'cod',
            'unidade',
            'qtd_unid',
            'tipo',
            'variedade',
            'especie',
            'cod_especie',
            'cultivar_info',
            'descricao_catalogo',
            'estoque',
            'preco',
            'status',
            'ncm',
            'cfop',
            'imagem',
            'data_cadastro',
            'ultima_atualizacao',
            'valor_total', # O @property 'valor_total' será incluído aqui
        ]
        read_only_fields = ['data_cadastro', 'ultima_atualizacao', 'valor_total', 'estoque']