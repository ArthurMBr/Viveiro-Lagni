# clientes_fornecedores/serializers.py
from rest_framework import serializers
from .models import Cliente, Fornecedor

# Se a aplicação 'produtos' tiver um serializer, pode importá-lo
# from produtos.serializers import ProdutoSerializer

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = [
            'id',
            'tipo_cliente',
            'nome_completo',
            'razao_social',
            'nome_fantasia',
            'cpf_cnpj',
            'telefone',
            'email',
            'endereco',
            'cidade',
            'estado',
            'observacoes',
            'data_cadastro',
            'inscricao_estadual',
            'codigo_unico',
        ]

class FornecedorSerializer(serializers.ModelSerializer):
    # Por padrão, ManyToManyField é representado por uma lista de IDs.
    # Se você quiser que o serializer de produtos seja exibido,
    # você precisaria de um 'ProdutoSerializer' e faria:
    # produtos_fornecidos = ProdutoSerializer(many=True, read_only=True)
    class Meta:
        model = Fornecedor
        fields = [
            'id',
            'nome_empresa',
            'nome_contato',
            'cpf_cnpj',
            'telefone',
            'email',
            'endereco',
            'cidade',
            'estado',
            'produtos_fornecidos', # Exibirá a lista de IDs dos produtos
            'observacoes',
        ]