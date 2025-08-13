# produtos/templatetags/produto_filters.py
from django import template
from django.template.defaultfilters import slugify

register = template.Library()

@register.filter
def slugify_custom(value):
    """
    Custom slugify para lidar com strings como 'Sem Estoque' para uso em classes CSS.
    Substitui espaços e outros caracteres não alfanuméricos por hífens.
    """
    return slugify(value).replace('-', '_') # Ou mantenha '-', dependendo da sua preferência para nomes de classes.
                                          # Usei '_' para status como 'sem_estoque'.