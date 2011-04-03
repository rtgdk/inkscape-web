Title: Google Summer of Code 2009 results
Author: prokoudine
Category: Events
Date: 2009-09-09


Google Summer of Code 2009 is now over and here are the results for Inkscape organization.

Krzysztof Kosinski has completely rewritten the Node Tool which now supports node editing for more than one path at a time and thus has a number of extra features. E.g. you will be able scale/rotate/skew a selection of nodes on-canvas and join nodes from different paths.

Arcadie Cracan has expanded the functionality of the Connector Tool. The Connector Tool now supports the adding and removing of user-placed connection points. The user can now toggle between either be polyline or orthogonal connectors. The connectors now support user-defined rounding of corners. Additionally there have been numerous other enhancements and bugfixes.

Felipe Sanches worked on better support for color management. The most noticeable changes are out-of-gamut display and color managed view in the `Fill and Stroke` dialog. Inkscape now checks whether colors picked in the RGB, HSL, CMYK selectors are in or out of gamut for a color space defined by a chosen color profile. There also are some changes with regards to how colors are stored internally.

Soren Berg has added a scripting API via D-Bus. You can read `his older proposal`_ to get an idea.

All these features and more will be added to 0.48.


.. _his older proposal: http://www.cs.grinnell.edu/~bergsore/inkscapeDbusRef.html
