from django import template

register = template.Library()

# Used to create the generated link url for the templates
@register.filter
def get_link_filter(obj, arg):
    base = obj.get_link(arg)
    return base

# Used to create the base url of the generated link for the templates
@register.filter
def get_base_link_filter(obj):
    base = obj.get_base_link()
    return base