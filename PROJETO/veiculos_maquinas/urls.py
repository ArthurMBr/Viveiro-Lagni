# viveiro_lagni/PROJETO/veiculos_maquinas/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'veiculos_maquinas'

# Crie um router para a API
router = DefaultRouter()
router.register(r'veiculos', views.VeiculoViewSet)
router.register(r'maquinas', views.MaquinaViewSet)
router.register(r'manutencoes', views.ManutencaoViewSet)

urlpatterns = [

    path('', views.veiculos_maquinas_menu, name='index'), # A página inicial do app agora é o menu
    path('menu/', views.veiculos_maquinas_menu, name='menu'), # URL explícita para o menu
    path('api/', include(router.urls)),
    # URLs para Veículos
    path('', views.veiculo_list, name='index'), # Página inicial do app pode listar veículos
    path('veiculos/', views.veiculo_list, name='veiculo_list'),
    path('veiculos/novo/', views.veiculo_create, name='veiculo_create'),
    path('veiculos/editar/<int:pk>/', views.veiculo_update, name='veiculo_update'),
    path('veiculos/excluir/<int:pk>/', views.veiculo_delete, name='veiculo_delete'),

    # URLs para Máquinas
    path('maquinas/', views.maquina_list, name='maquina_list'),
    path('maquinas/novo/', views.maquina_create, name='maquina_create'),
    path('maquinas/editar/<int:pk>/', views.maquina_update, name='maquina_update'),
    path('maquinas/excluir/<int:pk>/', views.maquina_delete, name='maquina_delete'),

    # URLs para Manutenções
    path('manutencoes/', views.manutencao_list, name='manutencao_list'),
    path('manutencoes/novo/', views.manutencao_create, name='manutencao_create'),
    path('manutencoes/editar/<int:pk>/', views.manutencao_update, name='manutencao_update'),
    path('manutencoes/excluir/<int:pk>/', views.manutencao_delete, name='manutencao_delete'),
]