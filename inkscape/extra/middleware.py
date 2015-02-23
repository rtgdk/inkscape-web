
from django.utils.translation import ugettext_lazy as _

class AutoBreadcrumbMiddleware(object):
    """
    This middleware controls and inserts some breadcrumbs
    into most pages. It attempts to navigate object hierachy
    to find the parent 
    """
    def process_template_response(self, request, response):
        if 'breadcrumbs' not in response.context_data:
            d = response.context_data
            if hasattr(d, 'dicts'):
                d = {}
                for dic in response.context_data.dicts:
                    d.update(dic)
            response.context_data['breadcrumbs'] = self._crumbs(**d)
        return response

    def _crumbs(self, object=None, object_list=None, action=None, **kwargs):
        yield ('/', _('Home'))
        if object is not None:
            for obj in self._ancestors(object):
                if hasattr(obj, 'get_absolute_url'):
                    yield (obj.get_absolute_url(), self._name(obj))
                else:
                    yield (None, self._name(obj))
        if action:
            yield (None, _(action))

    def _ancestors(self, obj):
        if hasattr(obj, 'parent') and obj.parent:
            for parent in self._ancestors(obj.parent):
                yield parent
        yield obj

    def _name(self, obj):
        if hasattr(obj, 'breadcrumb_name'):
            return obj.breadcrumb_name()
        elif hasattr(obj, 'name'):
            return obj.name
        return unicode(obj)

