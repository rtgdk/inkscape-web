#  Based on: http://www.djangosnippets.org/snippets/73/
#
#  Modified by Sean Reifschneider to be smarter about surrounding page
#  link context.  For usage documentation see:
#
#     http://www.tummy.com/Community/Articles/django-pagination/
#
#  Modified further by Chris Morgan for simpler usage, and with a Paginator.

from django import template

register = template.Library()

@register.inclusion_tag('paginator.html')
def paginator(page, adjacent_pages=4):
    """
    Creates a nice paginator display given a page from a Paginator.
    """

    start_page = max(page.number - adjacent_pages, 1)
    if start_page <= 2:
        start_page = 1

    end_page = page.number + adjacent_pages + 1
    if end_page >= page.paginator.num_pages - 1:
        end_page = page.paginator.num_pages + 1

    page_numbers = [n for n in range(start_page, end_page)
            if 1 <= n <= page.paginator.num_pages]

    return {
        'page': page,
        'paginator': page.paginator,
        'page_numbers': page_numbers,
        'show_first': 1 not in page_numbers,
        'show_last': page.paginator.num_pages not in page_numbers,
    }
