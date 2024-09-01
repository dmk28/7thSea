from django.http import Http404
from django.shortcuts import render
from django import template
from django.utils.safestring import mark_safe
from evennia.utils.ansi import parse_ansi


def render_to_response(request, template, context=None):
    """
    Wrapper for render() that catches Http404 errors and renders a 404 page.
    """
    try:
        return render(request, template, context)
    except Http404:
        return render(request, '404.html', context, status=404)

register = template.Library()

@register.filter
def mush_to_html(value):
    if not value:
        return value
    value = value.replace("&", "&amp")
    value = value.replace("<", "&lt")
    value = value.replace(">", "&gt")
    value = value.replace("%r", "<br>")
    value = value.replace("%R", "<br>")
    value = value.replace("\n", "<br>")
    value = value.replace("%b", " ")
    value = value.replace("%t", "&nbsp&nbsp&nbsp&nbsp")
    value = value.replace("|/", "<br>")
    value = value.replace("{/", "<br>")
    value = parse_ansi(value, strip_ansi=True)
    return mark_safe(value)



