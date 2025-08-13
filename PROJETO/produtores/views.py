# produtores/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.db import transaction
from django.contrib import messages
from .models import ProdutorRural, ResponsavelTecnico, CertificadoDigitalResponsavel
from .forms import ProdutorRuralForm, ResponsavelTecnicoForm, CertificadoDigitalResponsavelForm
from rest_framework import viewsets
from .serializers import (
    ProdutorRuralSerializer,
    ResponsavelTecnicoSerializer,
    CertificadoDigitalResponsavelSerializer
)


# Criar formsets de forma programática para Certificados, pois cada RT tem o seu
CertificadoDigitalResponsavelInlineFormSet = inlineformset_factory(
    ResponsavelTecnico,
    CertificadoDigitalResponsavel,
    form=CertificadoDigitalResponsavelForm,
    extra=0, # Alterado para 0, vamos adicionar dinamicamente via JS
    can_delete=True
)

# Criar o formset para ResponsavelTecnico
ResponsavelTecnicoFormSet = inlineformset_factory(
    ProdutorRural,
    ResponsavelTecnico,
    form=ResponsavelTecnicoForm,
    extra=1, # Permite adicionar um novo RT
    can_delete=True
)

def gerenciar_produtor_rural(request, pk=None):
    produtor_rural = None
    if pk:
        produtor_rural = get_object_or_404(ProdutorRural, pk=pk)

    erro_geral = None

    # INICIALIZE TODOS OS FORMULÁRIOS E FORMSETS AQUI, ANTES DO IF POST
    # Isso garante que eles sempre estarão disponíveis para o contexto,
    # seja para o GET inicial ou para re-renderizar em caso de erro no POST.
    form = ProdutorRuralForm(instance=produtor_rural)
    formset_rt = ResponsavelTecnicoFormSet(instance=produtor_rural, prefix='rt')
    formsets_cert_rt = {} # Dicionário para armazenar formsets de certificado por RT

    # Popule formsets_cert_rt no GET se estiver editando um produtor existente
    if produtor_rural:
        for rt in produtor_rural.responsaveis_tecnicos.all():
            CertificadoDigitalResponsavelInlineFormSetForRT = inlineformset_factory(
                ResponsavelTecnico,
                CertificadoDigitalResponsavel,
                form=CertificadoDigitalResponsavelForm,
                extra=0,
                can_delete=True
            )
            formsets_cert_rt[rt.pk] = CertificadoDigitalResponsavelInlineFormSetForRT(
                instance=rt, prefix=f'cert-rt-{rt.pk}'
            )

    # empty_form_template para o JS, sempre disponível
    cert_empty_form_template = CertificadoDigitalResponsavelInlineFormSet().empty_form.as_p()

    if request.method == 'POST':
        form = ProdutorRuralForm(request.POST, request.FILES, instance=produtor_rural)
        formset_rt = ResponsavelTecnicoFormSet(request.POST, request.FILES, instance=produtor_rural, prefix='rt')

        # Recriar os formsets de certificado com dados do POST para validação
        # Se você está no POST, você precisa re-inicializar os formsets_cert_rt
        # com os dados do POST, ou eles não terão os erros de validação.
        # Faça uma cópia do dicionário para iterar, pois podemos modificá-lo
        # ou adicionar novos RTs que não existiam no GET.

        # Pega as instâncias de RT que foram submetidas (seja existentes ou novas via POST)
        # É importante ter certeza de que você tem os RTs corretos aqui para instanciar os formsets de certificado
        # Se os RTs são novos e ainda não foram salvos, eles não terão PK, o que pode complicar.
        # A melhor abordagem é salvar o ProdutorRural e os Responsáveis Técnicos primeiro,
        # e depois usar as instâncias salvas para os certificados.

        # === INÍCIO DO BLOCO DE TRANSAÇÃO E SALVAMENTO ===
        if form.is_valid() and formset_rt.is_valid():
            try:
                with transaction.atomic():
                    produtor_rural_instance = form.save()

                    # Re-instancia o formset de RT com a instância salva para garantir foreign key
                    formset_rt.instance = produtor_rural_instance
                    # formset_rt.save() já cuida de novos, modificados e deletados RTs.
                    formset_rt.save()

                    # Agora que os RTs estão salvos e têm PKs (se novos), podemos processar os certificados
                    # Obtém a lista atualizada de RTs associados ao produtor_rural_instance
                    current_rt_instances = list(produtor_rural_instance.responsaveis_tecnicos.all())

                    all_cert_forms_valid = True
                    temp_formsets_cert_rt = {} # Usaremos um temp para construir os formsets pós-POST

                    for rt_instance in current_rt_instances:
                        CertificadoDigitalResponsavelInlineFormSetForRT = inlineformset_factory(
                            ResponsavelTecnico,
                            CertificadoDigitalResponsavel,
                            form=CertificadoDigitalResponsavelForm,
                            extra=0,
                            can_delete=True
                        )
                        # Tenta instanciar com os dados do POST para o prefixo específico do RT
                        cert_formset = CertificadoDigitalResponsavelInlineFormSetForRT(
                            request.POST,
                            request.FILES,
                            instance=rt_instance,
                            prefix=f'cert-rt-{rt_instance.pk}'
                        )
                        temp_formsets_cert_rt[rt_instance.pk] = cert_formset # Adiciona ao dicionário temporário

                        if cert_formset.is_valid():
                            cert_formset.save()
                        else:
                            all_cert_forms_valid = False
                            messages.error(request, f"Erros nos certificados para o Responsável Técnico {rt_instance.nome}: {cert_formset.errors}")

                    if all_cert_forms_valid:
                        messages.success(request, 'Produtor rural e informações relacionadas salvas com sucesso!')
                        return redirect('produtores:detalhes_produtor')
                    else:
                        erro_geral = "Verifique os erros nos certificados digitais."
                        # Se houver erros nos certificados, precisamos que o contexto passe os formsets com erros
                        # formsets_cert_rt já foi inicializado acima e será sobrescrito aqui.
                        formsets_cert_rt = temp_formsets_cert_rt # Passa os formsets com erros de volta para o template

            except Exception as e:
                erro_geral = f"Ocorreu um erro inesperado ao salvar: {e}"
                messages.error(request, erro_geral)
                # Se houver uma exceção, os formsets deveriam estar com os dados do POST

        else: # form principal OU formset_rt não é válido
            erro_geral = "Por favor, verifique os erros nos formulários."
            # Os formulários 'form' e 'formset_rt' já estão ligados aos dados do POST
            # e conterão os erros que serão exibidos no template.

            # Precisamos re-popular formsets_cert_rt para re-renderizar com dados do POST e seus erros
            # Mesmo que formset_rt seja inválido, o JS ainda pode ter adicionado formulários de certificado.
            # Então, vamos tentar re-instanciar os formsets de certificado com base nos dados do POST.
            # Isso é mais complexo porque os RTs podem não ter PKs se o formset_rt for inválido.
            # Uma abordagem para este cenário é iterar sobre os dados do POST para identificar os formsets de certificado.
            # Ou, mais simples para validação:
            # Re-instancie formsets_cert_rt com a instância atual (produtor_rural) para carregar os existentes
            # E depois tente carregar os dados do POST para eles, se o prefixo existir.
            
            # Recria formsets_cert_rt com os dados do POST para manter os erros e os campos preenchidos
            formsets_cert_rt = {}
            # Itera sobre os formsets de RT no POST para encontrar os PKs (existentes ou "__prefix__" para novos)
            for rt_form in formset_rt: # Itera sobre os forms dentro do formset
                if rt_form.instance.pk: # RT existente
                    rt_pk = rt_form.instance.pk
                elif '__prefix__' in rt_form.prefix: # Novo RT que ainda não foi salvo (temporário no POST)
                    # Para novos RTs que não foram salvos, não teremos um PK real.
                    # Mas o JS do admin faz isso com __prefix__.
                    # A forma correta de lidar com isso é que o JS crie um novo prefixo único para cada RT.
                    # Por enquanto, vamos assumir que o erro está mais na inicialização.
                    continue # Pula RTs novos que não foram salvos e ainda não têm PK

                if rt_pk: # Se tem um PK (RT existente)
                    CertificadoDigitalResponsavelInlineFormSetForRT = inlineformset_factory(
                        ResponsavelTecnico,
                        CertificadoDigitalResponsavel,
                        form=CertificadoDigitalResponsavelForm,
                        extra=0,
                        can_delete=True
                    )
                    formsets_cert_rt[rt_pk] = CertificadoDigitalResponsavelInlineFormSetForRT(
                        request.POST, request.FILES, instance=rt_form.instance, prefix=f'cert-rt-{rt_pk}'
                    )

    # === FIM DO BLOCO DE TRANSAÇÃO E SALVAMENTO ===

    context = {
        'form': form,
        'formset_rt': formset_rt,
        'formsets_cert_rt': formsets_cert_rt, # Esta variável agora sempre será definida
        'produtor_rural': produtor_rural,
        'erro_geral': erro_geral,
        'cert_empty_form_template': cert_empty_form_template,
    }
    return render(request, 'produtores/gerenciar_produtor.html', context)


def detalhes_produtor(request):
    produtor_rural = ProdutorRural.objects.first()
    responsaveis_tecnicos = []
    certificados_digitais_rt = {}

    if produtor_rural:
        responsaveis_tecnicos = produtor_rural.responsaveis_tecnicos.all()
        for rt in responsaveis_tecnicos:
            certificados_digitais_rt[rt.pk] = rt.certificados_digitais.all()

    context = {
        'produtor_rural': produtor_rural,
        'responsaveis_tecnicos': responsaveis_tecnicos,
        'certificados_digitais_rt': certificados_digitais_rt,
    }
    return render(request, 'produtores/detalhes_produtor.html', context)

# NOVAS VIEWS PARA A API
class ProdutorRuralViewSet(viewsets.ModelViewSet):
    queryset = ProdutorRural.objects.all().order_by('-data_cadastro')
    serializer_class = ProdutorRuralSerializer

class ResponsavelTecnicoViewSet(viewsets.ModelViewSet):
    queryset = ResponsavelTecnico.objects.all().order_by('nome')
    serializer_class = ResponsavelTecnicoSerializer

class CertificadoDigitalResponsavelViewSet(viewsets.ModelViewSet):
    queryset = CertificadoDigitalResponsavel.objects.all().order_by('-data_cadastro')
    serializer_class = CertificadoDigitalResponsavelSerializer