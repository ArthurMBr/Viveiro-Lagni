# caixa_pdv/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'caixa_pdv'

# Crie um router para a API
router = DefaultRouter()
router.register(r'vendas', views.VendaViewSet)
router.register(r'itens', views.ItemVendaViewSet)
router.register(r'caixa', views.MovimentoCaixaViewSet)
# Você pode adicionar viewsets de outras apps aqui se precisar
# router.register(r'lotes', views.LoteViewSet

urlpatterns = [
    path('', views.pdv_view, name='pdv'),
    path('api/search-lotes/', views.search_lotes_api, name='search_lotes_api'), # <--- NOVA URL DA API
    path('api/finalizar-venda/', views.finalizar_venda_api, name='finalizar_venda_api'),
    path('historico/', views.historico_vendas_view, name='historico_vendas'),
    path('api/search-vendas/', views.search_vendas_api, name='search_vendas_api'),
    path('api/delete-venda/<int:venda_id>/', views.delete_venda_api, name='delete_venda_api'),
    path('termo-de-conformidade/<int:venda_id>/', views.gerar_termo_conformidade_pdf, name='termo_conformidade_pdf'),
    path('caixa/movimento/', views.caixa_movimento, name='caixa_movimento'),
    path('api/', include(router.urls)),
]