
from django.db.models import signals
from django.dispatch import Signal

post_publish = Signal(providing_args=["instance"])

