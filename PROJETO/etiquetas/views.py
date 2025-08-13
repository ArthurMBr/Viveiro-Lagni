# etiquetas/views.py
from django.shortcuts import render
from rest_framework import viewsets
from .models import Etiqueta
from .serializers import EtiquetaSerializer

def etiquetas_index(request):
    """
    View para a página inicial do aplicativo Etiquetas,
    exibindo as opções de criação de etiquetas.
    """
    return render(request, 'etiquetas/index.html')

def personalizada_view(request):
    """
    View para a página de criação de etiquetas personalizadas.
    Aqui o usuário poderá digitar textos, selecionar produtos, etc.
    """
    context = {
        'page_title': 'Etiqueta Personalizada',
        # 'form': form, # Descomente quando criar o forms.py
    }
    return render(request, 'etiquetas/personalizada.html', context)

def buscar_lote_existente_view(request):
    """
    Renderiza a página para buscar lotes existentes dentro do app etiquetas.
    Esta página usará JavaScript para buscar dados da API do app 'lotes'.
    """
    return render(request, 'etiquetas/buscar_lote_existente.html', {'page_title': 'Buscar Lote Existente'})

# --- NOVAS VIEWS PARA A API ---
class EtiquetaViewSet(viewsets.ModelViewSet):
    queryset = Etiqueta.objects.all().order_by('-data_criacao')
    serializer_class = EtiquetaSerializer
