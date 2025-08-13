# produtos/models.py
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.db.models import Q
from decimal import Decimal
from django.utils import timezone # Certifique-se de que esta importação está presente

class Produto(models.Model):
    # Choices para Unidade de Medida
    UNIDADE_CHOICES = [
        ('BDJ', 'Bandeja'),
        ('VASO', 'Vaso'),
        ('CUIA', 'Cuia'),
        ('MUDAS', 'Mudas'),
        ('KG', 'Quilograma'),
        ('G', 'Grama'),
        ('PC', 'Pacote'),
        ('UN', 'Unidade'),
    ]

    # Choices para Quantidade por Unidade
    QTD_UNID_CHOICES = [
        ('1UN', '1 Unidade'),
        ('15UN', '15 Unidades'),
        ('128UN', '128 Unidades'),
        ('30UN', '30 Unidades'),
    ]

    # Choices para Tipo de Produto
    TIPO_CHOICES = [
        ('Tempero', 'Tempero'),
        ('Hibridos', 'Híbridos'),
        ('Cacto', 'Cacto'),
        ('Flores', 'Flores'),
        ('Frutas', 'Frutas'),
        ('Plantas Ornamentais', 'Plantas Ornamentais'),
        ('Arvores Frutiferas', 'Árvores Frutíferas'),
        ('Arvores Nativas', 'Árvores Nativas'),
        ('Hortalicas', 'Hortaliças'),
        ('Suculentas', 'Suculentas'),
        ('Vasos', 'Vasos'),
        ('Substratos', 'Substratos'),
        ('Adubos', 'Adubos'),
        ('Ferramentas', 'Ferramentas'),
        ('Outros', 'Outros'),
    ]

    # Choices para Status do Produto
    STATUS_CHOICES = [
        ('Ativo', 'Ativo'),
        ('Inativo', 'Inativo'),
        ('Com Estoque', 'Com Estoque'),
        ('Sem Estoque', 'Sem Estoque'),
    ]

    cod = models.CharField(max_length=50, unique=True, verbose_name="Código do Produto")
    unidade = models.CharField(max_length=10, choices=UNIDADE_CHOICES, verbose_name="Unidade de Medida")
    qtd_unid = models.CharField(max_length=10, choices=QTD_UNID_CHOICES, verbose_name="Quantidade por Unidade")
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, verbose_name="Tipo de Produto")
    variedade = models.CharField(max_length=100, verbose_name="Variedade")
    especie = models.CharField(max_length=100, verbose_name="Espécie", blank=True, null=True)
    cod_especie = models.CharField(max_length=50, verbose_name="Código da Espécie", blank=True, null=True)
    cultivar_info = models.TextField(verbose_name="Informações sobre Cultivar", blank=True, null=True)
    descricao_catalogo = models.TextField(verbose_name="Descrição Detalhada para Catálogo", blank=True, null=True, help_text="Descrição mais completa do produto para exibição no catálogo online.")
    estoque = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Estoque")
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ativo', verbose_name="Status")
    ncm = models.ForeignKey('NCM', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="NCM")
    cfop = models.ForeignKey('CFOP', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="CFOP")
    imagem = models.ImageField(upload_to='produtos_imagens/', blank=True, null=True, verbose_name="Imagem do Produto")
    
    # >>> MODIFICAÇÕES TEMPORÁRIAS PARA A MIGRAÇÃO <<<
    data_cadastro = models.DateTimeField(default=timezone.now, verbose_name="Data de Cadastro", null=True, blank=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização", null=True, blank=True)
    # >>> FIM DAS MODIFICAÇÕES TEMPORÁRIAS <<<

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['variedade']

    def __str__(self):
        return f"{self.variedade}"

    def save(self, *args, **kwargs):
        update_fields_arg = kwargs.pop('update_fields', None)

        if self.estoque <= 0:
            self.status = 'Sem Estoque'
        elif self.estoque > 0:
            self.status = 'Com Estoque'
        
        if update_fields_arg is not None:
            super().save(*args, update_fields=update_fields_arg, **kwargs)
        else:
            super().save(*args, **kwargs)

    @property
    def valor_total(self):
        return self.estoque * self.preco

class NCM(models.Model):
    codigo = models.CharField(max_length=8, unique=True, verbose_name="Código NCM")
    descricao = models.CharField(max_length=255, verbose_name="Descrição")

    class Meta:
        verbose_name = "NCM"
        verbose_name_plural = "NCMs"
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"

class CFOP(models.Model):
    codigo = models.CharField(max_length=4, unique=True, verbose_name="Código CFOP")
    descricao = models.CharField(max_length=255, verbose_name="Descrição")

    class Meta:
        verbose_name = "CFOP"
        verbose_name_plural = "CFOPs"
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"

@receiver(post_save, sender=NCM)
def NCM_post_save(sender, instance, created, **kwargs):
    if created:
        print(f"NCM '{instance.codigo}' criado.")

@receiver(pre_delete, sender=NCM)
def NCM_pre_delete(sender, instance, **kwargs):
    print(f"NCM '{instance.codigo}' será excluído.")

@receiver(post_save, sender=CFOP)
def CFOP_post_save(sender, instance, created, **kwargs):
    if created:
        print(f"CFOP '{instance.codigo}' criado.")

@receiver(pre_delete, sender=CFOP)
def CFOP_pre_delete(sender, instance, **kwargs):
    print(f"CFOP '{instance.codigo}' será excluído.")