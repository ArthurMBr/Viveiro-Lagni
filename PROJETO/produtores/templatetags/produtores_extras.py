# produtores/templatetags/produtores_extras.py
from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Permite acessar um item de um dicionário por uma chave no template.
    Ex: {{ my_dict|get_item:my_key }}
    """
    return dictionary.get(key)

@register.filter(name='unset')
def unset_session_key(session, key):
    """
    Remove uma chave da sessão. Usado para limpar flags após uso.
    """
    if key in session:
        del session[key]
    return ''