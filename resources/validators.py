"""
Some custom fields for storing and testing ranges.
"""

from django.db.models import CharField


class CsvList(list):
    def __init__(self, value):
        if value is not None:
            for item in value.split(','):
                self.append(item)

    def __str__(self):
        return ','.join(self)

    def __contains__(self, value):
        if len(self) == 0:
            return True
        return super(CsvList, self).__contains__(value)


class Range(list):
    scales = [
        dict((c, 10 ** (x * 3)) for (x, c) in enumerate(' KMGT')),
        dict((c, 2 ** (x * 10)) for (x, c) in enumerate(' KMGT')),
    ]

    def __init__(self, value, other=None):
        if value not in [None, '']:
            for item in str(value).split('-', 1):
                self.append(self._scale(item))
        if other is not None and len(self) == 1:
            self.append(self._scale(str(other)))
        self.sort()


    def _scale(self, value):
        """Scale the value to Kilo, mega etc units"""
        value = str(value).upper()
        scale = self.scales['B' in value]
        value = value.replace('B', '').strip()
        if value[-1] in ['K', 'M', 'G', 'T']:
            return int(value[:-1]) * scale[value[-1]]
        return int(value)

    def _descale(self, value):
        """Scale the value back and append unit if exactly divisible"""
        for char in 'TGMK':
            for (is_bytes, scale) in enumerate(self.scales):
                extra = 'B' if is_bytes else ''
                if value % scale[char] == 0:
                    return "%d%s%s" % (value / scale[char], char.strip(), extra)
        return str(value)

    __contains__ = lambda self, value: len(self) == 0 or not (value > self or value < self)
    __gt__ = lambda self, val: len(self) == 0 or self._scale(val) < min(self)
    __lt__ = lambda self, val: len(self) == 0 or self._scale(val) > max(self)
    __ge__ = lambda self, val: len(self) == 0 or self._scale(val) <= min(self)
    __le__ = lambda self, val: len(self) == 0 or self._scale(val) >= max(self)
    __str__ = lambda self: '-'.join(self._descale(v) for v in self)
    __repr__ = lambda self: "Range('%s')" % str(self)

    to_max = lambda self: self._descale(max(self))
    to_min = lambda self: self._descale(min(self))

