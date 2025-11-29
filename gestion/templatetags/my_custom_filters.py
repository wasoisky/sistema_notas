# gestion/templatetags/my_custom_filters.py
from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Permite acceder a un valor de diccionario usando una clave dinámica."""
    # Usamos .get() para evitar errores si la clave no existe
    return dictionary.get(key)