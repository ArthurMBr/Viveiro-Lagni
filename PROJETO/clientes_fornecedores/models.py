# clientes_fornecedores/models.py

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify # NOVO: Importação para criar slugs seguros
from django.db import transaction
import re

# Função de validação de CPF/CNPJ
def validate_cpf_cnpj(value):
    clean_value = ''.join(filter(str.isdigit, value))
    if not clean_value:
        raise ValidationError(_("CPF/CNPJ não pode ser vazio."))
    if len(clean_value) not in [11, 14]:
        raise ValidationError(_("CPF deve ter 11 dígitos ou CNPJ 14 dígitos."))

    # Validação simples de dígitos repetidos
    if len(set(clean_value)) == 1:
        raise ValidationError(_("CPF/CNPJ inválido: todos os dígitos são iguais."))

    return clean_value

class Cliente(models.Model):
    TIPO_CHOICES = (
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica'),
    )
    
    tipo_cliente = models.CharField(
        max_length=2,
        choices=TIPO_CHOICES,
        default='PF',
        verbose_name="Tipo de Cliente"
    )
    nome_completo = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Nome Completo"
    )
    razao_social = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Razão Social"
    )
    nome_fantasia = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Nome Fantasia"
    )
    cpf_cnpj = models.CharField(
        max_length=18, # Ex: 999.999.999-99 ou 99.999.999/9999-99
        unique=True,
        validators=[validate_cpf_cnpj],
        verbose_name="CPF/CNPJ"
    )
    telefone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Telefone"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email"
    )
    endereco = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Endereço"
    )
    cidade = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Cidade"
    )
    estado = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        verbose_name="Estado"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    inscricao_estadual = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Inscrição Estadual"
    )
    
    # NOVO CAMPO: O código único gerado automaticamente
    codigo_unico = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Código Único"
    )

    def __str__(self):
        if self.tipo_cliente == 'PF':
            return self.nome_completo or f"Cliente #{self.id}"
        else:
            return self.razao_social or f"Cliente #{self.id}"

    def _gerar_codigo_unico(self):
        """
        Gera um código único com base na Razão Social, Cidade e CNPJ.
        """
        # Extrai os dados relevantes
        razao = self.razao_social if self.razao_social else ''
        cidade = self.cidade if self.cidade else ''
        
        # Remove caracteres não numéricos do CPF/CNPJ para pegar os 2 primeiros dígitos
        cpf_cnpj_limpo = ''.join(filter(str.isdigit, self.cpf_cnpj or ''))
        cpf_cnpj_prefixo = cpf_cnpj_limpo[:2] if cpf_cnpj_limpo else ''

        # Junta as primeiras 2 letras de cada palavra da razão social
        letras_razao = "".join(word[:2] for word in razao.split() if word).upper()
        # Junta as primeiras 3 letras da cidade
        letras_cidade = cidade[:3].upper()

        # Constrói o código base
        codigo_base = f"{letras_razao}{letras_cidade}{cpf_cnpj_prefixo}"
        
        # Garante que o código é slug (sem caracteres especiais, espaços, etc.)
        return slugify(codigo_base)

    def save(self, *args, **kwargs):
        # Gera o código apenas se ele ainda não existir e se for um novo objeto
        if not self.codigo_unico:
            codigo_gerado = self._gerar_codigo_unico()

            # Garante a unicidade do código, adicionando um sufixo se necessário
            tentativa = 0
            codigo_final = codigo_gerado
            while Cliente.objects.filter(codigo_unico=codigo_final).exclude(pk=self.pk).exists():
                tentativa += 1
                codigo_final = f"{codigo_gerado}-{tentativa}"
            self.codigo_unico = codigo_final

        super().save(*args, **kwargs)


class Fornecedor(models.Model):
    nome_empresa = models.CharField(
        max_length=200,
        verbose_name="Nome da Empresa"
    )
    nome_contato = models.CharField(
        max_length=100,
        verbose_name="Nome do Contato"
    )
    cpf_cnpj = models.CharField(
        max_length=18,
        unique=True,
        validators=[validate_cpf_cnpj],
        verbose_name="CNPJ"
    )
    telefone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Telefone"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email"
    )
    endereco = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Endereço"
    )
    cidade = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Cidade"
    )
    estado = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        verbose_name="Estado"
    )
    produtos_fornecidos = models.ManyToManyField(
        'produtos.Produto',
        related_name='fornecedores',
        blank=True,
        verbose_name="Produtos Fornecidos"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )

    def __str__(self):
        return self.nome_empresa or f"Fornecedor #{self.id}"