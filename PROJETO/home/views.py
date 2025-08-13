# home/views.py
from django.shortcuts import render

def tela_inicial(request):
    """
    Renderiza a página inicial do sistema.
    """
    context = {
        'titulo': 'Bem-vindo ao Sistema de Vendas!',
        'descricao': 'Gerencie seus pedidos e estoque de forma eficiente.'
    }
    return render(request, 'home/tela_inicial.html', context)