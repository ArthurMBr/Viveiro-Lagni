# etiquetas/serializers.py
from rest_framework import serializers
from .models import Etiqueta

class EtiquetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etiqueta
        fields = [
            'id',
            'lote',
            'produto',
            'codigo_lote',
            'variedade_produto',
            'quantidade',
            'nome_cliente',
            'data_criacao',
        ]
        read_only_fields = ['data_criacao'] # Este campo não deve ser alterado pela API