============================================================
twill: an extensible scriptlet language for testing web apps
============================================================

CTB/Feb 2005

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

The primary use for twill/PBP is to do fairly simpleminded (but still
very useful!) automated testing of Web applications.

twill is based on PBP in concept, and (like PBP) is essentially a thin
shell around the mechanize_ package for Python browser emulation.
Unlike PBP, which implements its own scripting interface on top of
Twisted, twill is an even thinner shell around IPython_.  This means
that you can extend twill in a number of very simple ways.
Eventually, it should be possible to put straight Python code into the
scripts, although at the moment the IPython stuff is more than a bit
hacky & will break indentation.

.. _PBP: http://pbp.berlios.de/
.. _mechanize: http://wwwsearch.sf.net/
.. _IPython: http://ipython.scipy.org/

Why?
----

PBP is a great idea, but Cory Dodt (the author of PBP) is focusing on
other things at the moment, and I needed a solid scripting language
for Web testing.  Plus, I wanted to play with IPython and mechanize.

Availability
------------

Version 0.5 (at about the same level of functionality as PBP 0.3) is
available for download here_.  The latest development version can be
found at twill-latest.tar.gz_.

.. _here: .
.. _twill-latest.tar.gz: http://darcs.idyll.org/~t/projects/twill-latest.tar.gz

Note that you'll need to make one modification to IPython 0.6.10 to get this
to work; sorry.

::

   On line 1556 of IPython/iplib.py, change

        if pre == self.ESC_QUOTE:

   to

        if pre == self.ESC_QUOTE or hasattr(self, 'ctb_autoquote'):

I'm still figuring out how to make this work automatically...


Future Plans
------------

I'm scratching my own itch with twill at the moment, so development of
the core functionality will proceed sporadically.  I'd like to focus
on the IPython interface, because once that works then extending twill
will be really easy.

Acknowledgements and Credits
----------------------------

Cory Dodt had a great idea with PBP, and I thank him for his insight.
Ian Bicking gave me the idea of reimplementing PBP on top of IPython.
Grig Gheorghiu was strangely enthusiastic about the simple demo I
showed him.  Thanks, guys...
