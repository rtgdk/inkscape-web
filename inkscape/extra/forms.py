
from django.utils.translation import ugettext_lazy as _
from django.forms import *

class FeedbackForm(Form):
    comment = CharField(
        widget=Textarea(attrs={
            'placeholder': 'Your comments or questions...'
        }), required=True )


