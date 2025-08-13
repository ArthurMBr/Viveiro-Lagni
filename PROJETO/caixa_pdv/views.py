# viveiro_lagni/PROJETO/caixa_pdv/views.py
from django.shortcuts import render
from produtos.models import Produto 
from lotes.models import Lote 
from .models import Venda, ItemVenda, MovimentoCaixa 
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_GET, require_POST
from django.db import transaction
import json
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import HttpResponse
from rest_framework import viewsets
from .serializers import VendaSerializer, ItemVendaSerializer, MovimentoCaixaSerializer
from django.db.models import Sum
from django.contrib import messages
from django.shortcuts import render, redirect
from lotes.models import Lote
from lotes.serializers import LoteSerializer

# A importação de 'clientes.models.Cliente' foi removida.

def pdv_view(request):
    """
    Renderiza a interface principal do PDV.
    """
    context = {
        'page_title': 'Caixa PDV',
    }
    return render(request, 'caixa_pdv/pdv.html', context)

@require_GET
def search_lotes_api(request):
    """
    API para buscar lotes por código do lote, variedade do produto ou tipo do produto.
    """
    query = request.GET.get('query', '').strip()
    lotes_data = []

    if query:
        lotes = Lote.objects.filter(
            Q(codigo__icontains=query) |
            Q(produto__variedade__icontains=query) |
            Q(produto__tipo__icontains=query)
        ).select_related('produto').distinct()

        for lote in lotes:
            imagem_url = None
            if lote.produto and lote.produto.imagem:
                try:
                    imagem_url = lote.produto.imagem.url
                except ValueError:
                    imagem_url = None
                except Exception as e:
                    print(f"Erro ao obter URL da imagem para produto {lote.produto.id}: {e}")
                    imagem_url = None

            lotes_data.append({
                'id': lote.id,
                'codigo_lote': lote.codigo,
                'quantidade_estoque': lote.quantidade,
                'preco_unitario': str(lote.preco_unitario),
                'nome_produto': lote.produto.variedade if lote.produto and lote.produto.variedade else (lote.produto.get_tipo_display() if lote.produto else 'Produto Desconhecido'),
                'imagem_produto_url': imagem_url,
            })
    
    return JsonResponse({'lotes': lotes_data})

@require_POST
def finalizar_venda_api(request):
    """
    Finaliza uma venda, criando a Venda e os Itens de Venda,
    e deduzindo a quantidade dos lotes correspondentes.
    """
    try:
        data = json.loads(request.body)
        itens_venda = data.get('itens', [])

        if not itens_venda:
            return JsonResponse({'success': False, 'message': 'Nenhum item na venda para finalizar.'}, status=400)

        with transaction.atomic():
            nova_venda = Venda.objects.create(status='finalizada')

            for item_data in itens_venda:
                lote_id = item_data.get('lote_id')
                quantidade_solicitada = int(item_data.get('quantidade'))
                preco_unitario = item_data.get('preco_unitario')

                if not all([lote_id, quantidade_solicitada, preco_unitario is not None]):
                    raise ValueError("Dados incompletos ou inválidos para um item da venda.")
                
                try:
                    preco_unitario_decimal = Decimal(str(preco_unitario))
                except Exception:
                    raise ValueError(f"Preço unitário inválido para item do lote {lote_id}.")

                # Obtenha o objeto Lote usando o lote_id
                lote_do_item = Lote.objects.select_for_update().get(id=lote_id)

                if lote_do_item.quantidade < quantidade_solicitada:
                    raise ValueError(f"Estoque insuficiente para o lote '{lote_do_item.codigo}'. Disponível: {lote_do_item.quantidade}, Solicitado: {quantidade_solicitada}.")

                subtotal_item = preco_unitario_decimal * quantidade_solicitada

                ItemVenda.objects.create(
                    venda=nova_venda,
                    produto=lote_do_item.produto,
                    quantidade=quantidade_solicitada,
                    preco_unitario_vendido=preco_unitario_decimal,
                    subtotal=subtotal_item,
                    lote=lote_do_item  # Usamos a variável que acabamos de definir
                )

                lote_do_item.quantidade -= quantidade_solicitada
                lote_do_item.save()

            nova_venda.calcular_total()
            nova_venda.save()

        return JsonResponse({'success': True, 'message': 'Venda finalizada com sucesso!', 'venda_id': nova_venda.id})

    except Lote.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Um dos lotes da venda não foi encontrado.'}, status=404)
    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Requisição inválida: O corpo da requisição não é um JSON válido.'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': 'Ocorreu um erro interno inesperado ao finalizar a venda. Por favor, tente novamente.'}, status=500)

def historico_vendas_view(request):
    """
    Renderiza a página de histórico de vendas e calcula o saldo do caixa.
    """
    # 1. Calcular o total de entradas no caixa (total das vendas)
    total_vendas = Venda.objects.aggregate(Sum('total_venda'))['total_venda__sum'] or 0

    # 2. Calcular o total de retiradas do caixa
    total_retiradas = MovimentoCaixa.objects.filter(tipo='retirada').aggregate(Sum('valor'))['valor__sum'] or 0
    
    # 3. Calcular o saldo atual
    saldo_caixa = total_vendas - total_retiradas

    # 4. Obter o extrato dos movimentos do caixa para exibir
    movimentos_caixa = MovimentoCaixa.objects.all().order_by('-data_hora')

    context = {
        'page_title': 'Histórico de Vendas',
        'saldo_caixa': saldo_caixa,
        'movimentos_caixa': movimentos_caixa,
        # Você pode adicionar outras informações de contexto aqui, como a lista de vendas, se necessário
    }
    return render(request, 'caixa_pdv/historico_vendas.html', context)

@require_POST
def caixa_movimento(request):
    """
    Processa a retirada de valor do caixa.
    """
    try:
        valor = float(request.POST.get('valor', 0))
        descricao = request.POST.get('descricao', '')

        if valor <= 0:
            messages.error(request, 'O valor da retirada deve ser maior que zero.')
            return redirect('historico_vendas') # Redirecione para a URL correta

        # Crie o novo registo de movimento de caixa
        MovimentoCaixa.objects.create(
            tipo='retirada',
            valor=valor,
            descricao=descricao
        )
        messages.success(request, f'Retirada de R$ {valor:.2f} realizada com sucesso!')
    except (ValueError, TypeError):
        messages.error(request, 'Valor inválido para a retirada.')
    
    return redirect('historico_vendas') # Redirecione para a URL correta

@require_GET
def search_vendas_api(request):
    """
    API para buscar vendas no histórico com filtros.
    """
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    # O filtro de cliente foi removido
    venda_id_query = request.GET.get('venda_id')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))

    # select_related e prefetch_related foram ajustados para remover a dependência de 'cliente'
    vendas = Venda.objects.prefetch_related('itens').all()

    if start_date_str:
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            vendas = vendas.filter(data_venda__gte=start_date)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Formato de data de início inválido. Use YYYY-MM-DD.'}, status=400)

    if end_date_str:
        try:
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            vendas = vendas.filter(data_venda__lt=end_date + datetime.timedelta(days=1))
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Formato de data de fim inválido. Use YYYY-MM-DD.'}, status=400)

    # O filtro por cliente foi removido
    # if client_name_query:
    #     vendas = vendas.filter(cliente__nome__icontains=client_name_query)

    if venda_id_query:
        try:
            vendas = vendas.filter(id=int(venda_id_query))
        except ValueError:
            return JsonResponse({'success': False, 'message': 'ID da venda inválido.'}, status=400)

    vendas = vendas.order_by('-data_venda')

    total_vendas = vendas.count()
    offset = (page - 1) * page_size
    limit = offset + page_size
    vendas_paginadas = vendas[offset:limit]

    vendas_data = []
    for venda in vendas_paginadas:
        itens_data = []
        for item in venda.itens.all():
            itens_data.append({
                'produto_nome': item.produto.variedade,
                'lote_codigo': item.lote.codigo if hasattr(item, 'lote') and item.lote else 'N/A',
                'quantidade': item.quantidade,
                'preco_unitario_vendido': str(item.preco_unitario_vendido),
                'subtotal': str(item.subtotal),
            })
        vendas_data.append({
            'id': venda.id,
            'data_venda': timezone.localtime(venda.data_venda).strftime('%d/%m/%Y %H:%M:%S'),
            # A referência ao cliente foi removida
            'nome_cliente': 'Não Informado', 
            'forma_pagamento': venda.forma_pagamento.capitalize() if hasattr(venda, 'forma_pagamento') and venda.forma_pagamento else 'N/A',
            'total_venda': str(venda.total_venda),
            'status': venda.status.capitalize(),
            'observacoes': venda.observacoes if hasattr(venda, 'observacoes') and venda.observacoes else 'N/A',
            'itens': itens_data,
        })
    
    return JsonResponse({
        'success': True,
        'vendas': vendas_data,
        'total_vendas': total_vendas,
        'total_paginas': (total_vendas + page_size - 1) // page_size,
        'pagina_atual': page,
    })

@require_http_methods(["DELETE"])
@transaction.atomic
def delete_venda_api(request, venda_id):
    """
    API para apagar uma venda e seus itens associados.
    """
    try:
        venda = get_object_or_404(Venda, id=venda_id)
        for item in venda.itens.all():
            if item.lote:
                lote = Lote.objects.select_for_update().get(id=item.lote.id)
                lote.quantidade += item.quantidade
                lote.save()
            else:
                print(f"Aviso: Lote (ID {item.lote_id}) não encontrado para restauração de estoque na Venda {venda_id}.")

        venda_id_apagada = venda.id
        venda.delete()

        return JsonResponse({'success': True, 'message': f'Venda #{venda_id_apagada} apagada com sucesso e estoque restaurado.'})

    except Venda.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Venda não encontrada.'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': f'Ocorreu um erro ao apagar a venda: {str(e)}'}, status=500)

def gerar_termo_conformidade_pdf(request, venda_id):
    """
    Gera um PDF de Termo de Conformidade para uma venda específica.
    """
    try:
        # 1. SUBSTITUA 'NOME_DO_CAMPO_CORRETO_AQUI' PELO NOME DO CAMPO NO SEU MODELO Venda.
        #    Exemplo: se o campo se chama 'comprador', a linha ficaria:
        #    venda = get_object_or_404(Venda.objects.select_related('comprador'), pk=venda_id)
        venda = get_object_or_404(Venda.objects.select_related('NOME_DO_CAMPO_CORRETO_AQUI'), pk=venda_id)
        itens_venda = ItemVenda.objects.filter(venda=venda).select_related('produto', 'lote')

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="termo_conformidade_venda_{venda.id}.pdf"'

        doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2.5*cm, bottomMargin=2.5*cm)
        story = []
        styles = getSampleStyleSheet()

        styles.add(ParagraphStyle(name='TitleStyle', fontSize=18, leading=22, alignment=1, fontName='Helvetica', spaceAfter=6))
        styles.add(ParagraphStyle(name='HeaderInfo', fontSize=10, leading=12, alignment=1, fontName='Helvetica', spaceAfter=0))
        styles.add(ParagraphStyle(name='SubTitleStyle', fontSize=14, leading=18, alignment=1, fontName='Helvetica', spaceAfter=12))
        styles.add(ParagraphStyle(name='BodyTextCustom', fontSize=12, leading=14, fontName='Helvetica', spaceAfter=6))
        styles.add(ParagraphStyle(name='TableHeading', fontSize=10, leading=12, fontName='Helvetica-Bold', alignment=1))
        styles.add(ParagraphStyle(name='TableCell', fontSize=10, leading=12, fontName='Helvetica', alignment=0))

        story.append(Paragraph("Viveiro Lagni", styles['TitleStyle']))
        story.append(Paragraph("Rua Santa Rita, nº 595 - Centro", styles['HeaderInfo']))
        story.append(Paragraph("Chapecó - SC, CEP 89801-081", styles['HeaderInfo']))
        story.append(Paragraph("Fone: (49) 3328-5690 / (49) 99990-2550", styles['HeaderInfo']))
        story.append(Paragraph("E-mail: viveiro@lagnimudas.com.br", styles['HeaderInfo']))
        story.append(Spacer(1, 0.5*cm))

        story.append(Paragraph("Termo de Conformidade de Produtos", styles['SubTitleStyle']))
        story.append(Spacer(1, 0.5*cm))

        # Dados da Venda e Cliente
        # 2. SUBSTITUA 'venda.cliente' pelo nome real do campo
        cliente_obj = getattr(venda, 'NOME_DO_CAMPO_CORRETO_AQUI', None)
        if cliente_obj:
            nome = getattr(cliente_obj, 'nome_completo', None) or getattr(cliente_obj, 'nome', 'Não informado')
            cpf_cnpj = getattr(cliente_obj, 'cpf_cnpj', 'Não informado')
            endereco = getattr(cliente_obj, 'endereco', 'Não informado')
            cidade = getattr(cliente_obj, 'cidade', 'Não informado')
            estado = getattr(cliente_obj, 'estado', 'Não informado')

            cliente_info = f'<b>Cliente:</b> {nome}<br/>'
            cliente_info += f'<b>Documento:</b> {cpf_cnpj}<br/>'
            cliente_info += f'<b>Endereço:</b> {endereco}, {cidade} - {estado}<br/>'
        else:
            cliente_info = "<b>Cliente:</b> Cliente não especificado<br/>"

        cliente_info += f'<b>ID da Venda:</b> {venda.id}<br/>'
        cliente_info += f'<b>Data da Venda:</b> {venda.data_venda.strftime("%d/%m/%Y")}<br/>'

        story.append(Paragraph(cliente_info, styles['BodyTextCustom']))
        story.append(Spacer(1, 0.5*cm))

        data = [['ID', 'Produto', 'Lote', 'Quantidade', 'Preço Unitário', 'Subtotal']]
        for item in itens_venda:
            data.append([
                str(item.id),
                item.produto.variedade if item.produto else 'N/A',
                item.lote.codigo if item.lote else 'N/A',
                f"{item.quantidade}",
                f"R$ {item.preco_unitario_vendido}",
                f"R$ {item.subtotal}"
            ])

        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6D4C41')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E0E0D4')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E0E0D4')),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F4E3')),
        ])

        col_widths = [1*cm, 5*cm, 2.5*cm, 2.5*cm, 3*cm, 3*cm]
        table = Table(data, colWidths=col_widths)
        table.setStyle(table_style)
        story.append(table)
        story.append(Spacer(1, 0.5*cm))

        story.append(Paragraph(f'<b>Total da Venda:</b> R$ {venda.total_venda}', styles['BodyTextCustom']))
        story.append(Paragraph(f'<b>Forma de Pagamento:</b> {venda.forma_pagamento}', styles['BodyTextCustom']))
        story.append(Paragraph(f'<b>Observações da Venda:</b> {venda.observacoes}', styles['BodyTextCustom']))
        story.append(Spacer(1, 1*cm))

        termo = """
        <br/><b>Termo de Conformidade</b><br/><br/>
        Declaro, para os devidos fins, que os produtos listados acima foram inspecionados no ato da compra e se encontram em plenas condições de sanidade e vigor, de acordo com as informações fornecidas e as normas de qualidade do Viveiro Lagni. O cliente é responsável por seguir as instruções de plantio e cuidado para garantir o desenvolvimento saudável das plantas.
        <br/><br/><br/><br/>
        __________________________________<br/>
        Assinatura do Cliente
        <br/><br/><br/>
        __________________________________<br/>
        Assinatura do Responsável Viveiro Lagni
        """
        story.append(Paragraph(termo, styles['BodyTextCustom']))
        
        doc.build(story)
        return response

    except Venda.DoesNotExist:
        return HttpResponse("Venda não encontrada.", status=404)
    except Exception as e:
        return HttpResponse(f"Ocorreu um erro: {e}", status=500)

# NOVAS VIEWS PARA A API
class VendaViewSet(viewsets.ModelViewSet):
    queryset = Venda.objects.all().order_by('-data_venda')
    serializer_class = VendaSerializer

class ItemVendaViewSet(viewsets.ModelViewSet):
    queryset = ItemVenda.objects.all()
    serializer_class = ItemVendaSerializer

class MovimentoCaixaViewSet(viewsets.ModelViewSet):
    queryset = MovimentoCaixa.objects.all().order_by('-data_hora')
    serializer_class = MovimentoCaixaSerializer

class LoteViewSet(viewsets.ModelViewSet):
    # Exemplo para expor lotes da app 'lotes' através da app 'caixa_pdv' se necessário
    queryset = Lote.objects.all()
    serializer_class = LoteSerializer