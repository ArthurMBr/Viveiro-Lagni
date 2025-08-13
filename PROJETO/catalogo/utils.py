# catalogo/utils.py
import json

def get_cart(request):
    """
    Recupera o carrinho da sessão. Se não existir, retorna um dicionário vazio.
    Trata o caso em que o 'cart' pode ser um dicionário diretamente ou uma string JSON.
    """
    cart_data = request.session.get('cart')

    if isinstance(cart_data, dict):
        # Se já é um dicionário (pode acontecer em certas condições de sessão)
        return cart_data
    elif isinstance(cart_data, str) and cart_data:
        # Se é uma string não vazia, tente carregar como JSON
        try:
            return json.loads(cart_data)
        except json.JSONDecodeError:
            # Em caso de JSON inválido, retorna carrinho vazio ou loga erro
            print("WARNING: Dados do carrinho na sessão são JSON inválidos. Reiniciando carrinho.")
            return {}
    else:
        # Se for None ou string vazia, retorna um dicionário vazio
        return {}

def save_cart(request, cart):
    """
    Salva o carrinho na sessão como uma string JSON.
    """
    request.session['cart'] = json.dumps(cart)