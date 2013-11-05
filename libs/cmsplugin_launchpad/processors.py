#
# Copyright 2013(c) Martin Owens <mail@doctormo.org>
#
# Licensed: AGPLv3
#


def match(p, ps):
    for (v, n) in ps:
        if n == p or v == p:
            return v
    return None

_lp = None
def launchpad():
    global _lp
    if not _lp:
        from launchpadlib.launchpad import Launchpad
        _lp = Launchpad.login_anonymously('inkscape-website', 'production')
    return _lp


