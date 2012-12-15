==========================
Frequently Asked Questions
==========================

.. contents:: :local:

General
=======

What is Inkscape?
-----------------

Inkscape is an open-source vector graphics editor similar to Adobe Illustrator,
Corel Draw, Freehand, or Xara X. What sets Inkscape apart is its use of
`Scalable Vector Graphics <http://www.w3.org/Graphics/SVG/>`_ (SVG), an open
XML-based `W3C <http://www.w3.org>`_ standard, as the native format.

What are vector graphics?
-------------------------

In contrast to raster (bitmap) graphics editors such as Photoshop or Gimp,
Inkscape stores its graphics in a vector format.  `Vector graphics
<http://en.wikipedia.org/wiki/Vector_graphics>`_ is a resolution-independent
description of the actual shapes and objects that you see in the image. A
rasterization engine uses this information to determine how to plot each line
and curve at any resolution or zoom level.

Contrast that to `bitmap (raster) graphics
<http://en.wikipedia.org/wiki/Raster_format>`_ which is always bound to a
specific resolution and stores an image as a grid of pixels. 

Vector graphics are a complement, rather than an alternative, to bitmap
graphics. Each has its own purpose and are useful for different kinds of
things. Raster graphics tend to be better for photographs and some kinds of
artistic drawings, whereas vectors are more suitable for design compositions,
logos, images with text, technical illustrations, etc.

Note that Inkscape can import and display bitmap images, too. An imported
bitmap becomes yet another object in your vector graphics, and you can do with
it everything you can do to other kinds of objects (move, transform, clip,
etc.)

What is 'Scalable Vector Graphics'?
-----------------------------------

`Scalable Vector Graphics <http://www.w3.org/Graphics/SVG/>`_ (SVG) is an open,
industry-standard XML-based format for vector graphics developed by the `W3C
<http://www.w3.org>`_. Its acceptance is growing fast. Most vector editors
these days can import and export SVG, and modern browsers (such as Firefox and
Opera) can display it directly, i.e. without requiring any plugins. (For
Internet Explorer, there's an `SVG Viewer
<http://adobe.com/svg/viewer/install/main.html>`_ plugin from Adobe.) For more
information, see `SVG topics`_ below.

Is Inkscape ready for regular users to use?
-------------------------------------------

Yes! While Inkscape does not have all the features of the leading vector
editors, the latest versions provide for a large portion of basic vector
graphics editing capabilities. People report successfully using Inkscape in a
lot of very different projects (web graphics, technical diagrams, icons,
creative art, logos, maps). For example, thousands of images on Wikipedia are
`created with Inkscape
<http://commons.wikimedia.org/wiki/Category:Created_with_Inkscape>`_, as is the
majority of the content on `openclipart <http://openclipart.org/>`_; many
examples of Inkscape art can be seen `on deviantART
<http://inkscape.deviantart.com/favourites/>`_ and `here </galleries>`_. We try
to always keep the codebase usable for real users, as we believe that a tight
iteration cycle between users and developers will give best results.  You can
start using Inkscape alongside your other tools now!

What platforms does Inkscape run on?
------------------------------------

We provide binary packages for Linux, Windows 2000/2003/XP (fully
self-contained installer), and OSX (dmg package).  We know that Inkscape is
successfully used on FreeBSD and other Unix-like operating
systems. Note that Windows 98/ME is no longer supported.

How did Inkscape start?
-----------------------

Inkscape was started as a fork of `Sodipodi
<http://sourceforge.net/projects/sodipodi/>`_, in late 2003, by four Sodipodi
developers: Bryce Harrington, MenTaLguY, Nathan Hurst, and Ted Gould. Our
mission was creating a fully compliant `Scalable Vector Graphics (SVG)
<http://www.w3.org/Graphics/SVG/>`_ drawing tool written in C++ with a new,
more user friendly (`GNOME Human Interface Guidelines (HIG)
<http://library.gnome.org/devel/hig-book/stable/>`_ compliant) interface and an
open, community-oriented development process.  Within several months the
project had produced several releases, demonstrating a sequence of significant
new features and improvements to the codebase and quickly established Inkscape
as a noteworthy Open Source project.

What does 'Inkscape' mean?
--------------------------

The name is made up of the two English words 'ink' and 'scape'.  Ink is a
common substance for drawings, and is used when the sketched work is ready to
be permanently committed to paper, and thus evokes the idea that Inkscape is
ready for production work.  A scape is a view of a large number of objects,
such as a landscape or ocean-scape, and thus alludes to the object-oriented
nature of vector imagery.

Can I create webpages with it?
------------------------------

Sort of.

Many webpage authors use Inkscape for webpage mockups or to generate parts of
web pages, such as banners, logos, icons, and more.

With the recent advances in SVG support in web browsers (such as Firefox or
Opera), using SVG directly on the web becomes more of a possibility. For
example, with Firefox 1.5 or better, you can open any Inkscape SVG document
right in the browser, and Firefox will show it correctly. In theory, SVG and
XHTML can be used together within the same document, so interested users or
developers can explore this possibility further.  

Unfortunately, even though SVG is the internet standard for vector graphics,
some older (but still common) web browsers fail to support SVG.

Web page authors who need to support widest variety of web browsers convert
each SVG graphic to a raster image (.png) as the very last step.

How do I make a SVG object that link to an internet site when I click on it?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can `create clickable links from objects
<http://www.w3.org/TR/SVG/linking.html>`_ in Inkscape by right clicking the
object, and clicking 'Create Link'. Then, right click your new link and choose
'Link Properties' to set the web address and many other properties.

Another way to make objects into web links is to edit the XML directly.  Inside
Inkscape, open the XML editor (Shift+Ctrl+X) ... or use your favorite text
editor.

First look at the <svg> element and try adding the following if it's not there
already::

   xmlns:xlink="http://www.w3.org/1999/xlink"

Then find the object you want people to click on.  Let's say it's a red ellipse
that looks like this in the XML editor::

   <ellipse cx="2.5" cy="1.5" rx="2" ry="1" fill="red" />

Surround that object with the "``a xlink:href``" tag::

   <a xlink:href="">
     <ellipse cx="2.5" cy="1.5" rx="2" ry="1"
              fill="red" />
   </a>

then fill in the destination URL::

   <a xlink:href="http://inkscape.org/">
     <ellipse cx="2.5" cy="1.5" rx="2" ry="1" fill="red" />
   </a>

Then close the editor and return to normal graphical editing.

Can I create animations with it?
--------------------------------

No, Inkscape does not support SVG animation yet. It is for static 2-D graphics.
However you can export graphics from Inkscape to use in Flash or GIF
animations. And since February 2006, Blender can import SVG data and extrude it
to render 3D graphics.

Will there be an Inkscape 1.00?  What would it be like?
-------------------------------------------------------

Assuming development continues steadily, we will inevitably hit 1.00, but no
particular date has been discussed yet. 

One of the goals that must be completed before version 1.00 is the full
implementation of the SVG 1.1 Spec.

Before going gold with any kind of 1.00 release, there would be a significant
effort to tie down loose ends, a push for greater stability and smoothing off
of rough edges. This would be a time consuming process and until it does happen
Inkscape may be subject to substantial changes between releases.

To update to a new version of Inkscape in Windows, do I need to uninstall the old version?
------------------------------------------------------------------------------------------

When you already have Inkscape installed on your Windows XP computer and you
launch the installer for the new version, you should be asked if you wish to
uninstall the version you already have. If you answer *Yes*, a wizard will be
launched that will uninstall the old version; when it finishes, the install
wizard will then launch.

However, a file may be left in your installation folder (the default is
``C:\Program Files\Inkscape``) that prevents the installation from completing.
Simply use File Manager to navigate to that folder and remove any files that
may be there. You can then resume installation.

If you wish to keep the old version on your computer, simply choose a different
folder to which the newer Inkscape should be installed.

Using Inkscape
==============

How do I rotate objects?
------------------------

Inkscape follows the convention used by CorelDraw, Xara and some other
programs: instead of a separate "rotate" tool, you switch to Selector (arrow),
click to select, and then click selected objects again. The handles around the
object become rotation handles - drag them to rotate. You can also use the
Transform dialog for precise rotation and the [, ] keys to rotate selection
from the keyboard (with Ctrl to rotate 90 degrees, with Alt to rotate the
one-pixel amount at the current zoom).

How do I scale or rotate groups of nodes?
-----------------------------------------

You cannot yet do it by mouse, but you can do it from the keyboard. When
several nodes are selected, pressing the '<' or '>' button scales, while
pressing the '[' or ']' button rotates the selected nodes as if they were an
“object”, around the center of that node group or around the node over which
your mouse cursor hovers. (And arrow keys, of course, move the selected nodes
as a whole.) So, for example, in a single-path silhouette portrait, you can now
select the nodes of the nose and rotate/scale the nose as a whole without
breaking the path into pieces. Pressing Alt with these keys gives pixel-sized
movement depending on zoom, the same as in Selector. Also, you can press h or v
to flip the selected nodes horizontally or vertically.

How do I change the color of text?
----------------------------------

Text is not different from any other type of object in Inkscape. You can paint
its fill and stroke with any color, as you would do with any object. Swatches
palette, Fill and Stroke dialog, pasting style - all this works on texts
exactly as it does on, for example, rectangles. Moreover, if in the Text tool
you select part of a text by Shift+arrows or mouse drag, any color setting
method will apply only to the selected part of the text.

How do I change the color of markers (e.g. arrow ends)?
-------------------------------------------------------

By default, markers are black. You can change their color to match the color of
the stroke of the object they are applied to by enabling an effect: Extensions
> Modify Path > Color Markers to Match Stroke.

How to insert math symbols or other special symbols in the drawing?
-------------------------------------------------------------------

When editing text on canvas, press Ctrl+U, then type the Unicode code point of
the symbol you need. A preview of the symbol is shown in the statusbar. When
done, press Enter. A list of Unicode codes can be found at `unicode.org
<http://www.unicode.org/charts/>`_; for example, the integral sign character is
"222b". You must have a font installed on your system that has this character;
otherwise what you'll see is a placeholder rectangle.

When editing text on the Text tab of the Text and Font dialog, you can use any
GTK input modes that your GTK installation supports. Consult GTK documentation
for details.

There is also an extension called `textext
<http://www.iki.fi/pav/software/textext/index.html>`_, that allows you to
include LaTeX typeset formulas in inkscape.

When saving your work in eps format, we recommend to set the option "convert
text to path" in the export dialog box, to preserve the symbol.

How can sine curves be made in Inkscape?
----------------------------------------

Inkscape includes an extension called Function Plotter. It can be used to
create sine curves or any other function graphs.  To access it, go to the
Effects menu, and then the Render submenu.  Other software, such as Xfig, `KiG
<http://edu.kde.org/kig/>`_, or `KSEG <http://www.mit.edu/~ibaran/kseg.html>`_
can also be used to create complex curves and then export to SVG for use in
Inkscape.

How to measure distances and angles?
------------------------------------

Inkscape does not yet have a dedicated Measure tool. However, the Pen tool can
be used in its stead. Switch to Pen (Shift+F6), click at one end of the segment
you want to measure, and move the mouse (without clicking) to its other end. In
the statusbar, you will see the distance and angle measurement. Then press Esc
to cancel. 

The angle is measured by default from 3 o'clock origin counterclockwise (the
mathematical convention), but in Preferences you can switch this to using
compass-like measurement (from 12 o'clock, clockwise).

Starting from 0.44 we also have the Measure Path extension that will measure
the length of an arbitrary path.

Does Inkscape support palettes? Where can I "store" and save colours for further use?
-------------------------------------------------------------------------------------

Inkscape uses the same file format for palettes as the GNU Image Manipulation
Program (GIMP Colour Palettes, .gpl). To install a palette, copy the .gpl file
to the share/palettes directory in your Inkscape installation.

How can I print the tutorials? When printed from Inkscape they don't fit, and I don't like reading on screen.
-------------------------------------------------------------------------------------------------------------

All tutorials in all languages are available online in HTML at `this page
<http://inkscape.org/doc/index.php>`_ and can be easily printed from your
browser.

Can I use different settings for the new documents created by Inkscape?
-----------------------------------------------------------------------

Yes. When you do File > New (Ctrl+N) or start a new Inkscape session, Inkscape
loads the default template document which stores page format, grid and guide
parameters, snapping and export settings, etc. It can even contain any
pre-created objects. You can save any document as the default template by
writing it to ``~/.inkscape/templates/default.svg`` on Linux and ``[inkscape
dir]/share/templates/default.svg`` on Windows. If you save it under any other
name than ``default.svg`` in the same folder, it will appear in the File > New
submenu but will not load automatically unless chosen.

If you use a localized version of Inkscape, french for example, the document
``default.fr.svg`` will be used in place of ``default.svg``. Thus you can adapt
the document loaded by default to the user language.

Is there a way to apply a gradient to a stroke so that it bends with the stroke?
--------------------------------------------------------------------------------

A stroke can be painted with a gradient, but that gradient will not bend with
the stroke. It will remain linear or elliptic. If you meant something like
`this <http://www.mediascape.com/vp.html>`_, then Inkscape can emulate such
effects using blur (use the Blur slider in the Fill and Stroke dialog),
possibly in combination with clipping (see `this screenshot
<http://inkscape.org/screenshots/gallery/inkscape-0.45-3D-rope.png>`_). Another
method is to use the Blend extension to create a blend between two curved paths
painted with different colors or opacity levels; with enough intermediate
steps, such a blend will look almost like an arbitrarily curved gradient.

I'm trying to make a colored tiling of clones, but the tiles refuse to change color.
------------------------------------------------------------------------------------

The original object from which you're cloning must have its fill or stroke
*unset* (not removed, but unset!) for this to work. Use the "?" button in the
Fill & Stroke dialog to unset fill, or use the "Unset" command in the
right-click menu of the selected style indicator in the statusbar. If the
original is a group, only some of the objects in the group may have unset fill,
and only these objects will change colors in the tiling.

Gradients "disappear" when objects are moved or resized.
--------------------------------------------------------

You have the "move gradients" button toggled off in the Selector tool's
controls bar (above the canvas). That's the mode in which moving or resizing an
object does not affect the gradients - they stay in the original place relative
to canvas and therefore may seem to "disappear" if you move the object. Toggle
it back on and it will work as you expect.

I'm trying to apply a gradient opacity mask to an object, but the entire object disappears.
-------------------------------------------------------------------------------------------

Note that per SVG rules, **black** color is *opaque* in a mask (i.e. it
obscures the object under it); **white** color is *transparent* (the object
shows through). What's more, the "no color" fill or full transparency is
equivalent to "transparent black", i.e. (rather counterintuitively) also
becomes opaque in a mask. So, if you want to make your object gradually masked
out, create the masking gradient either *from white to transparent*, or *from
white to black*. The detailed rules of SVG masks are defined in
http://www.w3.org/TR/SVG11/masking.html#Masking.

Images in my document disappear and I get "Linked Image Not Found".
-------------------------------------------------------------------

This happens when bitmap/raster images are imported, because they are not
actually stored inside an Inkscape file by default. What is stored is a link to
the location of the bitmap image on your system. If you later move the original
bitmap image or send the document to someone else, the image will not be able
to be found by Inkscape. See `File Import
<http://tavmjong.free.fr/INKSCAPE/MANUAL/html/File-Import.html>`_ for more
information.

How can you fix this? There are several solutions.

1. You can "Embed" the images. Go to the Effects menu -> Images -> Embed All
   Images. This will save all bitmaps inside the file, but can make the file
   quite large. Inkscape will also only embed PNG or JPG files.

2. Another, possibly better, solution is to "Trace" the bitmap images so they
   become vector images. Inkscape does embed traced images by default, as they
   are now vector images. To do this, follow the instructions on tracing an
   image `here <http://www.inkscape.org/doc/tracing/tutorial-tracing.html>`_ or
   `in the manual <http://tavmjong.free.fr/INKSCAPE/MANUAL/html/Trace.html>`_.

A `bug request <https://bugs.launchpad.net/inkscape/+bug/171842>`_ has been
made to enable Inkscape users to embed bitmap images by default.

The PNGs exported by Inkscape have jagged edges/no antialiasing/funny background.
---------------------------------------------------------------------------------

This is a problem with whatever you use to view these PNG files, not with
Inkscape. For example, Internet Explorer prior to version 7 cannot show PNG
files with transparency properly. Use e.g. Firefox to view your PNGs. If you
absolutely must support IE 6, you can't have transparent background in PNG;
change it to opaque in Document Preferences and export the PNG file again.
Also, you should look into using Dean Edwards' `IE7 Library
<http://dean.edwards.name/IE7/>`_: *It fixes many CSS issues and makes
transparent PNG work correctly under IE5 and IE6.*

If you want to open the exported PNG bitmaps in MS-Word, you will also have to
change the alpha-opacity (in document-properties dialog) to full, and then
export -- the result will be much better.

I have two adjacent objects with their edges abutting precisely, but at some zoom levels, a seam is still visible.
------------------------------------------------------------------------------------------------------------------

That's a known problem of our renderer (as well as many other renderers, for
example Xara's). Antialiased display sometimes results in not-fully-opaque
pixels along the boundary of two objects even if there's absolutely no gap
between them. There are several ways to avoid this problem. If your boundary is
horizontal or vertical, you can suppress antialiasing by pixel-snapping (see
next question). Often, you can just union the two shapes so they become one and
the seam disappears. If this is not possible, just add a small overlap to the
abutting shapes. If this isn't possible either (for example, due to
transparency of these objects), sometimes blurring can help:  in Inkscape
0.45+, you can group the two objects and slightly blur the group to make the
seam disappear.

How to suppress antialiasing?
-----------------------------

With the current renderer, it is not possible to completely get rid of
antialiasing. However, it is possible to *partially* suppress it on export.
Usually, antialiasing is unwelcome in horizontal and vertical lines which
become "blurred". To work around this, make sure your horizontal/vertical edges
are snapped on the pixel grid, and all strokes are a whole number of pixels
wide. Then, export bitmap at the default 90dpi so that 1 px unit corresponds to
1 bitmap pixel. In the resulting bitmap, snapped color boundaries will be
perfectly crisp.

Can Inkscape be used from the command line?
-------------------------------------------

Yes, Inkscape has a powerful command line interface and can be used in scripts
for a variety of tasks, such as exporting and format conversions.  For details,
refer to the manual page (`online
<http://inkscape.org/doc/inkscape-man.html>`_, or via the *Help > Command line
options* command, or by ``man inkscape`` on Unix). Using command line interface
on Windows has `certain limitations and specifics`_.

.. _certain limitations and specifics:
   I'm on Windows, and command line parameters don't seem to work!

.. TODO fix that link if it doesn't work

Troubleshooting Inkscape
========================

Where do I ask for help troubleshooting an Inkscape problem?
------------------------------------------------------------

`https://answers.launchpad.net/inkscape/
<https://answers.launchpad.net/inkscape/>`_ is the best place to ask for help
in troubleshooting an Inkscape issue.

The `Inkscape-user <http://inkscape.org/mailing_lists.php>`_ mailing list is
also an excellent place to ask for help, although it may be harder and take
longer to get a question answered than through the Answers site.

Sometimes people join IRC thinking they can get a quick answer, however this
can be very hit and miss, as generally whomever is active on IRC at the moment
probably doesn't know the right answer for you.  Also, your question may result
in distracting other conversations.  Generally, IRC is best used only if you
specifically need to ask a particular person an Inkscape question.

Where else should I look when I have an Inkscape problem?
---------------------------------------------------------

Try `InstallHelp`

What is the proper way to ask questions on IRC?
-----------------------------------------------

Many people wonder why questions asked on the Inkscape IRC channel generally do
not receive an answer.  There are several reasons for this.

First, maybe IRC is the wrong place to be asking the question; see the previous
FAQ item.

Second, you may have asked the question wrong.  A common error people make on
IRC is to say something like, "Can someone answer a question?" without actually
indicating what the question is.  Most people won't respond to this, because
they have no idea what they'll be asked, and they may not know.  (For instance,
your question may have to do with Windows, whereas they only know Linux.)
Instead, *just ask the question*.  If someone has relevant advice, they'll
see your question and give it.

Third, you may not have waited long enough for an answer.  It's very, very
common for someone to join IRC, ask a question, wait a few minutes, log out
when no answer appears, and then a few seconds later someone submits the
answer.  Be patient; it could take as much as 30 min for someone to see and
respond to your question.

What to do when the cursor and tools end up in different places?
----------------------------------------------------------------

In Windows XP, there might be a problem where the cursor is at a different
location than where the drawing ends up. Their position relative to each other
varies. When the cursor is at the very center of the image, the lines might end
up far out in the periphery. The problem appears both in Version 0.44 and 0.45,
even after reinstalling the software.

There is yet no solution to this problem, and one simply has to find another
software than Inkscape.

How do I get extensions working?
--------------------------------

The extensions mechanism allows you to use external programs and scripts
written in any language to augment Inkscape's capabilities.  The tricky part is
satisfying all of the dependencies of the external programs. For help regarding
opening special file formats though extensions check
`GettingExtensionsWorking`. If you are interested in on-canvas Effects
(the Effects menu) go to `GettingEffectsWorking`.

Why do images 'grow' when imported into Inkscape?
-------------------------------------------------

There is a limitation in the way Inkscape imports `raster/bitmap images
<http://en.wikipedia.org/wiki/Raster_graphics>`_ (e.g JPEG, PNG, TIFF images):
it cannot read the image resolution. Inkscape assumes a 1-to-1 relation at
90dpi, so any imported image with a different resolution will appear to be
scaled. For example, an image of resolution 180 dpi, when imported into
Inkscape, will appear twice as big (180 = 90 x 2) in absolute units as it is in
other programs. Note that this just scales the pixels of the image, but never
adds or removes any pixels. 

When exporting back to a PNG image, changing the resolution will only resample
the image, not resize it. The only way to keep the image at the same size is to
scale it inside Inkscape, once it is imported. For this you need to know the
size (in pixels, cm, inches,...) of the image you import. Then select it and in
the selector's toolbar, click the lock between the width and height fields,
select the unit of the image size and enter either the width or height in the
appropriate field. When exporting, if you don't want to lose information from
your image, use a resolution larger or equal to the resolution of the original
image. 

*Example:* Import an image of size 800*600 pixels and resolution 150 dpi. It
will appear to be 1333 pixels wide and 1000 pixels high in Inkscape. Select it,
click the lock in the selector's toolbar, enter 800 in the width field. Add
some stuff on the image. Export the document to PNG with resolution 150 dpi.
The exported image will be identical to the original one expect for the stuff
you added on it.

I'm on Windows, and command line parameters don't seem to work!
---------------------------------------------------------------

Missing console output issue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Actually, things like exporting or converting to plain SVG do work, they just
do not output anything to the console. This is because Inkscape on Windows is a
GUI application and is not allowed to have any console output. (This means that
query options (such as ``--query-x``) will not work at all.)

One way to enable console output on windows is by running Inkscape from a
`batch file <http://kaioa.com/node/42>`_ or from a `launcher application
<http://kaioa.com/node/63>`_. Both options redirect the output to the console.

Another way to restore console output is by recompiling Inkscape for Windows as
a console application. See `this page <Win32Port>` for general Windows
compilation instructions; edit the file build.xml in the source tree's root
directory and replace the ``-mwindows`` that's in the flags section of the link
target with ``-mconsole`` then recompile. This will give you an inkscape.exe
which works exactly as it does on Linux with regard to command line parameters
and console output. If you regularly use Inkscape's command line interface on
Windows, please send a message to the `inkscape-devel list
<http://inkscape.org/mailing_lists.php>`_ and we may consider providing such a
console executable in our official Inkscape Windows builds.

'File not found' issue
~~~~~~~~~~~~~~~~~~~~~~

Note that on Windows you must provide full paths for all files::

   inkscape -e c:\mydir\file.png c:\mydir\file.svg

Without the ``c:\mydir\`` it won't work. If the path contains spaces, you must
enclose it all into quotes, for example ``"c:\my dir\file.svg"``.

How to make Alt+click and Alt+drag work on Linux?
-------------------------------------------------

Alt+click and Alt+drag are very useful Inkscape shortcuts ("select under" and
"move selected" in Selector, "node sculpting" in Node tool). However, on Linux
Alt+click and Alt+drag are often reserved by the window manager for
manipulating the windows. 

From version 0.46 onwards there is an option in the
~/.config/inkscape/preferences.xml file to allow another modifier key to be
used as an alias for Alt within Inkscape. The option is "mapalt" under group
"options" and has a numerical value. This value equates to the modifier key
that is mapped to Alt, 1 indicates Alt, ie, no mapping). The value you need to
use depends on the setup of your particular keyboard and may be 2, 3, 4, or 5.
The program xkeycaps available from `www.jwz.org
<http://www.jwz.org/xkeycaps/>`_ is useful in finding which mod values are
assigned to which keys on your keyboard, as well as setting them. The value
associated with a particular key is shown in that program at the top of the
screen beside the word "Modifiers" when the mouse is held over a key on the
main display.

Note that this setting makes the new key an alias for Alt in every keyboard
shortcut, not just those concerned with the mouse.

Alternatively, you can disable Alt-click and Alt-drag in your window manager as
shown below:

KDE
~~~

For example, in KDE this is done in Control Center > Desktop > Window Behavior
> Window Actions.

XFCE4
~~~~~

Please read `Xfce 4 Window Manager documentation
<http://www.xfce.org/documentation/4.2/manuals/xfwm4>`_ - (The documentation is
currently out of date for the 4.4 series.)

* To enable in XFCE 4.4 or greater, in the Settings Manager > Window Manager
  Tweaks > Accessibility Tab, change "Key used to grab and move windows" to
  "none" or something else.  Several other selections (such as "Meta") may
  still use the "Alt" key, however, so test it first.

* Before 4.4, edit ~/.config/xfce4/xfwm4/xfwm4rc to contain "easy_click=false".

GNOME
~~~~~

Go to System > Preferences > Windows. You are presented with three options to
move windows around: "Alt", "Ctrl" or "Super" (Windows logo key). Choose
"Super".

fluxbox
~~~~~~~

Beginning from version 1.0rc2, fluxbox allows changing the key used for
manipulating windows. To use windows logo key for this, open file
~/.fluxbox/init in a text editor and change line "session.modKey: Mod1" to
"session.modKey: Mod4"

IceWM
~~~~~

If you have not already done so, create a local copy of the IceWM system
preferences file.  (Typically the system file is
``/usr/share/icewm/preferences`` and your local copy is
``~/.icewm/preferences``. Your mileage may vary.)

Edit your local copy as follows; change::

   # MouseWinMove="Alt+Pointer_Button1"

to::

   MouseWinMove="Alt+Pointer_Button2"

and change::

   # MouseWinRaise="Ctrl+Alt+Pointer_Button1"

to::

   MouseWinRaise="Ctrl+Alt+Pointer_Button2"

Save the preferences file and restart IceWM.

This rebinds the window manager functions to the middle button, which frees up
Alt+click and Alt+drag with the left button for Inkscape.

I'm having problems with non-Latin filenames on Linux - help!
-------------------------------------------------------------

If your locale charset is not UTF-8, then you need to have this environment
variable set::

   $ G_BROKEN_FILENAMES=1
   $ export G_BROKEN_FILENAMES

This is necessary for Glib filename conversion from the locale charset to UTF-8
(used in SVG) and back to work. `Read more details
<http://www.gtk.org/gtk-2.0.0-notes.html>`_.

How can I change Inkscape's interface language?
-----------------------------------------------

If you are using the 0.47 development snapshot, you can change it using a
drop-down box in Inkscape Preferences -> Interface. It requires a restart to
take effect. Here are the instructions for older versions:

   Linux
      Fist type ``locale -a`` in the console to find out, which locale
      settings are supported on your system and how they were written.

      ``export LANGUAGE="C"`` in the commandline switches to the default
      language (English).

      ``export LANGUAGE="de_DE.utf-8"`` changes the language to german. This
      command works only temporary. After a system restart the original locale
      is active. The used locale has to be installed with inkscape on your
      computer (else, Inkscape falls back to the default language).  

      **Add a new locale** (need root permissions)::

         Add an entry to /etc/locale.gen:

         hu_HU ISO-8859-2
         en_US ISO-8859-1

         > locale-gen
         > update-locale

   Windows
      **Easy way**
         Create a batch file in your inkscape installation directory. Call it
         inkscape.bat.

         Add the lines (replace with your LANG setting)

         ::

            @set LANG=de_DE
            @start inkscape.exe

         Save and double-click to use it.

      **Using System Settings**: either delete the yyy language files, or
      change the language by setting the LANGUAGE environment variable.

      a. Deleting the yyy language files

         Beware, this changes the behaviour for **all** inkscape users on this
         machine.

         1. Locate the installation directory.
         2. Enter the Inkscape\\locale directory
         3. Locate the directory with the two letter locale you don't want to
            use.
         4. Rename (or remove) this directory to something like *disable_de*
            or *x_es*
         5. Restart inkscape and the default English (en) locale will be used.

      b. Setting the LANGUAGE environment variable

         Probably this only works when you have administrator (or poweruser?)
         rights on your pc.

         1. Go to the control panel, doubleclick on "System".
         2. Select the "Advanced" tab, and press the "Environment variables"
            button.
         3. You can either add the 'LANGUAGE' variable to the current user or
            to all users (system variables). Press the 'New' button and enter
            'LANGUAGE' as the variable name, and 'C' as value if you want to
            select the default language (English) or e.g. 'de' if you want to
            set the language to german.

Inkscape does not see some of the fonts (Windows)
-------------------------------------------------

This was a bug in versions of Inkscape up to 0.43, caused by using an obsolete
font cache. This cache is stored in the file called ``.fonts.cache-1``. This
file may be in your Windows folder, or in your Temp folder, or in "My
documents" folder, or in the folder listed in the $HOME environment variable.
Use file search by name to locate this file. Then simply delete this file and
restart Inkscape; now it will see the new fonts.

If you are using 0.44 or 0.45 then OpenType/PostScript and Type1 fonts are not
supported (this is a side-effect of the method used to fix the previous bug). 

The issues with OpenType/PostScript and Type 1 fonts have been fixed in
Inkscape 0.46.

Windows internally supports several different types of font:

* Bitmap and vector fonts (red 'A' icon) will never be supported by Inkscape
  because they are too simple to be useful for drawing. They're generally used
  on-screen only.
* TrueType fonts (blue/gray 'TT' icon) are fully supported
* Type1 fonts (red 'a' with shadow icon) are fully supported since 0.46
* OpenType fonts (green/black 'O' icon) come in two subtypes: TrueType outlines
  and PostScript outlines. To tell the difference, double click the font file
  from Control Panel, Fonts and read the second line of text. TrueType outlines
  are fully supported. PostScript outlines are fully supported since 0.46.

Bolding has no effect on some fonts
-----------------------------------

Some fonts are available with in an unique, "normal" variant (i.e. no italics
or bold). Nonetheless, Inkscape currently displays four styles available for
them: Normal, Italics, Bold, Bold Italics. Italics is correctly faked by
inclining the font but bolding cannot be faked at this point. Since the font
itself does not have a Bold variant, the result would likely be of poor quality
anyway. You should rather consider using a font with a real Bold variant.

On Linux, Inkscape crashes with "invalid pointer" message
---------------------------------------------------------

If your Inkscape crashes on start with the error message that looks like 

::

   *** glibc detected *** free(): invalid pointer: 0x086143b0 ***

this is caused by GCC versions incompatibility which affects C++ applications.
Your Inkscape is compiled by a different version of GCC than the C++ libraries
it uses. Recompile either Inkscape itself or its C++ libraries (libstdc++,
libsigc++, libglibmm and libgtkmm) with the single GCC version and the problem
will go away.

How do I turn off system beep on Windows when backspace is pressed at start of field?
-------------------------------------------------------------------------------------

When backspace is used at start of field Inkscape produces annoying system
sound/beep, The behavior is confirmed on Windows XP and 2000 with Inkscape up
to 0.46. On Windows XP this can be turned off in a following way (requires
administration rights):

#. Right-click on My Computer
#. On the Hardware tab, click on [Device Manager]
#. On the "View" menu, select "Show hidden devices"
#. Under "Non-Plug and Play Drivers", right-click "Beep"
#. Click "Disable"
#. Answer [Yes] when asked if you really want to disable it
#. Answer [No] when asked if you want to reboot
#. Right-click "Beep" again.
#. Click "Properties"
#. On the "Driver" tab, set the Startup type to Disabled
#. Click [Stop]
#. Click [OK]
#. Answer [No] when asked if you want to reboot

The procedure is obtained from `the How-To Geek
<http://www.howtogeek.com/howto/windows/turn-off-the-annoying-windows-xp-system-beeps/>`_
site.

Please note that this is Windows system-wide setting, and it affects other
programs as well. On Windows 2000 the steps may vary a bit. Last 6 steps (steps
8-13) are important, since steps 1-7 do not turn off the system beep in
Inkscape (but may turn it off somewhere else).

Mac OS X specific issues
========================

How to make the Alt key work?
-----------------------------

If you find yourself unable to use Inkscape functions that require the ``alt``
key (i.e. ``option`` key) such as Alt+D to create a clone or Alt+Click to
select under, you will need to turn off the "Emulate three button mouse" under
the Input Preferences for X11.

If you still cannot get it to work you can try using a keyboard mapping file
for X11 (the environment Inkscape is running in) called an xmodmap. Open a
terminal and type

::

   cd ~
   touch .xmodmap

This will create a new text file called ".xmodmap" in your home directory. The
period before the actual file name "xmodmap" causes the file to stay hidden
within the Finder.

Now open the file by typing

::

   open .xmodmap

and paste the following into the newly created file:

::

   keycode 66 = Alt_L

This defines the left ``option`` key as alt within **all** X11 applications,
enabling Alt based shortcuts. You need to re-start X11 to see the change.

The right ``option`` key stays the same though, so you cannot use it as Alt but
you can still use it to type special characters such as é, ß or \\ on non-US
keyboards (which is ``Shift+Option+7`` on a German keyboard for example). It
makes typing those letters more cumbersome but the user (unfortunately) has to
determine him/herself which of the two functionalities is needed most for
his/her daily business.

How to make keyboard shortcuts work with Command instead of Control?
--------------------------------------------------------------------

Inkscape runs under X11 and is originally a Linux app, so all keyboard
shortcuts are based on ``Control`` and not ``Command`` as in OS X. For example,
Copy is ⌃C and not ⌘C. You can use an ".xmodmap" file to switch the behaviours
of Control and Command in X11 applications. See above how to create and open
the .xmodmap file. Then paste this inside::

   ! Switch meta and control
   keycode 67 = Meta_L
   keycode 63 = Control_L
   keycode 71 = Control_R
   clear mod2
   clear control
   add mod2 = Meta_L
   add control = Control_L Control_R

Finally, in X11, make sure that the option "Enable key equivalents in X11" is
**un**\ checked and restart X11. Now ⌘C should copy, ⌘V paste etc.

How to change the interface language?
-------------------------------------

Inkscape should follow the settings in System Preferences > International. If
it does not that is a bug and you should report it. Alternatively, starting
with Inkscape 0.47, you can change the language for Inkscape only in Inscape's
preferences > Interface. Inkscape needs to be restarted for the change to take
effect.

Inkscape does not see some of the fonts
---------------------------------------

This issue is fixed in version 0.46. For older versions, the issue comes from
Pango (the library Inkscape uses to manage fonts). Pango does not handle fonts
in the .dfont format and Microsoft Font Suitcases. One solution is to convert
everything to individual ttf files (Times.dfont becomes TimesRegular.ttf,
TimesItalic.ttf, and so on) with fondu or/and fontforge (both are available via
Fink, DarwinPorts or with standalone installers). Beware though:

* you'll end up with duplicated fonts, you need to suppress or disable one
  version 
* do not disable system fonts (if you need system fonts in TTF for X11 apps
  only, put them in an X11 specific directory, such as ~/.fonts)
* this can cause problems with Firefox which mozilla guys do not seem ready to
  solve soon because the problem is inconsistent in its appearance

I've installed Inkscape in some subfolder of "Applications" on OS X but Inkscape does not run 
---------------------------------------------------------------------------------------------

Inkscape cannot be run from a folder containing strange characters in its name
(such as /, ƒ, &, etc.) so if the subfolder you installed Inkscape in contains
one of those, either change its name to something more conventional (spaces and
accented characters are ok) or move Inkscape to "Applications".

I cannot install the latest Inkscape version on OS X 10.3 (Panther)
-------------------------------------------------------------------

Panther is no longer supported by Inkscape. Please download Inkscape 0.45.1,
the last compatible version, from Inkscape's `Sourceforge download page
<http://sourceforge.net/project/showfiles.php?group_id=93438&package_id=99112&release_id=495106>`_.

I've installed Inkscape on Mac OS X but it does not start, or crashes on startup
--------------------------------------------------------------------------------

Please see `InstallHelp#Installing_on_a_Mac` for extended help on Mac install
issues with X11

Copying and pasting in Inkscape creates pixellated images instead of copying the vector objects
-----------------------------------------------------------------------------------------------

Starting with XQuartz 2.3.2, X11 has some functionality to exchange the content
of the clipboard with OS X. But it currently does not know how to deal with
vector images so it just captures the screen, i.e. creates a bitmap copy, and
then pastes that. You need to deactivate this functionality in X11 preferences
> Pasteboard: uncheck "Update Pasteboard when CLIPBOARD changes". However, this
will also prevent copying text from any X11 application to Mac OS X ones. It
will not prevent copying text from OS X to X11.

Users with non-english locale settings in System Preferences > International >
Language have to install the X11 `Localization updates
<http://static.macosforge.org/xquartz/downloads/X11-Locales-2.3.3.2.dmg>`_ for
`XQuartz <http://xquartz.macosforge.org/trac/wiki/Releases>`_ 2.3.3.2 and 2.1.6
to access the new Pasteboard preferences.

When you just want to make a copy of an object within Inkscape, you should use
*duplicate* (Ctrl-D) rather than *copy/paste* (Ctrl-C/Ctrl-V).  *Duplicate*
does not interact with the X11/OSX clipboards.

Contributing to Inkscape
========================

How can I help the Inkscape project?
------------------------------------

If you are a developer, grab the code and start hacking on whatever draws your
attention. Send in a patch when you're happy with it and ready to share your
efforts with others. We also need writers and translators for the user manual
and interface internationalization (`I18N`) files.

We take contributions very seriously and follow the principle of "patch first,
discuss later", so it is highly likely your efforts will appear in the
development codebase swiftly.  There are, of course, rules and standards that
must be followed, but we try to keep them unsurprising and obvious.

Are there non-coding ways to help?
----------------------------------

Certainly!  While there is certainly a lot of coding work to be done, there are
also a lot of other non-programming tasks needed to make the project
successful:

Bug wrangling and testing:
   Identifying and characterizing bugs can help a HUGE amount by reducing the
   amount of development time required to fix them.

   * **Find and** `report bugs <http://www.inkscape.org/report_bugs.php>`_.
     This is a critical need for ensuring the quality of the code.
   * **Review and verify reported bugs**.  Sometimes the bug reports don't have
     enough info, or are hard to reproduce.  Try seeing if the bug occurs for
     you too, and add details to the description.
   * **Performance Testing** - Create SVG's that stress out Inkscape, and post
     them as test cases to the Inkscape bug tracker, with your time
     measurements.
   * **Compatibility Testing**.  Compare the rendering of SVG's in Inkscape
     with other apps like `Batik <http://xml.apache.org/batik/>`_ and `Cairo
     <http://cairographics.org/>`_, and report differences found (to both
     projects).
   * **Bug prioritization**.  Bugs that are marked priority '5' are new bugs.
     Review them and set them to high/medium/low priority according to their
     severity.  See `Updating Tracker Items <UpdatingTrackerItems>` in Wiki
     for details.

Helping fellow users
   In addition to making a good drawing application, it's also extremely important
   to us to build a good community around it; you can help us achieve this
   goal directly, by helping other users.  Above all, keep in mind that we
   want to maintain Inkscape's community as a nice, polite place; so
   encourage good behavior through your own interactions with others in the
   group. 

   * **Write tutorials**.  If something isn't already documented in a tutorial,
     write up a description of how to use it.
   * **Participate on inkscape-user@.** Answer questions that pop up on the
     mailing list from other users.  Also, share your tips and tricks, and demo
     new ways of using Inkscape for cool stuff.
   * **Create clipart**.  You can upload it to the `openclipart.org
     <http://www.openclipart.org/>`_ project.
   * **Give Inkscape classes.**  Teach people local to you about using
     Inkscape.  Or give presentations at local events, Linux group meetings,
     etc. about Inkscape (and other Open Source art tools).

Development (no coding needed)
   * **Translations**.  Information on how to create translations for the
     interface is available on the `Translation Information
     <TranslationInformation>` page in Wiki.
   * **Design Icons and SVG themes**.  Create new icons for existing themes or
     start a new icon theme.  Also see `librsvg.sf.net
     <http://librsvg.sourceforge.net/theme.php>`_
   * **Mockup new dialogs**.  Draw up ideas for improving or adding dialogs.
     These are handy to the UI developers for figuring out what to do.
   * **Improve packaging**.  Figure out how to make the package for your
     operating system or Linux distribution install and work better.  See
     `Creating Dists <CreatingDists>` in Wiki. 
   * **Add extensions**.  For file input/output, special features, etc.
     Inkscape is able to tie into external programs.  Create new .inx files to
     hook these up for use in Inkscape.  Also, if you're comfortable scripting
     in Perl, Python, etc. have a shot at improving the extensions, too!
   * **Add source code documentation**  The source code needs even the simplest
     documentation in some places. Documenting functions will certainly help
     the next coder.
   * **Create templates.**  See the Inkscape share/templates directory.
   * **Work in Wiki**.  Wiki is a great place for gathering development info
     but always needs updating, copyediting, and elaboration.
   * **Plan future development**.  Review and help update the `Roadmap` in
     Wiki. Basically, talk with developers about what they're working on,
     planning to work on, or recently finished, and update the roadmap
     accordingly.

Spread the word - Inkscape Marketing and Evangelism
   Increasing the size of the userbase is important.  The network effects of
   more interested users means more potential contributors and hopefully people
   saying nice things about us, and giving Inkscape word of mouth advertising
   which we believe is important.  All our users and developers serve as
   ambassadors for Inkscape and others will judge Inkscape based on how well we
   behave.  It is important that we all be polite and friendly and make
   Inkscape a project people like using and enjoy working on, all other
   evangelism follows on naturally from there.  Generally though for building
   the community we prefer *quality* over *quantity* so be careful not to go
   too overboard with evangelizing or the "hard sell".  We want to work *with*
   other applications, rather than "killing" off other software and such
   comments are counter productive.  We need to manage expectations. We want
   users to be pleasantly surprised by how much Inkscape does, not disappointed
   that it does not match other programs feature for feature.  Inkscape should
   be thought of as providing artists another way to be creative which
   complements their existing skills and tools.  

   * **Write Articles**.  Get articles published in various online (or even
     printed) magazines and blogs.  Don't forget to include a link to Inkscape!
   * **Create Screenshots**.  Especially for new features. 
   * **Create Examples**.  `Examples <http://www.inkscape.org/screenshots/>`_
     are useful for showcasing different ways Inkscape can be used. Create some
     screenshots and text, and submit to the web wranglers (via the
     inkscape-devel mailing list) to add to the site.
   * **Work on the Website**.  Help on the website is ALWAYS appreciated.
     Knowledge of HTML is required; PHP know-how is helpful.  Check out the
     website code from the `Bazaar repository
     <https://code.launchpad.net/inkscape>`_ and send patches, or request
     direct Bazaar and shell access for doing on-going work.
   * **Give presentations**.  Give talks at expos, symposia, and other big
     events about Inkscape.  Be sure to announce it on an inkscape mailing list
     so we can post it to the Inkscape website.
   * **Recruit more developers**.  Find people with an interest in doing
     coding, and encourage them to work on Inkscape.

Where can I get a banner for Inkscape?
--------------------------------------

Here's one: 

   http://www.inkscape.org/images/inkscape_80x15.png

Feel free to contribute your own banners or buttons for promoting Inkscape. The
best ones will be linked here.

How can I avoid causing a flamewar on the mailing list?
-------------------------------------------------------

Inkscape prides itself on maintaining a friendly community that is passionate
about Inkscape.  Each member arrives here with some definite ideas about what
would make an excellent SVG editor.  When these ideas are discussed and some
folks start taking firm positions, it is easy for arguments to get out of hand
and become unproductive (possibly even driving valuable contributors away from
the project).

Here are some tips for effectively communicating in the Inkscape community

1) Make your argument first and foremost without comparison. Really great
   features can stand on their own and are obviously great from the use cases
   users give. Most often comparisons won't strengthen your case.  In fact they
   can often weaken your case because there is a built up resistance to this
   bandwagon sort of reasoning. Many people use Inkscape to escape from the
   software you want to compare it with. :-)

2) Don't assume that developers, users and industry professionals are mutually
   exclusive groups. Itch driven development means quite the opposite.
   Developers are users developing the software for their own uses. Some
   developers are industry professionals using Inkscape for their livelihood
   daily. This also means that arguments that start with generalizations about
   user wants and expectations have to struggle against the fact that the users
   are developing the software the way they want it.

3) Don't assume that resistance to your idea indicates rampant disregard for
   non-developer-users needs and wants. Many of the developers spend large
   amounts of time conversing with users in person, on IRC and on the mailing
   list. We know when issues are important because we can hear the consensus.
   As anecdotal evidence most of the features I have coded have been in direct
   response to the needs and requests of users who came with polite and
   persistent concerns.

   Indeed, since Inkscape developers typically judge by user consensus, an
   effective way to prove a point is to show a pattern of demand for the change
   from a range of users, or to demonstrate how your change will satisfy a
   large number of user requests.  (This isn't to say that what the unwashed
   masses ask for is always correct, but there are generally strong
   correlations.)

4) Street cred is earned, not demanded. :-) This is just a hard fact about
   community life. The project needs contributors to live and thrive, and
   everyone loves seeing new blood getting involved, and will bend over
   backwards to help.  The more you involve yourself; the more you give of your
   own blood, sweat and tears, the more the community will respond to you. The
   great part is that simple contributions really do matter.

   Remember Inkscape's slogan, "Patch first, discuss later."  This is not just
   an aphorism; oftentimes the principles in an argument won't really
   understand all the factors until they can see the thing in practice, even if
   just a mockup or prototype.  Presenting your ideas as a patch also bypasses
   the concern that others are going to have to put in the labor to implement
   the ideas.

5) Always remember we all share common goals.  If nothing else, we all want to
   see Inkscape made better.  When a discussion feels like it's starting to get
   hot, it's time for the arguers to seek areas of agreement, and focus on
   those.

SVG topics
==========

Are Inkscape's SVG documents valid SVG?
----------------------------------------

Yes. Inkscape does not yet support all features of SVG, but all files it
generates are valid SVG (with the partial and temporary exception of flowed
text, see below). All standard-conformant SVG renderers show them the same as
in Inkscape. If they do not, it's a bug. If this bug is in Inkscape, we will
fix it (especially if you help us by reporting it!). 

What about flowed text?
-----------------------

However, due to the utility of this much-requested feature, we decided to leave
it available to users. When the final SVG 1.2 specification is published, we
will change our flowed text implementation to be fully conformant to it, and
will provide a way to migrate the older flowed text objects to the new format.

Until that is done, however, you should not use flowed text in documents that
you intend to use outside of Inkscape. Flowed text is created by clicking and
dragging in the Text tool, while simple click creates plain SVG 1.1 text; so,
if you don't really need the flowing aspect, just use click to position text
cursor instead of dragging to create a frame. If however you really need flowed
text, you will have to **convert it to regular (non-flowed) text** by the
"Convert to text" command in the Text menu. This command fully preserves the
appearance and formatting of your flowed text but makes it non-flowed and SVG
1.1-compliant.

What, then, is "Inkscape SVG" as opposed to "Plain SVG" when saving a document?
-------------------------------------------------------------------------------

Inkscape SVG files use the Inkscape namespace to store some extra information
used by the program. Other SVG programs will not understand these extensions,
but this is OK because the extensions only affect how the document is *edited*,
not how it *looks*. Extensions must not cause any rendering problems in
SVG-compliant renderers.  However, some non-compliant renderers may have
trouble with the presence of the extensions, or you may want to save some space
by dropping the Inkscape information (if you're not planning to edit the file
in Inkscape again). This is what the "Plain SVG" option is provided for.

What SVG features does Inkscape implement?
------------------------------------------

The main parts of SVG that Inkscape does **not support** yet are some of the
filters (most are supported as of 0.46), animation (work on it is in planning
stages) and SVG fonts (implementation work is under way). The rest mostly
works, though of course there are bugs that we're always fixing. For a
comparison of Inkscape and other open source SVG tools on the `W3C` SVG test
suite, look `here <http://www.linuxrising.org/svg_test/test.html>`_.

I have hand-created SVG. Will everything be messed up, if I load and save it with Inkscape?
-------------------------------------------------------------------------------------------

Inkscape strives to avoid changing the SVG just because it does not recognize
some of the SVG elements, however it *does* make changes:

* All objects will get unique "id" attributes. If already existing and unique,
  they will be preserved, otherwise one will be derived from node name.
* Some sodipodi: and inkscape: namespaced metadata will be added to the
  beginning of document.
* If you edit a gradient, that gradient will be broken up into 2 linked
  gradients - one defining color vector, another one position. 
* Changing any style property forces reconstructing of the whole 'style'
  attribute, which means CSS (not XML) comments will be lost and formatting of
  CSS may change.
* The formatting style of the SVG file will be changed to follow the style
  hardcoded into Inkscape.

There is ongoing work to allow Inkscape to better preserve hand-created SVG
markup but it is a very difficult task requiring a lot of infrastructure work
and will happen very gradually - but help is always appreciated.  

Inkscape and renderer X show my SVGs differently. What to do?
-------------------------------------------------------------

That depends on X.  We accept `Batik <http://xml.apache.org/batik/>`_ and
`Adobe SVG plugin <http://www.adobe.com/svg/>`_ as authoritative SVG renderers
because they are backed by some of the the authors of the SVG standard and
really care about compliance. This may not be true for other renderers. So if
you are having a problem with some renderer, please try the same file with
either Batik or Adobe, or better yet, with both (they are free and
cross-platform). If you still see a discrepancy with Inkscape rendering, we
want to look into it. Please `submit a bug
<https://bugs.launchpad.net/inkscape>`_; don't forget to attach a sample of the
problem file to the bug report, and ideally include screenshots too.

Viewing SVG files like an image archive
---------------------------------------

The following may be used to view/preview files:

* Irfanview (http://www.irfanview.com/). Plugin is required, thumbnails
  available, but may display inaccurately.
* Opera (http://www.opera.com). The browser can be used to open files.
* Renesis Player (http://www.examotion.com)
* Adobe SVG (MS IE plugin)
* Others: Batik, webkit

Depending on which type of viewing will match your need, eg if zooming, quick
preview, quick launch, thumbnail gallery... will affect which is most suited to
you. Additional feature comments, editors welcome!

Inkscape and other programs
===========================

Why is Inkscape so different from Adobe Illustrator?
----------------------------------------------------

In many cases, this is simply because the feature in question is not yet
implemented, or is being actively worked on. But there are other reasons, too.
AI is not the only game in town. Even though it currently enjoys a
near-monopoly position, there still exist, for example, CorelDraw and Xara -
which are also quite different and, in the opinion of many people, superior to
AI in usability. Inkscape has borrowed a lot of user interface ideas from these
fine editors. It has also added many new tools and interface elements of its
own. We take usability very seriously, and we often knowingly depart from the
AI paradigms because we consider our approaches better. If you came from Adobe
Illustrator and are having trouble with Inkscape, please read (and maybe
eventually contribute to) the `Inkscape for Adobe Illustrator users` document
on our Wiki.

Is Inkscape a replacement for The GIMP or Photoshop?
----------------------------------------------------

In most cases, no. They're used for two very different things. Inkscape is used
for creating vector drawings, such as laying out a poster or creating a fancy
logo, whereas bitmap editors are for working on raster images, such as touching
up a photograph. In many projects, you would need to use *both* Inkscape and a
bitmap editor (such as GIMP), for example, to add bitmap effects to an image
exported from Inkscape.

However, currently bitmap editors are often used for common tasks they are not
well equipped for, such as creating web page layouts, logos, or technical line
art. In most cases, this is because users are not aware of the power (or even
the existence) of the  modern vector editors. Inkscape wants to amend this
situation, and to raise a vector editor to the status of an essential desktop
tool for everyone, rather than an exotic specialized tool that only
professionals use.

Why did Inkscape split from Sodipodi?
-------------------------------------

Inkscape started as a code fork of `Sodipodi <http://www.sodipodi.com>`_. The
main reasons were differences in objectives and in development approach.
Inkscape's objective is to be a fully compliant SVG editor, whereas for
Sodipodi SVG is more a means-to-an-end of being a vector illustration tool.
Inkscape's development approach emphasizes open developer access to the
codebase, as well as using and contributing back to 3rd party libraries and
standards such as HIG, CSS, etc. in preference to custom solutions.  Reusing
existing shared solutions helps developers to focus on the core work of
Inkscape.  

For background, it may also be worth reviewing Lauris' `Sodipodi direction
<http://sourceforge.net/mailarchive/message.php?msg_id=1067118318.5026.63.camel%40tont>`_
post from Oct 2003, and his thoughts on SVG, licensing, and the value of
splitting the project into two independent branches.

What's the difference between Inkscape and Dia?
-----------------------------------------------

`Dia <http://live.gnome.org/Dia/>`_ is for technical diagrams like database
charts, class diagrams, etc., whereas Inkscape is for vector drawing such as
logos, posters, scalable icons, etc. 

SVG is a useful format for creating diagrams, though, so we hope as Inkscape
grows as a fully-featured SVG editor, it will also be useful for making
attractive diagrams too.  Several of us hope Inkscape will become a useful
technical drawing tool and work on features with that goal in mind.  However,
Dia provides a number of useful capabilities such as support for UML,
autogeneration of diagrams, etc. that are well beyond the scope of a general
SVG editor.  Ideally both Inkscape and Dia can share various bits of code
infrastructure and third party libraries.

Is this intended to replace Flash?
----------------------------------

While SVG is often identified as a "Flash replacement", SVG has a huge range of
other uses outside that of vector animation.  Replacing `Flash
<http://www.adobe.com/products/flash/>`_ is not one of Inkscape's primary
intents.  If SVG can replace Flash, and Inkscape can help, that's great, but
there's a lot more to SVG than web animation that is worth exploring.  (See
also `SMIL <http://www.w3.org/AudioVideo/>`_)

Will Inkscape be part of the Gnome-Office?
------------------------------------------

Inkscape will need to mature a bit further before this can be considered.
Specifically, better support for embedding (Bonobo) is needed, and the
Gnome-Print subsystem needs to be tested more thoroughly (help very much
appreciated here).  If you can compile a recent version of Inkscape and help us
with testing it would be very useful.  

What formats can Inkscape import/export?
----------------------------------------

Inkscape natively supports opening or importing SVG, SVGZ (gzipped SVG), PDF,
and AI (Adobe Illustrator) formats.  

With the help of extensions, Inkscape can open a number other vector formats.
For importing PostScript or EPS, you need to install `Ghostscript
<http://pages.cs.wisc.edu/~ghost/>`_ and make sure ps2pdf is in your PATH. For
formats of Dia, XFig, or Sketch, you need to have these programs installed. For
CorelDraw, CGM, and SK1 files, you need to have `UniConverter
<http://sk1project.org/>`_ installed. 

Inkscape can natively import most raster formats (JPEG, PNG, GIF, etc.) as
bitmap images, but it can only export PNG bitmaps.

Inkscape can save as SVG, SVGZ, PDF, Postscript/EPS/EPSi, Adobe Illustrator
(``*.ai``), `LaTeX` (``*.tex``), POVRay (``*.pov``), HPGL, and others.

See `FileTypes` for discussion about file formats that people would like to
see supported, and third-party tools that can be used to convert files to or
from SVG.

Can I open/import `*.cdr` (Corel Draw Vector drawing file) files in Inkscape?
-----------------------------------------------------------------------------

You can use the `UniConvertor <http://sourceforge.net/projects/uniconvertor/>`_
for converting CDR files and some other formats to SVG. In Inkscape 0.46,
there's an input extension that will allow you to open or import CDR files
directly from Inkscape if you have UniConvertor installed on your system.

If you can't run UniConvertor, you can try this workaround:

#. Open the `CDR` file in Corel Draw. Save it as **binary encoded** `CGM`\ *
   file. It will save only vector graphics. It will not save bitmap graphics. 
#. Open the CGM file in OpenOffice Impress. Copy to Open Office Draw and
   insert original `JPG` or another bitmap graphics. Save file as `ODG` And
   you can continue in Open Office Draw program.)
#. Select all (CTRL+A)
#. Export as SVG.
#. Open SVG file in Inkscape and correct mistakes if they appear.

**Note:** OpenOffice will open only **binary encoded** *CGM* files in
Impress. If the *CGM* is encoded using clear-text encoding, it will be opened
in OpenOfice Writer, thus rendering the next steps invalid.

I exported an SVG file from Adobe Illustrator, edited it in Inkscape, and imported back to AI, but there my changes are lost!
-----------------------------------------------------------------------------------------------------------------------------

That's because Adobe cheats. It creates a valid SVG, but apart from the SVG
code it also writes to the file, in encoded binary form, the entire AI-format
source file of the image. Inkscape, of course, edits the SVG part of the image
and leaves the encoded binary untouched. But when you import the SVG file back
to AI, it completely disregards the SVG code with its edits and reads directly
from the encoded AI binary. Therefore, any SVG changes are lost. To work around
it, in Inkscape open the XML Editor and remove the non-SVG elements (everything
not with the svg: prefix in its name, usually towards the end of the tree). If
you need to do this job repeatedly you may consider using some `XSLT
<http://www.w3.org/Style/XSL/>`_-based automation. Alternatively, when
exporting SVG from Illustrator, uncheck the options "Preserve Adobe Illustrator
Editing" and "Optimize for Adobe SVG viewer".

Development topics
==================

What are Inkscape's development goals?
--------------------------------------

Inkscape wants to be a complete SVG-compliant vector graphics editor. Apart
from standards compliance, our primary goals are stability, performance, state
of the art vector graphics features, and an efficient and innovative user
interface.

What language and toolkit is Inkscape built upon?
-------------------------------------------------

The codebase Inkscape inherited from Sodipodi was C/`Gtk <http://www.gtk.org>`_
based. There is an ongoing effort to convert the codebase to C++/`Gtkmm
<http://www.gtkmm.org>`_. The ultimate goal is to simplify the code and make it
more maintainable. We invite you to join us. Just don't mention Qt. :)

What is your position on code sharing with other projects?
----------------------------------------------------------

Yes, sharing of code libraries with other projects is highly desirable,
provided the right conditions exist.  A good candidate for a library will be
mature, widely distributed, well documented, and actively maintained.  It
should not introduce massive dependency problems for end-users and should be
stable, powerful, and lightweight.  It should strive to do one thing, and do it
well.  Libraries that don't meet all the criteria will be considered on a
case-by-case basis.

How to create an Inkscape extension?
------------------------------------

You don't need to know much, if anything, about Inkscape internals to create a
useful extension. Aaron Spike, the author of most Python extensions that come
with Inkscape, wrote a helpful `web page
<http://www.ekips.org/comp/inkscape/extending.php>`_ (including a series of
tutorials) on creating extensions in Python (Perl and Ruby are also supported).

What's a good way to get familiar with the code?
------------------------------------------------

You can start with the `Doxygen documentation
<http://inkscape.sourceforge.net/doc/doxygen/html>`_. There you can find not
only the usual Doxygen stuff but also different categorized views into the
inkscape source.

In the Documentation section of the Inkscape website you can find some
high-level diagrams and links to other documentation that's been produced such
as the man page.  Historically, this codebase has not been kept well documented
so expect to find many areas where the only recourse is to work through the
code itself.  However, we place importance on working to change this, and to
flesh out the documentation further as we go.

Some developers have found that testing patches is a good way to quickly get
exposure to the code, as you see how other developers have approached making
changes to the codebase.  Other developers like to pick an interesting feature
request (or perhaps a feature wish of their own) and focus on figuring out how
to implement it.  Occasionally we also have large scale grunt-work type changes
that need to be applied to the codebase, and these can be easy ways to provide
significant contributions with very little experience. 

Getting beyond initial exposure, to the next stage of understanding of the
codebase, is challenging due to the lack of documentation, however with some
determination it can be done.  Some developers find that fixing a crash bug by
tracing execution through the various subsystems, brings good insights into
program flow.  Sometimes it is educational to start from an interesting dialog
box and tracing function calls in the code.  Or perhaps to start with the SVG
file loader and follow the flow into and through the parser.  Other developers
have found that writing inline comments into the code files to be highly useful
in gaining understanding of a particular area, with the fringe benefit of
making that bit of code easy for future developers to pick up, too.

Once you feel far enough up the learning curve, implementing features will firm
up your experience and understanding of the codebase.  Be certain to also write
test cases and documentation, as this will be of great help to future
developers and thus ensure the longevity of the codebase.

What rendering engine do you use?
---------------------------------

Currently we use our own renderer called livarot. We plan to migrate to `Cairo
<http://cairographics.org/>`_ when it is mature enough. In 0.46, Cairo is
already used for Outline mode.

What is the development platform?
---------------------------------

Most developers work on Linux. However it is also possible to compile Inkscape
on Windows; `this page <Win32Port>` provides detailed instructions for this as
well as for cross-compiling Windows binaries on Linux.

What is the Linux command to download the code through Subversion?
------------------------------------------------------------------

Generic directions are under the `Subversion
<http://sourceforge.net/svn/?group_id=93438>`_ link on the `inkscape
sourceforge page <http://www.sourceforge.net/projects/inkscape/>`_.  Note,
however, that the command given on the sourceforge page will check out *all*
modules of the Inkscape project and *all* branches of those modules.

* To *only* check out the latest copy of the main branch (also called "trunk")
  of the Inkscape program, do::
  
     svn checkout https://inkscape.svn.sourceforge.net/svnroot/inkscape/inkscape/trunk/

* To *only* check out the trunk of another Inkscape module, do::
  
     svn checkout https://svn.sourceforge.net/svnroot/inkscape/MODULE_NAME/trunk/
     
  where ``MODULE_NAME`` is the name of the module you want to check out.  Other
  modules you can check out include: ``experimental``, our development
  "scratchpad" for working up prototypes; ``inkscape_web``, which holds our
  website files; and ``inkscape_project``, which holds config files and other
  project-level things.  You can use `our Subversion viewer
  <http://inkscape.svn.sourceforge.net/viewcvs.cgi/inkscape/>`_ to get the
  names of available modules.

* To *only* check out a branch of some Inkscape module, do::
  
     svn checkout https://inkscape.svn.sourceforge.net/svnroot/inkscape/MODULE_NAME/branches/BRANCH_NAME/

  where ``MODULE_NAME`` is the name of the module you want to check out, and
  ``BRANCH_NAME`` is the name of the branch that you are interested in.  You
  can use `our Subversion viewer
  <http://inkscape.svn.sourceforge.net/viewcvs.cgi/inkscape/>`_ to get the
  names of available modules and branches.

These commands will download the requested module into a directory named either
``trunk`` or ``BRANCH_NAME``, depending on whether you chose to check out the
trunk or a branch.

* If you'd like to later test out a different branch of any of Inkscape's
  modules, you can do that by running
  
  ::
  
     svn switch https://inkscape.svn.sourceforge.net/svnroot/inkscape/MODULE_NAME/branches/BRANCH_NAME

  in your working copy, where ``MODULE_NAME`` is the name of the module you are
  working in, and ``BRANCH_NAME`` is the name of the branch that you want to
  switch to. 

* You can do something similar for tagged branches::
  
     svn switch https://inkscape.svn.sourceforge.net/svnroot/inkscape/MODULE_NAME/tags/BRANCH_NAME

  Note that Subversion supports the ability to move individual subdirectories
  of a working copy of a module to different branches of that module, so if you
  want to switch an entire working copy to a different branch, run ``svn
  switch`` in the root directory of the working copy.

How are feature requests selected for implementing?
---------------------------------------------------

Many developers become involved because they wish to "scratch an itch", so of
course if they wish to work on a particular feature, then by definition that
one will receive implementational attention.  This is the primary mechanism by
which features get implemented.

Inkscape also strives to take user requests for features seriously, especially
if they're easy to do or mesh with what one of the existing developers already
wants to do, or if the user has helped the project in other ways.  

If you have a feature that you'd really like to see implemented, but others
aren't working on, the right thing to do is delve into the code and develop it
yourself.  We put great importance on keeping the development process open and
straightforward with exactly this in mind.

I'd prefer the interface to look like ...
-----------------------------------------

Understandably, many users are accustomed to other programs (such as
Illustrator, the GIMP, etc.) and would prefer Inkscape to follow them in
design.  Inkscape developers are constantly examining other projects and on the
look for better interface ideas.  A large motivation is to make the application
follow the `GNOME Human Interface Guidelines (HIG)
<http://library.gnome.org/devel/hig-book/stable/>`_, which has a number of
rules in how the interface is made.  The Inkscape developers also seek advice
and ideas from other GUI app designers, such as the `GIMP
<http://www.gimp.org/>`_ crew, `AbiWord <http://www.abisource.com/>`_, and
`Gnumeric <http://projects.gnome.org/gnumeric/>`_; they've been at it longer
and we view them as an excellent source of battle tested experience.

But please understand that the Inkscape interface will, at the end of the day,
be the "Inkscape interface".  We will strive to find our own balance of
compatibility with common drawing programs, wishes of our userbase, good
workflow, creativity of our developers, and compliance with UI guidelines.
It's unlikely that this balance will meet every user's wish, or achieve 100%
compliance with the various platform specific Interface Guidelines, or include
every developer's idea, and if it did it probably wouldn't be as good.  ;-)

Usually when we discuss interface look and feel, we arrive at the conclusion
that, really, it should be configurable so that each user can flip a few
switches and get an app that is most cozy to them.  However, flexibility should
not be used as an excuse not to make tough decisions when they are called for.

Legal
=====

What License is Inkscape released under?
----------------------------------------

GNU GENERAL PUBLIC LICENSE Version 2, June 1991
[http://www.gnu.org/licenses/gpl-2.0.html]. In short, this means you are free
to use and distribute Inkscape for any purpose, commercial or non-commercial,
without any restrictions.  You are also free to modify the program as you wish,
but with the only restriction that if you distribute the modified version, you
must provide access to the source code of the distributed version.  
