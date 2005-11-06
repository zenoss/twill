============================================================
twill: an extensible scriptlet language for testing web apps
============================================================

.. contents::

What is 'twill'?
----------------

twill is a tool for Web application testing.  twill implements a
simple scripting language that can be used interactively or from
scripts; this language contains commands for browsing the Web,
filling out forms, and asserting various conditions.

twill scripts look something like this:

::

   # go to my Quixote demo page
   go http://issola.caltech.edu/~t/qwsgi/qwsgi-demo.cgi/

   # go to the widgets sub-page
   go ./widgets
   showforms

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


twill commands can also be used directly from Python.

The primary use for twill is to do automated testing of Web
applications via a straightforward declarative language.  In addition
to basic Web crawling, I wanted to be able to extend the language via
Python, and I also wanted to be able to record things with maxq_.
Hence, twill.

twill was originally based on Cory Dodt's "Python Browser Poseur",
a.k.a. PBP_.  It has diverged quite a bit since then.

Use cases
~~~~~~~~~

Here are some of things that I'm using twill for, or that I plan to use
it for:

 * checking that Web sites are alive;

 * testing functionality in my Quixote extensions;

 * demonstrating specific problems with my (and other) Web sites;

 * regression testing of Web projects, and making sure that existing
   projects work like they should;

 * interacting with Mailman lists;

 * stress-testing applications with multiple hits;

Send me an e-mail if you have additional ideas.

Grig Gheorgiu has written a blog entry on `Web app testing using twill`_
if you want to get his take on things.

.. _Web app testing using twill: http://agiletesting.blogspot.com/2005/09/web-app-testing-with-python-part-3.html

Command Reference
-----------------

The following commands are built into twill.  Note that all text after
a '#' is ignored as a comment, unless it's in a quoted string.

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

**url** *<regexp>* -- assert that the current URL matches the given regexp.

**title** *<regexp>* -- assert that the title of this page matches this regular expression.

Display
~~~~~~~

**show** -- show the current page's HTML.

**showlinks** -- show all of the links on the current page.

**echo** *<string>* -- echo the string to the screen via 'print'.

**save_html** *<filename>* -- save the current page's HTML into a file.

Forms
~~~~~

**showforms** -- show all of the forms on the page.

**submit** *[<n>]* -- click the n'th submit button, if given;
otherwise submit via the last submission button clicked; if nothing
clicked, use the first submit button on the form.  See `details on
form handling`_ for more information.

**formvalue** *<formnum> <fieldname> <value>* --- set the given field in the
given form to the given value.  For read-only form widgets/controls, the
click may be recorded for use by **submit**, but the value is not changed
unless the 'config' command has changed the default behavior.
See 'config' and `details on form handling`_ for more information on
the 'formvalue' command.

**fv** -- abbreviation for 'formvalue'

**formclear** -- clear all values in the form.

**formfile** *<formspec> <fieldspec> <filename> [ <content_type> ]* -- attach a file to a file upload button by filename.

Cookies
~~~~~~~

**save_cookies** *<filename>* -- save current cookie jar into a file.

**load_cookies** *<filename>* -- replace current cookie jar with file contents.

**clear_cookies** -- clear all of the current cookies.

**show_cookies** -- show all of the current cookies.

Debugging
~~~~~~~~~

**debug** *<what>* *<level>* -- turn on debugging/tracing for various functions.  Currently will show HTTP headers ('http') and twill commands ('twill').

Variable handling
~~~~~~~~~~~~~~~~~

**setglobal** *<name> <value>* -- set variable <name> to value <value> in
global dictionary

**setlocal** *<name> <value>* -- set variable <name> to value <value> in
local dictionary

The local dictionary is file-specific, while the global module is general
to all the commands.  Local variables will override global variables if
they exist.

Other commands
~~~~~~~~~~~~~~

**exit** *[<code>]* -- exit with the given integer code, if specified.  'code' defaults to 0.

**run** *<command>* -- exec the given Python command.

**runfile** *<file1> [ <file2> ... ]* -- execute the given files.

**sleep** *[<seconds>]* -- sleep the given number of seconds.  Defaults to 1 second.

**reset_browser** -- reset the browser.

**extend_with** *<module>* -- import commands from Python module.  This acts
like ``from <module> import *`` does in Python, so e.g. a function
``fn`` in ``extmodule`` would be available as ``fn``.  See *examples/extend_example.py* for an example.

**getinput** *<prompt>* -- get keyboard input and store it in ``__input__``.

**getpassword** *<prompt>* -- get *silent* keyboard input and store
it in ``__password__``.

**add_auth** *<realm> <uri> <user> <password>* -- add HTTP Basic Authentication information for the given realm/URI combination.  For example, ::

   add_auth IdyllStuff http://www.idyll.org/ titus test

would tell twill that a request from the authentication realm
"IdyllStuff" under http://www.idyll.org/ should be answered with
username 'titus', password 'test'.

**config** [*<key>* [*<value>*]] -- show/set configuration options.

Special variables
~~~~~~~~~~~~~~~~~

**__input__** -- result of last **getinput**

**__password__** -- result of last **getpassword**

**__url__** -- current URL

Details on Form Handling
~~~~~~~~~~~~~~~~~~~~~~~~

.. _details on form handling:

Both the `formvalue` (or `fv`) and `submit` commands rely on a certain
amount of implicit cleverness to do their work.  In odd situations, it
can be annoying to determine exactly what form field `formvalue` is
going to pick based on your field name, or what form & field `submit`
is going to "click" on.

Here is the pseudocode for how `formvalue` and `submit` figure out
what form to use (function `twill.commands.browser.get_form`)::

   for each form on page:
       if supplied regexp pattern matches the form name, select
   
   if no form name, try converting to an integer N & using N-1 as
   an index into the list or forms on the page (i.e. form 1 is the
   first form on the page).

Here is the pseudocode for how `formvalue` and `submit` figure out
what form field to use (function `twill.commands.browser.get_form_field`)::

   search current form for control name with exact match to fieldname;
   if single (unique) match, select.

   if no match, search current form for control name with regexp match to fieldname;
   if single (unique) match, select.

   if no match, convert fieldname into a number and use as an index, if
   possible.

   if *still* no match, look for exact matches to submit-button values.
   if single (unique) match, select.

Here is the pseudocode for `submit`::

   if a form was _not_ previously selected by formvalue:
      if there's only one form on the page, select it.
      otherwise, fail.

   if a field is not explicitly named:
      if a submit button was "clicked" with formvalue, use it.
      otherwise, use the first submit button on the form, if any.
   otherwise:
      find the field using the same rules as formvalue

   finally, if a button has been picked, submit using it;
   otherwise, submit without using a button

Requirements, Availability and Licensing
----------------------------------------

twill is developed in python 2.3, and should work fine with python 2.4.
You don't need any other software; both pyparsing_ and mechanize_ are
required but included with twill.

Version 0.8 is available for download here_.  The latest development
version can be found at twill-latest.tar.gz_.  There's a darcs
repository for the project at
http://darcs.idyll.org/~t/projects/twill/.

Licensing
~~~~~~~~~

twill 0.8 is licensed under the `GNU LGPL`_, although I am amenable
to changing to an MIT-like license in the future.  All code currently
contained in twill is Copyright (C) 2005, C. Titus Brown
<titus@caltech.edu>.

In plain English: I own the code, but you're welcome to use it and
even subsume it into other projects.  Either way you are currently
obligated to make any changes to twill publicly available, in source
code form, if and only if you are distributing those changes in some
*other* form (e.g. as part of another package).  You do *not* need to
provide the source to packages that use twill, and you are not
obligated to publish your own private changes to twill, or twill scripts,
or twill extensions.

pyparsing_ and mechanize_ are both included with twill, but are under
their own licenses.  (Both are currently more lenient than the LGPL,
so you should have no problems.)

.. _here: http://darcs.idyll.org/~t/projects/twill-0.8.tar.gz
.. _twill-latest.tar.gz: http://darcs.idyll.org/~t/projects/twill-latest.tar.gz
.. _GNU LGPL: http://www.gnu.org/copyleft/lesser.html

Mailing list
~~~~~~~~~~~~

There is a `twill mailing list`_ for discussion and help purposes; for
announcements, either subscribe to the twill list, or monitor
``comp.lang.python.announce``/PyPi.  You can also check out the
archives_.

.. _twill mailing list: http://lists.idyll.org/listinfo/twill
.. _archives: http://lists.idyll.org/pipermail/twill/

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

See the output of 'twill-sh -h' for help on command line options.

There are several example scripts under the ``examples/``
subdirectory.  Included in the examples is a test of the Quixote demo
site, and a script for clearing out SourceForge Mailman lists.  The
latter script makes use of the (very simple!) extension feature, if
you're interested...

Recording scripts
~~~~~~~~~~~~~~~~~

Writing twill scripts is boring.  One simple way to get at least a
rough initial script is to use the maxq_ recorder to generate a twill
script.  maxq_ acts as an HTTP proxy and records all HTTP traffic; I
have written a simple twill script generator for it.  The script
generator and installation docs are included in the twill distribution
under the directory ``maxq/``.

Stress testing
~~~~~~~~~~~~~~

A new script, `twill-fork`, has been added.  The syntax is 

::

   twill-fork -n <number to execute> -p <number of processes> script [ scripts... ]

For example,

::

   twill-fork -n 500 -p 10 test-script

will fork 10 times and run `test-script` 50 times in each process.
`twill-fork` will record the time it takes to run all of the scripts specified
on the command and print a summary at the end.

The time recorded is *not* the CPU time used.  (This would lead to an
inaccurate estimate because the client code uses blocking calls to
retrieve Web pages.)  Rather, the time recorded is the clock time
measured between the start and end of script execution.

Try `twill-fork -h` to get a list of other command line arguments.

Implementation and Extending Twill
----------------------------------

twill is pretty small at the moment, and I'm hoping to keep the core
of it very simple.  twill is essentially a thin shell around the
mechanize_ package.  All twill commands are implemented in the
``commands.py`` file, and pyparsing_ does the work of parsing the
input and converting it into Python commands (see ``parse.py``).
Interactive shell work and readline support is implemented via the
`cmd`_ module (from the standard Python library).

Extending twill
~~~~~~~~~~~~~~~

Right now twill is very easy to extend: just build a Python module
that exports the functions you want to call, place it in the
PYTHONPATH, and run ``extend_with <modulename>``.  See
``extensions/mailman_sf.py`` for an extension that helps deal
with mailman lists on SourceForge; this extension is used by
``examples/discard-sf-mailman-msgs``.

Notes:

  * If your extension raises ``SystemExit``, twill will stop
    processing the script.  This is a useful way to build in
    conditionals, e.g. see the ``discard-sf-mailman-msgs`` example
    script.
    
Using twill in other Python programs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All of the commands available in twill are implemented as top-level functions
in the `twill.commands` module.  For example, to use twill functionality from
another Python program, you can do:

::

   from twill.commands import go, showforms, formclear, fv, submit

   go('http://issola.caltech.edu/~t/qwsgi/qwsgi-demo.cgi/')
   go('./widgets')
   showforms()

   formclear('1')
   fv("1", "name", "test")
   fv("1", "password", "testpass")
   fv("1", "confirm", "yes")
   showforms()

   submit('0')

Note that all arguments need to be strings, at least for the moment.

twill also provides a simple wrapper for mechanize_ functionality, in
the `browser.py` module.  This may be useful for twill extensions as
well as for other toolkits, but the API is still unstable.

Miscellaneous Implementation Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 * twill ignores robots.txt.
 * twill does not understand javascript

.. _PBP: http://pbp.berlios.de/
.. _maxq: http://maxq.tigris.org/
.. _mechanize: http://wwwsearch.sf.net/
.. _pyparsing: http://pyparsing.sourceforge.net/
.. _cmd: http://docs.python.org/lib/module-cmd.html

Future Plans
------------

TODO:

0.8 release:

 1. test the documented fieldname spec for fv/submit.
 2. 'go' on non-absolute URLs breaks when executed twice in a row.
 3. UPGRADE wwwsearch.

after that:

 1. break "unit tests" down into units.
 2. execute directories/directory trees?
 3. record scripts
 4. systematize variable handling a bit better: __ vs $
 5. expose 'browser' & document re Grig; regexp esp.
 6. basic auth (http://www.quixote.ca/qx/HttpBasicAuthentication?) example.
 7. HTTP-EQUIV refresh/redirect commands w/in mechanize? (issola.caltech.edu/~t/transfer/redir-test.html)
 8. twill-fork: make file writing stuff optional; test massive fork fn.
 9. Test HTTP basic auth.

Longer term fixes & cleanups:

 1. fix spaces-in-URLs problem more generally (in urllib2).
 2. Paul McGuire's pyparsing suggestions
 3. cookie "1" vs 1, in cookielib.
 4. command line completion doesn't understand extend_with results yet.
 5. extend_with etc. -- module namespaces, e.g. extmodule.fn?
 6. doc reorganization: separate out commands, make source docs.

Contributions are welcome & will be duly acknowledged!

Acknowledgements and Credits
----------------------------

twill was designed and written by C. Titus Brown.

Cory Dodt had a great idea with PBP, and I thank him for his insight.
Ian Bicking gave me the idea of reimplementing PBP on top of IPython
(since abandoned in favor of cmd_).  Grig Gheorghiu was strangely
enthusiastic about the simple demo I showed him.  John J. Lee has
promptly and enthusiastically checked in my various patches to
mechanize.  Michele Simionato is an early adopter who has helped quite
a bit.  Thanks, guys...

Bug reports have come in from the following fine people: Chris Miles,
MATSUNO Tokuhiro, and Elvelind Grandin.

Patches have been submitted by: Joeri van Ruth, Paul McGuire, Ed Rahn,
Nic Ferrier, Robert Leftwich, James Cameron, and Tommi Virtanen.  Thanks!

This document was written by C. Titus Brown, titus@caltech.edu.
Last updated November '05.
