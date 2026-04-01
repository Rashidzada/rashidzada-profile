from django import template

from website.image_utils import resolve_image_src


register = template.Library()


@register.filter
def asset_url(value):
    return resolve_image_src(value)
