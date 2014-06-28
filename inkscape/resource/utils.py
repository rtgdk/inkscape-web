
try:
    from pygments import highlight, lexers, formatters
    pygments = True
except ImportError:
    pygments = False

from django.utils.safestring import mark_safe

def syntaxer(text):
    if not pygments:
        return text
    formatter = formatters.HtmlFormatter(encoding='utf8')
    lexer = lexers.guess_lexer(text)
    return mark_safe(highlight(text, lexer, formatter))

