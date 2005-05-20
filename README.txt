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
   showform

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

**find** *<regexp>* -- assert that the page contains this regexp.

**notfind** *<regexp>* -- assert that the page *does not* contain this regexp.

Display
~~~~~~~

**show** -- show the current page's HTML.

**echo** *<string>* -- echo the string to the screen via 'print'.

Forms
~~~~~

**showforms** -- show all of the forms on the page.

**submit** *<n>* -- click the n'th submit button.  (Doesn't quite work predictably yet...)

**formvalue** *<formnum> <fieldname> <value>* --- set the given field in the
given form to the given value.

**fv** -- abbreviation for 'formvalue'

**formclear** -- clear all values in the form.

Other commands
~~~~~~~~~~~~~~

**extend_with** *<module>* -- import commands from Python module.

**save_cookies** *<filename>* -- save current cookie jar into a file.

**load_cookies** *<filename>* -- replace current cookie jar with file contents.

**getinput** *<prompt>* -- get keyboard input and store it in ``__input__``.

**getpassword** *<prompt>* -- get *silent* keyboard input and store
it in ``__password__``.

Availability
------------

Version 0.7 ("more things work") is available for
download here_.  The latest development version can be found at
twill-latest.tar.gz_.  There's a darcs repository for the project at
http://darcs.idyll.org/~t/projects/twill/.

.. _here: http://darcs.idyll.org/~t/projects/twill-0.7.tar.gz
.. _twill-latest.tar.gz: http://darcs.idyll.org/~t/projects/twill-latest.tar.gz

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

twill is essentially a thin shell around the mechanize_ package.
All twill commands are implemented in the ``commands.py`` file,
and pyparsing_ does the work of translating from the input into
the commands (see ``parse.py``).  Interactive shell work and
readline support is implemented via the `cmd`_ module from the
Python distribution.

twill is pretty small at the moment, and I'm hoping to keep the core
of it very simple.  Right now it's very easy to extend: just build
a Python module that exports the functions you want to call and
run ``extend_with <modulename>``.

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
starting to integrate it into my own projects, so expect some of the
following, soon:

 * maxq recorder;

 * more clever wrapping of mechanize;

 * bug fixes galore.

Contributions are welcome & will be duly acknowledged!

Acknowledgements and Credits
----------------------------

Cory Dodt had a great idea with PBP, and I thank him for his insight.
Ian Bicking gave me the idea of reimplementing PBP on top of IPython
(since abandoned in favor of `cmd`.)  Grig Gheorghiu was strangely
enthusiastic about the simple demo I showed him.  John J. Lee has
promptly and enthusiastically checked in patches to mechanize.
Michele Simionato is an early adopter who has helped quite a bit.
Thanks, guys...

::

   CTB 5/05
