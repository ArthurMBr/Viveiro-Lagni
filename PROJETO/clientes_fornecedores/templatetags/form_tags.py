from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    """
    Adiciona classes CSS a um campo de formulário do Django.
    Uso: {{ form.my_field|add_class:"my-class other-class" }}
    """
    return value.as_widget(attrs={'class': arg})

@register.filter(name='attr')
def attr(value, arg):
    """
    Adiciona um atributo HTML a um campo de formulário do Django.
    Uso: {{ form.my_field|attr:"placeholder:My Placeholder" }}
    """
    attrs = {}
    if ':' in arg:
        key, val = arg.split(':', 1)
        attrs[key] = val
    else:
        attrs[arg] = ''
    
    return value.as_widget(attrs=attrs)