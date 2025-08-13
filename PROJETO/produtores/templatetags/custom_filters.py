# PROJETO/produtores/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    """
    Adiciona classes CSS a um widget de campo de formulário Django.
    Uso: {{ field|add_class:"form-control my-class" }}
    """
    return value.as_widget(attrs={'class': arg})

@register.filter(name='get_field')
def get_field(form, field_name):
    """
    Retorna um campo específico de um formulário pelo seu nome.
    Uso: {% with field=form|get_field:"campo_nome" %}{{ field.label_tag }}{% endwith %}
    """
    try:
        return form[field_name]
    except KeyError:
        return None