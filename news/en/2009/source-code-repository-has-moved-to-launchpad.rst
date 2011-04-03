Title: Source code repository has moved to Launchpad
Author: prokoudine
Category: Community
Date: 2009-12-09


Following the switch to Launchpad for a new bug tracker and blueprints last year we just have moved our source code repository to Launchpad too. This will make both bug tracking and managing branches quite a bit easier. The repository now uses version control system called bazaar-ng instead of Subversion.

To fetch the main branch where most development happens you need to run (on Linux):

``$ bzr branch lp:inkscape``

To update your local copy of the branch inside root 'inkscape' directory run:

``$ bzr pull``

Since releasing 0.47 the main branch features now a new Airbrush tool, a much improved Connector and various color management related improvements. Our traditional daily snapshots are currently behind the time. We'll figure out how to best reorganize them and then we will let you know.

We thank SourceForge for being our respected source code host for all these years.


