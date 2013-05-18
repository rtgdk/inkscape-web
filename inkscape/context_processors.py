
from django.conf import settings

def design(request):
    """
    Adds static-related context variables to the context.
    """
    return {'DESIGN_URL': settings.DESIGN_URL}