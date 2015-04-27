
from social_auth.backends.pipeline.social import social_auth_user
from social_auth.backends.google import GoogleBackend

def migrate_from_openid(backend, **kwargs):
    """Attempt to attach google openid clients to google-oauth2 clients"""
    if backend.name != 'google-oauth2':
        return None
    ret = social_auth_user(backend=GoogleBackend(), **kwargs)
    if ret.get('social_user', None):
        ret['social_user'].provider = 'google-oauth2'
    return ret

