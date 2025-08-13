import requests
from django.http import JsonResponse
import re
from django.views.decorators.http import require_GET
from django.shortcuts import render
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Cliente, Fornecedor
from .forms import ClienteForm
from .forms import ClienteForm, FornecedorForm
from rest_framework import viewsets
from .serializers import ClienteSerializer, FornecedorSerializer

def cadastros_home(request):
    return render(request, 'clientes_fornecedores/cadastros_home.html')

@require_GET
def consulta_cnpj_api(request):
    """
    Consulta uma API pública de CNPJ para obter dados da empresa.
    """
    cnpj = request.GET.get('cnpj', '')
    if not cnpj or len(cnpj) != 14:
        return JsonResponse({'error': 'CNPJ inválido'}, status=400)

    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status() # Lança um erro para status 4xx/5xx
        data = response.json()
        
        if data['status'] == 'OK':
            # Mapeia os dados da API para o formato do seu modelo Cliente
            endereco_completo = [
                data.get('logradouro', ''),
                data.get('numero', ''),
                data.get('complemento', ''),
                data.get('bairro', '')
            ]
            endereco_completo = ', '.join(filter(None, endereco_completo))
            
            response_data = {
                'razao_social': data.get('nome', '').strip(),
                'nome_fantasia': data.get('fantasia', '').strip(),
                'endereco': endereco_completo,
                'telefone': data.get('telefone', '').strip(),
                'email': data.get('email', '').strip(),
                'cidade': data.get('municipio', '').strip(),
                'estado': data.get('uf', '').strip(),
                'cep': data.get('cep', '').replace('.', '').replace('-', '').strip(),
                'inscricao_estadual': data.get('inscricao_estadual', '').strip()
            }
            return JsonResponse(response_data)
        else:
            return JsonResponse({'error': data.get('message', 'CNPJ não encontrado ou inválido.')}, status=404)
    
    except requests.exceptions.Timeout:
        return JsonResponse({'error': "Tempo limite excedido ao consultar CNPJ."}, status=504)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f"Erro na requisição à API do CNPJ: {e}"}, status=500)
    except ValueError:
        return JsonResponse({'error': "Resposta inválida da API do CNPJ."}, status=500)

# --- Views para Clientes ---

class ClienteListView(ListView):
    model = Cliente
    template_name = 'clientes_fornecedores/cliente_list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nome_completo__icontains=query) |
                Q(razao_social__icontains=query) |
                Q(cpf_cnpj__icontains=query)
            )
        return queryset

class ClienteDetailView(DetailView):
    model = Cliente
    template_name = 'clientes_fornecedores/cliente_detail.html'

# Vista base para listar todos os clientes
class ClienteListView(ListView):
    model = Cliente
    template_name = 'clientes_fornecedores/cliente_list.html'
    context_object_name = 'clientes'

# Vista para criar um novo cliente
class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes_fornecedores/cliente_form.html'
    success_url = reverse_lazy('clientes_fornecedores:cliente_list')

# Vista para exibir os detalhes de um cliente
class ClienteDetailView(DetailView):
    model = Cliente
    template_name = 'clientes_fornecedores/cliente_detail.html'
    context_object_name = 'cliente'
    slug_field = 'codigo_unico'      # NOVO: Diz à vista para usar este campo
    slug_url_kwarg = 'codigo_unico' # NOVO: Mapeia o argumento da URL para o campo

# Vista para editar um cliente
class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes_fornecedores/cliente_form.html'
    success_url = reverse_lazy('clientes_fornecedores:cliente_list')
    slug_field = 'codigo_unico'      # NOVO: Diz à vista para usar este campo
    slug_url_kwarg = 'codigo_unico' # NOVO: Mapeia o argumento da URL para o campo

# Vista para apagar um cliente
class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = 'clientes_fornecedores/cliente_confirm_delete.html'
    success_url = reverse_lazy('clientes_fornecedores:cliente_list')
    slug_field = 'codigo_unico'      # NOVO: Diz à vista para usar este campo
    slug_url_kwarg = 'codigo_unico' # NOVO: Mapeia o argumento da URL para o campo
# --- Views para Fornecedores ---

class FornecedorListView(ListView):
    model = Fornecedor
    template_name = 'clientes_fornecedores/fornecedor_list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nome_empresa__icontains=query) |
                Q(nome_contato__icontains=query) |
                Q(cpf_cnpj__icontains=query)
            )
        return queryset

class FornecedorDetailView(DetailView):
    model = Fornecedor
    template_name = 'clientes_fornecedores/fornecedor_detail.html'

class FornecedorCreateView(CreateView):
    model = Fornecedor
    form_class = FornecedorForm # <-- Alterado aqui
    template_name = 'clientes_fornecedores/fornecedor_form.html'
    success_url = reverse_lazy('clientes_fornecedores:fornecedor_list')

class FornecedorUpdateView(UpdateView):
    model = Fornecedor
    form_class = FornecedorForm # <-- Alterado aqui
    template_name = 'clientes_fornecedores/fornecedor_form.html'
    success_url = reverse_lazy('clientes_fornecedores:fornecedor_list')

class FornecedorDeleteView(DeleteView):
    model = Fornecedor
    template_name = 'clientes_fornecedores/fornecedor_confirm_delete.html'
    success_url = reverse_lazy('clientes_fornecedores:fornecedor_list')

# NOVAS VIEWS PARA A API
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by('nome_completo')
    serializer_class = ClienteSerializer

class FornecedorViewSet(viewsets.ModelViewSet):
    queryset = Fornecedor.objects.all().order_by('nome_empresa')
    serializer_class = FornecedorSerializer