
from django.utils.text import slugify
from django.db.models import Q

def unique_slug(model, proposed, field='slug'):
    """Return a unique slug that doesn't exist already"""
    qs = Q(**{field: proposed}) | Q(**{field+'__startswith': proposed+'+'})
    existing = model.objects.filter(qs).values_list(field, flat=True)

    for increment in [u'%s+%d' % (proposed, x) for x in range(len(existing))]:
        if increment not in existing:
            return increment
    return proposed


def set_slug(obj, field='slug', source='name'):
    """Sets a slug attribute smartly"""

    original = (getattr(obj, field, '') or '').rsplit('+', 1)[0]
    proposed = slugify(unicode(getattr(obj, source)))

    if not original or proposed != original:
        setattr(obj, field, unique_slug(type(obj), proposed, field=field))

    return getattr(obj, field)
    

