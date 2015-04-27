
from django.utils.text import slugify
from django.db.models import Q


def set_slug(obj, field='slug', target='name'):
    """Sets a slug attribute smartly"""
    old_slug = getattr(obj, field)
    slug = old_slug.rsplit('+', 1)[0] if old_slug else 'SNAIL'
    snail = slugify(getattr(obj, target))
    if slug == 'SNAIL' or slug != snail:
        qs = Q(slug=snail) | Q(slug__startswith=snail+'+')
        slugs = type(obj).objects.filter(qs).values_list('slug', flat=True)
        for x in range(len(slugs)):
            if snail+'+'+str(x) not in slugs:
                snail = snail+'+'+str(x)
                break
        setattr(obj, field, snail)
    return getattr(obj, field)
    

