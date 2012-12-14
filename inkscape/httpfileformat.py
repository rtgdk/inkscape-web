class HttpFormatFile(dict):
    """
    Simple parser for files or strings in the style of HTTP requests with a
    header block and body. Stores headers in items - self['Header-Name'] - and
    the body in self.body.
    """

    __slots__ = ('body',)

    def __init__(self, file_name_or_handle):
        super(HttpFormatFile, self).__init__()
        if isinstance(file_name_or_handle, basestring):
            handle = open(file_name_or_handle, 'U')
        else:
            handle = file_name_or_handle

        for line in handle:
            if line == '\n':
                break
            try:
                key, value = line.rstrip('\n').split(': ')
            except ValueError:
                raise ValueError('Invalid file format.')
            self[key] = value
        else:
            raise ValueError('Invalid file format.')

        self.body = ''
        for line in handle:
            self.body += line

    def __repr__(self):
        return '<HttpFormatFile with headers %s>' % super(HttpFormatFile,
                self).__repr__()

    def __unicode__(self):
        return '\n'.join('%s: %s' % i for i in self.iteritems()) + '\n\n' + self.body

    def __str__(self):
        return str(unicode(self))
