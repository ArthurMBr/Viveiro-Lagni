from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView # Importe TemplateView
from django.conf import settings # <-- Adicione esta linha
from django.conf.urls.static import static # <-- Adicione esta linha

urlpatterns = [
    path('admin/', admin.site.urls),
    path('lotes/', include('lotes.urls')),
    path('produtos/', include('produtos.urls')),
    path('pedidos/', include('pedidos.urls', namespace='pedidos')),  # <-- ADICIONAR ESTA LINHA
    path('produtores/', include('produtores.urls')),
    path('', include('home.urls')), # Inclui as URLs do app 'home'. Isso fará com que 'home/urls.py' seja a raiz do seu site.
    path("", TemplateView.as_view(template_name="tela_inicial.html"), name="home"),
    path('select2/', include('django_select2.urls')),
    path('etiquetas/', include('etiquetas.urls')),
    path('pdv/', include('caixa_pdv.urls')),
    path('veiculos-maquinas/', include('veiculos_maquinas.urls', namespace='veiculos_maquinas')),
    path('catalogo/', include('catalogo.urls', namespace='catalogo')),
    path('cadastros/', include('clientes_fornecedores.urls', namespace='clientes_fornecedores')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Descomente a linha abaixo para servir arquivos de mídia durante o desenvolvimento
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # <--- ESSA LINHA FOI DESCOMENTADA
    

