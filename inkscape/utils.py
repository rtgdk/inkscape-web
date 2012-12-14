
import os
import sys
import logging
import email


def get_bzr_version(project_dir, debug):
    """return the bzr revision number and version of the project"""

    version_file = os.path.join(project_dir, 'version')
    if not os.path.exists(version_file):
        return ("version unknown", 0)

    emai_msg = email.message_from_file(open(version_file))
    version = emai_msg["version"]
    bzr_revno = emai_msg["revno"]
    inkscape = emai_msg["inkscape"]

    if debug:
        try:
            from bzrlib.branch import Branch
            branch = Branch.open_containing('.')[0]
            bzr_revno = branch.revno()
        except:
            pass

    return ("version %s (rev %s)" % (version, bzr_revno), inkscape)
