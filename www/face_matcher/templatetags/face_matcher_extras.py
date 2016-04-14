from django import template

register = template.Library()


@register.inclusion_tag('tags/header.html', takes_context=True)
def header(context):
    return {
        'user': context.get('user'),
        'prefix': context.get('request').path == '/' and ' ' or '/',
    }


@register.inclusion_tag('tags/footer.html')
def footer(block_class=''):
    return {'block_class': block_class}


@register.simple_tag()
def multiply_100(number, *args, **kwargs):
    return "{0:.2f}".format(float(number) * 100)


@register.simple_tag()
def calc_time(history):
    value = (history.finished_at - history.created_at).total_seconds()
    unit = 'sec'
    if value < 1:
        value = int(value * 1000)
        unit = 'ms'
        return '{0} {1}'.format(value, unit)
    elif value >= 60:
        value /= 60
        unit = 'min'
    return '{0:.2f} {1}'.format(value, unit)


@register.simple_tag()
def status_label_class(status):
    if status == 'P':
        return 'warning'
    if status == 'R':
        return 'info'
    if status == 'F':
        return 'success'
    return 'danger'
