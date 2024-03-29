from cms.models.pages import HomePage
from django import template
from django.conf import settings
from wagtail.core.models import Page
from django.utils.safestring import mark_safe
import json as jsn

register = template.Library()


@register.filter
def get_section(current_page):
    '''Returns the highest ancestor of current_page'''
    homepage = HomePage.objects.first()
    current_section = Page.objects.ancestor_of(current_page, inclusive=True)\
        .child_of(homepage).first()
    return current_section


@register.filter
def order_by(queryset, field):
    return queryset.order_by(field)


@register.filter
def next(some_list, current_index):
    """
    Returns the next element of the list using the current index if it exists.
    Otherwise returns an empty string.
    """
    try:
        return some_list[int(current_index) + 1]  # access the next element
    except Exception:
        return ''  # return empty string in case of exception


@register.filter
def previous(some_list, current_index):
    """
    Returns the previous element of the list using the current
    index if it exists. Otherwise returns an empty string.
    """
    try:
        return some_list[int(current_index) - 1]  # access the previous element
    except Exception:
        return ''  # return empty string in case of exception


@register.filter
def json(python_var):
    """
    returns the json version of the python_var
    """
    return mark_safe(jsn.dumps(python_var))


@register.simple_tag
def are_comments_allowed():
    """Returns True if commenting on the site is allowed, False otherwise."""
    return getattr(settings, 'ALLOW_COMMENTS', False)


@register.simple_tag(takes_context=True)
def get_site_root(context):
    """Returns the site root Page, not the implementation-specific model used.
    Object-comparison to self will return false as objects would differ.

    :rtype: `wagtail.wagtailcore.models.Page`
    """
    return context['request'].site.root_page


@register.simple_tag
def has_view_restrictions(page):
    """Returns True if the page has view restrictions set up, False
    otherwise."""
    return page.view_restrictions.count() > 0


@register.inclusion_tag('cms/tags/main_menu.html', takes_context=True)
def main_menu(context, root, current_page=None):
    """Returns the main menu items, the children of the root page. Only live
    pages that have the show_in_menus setting on are returned. """
    menu_pages = []
    live_pages = root.get_descendants().live().specific()

    root.active = (current_page.url == root.url
                   if current_page else False)

    for page in live_pages:
        if page.show_in_main_menu:
            page.active = (current_page.url.startswith(page.url)
                           if current_page else False)
            menu_pages.append(page)

    return {'request': context['request'], 'root': root,
            'current_page': current_page, 'menu_pages': menu_pages}


@register.inclusion_tag('cms/tags/sub_menu.html', takes_context=True)
def sub_menu(context, root):
    """Returns the sub menu items, the children of the root page. Only live
    pages that have the show_in_menus setting on are returned."""
    menu_pages = root.get_children().live().in_menu()

    return {'request': context['request'], 'root': root,
            'menu_pages': menu_pages}
