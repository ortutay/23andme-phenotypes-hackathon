from django import template

register = template.Library()


@register.filter
def ph_id(value):
    return value.replace("_", " ").replace('facebook', 'Facebook').replace('fitbit', 'FitBit')
