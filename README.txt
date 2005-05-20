============================================================
twill: an extensible scriptlet language for testing web apps
============================================================

.. contents::

What is 'twill'?
----------------

twill is a reimplementation of PBP_, the "Python Browser Poseur".
twill and PBP both let you execute scripts that looks something like
this:

::

   # go to my Quixote demo page
   go http://issola.caltech.edu/~t/qwsgi/qwsgi-demo.cgi/

   # go to the widgets sub-page
   go ./widgets
   showform

   # fill out the form
   formclear 1
   fv 1 name test
   fv 1 password testpass
   fv 1 confirm yes
   showforms

   # submit form
   submit 0

   # show results
   show

   # confirm success, etc.
   code 200
   find testpass

The primary use for twill (as with PBP) is to do automated testing of
Web applications via a straightforward declarative language.  In
addition to basic Web crawling, I wanted to be able to extend the
language via Python, and I also wanted to be able to record things
with maxq_.  Hence, twill.

Command Reference
-----------------

The following commands are built into twill.

Browsing
~~~~~~~~

**go** *<url>* -- visit the given URL.

**back** -- return to the previous URL.

**reload** -- reload the current URL.

**follow** *<link name>* -- follow the given link.


Assertions
~~~~~~~~~~

**code** *<code>* -- assert that the last page loaded had this HTTP status,
e.g. ``code 200`` asserts that the page loaded fine.

**find** *<regexp>* -- assert that the page contains this regular expression.

**notfind** *<regexp>* -- assert that the page *does not* contain this
regular expression.

Display
~~~~~~~

**show** -- show the current page's HTML.

**echo** *<string>* -- echo the string to the screen via 'print'.

Forms
~~~~~

**showforms** -- show all of the forms on the page.

**submit** *[<n>]* -- click the n'th submit button, if given; otherwise
submit via the last submission button clicked; if nothing clicked, use
the first submit button on the form.

**formvalue** *<formnum> <fieldname> <value>* --- set the given field in the
given form to the given value.  For read-only form widgets/controls, the
click may be recorded for use by **submit**, but the value is not changed.

**fv** -- abbreviation for 'formvalue'

**formclear** -- clear all values in the form.

Cookies
~~~~~~~

**save_cookies** *<filename>* -- save current cookie jar into a file.

**load_cookies** *<filename>* -- replace current cookie jar with file contents.

**clear_cookies** -- clear all of the current cookies.

**show_cookies** -- show all of the current cookies.

Other commands
~~~~~~~~~~~~~~

**extend_with** *<module>* -- import commands from Python module.

**getinput** *<prompt>* -- get keyboard input and store it in ``__input__``.

**getpassword** *<prompt>* -- get *silent* keyboard input and store
it in ``__password__``.

Requirements, Availability and Licensing
----------------------------------------

twill is developed in python 2.3, and should work fine with python 2.4.
You don't need any other software; both pyparsing_ and mechanize_ are
required but included with twill.

Version 0.7 ("more things work") is available for
download here_.  The latest development version can be found at
twill-latest.tar.gz_.  There's a darcs repository for the project at
http://darcs.idyll.org/~t/projects/twill/.

Licensing
~~~~~~~~~

twill is licensed under the `GNU LGPL`_, although I am amenable to
changing to an MIT-like license in the future.  All code currently
contained in twill is Copyright (C) 2005, C. Titus Brown
<titus@caltech.edu>.

In plain English: I own the code, but you're welcome to use it as-is,
as well as use it/subsume it into other projects.  Either way you are
currently obligated to make your changes to twill publicly available,
in source code form, assuming that you are distributing those changes
in any *other* form (e.g. as part of another package).  You do *not*
need to provide the source to packages that use twill, and you are
not obligated to publish your own private changes, or scripts, or
extensions, or...

pyparsing_ and mechanize_ are both included with twill, but are under
their own licenses.  (Both are currently more lenient than the LGPL,
so you should have no problems.)

.. _here: http://darcs.idyll.org/~t/projects/twill-0.7.tar.gz
.. _twill-latest.tar.gz: http://darcs.idyll.org/~t/projects/twill-latest.tar.gz
.. _GNU LGPL: http://www.gnu.org/copyleft/lesser.html

Installation and Examples
-------------------------

To install twill, just run

::

   python setup.py install

To run twill, type 'twill-sh' and try

::

   go http://www.python.org/
   show

You can also run scripts (e.g. the files in ``examples/``) directly by
specifying them on the command line.

There are several examples under the ``examples/`` subdirectory.  Included
in the examples is a test of the Quixote demo site, and a script for
clearing out SourceForge Mailman lists.  The latter script makes use of the
(very simple!) extension feature, if you're interested...

Implementation and Extending Twill
----------------------------------

twill is pretty small at the moment, and I'm hoping to keep the core
of it very simple.  twill is essentially a thin shell around the
mechanize_ package.  All twill commands are implemented in the
``commands.py`` file, and pyparsing_ does the work of parsing the
input and converting it into Python commands (see ``parse.py``).
Interactive shell work and readline support is implemented via the
`cmd`_ module (from the standard Python library).

Right now twill is very easy to extend: just build a Python module that
exports the functions you want to call and run ``extend_with
<modulename>``.

twill also provides a simple wrapper for mechanize_ functionality, in
the `commands.py` module, that may be useful for twill extensions as
well as for other toolkits.

Miscellaneous Implementation Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 * twill ignores robots.txt.

.. _PBP: http://pbp.berlios.de/
.. _maxq: http://maxq.tigris.org/
.. _mechanize: http://wwwsearch.sf.net/
.. _pyparsing: http://pyparsing.sourceforge.net/
.. _cmd: http://docs.python.org/lib/module-cmd.html

Why Reimplement PBP?
--------------------

PBP is a great idea, but Cory Dodt (the author of PBP) is focusing on
other things at the moment, and I needed a solid scripting language
for Web testing.  Plus, I wanted to play with mechanize.

Future Plans
------------

I'm scratching my own itch with twill at the moment, so development of
the core functionality will proceed sporadically.  Right now I'm
starting to integrate it into my own projects, so expect many bug
fixes, soon...

TODO:

 1. test & document the fieldname spec for fv; put into shell help.
 2. unit testing?

Contributions are welcome & will be duly acknowledged!

Acknowledgements and Credits
----------------------------

Cory Dodt had a great idea with PBP, and I thank him for his insight.
Ian Bicking gave me the idea of reimplementing PBP on top of IPython
(since abandoned in favor of cmd_.)  Grig Gheorghiu was strangely
enthusiastic about the simple demo I showed him.  John J. Lee has
promptly and enthusiastically checked in my various patches to
mechanize.  Michele Simionato is an early adopter who has helped quite
a bit.  Thanks, guys...

This document was written by C. Titus Brown, titus@caltech.edu.
Last updated May '05.
