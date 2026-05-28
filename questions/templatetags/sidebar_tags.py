from django import template

from questions.services import get_best_members, get_popular_tags

register = template.Library()


@register.inclusion_tag('particles/sidebar_tags.html')
def popular_tags():
    return {'tags': get_popular_tags()}


@register.inclusion_tag('particles/sidebar_members.html')
def best_members():
    return {'members': get_best_members()}
