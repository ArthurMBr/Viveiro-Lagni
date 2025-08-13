# home/urls.py
from django.urls import path
from . import views

app_name = 'home' # Opcional, mas boa prática para namespace

urlpatterns = [
    path('', views.tela_inicial, name='inicio'), # URL vazia para ser a raiz do app
]