# produtos/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Q
from django.http import JsonResponse
from .models import Produto, NCM, CFOP
from .forms import ProdutoForm
from .forms import ProdutoFilterForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework import viewsets
from .serializers import ProdutoSerializer, NCMSerializer, CFOPSerializer


class ProdutoListView(ListView):
    model = Produto
    template_name = 'produtos/produto_list.html'
    context_object_name = 'produtos'
    paginate_by = 10

    def get_queryset(self):
        queryset = Produto.objects.all().order_by('cod')

        form = ProdutoFilterForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get('q')
            tipo = form.cleaned_data.get('tipo')
            status = form.cleaned_data.get('status')

            if query:
                queryset = queryset.filter(
                    Q(cod__icontains=query) |
                    Q(variedade__icontains=query) |
                    Q(especie__icontains=query) |
                    Q(cultivar_info__icontains=query) |
                    Q(ncm__codigo__icontains=query) | # Adicionado __codigo para busca em Foreign Key
                    Q(ncm__descricao__icontains=query) | # Adicionado __descricao para busca em Foreign Key
                    Q(cfop__codigo__icontains=query) | # Adicionado __codigo para busca em Foreign Key
                    Q(cfop__descricao__icontains=query) # Adicionado __descricao para busca em Foreign Key
                )

            if tipo:
                queryset = queryset.filter(tipo=tipo)
            if status:
                queryset = queryset.filter(status=status)
        return queryset


class ProdutoCreateView(CreateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'produtos/produto_form.html'
    success_url = reverse_lazy('produtos:list')

    def form_valid(self, form):
        messages.success(self.request, "Produto cadastrado com sucesso!")
        return super().form_valid(form)

    def form_invalid(self, form):
        # >>> ADIÇÃO PARA DEBUG <<<
        print("Erros no formulário de criação:", form.errors)
        messages.error(self.request, "Erro ao cadastrar o produto. Verifique os dados.")
        return super().form_invalid(form)


class ProdutoUpdateView(UpdateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'produtos/produto_form.html'
    success_url = reverse_lazy('produtos:list')

    def form_valid(self, form):
        messages.success(self.request, "Produto atualizado com sucesso!")
        return super().form_valid(form)

    def form_invalid(self, form):
        # >>> ADIÇÃO PARA DEBUG <<<
        print("Erros no formulário de atualização:", form.errors)
        messages.error(self.request, "Erro ao atualizar o produto. Verifique os dados.")
        return super().form_invalid(form)


class ProdutoDeleteView(DeleteView):
    model = Produto
    template_name = 'produtos/produto_confirm_delete.html'
    success_url = reverse_lazy('produtos:list')
    context_object_name = 'produto'

class ProdutoDetailView(DetailView):
    model = Produto
    template_name = 'produtos/produto_detail.html' # Nome do template para exibir o detalhe
    context_object_name = 'produto'

    def form_valid(self, form):
        messages.success(self.request, "Produto excluído com sucesso!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Erro ao excluir o produto.")
        return super().form_invalid(form)

# VIEW DE API DE BUSCA DE NCM
def ncm_search_api(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        # Normaliza a query para busca exata (remove pontos)
        exact_query = query.replace('.', '')
        # Verifica se a query parece ser um código NCM (apenas dígitos, 8 caracteres)
        is_code_like = exact_query.isdigit() and len(exact_query) == 8

        ncm_results = NCM.objects.none() # Começa com um queryset vazio

        if is_code_like:
            # Prioriza busca exata pelo código (com ou sem pontos)
            ncm_results = NCM.objects.filter(
                Q(codigo__exact=query) | Q(codigo__exact=exact_query)
            ).distinct()

        if not ncm_results.exists(): # Se a busca exata não encontrou ou não foi tentada
            # Fallback para busca mais ampla (contém)
            ncm_results = NCM.objects.filter(
                Q(codigo__icontains=query) |
                Q(descricao__icontains=query)
            ).distinct()

        for ncm in ncm_results[:10]: # Limita os resultados para performance
            results.append({'id': ncm.id, 'text': f"{ncm.codigo} - {ncm.descricao}"})
    
    return JsonResponse({'results': results})

# VIEW DE API DE BUSCA DE CFOP
def cfop_search_api(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        # Normaliza a query para busca exata (remove pontos)
        exact_query = query.replace('.', '')
        # Verifica se a query parece ser um código CFOP (apenas dígitos, 4 ou 5 caracteres)
        is_code_like = exact_query.isdigit() and (len(exact_query) >= 4 and len(exact_query) <= 5)

        cfop_results = CFOP.objects.none() # Começa com um queryset vazio

        if is_code_like:
            # Prioriza busca exata pelo código (com ou sem pontos)
            cfop_results = CFOP.objects.filter(
                Q(codigo__exact=query) | Q(codigo__exact=exact_query)
            ).distinct()

        if not cfop_results.exists(): # Se a busca exata não encontrou ou não foi tentada
            # Fallback para busca mais ampla (contém)
            cfop_results = CFOP.objects.filter(
                Q(codigo__icontains=query) |
                Q(descricao__icontains=query)
            ).distinct()

        for cfop in cfop_results[:10]: # Limita os resultados para performance
            results.append({'id': cfop.id, 'text': f"{cfop.codigo} - {cfop.descricao}"})
    
    return JsonResponse({'results': results})

# NOVAS VIEWS PARA A API
class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all().order_by('variedade')
    serializer_class = ProdutoSerializer

class NCMViewSet(viewsets.ModelViewSet):
    queryset = NCM.objects.all().order_by('codigo')
    serializer_class = NCMSerializer

class CFOPViewSet(viewsets.ModelViewSet):
    queryset = CFOP.objects.all().order_by('codigo')
    serializer_class = CFOPSerializer