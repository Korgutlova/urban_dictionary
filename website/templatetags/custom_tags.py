from django import template

from website.models import Favorites

register = template.Library()


@register.simple_tag
def is_favoured(definition, user):
    if Favorites.objects.filter(user=user.custom_user, definition=definition).exists():
        return "favoritesadded"
    else:
        return "favorites"
