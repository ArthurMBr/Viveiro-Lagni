# viveiro_lagni/PROJETO/veiculos_maquinas/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Veiculo, Maquina, Manutencao
from .forms import VeiculoForm, MaquinaForm, ManutencaoForm # Criaremos os forms no próximo passo
from rest_framework import viewsets
from .serializers import VeiculoSerializer, MaquinaSerializer, ManutencaoSerializer

def veiculo_list(request):
    veiculos = Veiculo.objects.all()
    context = {
        'veiculos': veiculos,
        'page_title': 'Lista de Veículos',
    }
    return render(request, 'veiculos_maquinas/veiculo_list.html', context)

def maquina_list(request):
    maquinas = Maquina.objects.all()
    context = {
        'maquinas': maquinas,
        'page_title': 'Lista de Máquinas',
    }
    return render(request, 'veiculos_maquinas/maquina_list.html', context)

def manutencao_list(request):
    manutencoes = Manutencao.objects.all()
    context = {
        'manutencoes': manutencoes,
        'page_title': 'Histórico de Manutenções',
    }
    return render(request, 'veiculos_maquinas/manutencao_list.html', context)


# Views para CRUD (Formulários) - Opcional para começar, mas útil
def veiculo_create(request):
    if request.method == 'POST':
        form = VeiculoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('veiculos_maquinas:veiculo_list')
    else:
        form = VeiculoForm()
    return render(request, 'veiculos_maquinas/veiculo_form.html', {'form': form, 'page_title': 'Novo Veículo'})

def veiculo_update(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    if request.method == 'POST':
        form = VeiculoForm(request.POST, instance=veiculo)
        if form.is_valid():
            form.save()
            return redirect('veiculos_maquinas:veiculo_list')
    else:
        form = VeiculoForm(instance=veiculo)
    return render(request, 'veiculos_maquinas/veiculo_form.html', {'form': form, 'page_title': f'Editar Veículo: {veiculo.nome}'})

def veiculo_delete(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    if request.method == 'POST':
        veiculo.delete()
        return redirect('veiculos_maquinas:veiculo_list')
    return render(request, 'veiculos_maquinas/veiculo_confirm_delete.html', {'veiculo': veiculo, 'page_title': f'Excluir Veículo: {veiculo.nome}'})

def maquina_create(request):
    if request.method == 'POST':
        form = MaquinaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('veiculos_maquinas:maquina_list')
    else:
        form = MaquinaForm()
    return render(request, 'veiculos_maquinas/maquina_form.html', {'form': form, 'page_title': 'Nova Máquina'})

def maquina_update(request, pk):
    maquina = get_object_or_404(Maquina, pk=pk)
    if request.method == 'POST':
        form = MaquinaForm(request.POST, instance=maquina)
        if form.is_valid():
            form.save()
            return redirect('veiculos_maquinas:maquina_list')
    else:
        form = MaquinaForm(instance=maquina)
    return render(request, 'veiculos_maquinas/maquina_form.html', {'form': form, 'page_title': f'Editar Máquina: {maquina.nome}'})

def maquina_delete(request, pk):
    maquina = get_object_or_404(Maquina, pk=pk)
    if request.method == 'POST':
        maquina.delete()
        return redirect('veiculos_maquinas:maquina_list')
    return render(request, 'veiculos_maquinas/maquina_confirm_delete.html', {'maquina': maquina, 'page_title': f'Excluir Máquina: {maquina.nome}'})

def manutencao_create(request):
    if request.method == 'POST':
        form = ManutencaoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('veiculos_maquinas:manutencao_list')
    else:
        form = ManutencaoForm()
    return render(request, 'veiculos_maquinas/manutencao_form.html', {'form': form, 'page_title': 'Nova Manutenção'})

def manutencao_update(request, pk):
    manutencao = get_object_or_404(Manutencao, pk=pk)
    if request.method == 'POST':
        form = ManutencaoForm(request.POST, instance=manutencao)
        if form.is_valid():
            form.save()
            return redirect('veiculos_maquinas:manutencao_list')
    else:
        form = ManutencaoForm(instance=manutencao)
    return render(request, 'veiculos_maquinas/manutencao_form.html', {'form': form, 'page_title': f'Editar Manutenção'})

def manutencao_delete(request, pk):
    manutencao = get_object_or_404(Manutencao, pk=pk)
    if request.method == 'POST':
        manutencao.delete()
        return redirect('veiculos_maquinas:manutencao_list')
    return render(request, 'veiculos_maquinas/manutencao_confirm_delete.html', {'manutencao': manutencao, 'page_title': f'Excluir Manutenção'})

def veiculos_maquinas_menu(request):
    """
    Renderiza a página de menu para Veículos, Máquinas e Manutenções.
    """
    context = {
        'page_title': 'Veículos e Máquinas',
    }
    return render(request, 'veiculos_maquinas/veiculos_maquinas_menu.html', context)

# NOVAS VIEWS PARA A API
class VeiculoViewSet(viewsets.ModelViewSet):
    queryset = Veiculo.objects.all().order_by('nome')
    serializer_class = VeiculoSerializer

class MaquinaViewSet(viewsets.ModelViewSet):
    queryset = Maquina.objects.all().order_by('nome')
    serializer_class = MaquinaSerializer

class ManutencaoViewSet(viewsets.ModelViewSet):
    queryset = Manutencao.objects.all().order_by('-data_manutencao')
    serializer_class = ManutencaoSerializer