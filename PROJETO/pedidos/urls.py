# pedidos/urls.py
from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    # Exemplo: Se você for criar views para listagem, criação, edição de pedidos fora do admin
    # path('', views.lista_pedidos, name='lista_pedidos'),
    # path('novo/', views.criar_pedido, name='criar_pedido'),
    # path('<int:pk>/', views.detalhe_pedido, name='detalhe_pedido'),
    # path('<int:pk>/editar/', views.editar_pedido, name='editar_pedido'),
    # path('<int:pk>/excluir/', views.excluir_pedido, name='excluir_pedido'),

    # No momento, manteremos este arquivo para futuras APIs ou views customizadas.
    # A maior parte da interação inicial com pedidos será via Admin ou o futuro Catálogo.
]