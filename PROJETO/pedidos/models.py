# pedidos/models.py
from django.db import models
from produtos.models import Produto
from lotes.models import Lote
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from decimal import Decimal
from django.db.models import Sum

# O import do modelo 'Cliente' foi removido.

class Pedido(models.Model):
    STATUS_CHOICES = (
        ('PENDENTE', 'Pendente'),
        ('EM_PROCESSAMENTO', 'Em Processamento'),
        ('ENVIADO', 'Enviado'),
        ('ENTREGUE', 'Entregue'),
        ('CANCELADO', 'Cancelado'),
    )

    data_pedido = models.DateTimeField(auto_now_add=True, verbose_name="Data do Pedido")
    previsao_entrega = models.DateField(blank=True, null=True, verbose_name="Previsão de Entrega")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE', verbose_name="Status")
    total_pedido = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total do Pedido")
    valor_frete = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Valor do Frete")
    desconto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Desconto Total")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    def __str__(self):
        # A referência ao cliente foi removida para evitar erros
        return f"Pedido #{self.id} - {self.status}"

    def calcular_total(self):
        total_itens_agg = self.itens_pedido.aggregate(total=Sum('subtotal'))
        total_itens = total_itens_agg['total'] or Decimal('0.00')
        
        total_final = (total_itens + self.valor_frete) - self.desconto_total
        self.total_pedido = total_final
        self.save()

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens_pedido', verbose_name="Pedido")
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name='itens_pedido', verbose_name="Produto")
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name='itens_pedido', verbose_name="Lote")
    quantidade = models.PositiveIntegerField(verbose_name="Quantidade")
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")

    def save(self, *args, **kwargs):
        self.subtotal = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantidade}x {self.produto.variedade} ({self.lote.numero_lote})"

@receiver(post_save, sender=ItemPedido)
def update_pedido_on_item_save(sender, instance, created, **kwargs):
    if created:
        instance.pedido.calcular_total()

@receiver(post_delete, sender=ItemPedido)
def update_pedido_on_item_delete(sender, instance, **kwargs):
    instance.pedido.calcular_total()