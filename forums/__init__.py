
default_app_config = 'forums.app.ForumsConfig'

def get_form():
    """Replace to django_comments form with our own"""
    from forums.forms import AddCommentForm
    return AddCommentForm

