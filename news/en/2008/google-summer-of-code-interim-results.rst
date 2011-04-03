Title: Google Summer of Code interim results
Author: prokoudine
Category: Events
Date: 2008-07-30


Here are results of midterm evaluation of five Inkscape's projects at Google Summer of Code 2008 program.

- **SVG Fonts**, by Felipe Corrêa da Silva Sanches. Thanks to his work Inkscape can already render glyphs that are decribed using the **d** (path description) attribute, but not those described by arbitrary SVG fragments. Glyph kerning is also supported now. Cairo user fonts feature is used for rendering on an auxiliary GtkWindow, since libpango still does not support the user fonts feature. That is a current blocker for on-canvas rendering. The next half of Felipe's SoC project will be more focused on user interface for the SVG Fonts.
- **Lib2geom integration: path representation**, by Johan Engelen. Results aren't so visible and most work is under the hood. He has finished converting the basic path handling to 2geom. This has resulted in much more readable code and has stimulated 2geom development where functionality was lacking or could be improved.
- **lib2geom development**, by Marco Cecchetti. Marco made elliptical arc class compliant to SVG standard with methods implemented natively, created point-curve nearest-point and distance routines specialized for all curve types, added some technical drawing routines and more.
- **Tech Drawing Abilities for Inkscape**, by Maximilian Albert. Maximilian wrote a number of live path effects (LPEs) to simplify geometric constructions and at the same time considerably expanded the underlying LPE framework to make user interaction much easier. Notable enhancements are: handles for parameter adjustment, custom helper paths. This also led to the addition of long-timed anticipated vector brushes to pen and pencil tool.
- **Test Suite**, by Jasper Joris van de Gronde. Jasper has made new unit tests for a number of files related to reading/writing svg's and rendering, and converted any remaining old-style unit tests to the CxxTest framework. And you can now also build the tests on Windows. At the moment I'm working on rendering/verb tests and getting the new tests to build on Linux.

Notably, almost all work work is done in main development branch (trunk) of either Inkscape or lib2geom. Thus most of the new features are likely to be seen in the 0.47 version.