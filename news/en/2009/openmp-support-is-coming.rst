Title: OpenMP support is coming
Author: prokoudine
Category: Events
Date: 2009-01-02

Those Inkscape users who tend to create complex drawings with a lot of blur know that the application easily becomes less reponsive.

Recently our former GSoC student Jasper van der Gronde started working on support for OpenMP which is an API for programming applications that can make use of several CPU available in a system instead of just one. Jasper started with Gaussian blur which is by far most widely used SVG filter primitive. With OpenMP in use rendering speedup on a dual-core system is reported to be 40-50%. While Inkscape doesn't have a truly threaded design yet, such an improvement will definitely make the application a lot more useful.

If you have experience of creating complex threaded applications and willing to help, don't hesitate to do so. Drop to `inkscape-devel`_ mailing list and let us know.

.. _inkscape-devel: http://lists.sourceforge.net/mailman/listinfo/inkscape-devel