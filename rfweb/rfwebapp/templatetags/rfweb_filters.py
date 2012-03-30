from django import template
from django.template.defaultfilters import stringfilter

#assert False, dir(template)
register = template.Library()

@register.filter
@stringfilter
def nbsp(value):
    return value.replace(' ', '&nbsp;')

@register.filter
@stringfilter
def first_line(value):
    return value.split('\n')[0]

@register.filter
@stringfilter
def eol(value):
    return value.replace('\n', '<br>').replace('\\n', '<br>')

