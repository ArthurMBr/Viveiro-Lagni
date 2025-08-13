# viveiro_lagni/PROJETO/veiculos_maquinas/models.py

from django.db import models
from django.utils import timezone

class Veiculo(models.Model):
    TIPO_COMBUSTIVEL_CHOICES = [
        ('GASOLINA', 'Gasolina'),
        ('ETANOL', 'Etanol'),
        ('DIESEL', 'Diesel'),
        ('FLEX', 'Flex'),
        ('ELETRICO', 'Elétrico'),
        ('OUTRO', 'Outro'),
    ]

    nome = models.CharField(max_length=100, verbose_name="Nome do Veículo")
    placa = models.CharField(max_length=10, unique=True, blank=True, null=True, verbose_name="Placa")
    modelo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Modelo")
    ano_fabricacao = models.PositiveIntegerField(blank=True, null=True, verbose_name="Ano de Fabricação")
    tipo_combustivel = models.CharField(
        max_length=20,
        choices=TIPO_COMBUSTIVEL_CHOICES,
        default='OUTRO',
        verbose_name="Tipo de Combustível"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_cadastro = models.DateTimeField(default=timezone.now, verbose_name="Data de Cadastro")

    class Meta:
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.placa if self.placa else 'N/A'})"

class Maquina(models.Model):
    TIPO_MAQUINA_CHOICES = [
        ('TRATOR', 'Trator'),
        ('ROÇADEIRA', 'Roçadeira'),
        ('PULVERIZADOR', 'Pulverizador'),
        ('GERADOR', 'Gerador'),
        ('CULTIVADOR', 'Cultivador'),
        ('OUTRO', 'Outro'),
    ]

    nome = models.CharField(max_length=100, verbose_name="Nome da Máquina")
    tipo = models.CharField(
        max_length=50,
        choices=TIPO_MAQUINA_CHOICES,
        default='OUTRO',
        verbose_name="Tipo de Máquina"
    )
    identificacao = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="Identificação/Série")
    ano_fabricacao = models.PositiveIntegerField(blank=True, null=True, verbose_name="Ano de Fabricação")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_cadastro = models.DateTimeField(default=timezone.now, verbose_name="Data de Cadastro")

    class Meta:
        verbose_name = "Máquina"
        verbose_name_plural = "Máquinas"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.tipo})"

class Manutencao(models.Model):
    TIPO_MANUTENCAO_CHOICES = [
        ('PREVENTIVA', 'Preventiva'),
        ('CORRETIVA', 'Corretiva'),
        ('LUBRIFICACAO', 'Lubrificação'),
        ('OUTRO', 'Outro'),
    ]

    veiculo = models.ForeignKey(
        Veiculo,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='manutencoes',
        verbose_name="Veículo"
    )
    maquina = models.ForeignKey(
        Maquina,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='manutencoes',
        verbose_name="Máquina"
    )
    data_manutencao = models.DateField(default=timezone.now, verbose_name="Data da Manutenção")
    tipo_manutencao = models.CharField(
        max_length=50,
        choices=TIPO_MANUTENCAO_CHOICES,
        default='PREVENTIVA',
        verbose_name="Tipo de Manutenção"
    )
    descricao = models.TextField(verbose_name="Descrição da Manutenção")
    custo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Custo (R$)")
    realizada_por = models.CharField(max_length=100, blank=True, null=True, verbose_name="Realizada por")

    class Meta:
        verbose_name = "Manutenção"
        verbose_name_plural = "Manutenções"
        ordering = ['-data_manutencao'] # Mais recente primeiro

    def __str__(self):
        if self.veiculo:
            return f"Manutenção de {self.veiculo.nome} em {self.data_manutencao}"
        elif self.maquina:
            return f"Manutenção de {self.maquina.nome} em {self.data_manutencao}"
        else:
            return f"Manutenção genérica em {self.data_manutencao}"