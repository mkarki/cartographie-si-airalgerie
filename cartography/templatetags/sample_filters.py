from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    if dictionary is None:
        return ''
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    elif isinstance(dictionary, list):
        # Si c'est une liste, essayer d'accéder par index
        try:
            return dictionary[int(key)] if key.isdigit() else ''
        except (IndexError, ValueError, TypeError):
            return ''
    return ''
