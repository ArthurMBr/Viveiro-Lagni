from django.db import models
from django.utils import timezone

# Importe os modelos das outras aplicações
# Ajuste o caminho se necessário (ex: 'caixa_pdv.models')
from caixa_pdv.models import Lote, Produto 

class Etiqueta(models.Model):
    """
    Modelo para armazenar as informações de uma etiqueta de produto ou lote.
    """
    # Relação com Lote e Produto (pode ser opcional para etiquetas personalizadas)
    lote = models.ForeignKey(Lote, on_delete=models.SET_NULL, null=True, blank=True)
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True, blank=True)

    # Campos que podem ser personalizados ou preenchidos automaticamente
    codigo_lote = models.CharField(max_length=50, null=True, blank=True, verbose_name="Código do Lote")
    variedade_produto = models.CharField(max_length=100, null=True, blank=True, verbose_name="Variedade do Produto")
    quantidade = models.PositiveIntegerField(null=True, blank=True, verbose_name="Quantidade")
    nome_cliente = models.CharField(max_length=255, null=True, blank=True, verbose_name="Nome do Cliente")

    # Campos de controlo
    data_criacao = models.DateTimeField(default=timezone.now, verbose_name="Data de Criação")

    def save(self, *args, **kwargs):
        """
        Preenche automaticamente os campos de código e variedade se um lote for selecionado.
        """
        if self.lote:
            self.codigo_lote = self.lote.codigo
            if self.lote.produto:
                self.variedade_produto = self.lote.produto.variedade
        super().save(*args, **kwargs)

    def __str__(self):
        if self.codigo_lote:
            return f"Etiqueta para o Lote: {self.codigo_lote}"
        return f"Etiqueta Personalizada criada em {self.data_criacao.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Etiqueta"
        verbose_name_plural = "Etiquetas"
        ordering = ['-data_criacao']