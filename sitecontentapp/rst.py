from docutils.parsers.rst import roles
from docutils import nodes


def wiki_reference_role(role, rawtext, text, lineno, inliner,
                       options={}, content=[]):
    if text.endswith('>'):
        title, page = text[:-1].rsplit('<')
        title = title.rstrip()
    else:
        title = page = text
    ref = 'http://wiki.inkscape.org/wiki/index.php/%s' % page
    roles.set_classes(options)
    return [nodes.reference(rawtext, title, refuri=ref,
                            **options)], [] # title => utils.unescape(title)?

roles.register_local_role('wiki', wiki_reference_role)
roles._roles[''] = wiki_reference_role
