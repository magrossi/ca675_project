from django import template

register = template.Library()


@register.inclusion_tag('tags/header.html', takes_context=True)
def header(context):
    return {
        'user': context.get('user'),
        'prefix': context.get('request').path == '/' and ' ' or '/',
    }


@register.simple_tag()
def multiply_100(number, *args, **kwargs):
    return "{0:.2f}".format(number * 100)
