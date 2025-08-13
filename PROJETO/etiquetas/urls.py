# etiquetas/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'etiquetas' # Define o namespace da sua aplicação

# Crie um router para a API
router = DefaultRouter()
router.register(r'etiquetas', views.EtiquetaViewSet)

urlpatterns = [
    path('', views.etiquetas_index, name='index'), # Rota para a página principal das etiquetas
    path('personalizada/', views.personalizada_view, name='personalizada'),
    path('buscar_lote_existente/', views.buscar_lote_existente_view, name='buscar_lote_existente'),
    path('api/', include(router.urls)),
    # path('novo-lote/', views.novo_lote_view, name='novo_lote'),
    # path('lote-existente/', views.lote_existente_view, name='lote_existente'),
    # path('personalizada/', views.personalizada_view, name='personalizada'),
]