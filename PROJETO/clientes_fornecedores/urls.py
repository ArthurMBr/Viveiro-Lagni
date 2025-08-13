from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'clientes_fornecedores'

# Crie um router para a API
router = DefaultRouter()
router.register(r'clientes', views.ClienteViewSet)
router.register(r'fornecedores', views.FornecedorViewSet)

urlpatterns = [
    # Nova URL para a página inicial do app
    path('', views.cadastros_home, name='cadastros_home'),

    # URLs para Clientes
    path('clientes/', views.ClienteListView.as_view(), name='cliente_list'),
    path('clientes/novo/', views.ClienteCreateView.as_view(), name='cliente_create'),
    path('clientes/<int:pk>/', views.ClienteDetailView.as_view(), name='cliente_detail'),
    path('clientes/<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='cliente_update'),
    path('clientes/<int:pk>/excluir/', views.ClienteDeleteView.as_view(), name='cliente_delete'),

    # URLs para Fornecedores
    path('fornecedores/', views.FornecedorListView.as_view(), name='fornecedor_list'),
    path('fornecedores/novo/', views.FornecedorCreateView.as_view(), name='fornecedor_create'),
    path('fornecedores/<int:pk>/', views.FornecedorDetailView.as_view(), name='fornecedor_detail'),
    path('fornecedores/<int:pk>/editar/', views.FornecedorUpdateView.as_view(), name='fornecedor_update'),
    path('fornecedores/<int:pk>/excluir/', views.FornecedorDeleteView.as_view(), name='fornecedor_delete'),
    path('api/consulta-cnpj/', views.consulta_cnpj_api, name='consulta_cnpj_api'),

    path('api/', include(router.urls)),
]