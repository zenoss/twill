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

twill is essentially a thin shell around the mechanize_ package.  It
also utilizes IPython_ for various shell magic.  At the heart of twill,
there is basically one short module that implements all of the major
functionality.

twill is *very* small at the moment, and I'm hoping to keep the core
of it very simple.

.. _PBP: http://pbp.berlios.de/
.. _maxq: http://maxq.tigris.org/
.. _mechanize: http://wwwsearch.sf.net/
.. _IPython: http://ipython.scipy.org/

Why Reimplement PBP?
--------------------

PBP is a great idea, but Cory Dodt (the author of PBP) is focusing on
other things at the moment, and I needed a solid scripting language
for Web testing.  Plus, I wanted to play with IPython and mechanize.

Availability
------------

Version 0.6 ("everything works, more or less") is available for
download here_.  The latest development version can be found at
twill-latest.tar.gz_.  There's a darcs repository for the project at
http://darcs.idyll.org/~t/projects/twill/.

.. _here: http://darcs.idyll.org/~t/projects/twill-0.6.tar.gz
.. _twill-latest.tar.gz: http://darcs.idyll.org/~t/projects/twill-latest.tar.gz

Documentation
-------------

There are some examples under the ``examples/`` subdirectory.  Included
in the examples is a test of the Quixote demo site, and a script for
clearing out SourceForge Mailman lists.  The latter script makes use of the
(very simple!) extension feature, if you're interested...

Future Plans
------------

I'm scratching my own itch with twill at the moment, so development of
the core functionality will proceed sporadically.  Right now I'm
starting to integrate it into my own projects, so expect some of the
following, soon:

 * maxq recorder;

 * better handling of script execution;

 * more clever wrapping of mechanize;

 * bug fixes galore.

Contributions are welcome & will be duly acknowledged!

Acknowledgements and Credits
----------------------------

Cory Dodt had a great idea with PBP, and I thank him for his insight.
Ian Bicking gave me the idea of reimplementing PBP on top of IPython.
Grig Gheorghiu was strangely enthusiastic about the simple demo I
showed him.  John J. Lee has promptly and enthusiastically checked in
patches to mechanize.  Thanks, guys...

::

   CTB 4/05
