"""
Various ugly utility functions for twill.
"""
import ClientForm
import urllib2, re
import pullparser
from cStringIO import StringIO
import os
import tempfile

class ResultWrapper:
    """
    Deal with mechanize/urllib2/whatever results, and present them in a
    unified form.  Returned by 'journey'-wrapped functions.
    """
    def __init__(self, http_code, url, page):
        self.http_code = int(http_code)
        self.url = url
        self.page = page

    def get_url(self):
        return self.url

    def get_http_code(self):
        return self.http_code

    def get_page(self):
        return self.page

    def get_title(self):
        p = pullparser.PullParser(StringIO(self.get_page()))

        title = None
        if p.get_tag("title"):
            title = p.get_compressed_text()
        return title

def journey(func, *args, **kwargs):
    """
    Wrap 'func' so that HTTPErrors and other things are captured when
    'func' is executed as func(*args, **kwargs).  Convert result into
    a 'ResultWrapper'.
    
    Idea stolen straight from PBP, which used lambda functions waaaaay
    too much.
    """
    result = func(*args, **kwargs)

    if result is None:
        return None

    result.seek(0)
    new_result = ResultWrapper(result.code, # HTTP response code
                               result.geturl(), #  URL
                               result.read() # HTML
                               )

    return new_result

def trunc(s, length):
    """
    Truncate a string s to length length, by cutting off the last 
    (length-4) characters and replacing them with ' ...'
    """
    if not s:
        return ''
    
    if len(s) > length:
        return s[:length-4] + ' ...'
    
    return s

def print_form(n, f):
    """
    Pretty-print the given form, assigned # n.
    """
    if f.name:
        print 'Form name=%s' % (f.name,)
    else:
        print 'Form #%d' % (n + 1,)

    if f.controls:
        print "## __Name______ __Type___ __ID________ __Value__________________"

    clickies = [c for c in f.controls if c.is_of_kind('clickable')]
    nonclickies = [c for c in f.controls if c not in clickies]

    for field in nonclickies:
        if hasattr(field, 'possible_items'):
            value_displayed = "%s of %s" % (field.value,
                                            field.possible_items())
        else:
            value_displayed = "%s" % (field.value,)
        strings = ("  ",
                   "%-12s %-9s" % (trunc(str(field.name), 12),
                                   trunc(field.type, 9)),
                   "%-12s" % (trunc(field.id or "(None)", 12),),
                   trunc(value_displayed, 40),
                   )
        for s in strings:
            print s,
        print ''

    for n, field in enumerate(clickies):
        strings = ("%-2s" % (n+1,),
                   "%-12s %-9s" % (trunc(field.name, 12),
                                   trunc(field.type, 9)),
                   "%-12s" % (trunc(field.id or "(None)", 12),),
                   trunc(field.value, 40),
                   )
        for s in strings:
            print s,
        print ''

def set_form_control_value(control, val):
    """
    Helper function to deal with setting form values on lists etc.
    """
    if isinstance(control, ClientForm.ListControl):
        control.set(1, val)
    else:
        control.value = val

def run_tidy(html):
    """
    Run the 'tidy' command-line program on the given HTML string.

    Return a 2-tuple (output, errors).  (None, None) will be returned if
    'tidy' doesn't exist or otherwise fails.
    """
    cmd = "tidy -q -ashtml -o %(output)s -f %(err)s %(input)s >& %(err)s"

    # build the input filename.
    (fd, inp_filename) = tempfile.mkstemp('.tidy')
    os.write(fd, html)
    os.close(fd)

    # build the output filename.
    (fd, out_filename) = tempfile.mkstemp('.tidy.out')
    os.close(fd)
    os.unlink(out_filename)

    # build the error filename.
    (fd, err_filename) = tempfile.mkstemp('.tidy.err')
    os.close(fd)
    
    # build the command to run
    cmd = cmd % dict(input=inp_filename, err=err_filename, output=out_filename)

    #
    # run the command
    #
    
    success = False
    try:
        os.system(cmd)
        success = True
    except Exception, e:
        pass

    #
    # get the cleaned-up HTML
    #

    clean_html = None
    errors = None
    if success:
        try:
            clean_html = open(out_filename).read()
            errors = open(err_filename).read()
        except IOError:
            pass

    #
    # remove temp files
    #
    try:
        os.unlink(inp_filename)
    except OSError:
        pass

    try:
        os.unlink(out_filename)
    except OSError:
        pass

    try:
        os.unlink(err_filename)
    except OSError:
        pass

    return (clean_html, errors)
