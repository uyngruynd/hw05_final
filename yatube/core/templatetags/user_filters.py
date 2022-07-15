from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """Собственный фильтр для применения в шаблонах проекта."""
    return field.as_widget(attrs={'class': css})
