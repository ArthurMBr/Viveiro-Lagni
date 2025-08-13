# lotes/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "lotes"

router = DefaultRouter()
router.register(r'lotes', views.LoteViewSet)

urlpatterns = [
    path("", views.lote_list, name="lote_list"),
    path("novo/", views.lote_create, name="lote_create"), # <--- ADICIONE ESTA LINHA
    path("editar/<int:pk>/", views.lote_update, name="lote_update"), # <--- ADICIONE ESTA LINHA para edição
    path("excluir/<int:pk>/", views.lote_delete, name="lote_delete"), # <--- ADICIONE ESTA LINHA para exclusão
    path("etiqueta/<int:pk>/", views.gerar_etiqueta_lote, name="gerar_etiqueta_lote"),
    path('api/listar/', views.listar_lotes_api, name='listar_lotes_api'), # Esta é a API para o frontend
    path('api/', include(router.urls)),
]