# catalogo/urls.py

from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.lista_produtos, name='lista_produtos'),
    path('carrinho/', views.carrinho_detalhe, name='carrinho_detalhe'),
    path('carrinho/adicionar/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/remover/', views.remover_do_carrinho, name='remover_do_carrinho'),
    path('carrinho/atualizar_quantidade/', views.atualizar_quantidade_carrinho, name='atualizar_quantidade_carrinho'),
    path('carrinho/obter_conteudo/', views.obter_conteudo_carrinho, name='obter_conteudo_carrinho'),
    path('carrinho/contagem-itens/', views.get_cart_item_count, name='get_cart_item_count'),
    path('finalizar-compra/', views.finalizar_compra, name='finalizar_compra'),
]