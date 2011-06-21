from collections import namedtuple, OrderedDict
from django.http import Http404
from django.views.generic.simple import direct_to_template
from django.utils.translation import ugettext_lazy as _

Screenshot = namedtuple('Screenshot', ('filename', 'description'))

model_values = OrderedDict((
        ('0.48', (
            Screenshot('inkscape-0.48-webdesign-text.png', '''<p>Inkscape 0.48 has brought many improvements to the Text Tool. There are now controls for superscript, subscript, line spacing, letter spacing, word spacing, horizontal kerning, vertical kerning, and rotation. Thanks to <a href="http://developmentseed.org/">Development Seed</a> for contributing this screenshot.</p>'''),
            Screenshot('inkscape-0.48-multipath.png', '''<p>After many years and countless requests, Inkscape 0.48 now supports editing multiple paths at the same time. Previously editing with the Node Tool had a limitation of working with only one path at a time. Thanks to <a href="http://happyline.deviantart.com/">happyline</a> for the wonderful example screenshot.</p>'''),
            Screenshot('inkscape-0.48-moonlight-views.png', '''<p>Inkscape 0.48 has added a Spray Tool to quickly and easily spray multiple copies of items. With the parameters for rotation and size it allows creating effects that previously would take much longer to achieve. Thanks to <a href="http://www.sweetpsychoid-studio.com/">DiSmeCha</a> for contributing this screenshot.</p>'''),
            Screenshot('inkscape-0.48-ferrari.png', '''<p>This illustration of a Ferrari by <a href="http://www.flickr.com/photos/35772571@N03/">Gilles Pinard</a> was done by hand without any tracing. Gradients, blurs, and other various other techniques really bring this image to life.</p>'''),
            Screenshot('inkscape-0.48-blur.png', '''<p>Inkscape 0.48 now has a preference that allows users to take advantage of multi-threading for the Gaussian Blur filter. This filter makes one of the biggest impacts on Inkscape's performance when in use. <a href="http://haruwen.deviantart.com">Mariana Sing</a> uses blur throughout this image for subtle details, smooth color transitions, and numerous effects. Thankfully the blur operation is now faster than before when using a multi-core or multi-processor computer.</p>'''),
            )),
        ('0.47', ()),
        ('0.46', ()),
        ('0.45', ()),
        ('0.44', ()),
        ('0.43', ()),
        ('0.42', ()),
        ('0.41', ()),
        ('0.40', ()),
        ('0.39', ()),
        ('0.38', ()),
        ('0.37', ()),
        ))


def screenshots(request, version=None):
    if version is None:
        version = model_values.keys()[0]
    elif version not in model_values:
        raise Http404('No screenshots for version %r.' % version)

    return direct_to_template(request, 'screenshots.html', {'title': _('Inkscape screenshots'), 'pagetitle': _('Inkscape screenshots'), 'screenshots': model_values[version], 'versions': model_values.keys(), 'version': version})
