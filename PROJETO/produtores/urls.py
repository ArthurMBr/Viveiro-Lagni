from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Define o namespace da aplicação para evitar conflitos de nome
app_name = 'produtores'


# Crie um router para a API
router = DefaultRouter()
router.register(r'produtores', views.ProdutorRuralViewSet)
router.register(r'responsaveis-tecnicos', views.ResponsavelTecnicoViewSet)
router.register(r'certificados-digitais', views.CertificadoDigitalResponsavelViewSet)

urlpatterns = [
    # URL para a página de detalhes do Produtor Rural (NÃO espera PK)
    path('detalhes/', views.detalhes_produtor, name='detalhes_produtor'),

    # URL para gerenciar (cadastrar/editar) o Produtor Rural
    # Permite acesso sem PK (para cadastrar novo) ou com PK (para editar existente)
    path('gerenciar/', views.gerenciar_produtor_rural, name='gerenciar_produtor'),
    path('gerenciar/<int:pk>/', views.gerenciar_produtor_rural, name='gerenciar_produtor_edit'),
    path('api/', include(router.urls)),
]