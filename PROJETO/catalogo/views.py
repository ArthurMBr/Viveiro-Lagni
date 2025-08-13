# catalogo/views.py

import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .utils import get_cart, save_cart
from produtos.models import Produto
from django.contrib import messages
from django.db import transaction
from pedidos.models import Pedido, ItemPedido
from lotes.models import Lote
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.core.exceptions import ValidationError

# A importação do modelo Cliente foi removida.

# --- Funções do Carrinho ---

def get_cart_item_count(request):
    """
    Retorna a contagem total de itens no carrinho.
    """
    cart = get_cart(request)
    count = sum(item.get('quantidade', 0) for item in cart.values())
    return JsonResponse({'count': count})

@require_http_methods(["POST"])
def adicionar_ao_carrinho(request):
    """
    Adiciona um produto ao carrinho de compras.
    """
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Requisição inválida.'}, status=400)

    try:
        produto_id = request.POST.get('produto_id')
        quantidade = int(request.POST.get('quantidade', 1))

        produto = get_object_or_404(Produto, pk=produto_id)

        if quantidade <= 0:
            return JsonResponse({'success': False, 'message': 'A quantidade deve ser maior que zero.'}, status=400)

        cart = get_cart(request)
        item_key = str(produto.id)

        quantidade_no_carrinho = cart.get(item_key, {}).get('quantidade', 0)
        nova_quantidade_total = quantidade_no_carrinho + quantidade

        if produto.estoque < nova_quantidade_total:
            return JsonResponse({'success': False, 'message': f'Quantidade insuficiente em estoque para o produto {produto.variedade}. Disponível: {int(produto.estoque)} (já existem {quantidade_no_carrinho} no carrinho).'}, status=400)

        if item_key in cart:
            cart[item_key]['quantidade'] = nova_quantidade_total
        else:
            imagem_url = produto.imagem.url if produto.imagem else None
            
            cart[item_key] = {
                'produto_id': produto.id,
                'variedade': produto.variedade,
                'quantidade': quantidade,
                'preco_unitario': produto.preco,
                'subtotal': produto.preco * quantidade,
                'imagem_url': imagem_url,
            }

        save_cart(request, cart)
        return JsonResponse({'success': True, 'message': 'Produto adicionado ao carrinho com sucesso!', 'cart_count': sum(item.get('quantidade', 0) for item in cart.values())})

    except ValueError:
        return JsonResponse({'success': False, 'message': 'Quantidade inválida.'}, status=400)
    except Produto.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Produto não encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Ocorreu um erro interno: {str(e)}'}, status=500)

@require_http_methods(["POST"])
def remover_do_carrinho(request):
    """
    Remove um produto do carrinho de compras.
    """
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Requisição inválida.'}, status=400)

    item_key = request.POST.get('item_key')
    cart = get_cart(request)

    if item_key in cart:
        del cart[item_key]
        save_cart(request, cart)
        return JsonResponse({'success': True, 'message': 'Produto removido do carrinho.', 'cart_count': sum(item.get('quantidade', 0) for item in cart.values())})
    else:
        return JsonResponse({'success': False, 'message': 'Item não encontrado no carrinho.'}, status=404)


@require_http_methods(["POST"])
def atualizar_quantidade_carrinho(request):
    """
    Atualiza a quantidade de um produto no carrinho.
    """
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Requisição inválida.'}, status=400)

    try:
        item_key = request.POST.get('item_key')
        nova_quantidade = int(request.POST.get('quantidade'))
        cart = get_cart(request)

        if item_key not in cart:
            return JsonResponse({'success': False, 'message': 'Item não encontrado no carrinho.'}, status=404)

        if nova_quantidade <= 0:
            del cart[item_key]
            save_cart(request, cart)
            return JsonResponse({'success': True, 'message': 'Item removido do carrinho.', 'cart_count': sum(item.get('quantidade', 0) for item in cart.values())})
        
        produto = get_object_or_404(Produto, pk=item_key)

        if produto.estoque < nova_quantidade:
            return JsonResponse({'success': False, 'message': f'Quantidade insuficiente em estoque para o produto {produto.variedade}. Disponível: {int(produto.estoque)}'}, status=400)

        cart[item_key]['quantidade'] = nova_quantidade
        
        preco_unitario_decimal = Decimal(cart[item_key]['preco_unitario'])
        cart[item_key]['subtotal'] = str(preco_unitario_decimal * nova_quantidade)

        save_cart(request, cart)
        
        total_carrinho = sum(Decimal(item['preco_unitario']) * item['quantidade'] for item in cart.values())

        return JsonResponse({
            'success': True,
            'message': 'Quantidade atualizada com sucesso.',
            'new_subtotal': cart[item_key]['subtotal'],
            'total_carrinho': str(total_carrinho),
            'cart_count': sum(item.get('quantidade', 0) for item in cart.values())
        })

    except ValueError:
        return JsonResponse({'success': False, 'message': 'Quantidade inválida.'}, status=400)
    except Produto.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Produto não encontrado para verificação de estoque.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Ocorreu um erro interno: {str(e)}'}, status=500)


def carrinho_detalhe(request):
    carrinho_da_sessao = get_cart(request)
    itens_carrinho = []
    total_carrinho = Decimal('0.00')

    itens_para_remover = []
    
    for item_key, item_data in list(carrinho_da_sessao.items()):
        try:
            produto = get_object_or_404(Produto, pk=item_data['produto_id'])
            item_data['produto'] = produto 

            subtotal_decimal = Decimal(str(item_data['subtotal']))
            item_data['subtotal'] = subtotal_decimal
            
            itens_carrinho.append(item_data)
            
            total_carrinho += subtotal_decimal

        except (Produto.DoesNotExist, ValueError, TypeError) as e:
            print(f"Erro ao carregar produto para o carrinho. Item inválido encontrado: {e}")
            itens_para_remover.append(item_key)

    for item_key in itens_para_remover:
        del carrinho_da_sessao[item_key]

    if itens_para_remover:
        request.session.modified = True

    context = {
        'itens_carrinho': itens_carrinho,
        'total_carrinho': total_carrinho,
    }
    return render(request, 'catalogo/carrinho_detalhe.html', context)


def carrinho_detalhe_ajax(request):
    """
    Retorna o conteúdo HTML do carrinho para atualização via AJAX (carrinho lateral).
    """
    cart = get_cart(request)
    itens_carrinho = []
    total_carrinho = Decimal('0.00')

    for item_key, item_data in list(cart.items()):
        produto_id = item_data['produto_id']
        try:
            produto = Produto.objects.get(id=produto_id)
            
            preco_unitario_decimal = Decimal(item_data['preco_unitario'])
            quantidade_int = item_data['quantidade']
            subtotal_item = preco_unitario_decimal * quantidade_int
            total_carrinho += subtotal_item

            itens_carrinho.append({
                'item_key': item_key,
                'produto_id': produto.id,
                'variedade': produto.variedade,
                'quantidade': quantidade_int,
                'preco_unitario': str(preco_unitario_decimal),
                'imagem_url': produto.imagem.url if produto.imagem else None,
                'subtotal': str(subtotal_item),
            })
        except Produto.DoesNotExist:
            del cart[item_key]
            save_cart(request, cart)
            continue
        except Exception as e:
            print(f"Erro ao processar item {item_key} no carrinho_detalhe_ajax: {str(e)}")
            del cart[item_key]
            save_cart(request, cart)
            continue

    html_content = render(request, 'catalogo/_cart_content.html', {
        'itens_carrinho': itens_carrinho,
        'total_carrinho': total_carrinho
    }).content.decode('utf-8')

    return JsonResponse({'success': True, 'html': html_content, 'total_carrinho': str(total_carrinho)})


def lista_produtos(request):
    """
    Exibe a lista de todos os produtos disponíveis.
    """
    produtos = Produto.objects.all().order_by('variedade')

    context = {
        'produtos': produtos,
    }
    return render(request, 'catalogo/lista_produtos.html', context)

def obter_conteudo_carrinho(request):
    cart = get_cart(request)
    itens_carrinho = []
    total_carrinho = Decimal('0.00')
    item_count = 0

    for item_key, item_data in cart.items():
        produto = get_object_or_404(Produto, id=item_data['produto_id'])
        quantidade = item_data['quantidade']
        preco_unitario = Decimal(item_data['preco_unitario'])
        subtotal = preco_unitario * quantidade
        total_carrinho += subtotal
        item_count += quantidade

        itens_carrinho.append({
            'item_key': item_key,
            'produto': produto,
            'variedade': produto.variedade,
            'preco_unitario': preco_unitario,
            'quantidade': quantidade,
            'subtotal': subtotal,
            'imagem_url': produto.imagem.url if produto.imagem else None
        })

    context = {
        'itens_carrinho': itens_carrinho,
        'total_carrinho': total_carrinho,
        'item_count': item_count,
    }
    html_content = render(request, 'catalogo/_cart_content.html', context).content.decode('utf-8')
    return JsonResponse({
        'html': html_content,
        'total_carrinho': str(total_carrinho),
        'item_count': item_count
    })


@require_POST
def finalizar_compra(request):
    """
    Processa a finalização da compra, criando um Pedido e ItensPedido.
    Deduz a quantidade do estoque e limpa o carrinho da sessão.
    O pedido é criado sem um cliente associado, pois o modelo `Cliente` foi removido.
    """
    carrinho = get_cart(request)

    if not carrinho:
        messages.error(request, "Seu carrinho está vazio. Adicione produtos antes de finalizar a compra.")
        return JsonResponse({'success': False, 'message': 'Carrinho vazio.'})

    try:
        with transaction.atomic():
            novo_pedido = Pedido.objects.create(
                status='PENDENTE',
            )

            for item_key, item_data in carrinho.items():
                produto = get_object_or_404(Produto, id=item_data['produto_id'])
                quantidade_pedida = item_data['quantidade']
                preco_unitario_item = Decimal(item_data['preco_unitario'])

                # Encontrar o lote mais apropriado para o produto
                lote_usado = Lote.objects.filter(
                    produto=produto,
                    quantidade__gte=quantidade_pedida,
                    ativo=True
                ).order_by('data_validade').first()

                if not lote_usado:
                    raise ValidationError(f"Estoque insuficiente para o produto {produto.variedade}.")

                ItemPedido.objects.create(
                    pedido=novo_pedido,
                    produto=produto,
                    lote=lote_usado,
                    quantidade=quantidade_pedida,
                    preco_unitario=preco_unitario_item,
                )

                # Deduz a quantidade do lote
                lote_usado.quantidade -= quantidade_pedida
                lote_usado.save()

            del request.session['carrinho']
            request.session.modified = True

            messages.success(request, f"Seu pedido #{novo_pedido.id} foi finalizado com sucesso!")

            return JsonResponse({'success': True, 'message': 'Pedido finalizado com sucesso!', 'redirect_url': reverse('catalogo:lista_produtos')})

    except ValidationError as e:
        messages.error(request, f"Erro de validação: {e.message}")
        return JsonResponse({'success': False, 'message': f"Erro de validação: {e.message}"}, status=400)
    except Exception as e:
        messages.error(request, f"Ocorreu um erro ao finalizar o pedido: {e}")
        return JsonResponse({'success': False, 'message': f"Erro interno: {e}"}, status=500)

# As views `processar_finalizacao` e `processar_pagamento` foram removidas pois dependiam do modelo Cliente.