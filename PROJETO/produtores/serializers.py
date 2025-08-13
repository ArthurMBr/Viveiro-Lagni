# produtores/serializers.py
from rest_framework import serializers
from .models import ProdutorRural, ResponsavelTecnico, CertificadoDigitalResponsavel

class CertificadoDigitalResponsavelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificadoDigitalResponsavel
        fields = [
            'id',
            'responsavel_tecnico',
            'nome_arquivo',
            'arquivo_pfx',
            'senha_pfx',
            'data_validade',
            'observacoes',
            'data_cadastro',
        ]
        read_only_fields = ['data_cadastro']

class ResponsavelTecnicoSerializer(serializers.ModelSerializer):
    # Exibe a lista de certificados digitais do responsável técnico
    certificados_digitais = CertificadoDigitalResponsavelSerializer(many=True, read_only=True)
    
    class Meta:
        model = ResponsavelTecnico
        fields = [
            'id',
            'produtor_rural',
            'nome',
            'cpf',
            'registro_profissional',
            'telefone',
            'email',
            'observacoes',
            'data_cadastro',
            'data_atualizacao',
            'certificados_digitais',
        ]
        read_only_fields = ['data_cadastro', 'data_atualizacao']

class ProdutorRuralSerializer(serializers.ModelSerializer):
    # Exibe a lista de responsáveis técnicos do produtor
    responsaveis_tecnicos = ResponsavelTecnicoSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProdutorRural
        fields = [
            'id',
            'nome_fantasia',
            'razao_social',
            'tipo_pessoa',
            'cpf_cnpj',
            'rg',
            'inscricao_estadual',
            'email_contato',
            'telefone_principal',
            'telefone_secundario',
            'cep',
            'endereco',
            'numero',
            'complemento',
            'bairro',
            'cidade',
            'estado',
            'renasem',
            'funrural_recolhimento_tipo',
            'certificado_digital_produtor_arquivo',
            'certificado_digital_produtor_senha',
            'certificado_digital_produtor_validade',
            'observacoes',
            'data_cadastro',
            'data_atualizacao',
            'responsaveis_tecnicos',
        ]
        read_only_fields = ['data_cadastro', 'data_atualizacao']