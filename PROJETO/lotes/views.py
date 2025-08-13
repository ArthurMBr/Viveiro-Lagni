# lotes/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Lote
from .forms import LoteForm
from rest_framework import viewsets
from .serializers import LoteSerializer

# NOVO: Importar Q para consultas complexas
from django.db.models import Q # <--- ESSA LINHA FOI ADICIONADA/CORRIGIDA AQUI

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import JsonResponse
from django.urls import reverse
from reportlab.lib.utils import ImageReader

from io import BytesIO
import requests
import os
from PIL import Image

# Importações para o código de barras da biblioteca python-barcode
from barcode import Code128
from barcode.writer import ImageWriter

# --- Registro da Fonte ---
FONT_PATH = os.path.join(os.path.dirname(__file__), 'static', 'lotes', 'fonts', 'AgencyFB.ttf')
AGENCY_FB_FONT_NAME = 'AgencyFB'
FALLBACK_FONT_NAME = 'Helvetica'

agency_fb_registered = False

try:
    if os.path.exists(FONT_PATH):
        pdfmetrics.registerFont(TTFont(AGENCY_FB_FONT_NAME, FONT_PATH))
        agency_fb_registered = True
        print(f"Fonte '{AGENCY_FB_FONT_NAME}' registrada com sucesso de: {FONT_PATH}")
    else:
        print(f"ATENÇÃO: '{AGENCY_FB_FONT_NAME}.ttf' não encontrado em {FONT_PATH}. O ReportLab usará uma fonte padrão para '{AGENCY_FB_FONT_NAME}'.")
except Exception as e:
    print(f"ERRO ao tentar registrar a fonte '{AGENCY_FB_FONT_NAME}' de {FONT_PATH}: {e}. O ReportLab usará uma fonte padrão para '{AGENCY_FB_FONT_NAME}'.")


# --- Caminho da Logo ---
LOGO_PATH = os.path.join(os.path.dirname(__file__), 'static', 'lotes', 'images', 'Studio Santana (14).png')


def lote_list(request):
    # Lógica de pesquisa adicionada/corrigida aqui
    query = request.GET.get('q')
    lotes = Lote.objects.all().order_by("data_semeadura")

    if query:
        lotes = lotes.filter(
            Q(codigo__icontains=query) |
            Q(variedade__icontains=query) |
            Q(produto__variedade__icontains=query) |
            Q(produto__especie__icontains=query)
        ).distinct()

    return render(request, "lotes/lote_list.html", {"lotes": lotes, "query": query})

def lote_create(request):
    if request.method == 'POST':
        form = LoteForm(request.POST)
        if form.is_valid():
            lote = form.save()
            return redirect('lotes:lote_list')
    else:
        form = LoteForm()
    return render(request, 'lotes/lote_form.html', {'form': form, 'action': 'Adicionar Novo Lote'})

def lote_update(request, pk):
    lote = get_object_or_404(Lote, pk=pk)
    if request.method == 'POST':
        form = LoteForm(request.POST, instance=lote)
        if form.is_valid():
            form.save()
            return redirect('lotes:lote_list')
    else:
        form = LoteForm(instance=lote)
    return render(request, 'lotes/lote_form.html', {'form': form, 'action': 'Editar Lote'})

def lote_delete(request, pk):
    lote = get_object_or_404(Lote, pk=pk)
    if request.method == 'POST':
        lote.delete()
        return redirect('lotes:lote_list')
    return render(request, 'lotes/lote_confirm_delete.html', {'lote': lote})

def criar_novo_lote(request):
    return render(request, 'lotes/novo_lote.html', {'page_title': 'Novo Lote de Etiquetas'})

def listar_lotes_api(request):
    query = request.GET.get('search', '')
    lotes = Lote.objects.all()

    if query:
        # Filtra por código do lote, nome do produto, ou data de semeadura
        lotes = lotes.filter(
            Q(codigo__icontains=query) |
            Q(produto__variedade__icontains=query) |
            Q(produto__tipo__icontains=query) |
            Q(data_semeadura__icontains=query.replace('/', '-')) # Permite buscar por data em DD-MM-AAAA
        )
    
    final_data = []
    for lote in lotes:
        final_data.append({
            'id': lote.id,
            'codigo': lote.codigo,
            'produto_nome': lote.nome_produto, # Usa a @property corretamente
            'data_semeadura': lote.data_semeadura.strftime('%d/%m/%Y'),
            'quantidade_display': f"{lote.quantidade} {lote.unidade_medida}", # Para exibição
            'quantidade_raw': lote.quantidade, # NOVO: Quantidade como número inteiro
            'unidade_medida': lote.unidade_medida, # NOVO: Unidade de medida separada
            'url_etiqueta': reverse('lotes:gerar_etiqueta_lote', args=[lote.id])
        })
    return JsonResponse({'lotes': final_data})

def gerar_etiqueta_lote(request, pk):
    lote = get_object_or_404(Lote, pk=pk)

    quantidade_para_etiqueta = lote.quantidade # Garante que a variável sempre tenha um valor inicial

    quantidade_para_etiqueta_str = request.GET.get('quantidade')
    if quantidade_para_etiqueta_str: # ADICIONE ESTA LINHA E INDENTE O BLOCO ABAIXO
        try:
            temp_quantidade = int(quantidade_para_etiqueta_str)
            if temp_quantidade >= 0:
                quantidade_para_etiqueta = temp_quantidade
            else:
                print(f"DEBUG: Quantidade negativa '{quantidade_para_etiqueta_str}' recebida. Usando quantidade original do lote: {lote.quantidade}")
        except (TypeError, ValueError):
            print(f"DEBUG: Parâmetro 'quantidade' inválido ('{quantidade_para_etiqueta_str}'). Usando quantidade original do lote: {lote.quantidade}")

    buffer = BytesIO()

    # --- DIMENSÕES DA ETIQUETA DE ROLO ---
    etiqueta_largura = 50 * mm
    etiqueta_altura = 15 * mm

    p = canvas.Canvas(buffer, pagesize=(etiqueta_largura, etiqueta_altura))

    # --- DEFINIÇÕES DE MARGENS INTERNAS DA ETIQUETA ---
    margem_para_logo_esquerda = 15 * mm
    margem_direita_conteudo = 1 * mm

    margem_inicial_topo = 1.5 * mm
    espacamento_entre_linhas = 3.2 * mm

    font_to_use = AGENCY_FB_FONT_NAME if agency_fb_registered else FALLBACK_FONT_NAME

    # --- POSICIONAMENTO DO TEXTO ---
    base_font_size = 9

    x_pos_text = margem_para_logo_esquerda
    y_pos_lote = etiqueta_altura - margem_inicial_topo - base_font_size * 0.8

    p.setFont(font_to_use, base_font_size)
    p.drawString(x_pos_text, y_pos_lote, f"LOTE: {lote.codigo}")

    y_pos_renasem = y_pos_lote - espacamento_entre_linhas
    p.setFont(font_to_use, base_font_size)
    p.drawString(x_pos_text, y_pos_renasem, "RENASEM: SC-04016/2022")

    y_pos_produto_variedade = y_pos_renasem - espacamento_entre_linhas

    # Usa o str(lote.produto) que agora pega APENAS a variedade (se o __str__ de Produto estiver configurado)
    product_variety_line = str(lote.produto) .upper()

    original_font_size_variety = 9
    min_font_size_variety = 8
    current_font_size_variety = original_font_size_variety

    max_text_width_variety = etiqueta_largura - x_pos_text - margem_direita_conteudo

    font_for_width_calc = font_to_use
    while True:
        text_width = p.stringWidth(product_variety_line, font_for_width_calc, current_font_size_variety)
        if text_width <= max_text_width_variety:
            break
        if current_font_size_variety <= min_font_size_variety:
            break
        current_font_size_variety -= 0.5

    p.setFont(font_to_use, current_font_size_variety)
    p.drawString(x_pos_text, y_pos_produto_variedade, product_variety_line)


    # Geração do Código de Barras (Code 128) usando python-barcode
    barcode_value = lote.codigo

    try:
        # Cria um objeto BytesIO para armazenar a imagem do código de barras
        barcode_img_buffer = BytesIO()

        # Configurações para o ImageWriter: write_text=False para não incluir os números
        writer_options = {
            'write_text': False,
            'text_distance': 0.0,
            'font_size': 0,
            'module_height': 5.0,
            'module_width': 0.18,
            'quiet_zone': 0.5,
            'dpi': 300,
        }

        # Gera o código de barras e salva no buffer como PNG
        Code128(barcode_value, writer=ImageWriter()).write(barcode_img_buffer, options=writer_options)
        barcode_img_buffer.seek(0) # Volta ao início do buffer para leitura

        barcode_image_reader = ImageReader(barcode_img_buffer)

        # Dimensões e posicionamento para o ReportLab
        barcode_pdf_height = 4 * mm
        barcode_pdf_width = 30 * mm

        # Posição X: Centraliza o código de barras na área disponível à direita da logo
        max_barcode_width_available = etiqueta_largura - margem_para_logo_esquerda - margem_direita_conteudo
        barcode_x_pos = x_pos_text  
        
        # Garante que o código de barras não vá muito para a esquerda
        if barcode_x_pos < margem_para_logo_esquerda:
            barcode_x_pos = margem_para_logo_esquerda

        barcode_y_pos = 0 * mm # Posição Y: Próximo à parte inferior da etiqueta

        p.drawImage(barcode_image_reader, barcode_x_pos, barcode_y_pos,
                            width=barcode_pdf_width, height=barcode_pdf_height)
        

    except Exception as e:
        p.setFont("Helvetica-Bold", 6)
        p.drawString(x_pos_text, 0.5*mm, f"Erro ao gerar código de barras: {e}")
        print(f"Erro ao gerar código de barras para o lote {lote.codigo}: {e}")

    # --- DESENHAR A LOGO ---
    try:
        if os.path.exists(LOGO_PATH):
            # 1. Abre a imagem PNG com Pillow
            img_pillow = Image.open(LOGO_PATH)

            # 2. Cria um buffer de bytes para salvar a imagem como PNG.
            # Isso garante que a transparência seja mantida e ReportLab a processe.
            img_buffer = BytesIO()
            # Salva a imagem no buffer como PNG, mantendo o canal alpha se presente
            img_pillow.save(img_buffer, format='PNG')
            img_buffer.seek(0) # Volta ao início do buffer para que o ImageReader possa ler

            # 3. Cria um ImageReader a partir do buffer de bytes
            logo_image_reader = ImageReader(img_buffer)

            # Dimensões da logo (ajuste conforme necessário para sua imagem)
            logo_width = 13 * mm 
            logo_height = 13 * mm 

            # Posição da logo (centralizada verticalmente na margem da esquerda)
            logo_x = 1 * mm 
            logo_y = (etiqueta_altura / 2) - (logo_height / 2)

            # Desenha a imagem. Sem o parâmetro 'mask' explícito, o ReportLab
            # deve usar o canal alpha presente no próprio arquivo PNG.
            p.drawImage(logo_image_reader, logo_x, logo_y,
                                width=logo_width, height=logo_height)
            print(f"Logo desenhada com sucesso de: {LOGO_PATH}")
        else:
            print(f"AVISO: Logo não encontrada em {LOGO_PATH}. A etiqueta será gerada sem a logo.")
    except Exception as e:
        print(f"ERRO ao desenhar a logo de {LOGO_PATH}: {e}")


    p.save()

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="etiqueta_lote_{lote.codigo}.pdf"'
    return response

# NOVAS VIEWS PARA A API
class LoteViewSet(viewsets.ModelViewSet):
    queryset = Lote.objects.all().order_by('-data_semeadura')
    serializer_class = LoteSerializer