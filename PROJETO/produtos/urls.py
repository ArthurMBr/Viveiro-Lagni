# produtos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'produtos' # Define o namespace da aplicação

# Crie um router para a API
router = DefaultRouter()
router.register(r'produtos', views.ProdutoViewSet)
router.register(r'ncms', views.NCMViewSet)
router.register(r'cfops', views.CFOPViewSet)

urlpatterns = [
    # URLs para as operações CRUD de Produto
    # Usando .as_view() para views baseadas em classe
    path('', views.ProdutoListView.as_view(), name='list'),
    path('cadastrar/', views.ProdutoCreateView.as_view(), name='create'),
    path('editar/<int:pk>/', views.ProdutoUpdateView.as_view(), name='update'),
    path('excluir/<int:pk>/', views.ProdutoDeleteView.as_view(), name='delete'),
    path('<int:pk>/', views.ProdutoDetailView.as_view(), name='detail'),
    path('api/', include(router.urls)),

    # REINTRODUZINDO E CORRIGINDO AS URLs PARA AS APIs de busca do Select2
    # Agora apontando para as suas FUNÇÕES de view (sem .as_view())
    path(
        'api/ncm_search/',
        views.ncm_search_api, # Aponta diretamente para a função
        name='ncm_search_api'
    ),
    path(
        'api/cfop_search/',
        views.cfop_search_api, # Aponta diretamente para a função
        name='cfop_search_api'
    ),
]