# caixa_pdv/models.py
from django.db import models
from produtos.models import Produto
from lotes.models import Lote
from decimal import Decimal
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import models
from django.utils import timezone

class Venda(models.Model):
    STATUS_CHOICES = [
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]
    data_venda = models.DateTimeField(auto_now_add=True, verbose_name="Data da Venda")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='finalizada', verbose_name="Status")
    total_venda = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total da Venda")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    def calcular_total(self):
        total_itens_agg = self.itens.aggregate(total=Sum('subtotal'))
        total_itens = total_itens_agg['total'] or Decimal('0.00')
        self.total_venda = total_itens
        self.save()

    def __str__(self):
        return f"Venda #{self.id} - {self.data_venda.strftime('%d/%m/%Y %H:%M')}"

class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens', verbose_name="Venda")
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name='itens_venda', verbose_name="Produto")
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name='itens_venda', verbose_name="Lote")
    quantidade = models.PositiveIntegerField(verbose_name="Quantidade")
    preco_unitario_vendido = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário Vendido")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")

    def save(self, *args, **kwargs):
        self.subtotal = self.quantidade * self.preco_unitario_vendido
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantidade}x {self.produto.variedade} ({self.lote.codigo})"

@receiver(post_save, sender=ItemVenda)
def update_venda_on_item_save(sender, instance, created, **kwargs):
    if created:
        instance.venda.calcular_total()

@receiver(post_delete, sender=ItemVenda)
def update_venda_on_item_delete(sender, instance, **kwargs):
    instance.venda.calcular_total()

class MovimentoCaixa(models.Model):
    TIPO_MOVIMENTO_CHOICES = [
        ('entrada', 'Entrada'),
        ('retirada', 'Retirada'),
    ]
    
    data_hora = models.DateTimeField(default=timezone.now)
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMENTO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - R$ {self.valor} em {self.data_hora.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Movimento de Caixa"
        verbose_name_plural = "Movimentos de Caixa"
        ordering = ['-data_hora']