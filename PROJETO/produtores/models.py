# produtores/models.py
from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import os
from datetime import date

# Função para validar CPF/CNPJ (básica, você pode usar libs mais robustas)
def validate_cpf_cnpj(value):
    clean_value = ''.join(filter(str.isdigit, value))
    if len(clean_value) not in [11, 14]:
        raise ValidationError(
            _('%(value)s deve ter 11 dígitos para CPF ou 14 para CNPJ.'),
            params={'value': value},
        )

# Função para definir o caminho de upload do certificado digital
def certificado_digital_upload_path(instance, filename):
    base_dir = 'certificados'
    # Se a instância é um ProdutorRural
    if isinstance(instance, ProdutorRural):
        # Garante que 'cpf_cnpj' não seja None antes de tentar limpar
        identificador = ''.join(filter(str.isalnum, instance.cpf_cnpj or ''))
        # Garante um identificador padrão se cpf_cnpj for vazio ou None
        if not identificador:
            identificador = 'produtor_desconhecido'
        return os.path.join(base_dir, 'produtor', identificador, filename)
    # Se a instância é um CertificadoDigitalResponsavel
    elif isinstance(instance, CertificadoDigitalResponsavel):
        # Acessa o cpf do ResponsavelTecnico, com fallback
        identificador_rt = ''.join(filter(str.isalnum, instance.responsavel_tecnico.cpf or ''))
        if not identificador_rt:
            identificador_rt = 'responsavel_desconhecido'
        return os.path.join(base_dir, 'responsavel_tecnico', identificador_rt, filename)
    return os.path.join(base_dir, 'outros', filename) # Fallback

class ProdutorRural(models.Model):
    TIPO_PESSOA_CHOICES = [
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica'),
    ]

    FUNRURAL_RECOLHIMENTO_CHOICES = [
        ('folha_pagamento', 'Sobre a Folha de Pagamento'),
        ('comercializacao_producao', 'Sobre a Comercialização da Produção (2,3%)'),
        ('nao_se_aplica', 'Não se Aplica'),
    ]

    nome_fantasia = models.CharField(
        max_length=255,
        blank=True, null=True,
        verbose_name="Nome Fantasia"
    )
    razao_social = models.CharField(
        max_length=255,
        blank=True, null=True,
        verbose_name="Razão Social"
    )
    tipo_pessoa = models.CharField(
        max_length=2,
        choices=TIPO_PESSOA_CHOICES,
        default='PF',
        verbose_name="Tipo de Pessoa"
    )
    cpf_cnpj = models.CharField(
        max_length=18, # Acomoda 14 dígitos de CNPJ + máscara
        unique=True,
        verbose_name="CPF/CNPJ",
        help_text="Informe o CPF (11 dígitos) ou CNPJ (14 dígitos).",
        # Adiciona o validador no nível do modelo também, para consistência
        validators=[validate_cpf_cnpj]
    )
    rg = models.CharField(
        max_length=20,
        blank=True, null=True,
        verbose_name="RG",
        help_text="Obrigatório para Pessoa Física."
    )
    inscricao_estadual = models.CharField(
        max_length=20,
        blank=True, null=True,
        verbose_name="Inscrição Estadual"
    )
    email_contato = models.EmailField(
        max_length=255,
        blank=True, null=True,
        verbose_name="E-mail de Contato"
    )
    telefone_principal = models.CharField(
        max_length=15, # Ex: (99) 99999-9999
        blank=True, null=True,
        verbose_name="Telefone Principal"
    )
    telefone_secundario = models.CharField(
        max_length=15,
        blank=True, null=True,
        verbose_name="Telefone Secundário"
    )
    cep = models.CharField(
        max_length=9, # Ex: 99999-999
        blank=True, null=True,
        verbose_name="CEP"
    )
    endereco = models.CharField(
        max_length=255,
        blank=True, null=True,
        verbose_name="Endereço"
    )
    numero = models.CharField(
        max_length=10,
        blank=True, null=True,
        verbose_name="Número"
    )
    complemento = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name="Complemento"
    )
    bairro = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name="Bairro"
    )
    cidade = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name="Cidade"
    )
    estado = models.CharField(
        max_length=2,
        blank=True, null=True,
        verbose_name="Estado"
    )
    renasem = models.CharField(
        max_length=50,
        blank=True, null=True,
        verbose_name="RENASEM",
        help_text="Registro Nacional de Sementes e Mudas."
    )
    funrural_recolhimento_tipo = models.CharField(
        max_length=30,
        choices=FUNRURAL_RECOLHIMENTO_CHOICES,
        default='nao_se_aplica',
        verbose_name="Tipo de Recolhimento FUNRURAL"
    )
    certificado_digital_produtor_arquivo = models.FileField(
        upload_to=certificado_digital_upload_path,
        blank=True, null=True,
        verbose_name="Certificado Digital (PF ou PJ)",
        help_text="Certificado digital do produtor (se aplicável)."
    )
    certificado_digital_produtor_senha = models.CharField(
        max_length=255,
        blank=True, null=True,
        verbose_name="Senha do Certificado do Produtor",
        help_text="Senha do arquivo de certificado do produtor."
    )
    certificado_digital_produtor_validade = models.DateField(
        blank=True, null=True,
        verbose_name="Validade do Certificado do Produtor",
        help_text="Data de expiração do certificado do produtor."
    )
    observacoes = models.TextField(
        blank=True, null=True,
        verbose_name="Observações Gerais"
    )
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Produtor Rural"
        verbose_name_plural = "Produtores Rurais"
        ordering = ['nome_fantasia', 'razao_social']

    def __str__(self):
        return self.nome_fantasia or self.razao_social or f"Produtor {self.cpf_cnpj}"

class ResponsavelTecnico(models.Model):
    produtor_rural = models.ForeignKey(
        ProdutorRural,
        on_delete=models.CASCADE,
        related_name='responsaveis_tecnicos',
        verbose_name="Produtor Rural"
    )
    nome = models.CharField(
        max_length=255,
        verbose_name="Nome Completo"
    )
    cpf = models.CharField(
        max_length=14, # Acomoda máscara de CPF
        unique=True, # CPF deve ser único para RTs também
        verbose_name="CPF",
        validators=[validate_cpf_cnpj] # Reutiliza o validador
    )
    registro_profissional = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name="Registro Profissional (Ex: CREA/CAU)"
    )
    telefone = models.CharField(
        max_length=15,
        blank=True, null=True,
        verbose_name="Telefone de Contato"
    )
    email = models.EmailField(
        max_length=255,
        blank=True, null=True,
        verbose_name="E-mail de Contato"
    )
    observacoes = models.TextField(
        blank=True, null=True,
        verbose_name="Observações do Responsável Técnico"
    )
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Responsável Técnico"
        verbose_name_plural = "Responsáveis Técnicos"
        ordering = ['nome']
        # Adicionar uma restrição de unicidade para (produtor_rural, cpf)
        # O CPF já é unique=True, mas se você quisesse um RT com o mesmo CPF
        # em produtores diferentes, isso seria necessário.
        # constraints = [
        #     models.UniqueConstraint(fields=['produtor_rural', 'cpf'], name='unique_rt_per_produtor')
        # ]

    def __str__(self):
        return self.nome

class CertificadoDigitalResponsavel(models.Model):
    responsavel_tecnico = models.ForeignKey(
        ResponsavelTecnico,
        on_delete=models.CASCADE,
        related_name='certificados_digitais',
        verbose_name="Responsável Técnico"
    )
    nome_arquivo = models.CharField(
        max_length=255,
        verbose_name="Nome do Arquivo (Ex: Certificado RT João)",
        blank=True, null=True
    )
    arquivo_pfx = models.FileField(
        upload_to=certificado_digital_upload_path,
        blank=True, null=True,
        verbose_name="Arquivo Certificado (.pfx)",
        help_text="Arquivo de certificado digital do responsável técnico."
    )
    senha_pfx = models.CharField(
        max_length=255,
        blank=True, null=True,
        verbose_name="Senha do Certificado",
        help_text="Senha do arquivo .pfx."
    )
    data_validade = models.DateField(
        blank=True, null=True,
        verbose_name="Data de Validade",
        help_text="Data de expiração do certificado."
    )
    observacoes = models.TextField(
        blank=True, null=True,
        verbose_name="Observações do Certificado"
    )
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")

    class Meta:
        verbose_name = "Certificado Digital do Responsável"
        verbose_name_plural = "Certificados Digitais dos Responsáveis"
        ordering = ['responsavel_tecnico__nome', 'nome_arquivo']

    def __str__(self):
        return self.nome_arquivo or f"Certificado para {self.responsavel_tecnico.nome}"