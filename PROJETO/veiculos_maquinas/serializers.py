# veiculos_maquinas/serializers.py
from rest_framework import serializers
from .models import Veiculo, Maquina, Manutencao

class VeiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veiculo
        fields = [
            'id',
            'nome',
            'placa',
            'modelo',
            'ano_fabricacao',
            'tipo_combustivel',
            'observacoes',
            'data_cadastro',
        ]
        read_only_fields = ['data_cadastro']

class MaquinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maquina
        fields = [
            'id',
            'nome',
            'tipo',
            'identificacao',
            'ano_fabricacao',
            'observacoes',
            'data_cadastro',
        ]
        read_only_fields = ['data_cadastro']

class ManutencaoSerializer(serializers.ModelSerializer):
    # Serializers aninhados para exibir os detalhes completos do veículo/máquina
    veiculo = VeiculoSerializer(read_only=True)
    maquina = MaquinaSerializer(read_only=True)
    
    class Meta:
        model = Manutencao
        fields = [
            'id',
            'veiculo',
            'maquina',
            'data_manutencao',
            'tipo_manutencao',
            'descricao',
            'custo',
            'realizada_por',
        ]