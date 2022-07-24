from django import template
from posts.models import Group

register = template.Library()


@register.filter
def addclass(field, css):
    """Собственный фильтр для применения в шаблонах проекта."""
    return field.as_widget(attrs={'class': css})


@register.simple_tag
def get_cached_time():
    """Продолжительность кэширования в шаблонах"""
    return 60*15


@register.simple_tag
def get_groups():
    """Полный перечень групп организации навигации в шапке."""
    return Group.objects.all()
