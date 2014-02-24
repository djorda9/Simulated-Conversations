from django import template
#used to get index of arrays in a template....
register = template.Library()
@register.filter
def get_at_index(list, index):
    return list[index]

