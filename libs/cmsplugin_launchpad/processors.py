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

_launchpad = None
def launchpad():
    global _launchpad
    if not _launchpad:
        from launchpadlib.launchpad import Launchpad
        _launchpad = Launchpad.login_anonymously('inkscape-website')
    return _launchpad


