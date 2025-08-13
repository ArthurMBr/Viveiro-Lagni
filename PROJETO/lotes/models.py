# lotes/models.py

from django.db import models
from django.utils import timezone
from produtos.models import Produto
import random
from decimal import Decimal

class Lote(models.Model):

    # Seu campo 'codigo' existente (para identificação interna, gerado automaticamente)

    codigo = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name="Código de Identificação Interna do Lote",
        help_text="Gerado automaticamente: Código do Produto + Data de Semeadura (DDMMYY)."
    )

    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name="lotes",
        verbose_name="Produto",
        help_text="Produto ao qual este lote pertence."
    )
    data_semeadura = models.DateField(
        verbose_name="Data de Semeadura"
    )
    
    quantidade = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantidade em Unidades",
        help_text="Quantidade disponível neste lote (unidades)."
    )
    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        verbose_name="Preço Unitário",
        help_text="Copiado do preço do Produto ao salvar."
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações do Lote",
        help_text="Informações adicionais sobre este lote."
    )

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"
        ordering = ['-data_semeadura', 'codigo']

    def __str__(self):
        produto_display_name = "Produto Desconhecido"
        if self.produto:
            if self.produto.variedade:
                produto_display_name = self.produto.variedade
            else:
                # Se 'variedade' estiver vazia, usa o valor de exibição de 'tipo'
                produto_display_name = self.produto.get_tipo_display() 
        
        return f"{self.codigo} - {produto_display_name} ({self.quantidade} unids.)"

    def save(self, *args, **kwargs):
        old_qty = 0
        if self.pk:
            try:
                old_instance = Lote.objects.get(pk=self.pk)
                old_qty = old_instance.quantidade
            except Lote.DoesNotExist:
                pass

        # Geração do 'codigo' interno do lote (Código do Produto + Data de Semeadura)
        if not self.codigo:
            if self.produto and self.data_semeadura:
                produto_identifier = getattr(self.produto, 'cod', None) or getattr(self.produto, 'codigo', None)
                if produto_identifier:
                    self.codigo = f"{produto_identifier}{self.data_semeadura.strftime('%d%m%y')}"
                else:
                    self.codigo = f"ERRO_PROD_{timezone.now().strftime('%d%m%y%H%M%S')}-{random.randint(1000, 9999)}"
            else:
                self.codigo = f"ERRO_LOTE_{timezone.now().strftime('%d%m%y%H%M%S')}-{random.randint(1000, 9999)}"

        # Geração do 'numero_lote' (código de barras) se ele não foi definido (para novas instâncias)

        # Copia o preço do Produto para o Lote
        if self.produto and (not self.pk or self.produto_id != (Lote.objects.get(pk=self.pk).produto_id if self.pk else None)):
            self.preco_unitario = getattr(self.produto, 'preco', None) or getattr(self.produto, 'valor_unitario', Decimal('0.00'))
            if self.preco_unitario is None:
                self.preco_unitario = Decimal('0.00')

        super().save(*args, **kwargs)

        # Atualiza o estoque no Produto conforme a diferença de quantidade do lote
        if self.produto:
            diff = self.quantidade - old_qty
            if diff != 0:
                produto = self.produto
                produto.refresh_from_db()
                if hasattr(produto, 'estoque'):
                    produto.estoque = (produto.estoque or Decimal('0.00')) + Decimal(str(diff))
                    produto.save(update_fields=['estoque'])
                else:
                    print(f"Aviso: O modelo Produto para {produto.pk} não possui o campo 'estoque'.")

    def delete(self, *args, **kwargs):
        produto = self.produto
        if produto:
            produto.refresh_from_db()
            if hasattr(produto, 'estoque'):
                produto.estoque = (produto.estoque or Decimal('0.00')) - Decimal(str(self.quantidade))
                produto.save(update_fields=['estoque'])
            else:
                print(f"Aviso: O modelo Produto para {produto.pk} não possui o campo 'estoque' ao deletar.")
        super().delete(*args, **kwargs)

    @property
    def quantidade_disponivel(self):
        """Retorna a quantidade disponível deste lote."""
        # Aqui, estamos simplesmente retornando o valor do campo 'quantidade'
        return self.quantidade

    @property
    def unidade_medida(self):
        """Retorna a unidade de medida do produto associado ao lote."""
        # Assume que o modelo Produto tem um campo 'unidade'
        return self.produto.unidade if self.produto else 'UN'

    # ESTA É A PROPRIEDADE QUE ESTAVA FALTANDO!
    @property
    def nome_produto(self):
        """
        Retorna o nome de exibição do produto associado ao lote.
        Prioriza a 'variedade', caso contrário, usa o 'tipo' de exibição.
        """
        if self.produto:
            if self.produto.variedade:
                return self.produto.variedade
            return self.produto.get_tipo_display() # Fallback para o tipo
        return 'Produto Desconhecido'