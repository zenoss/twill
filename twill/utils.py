"""
Various ugly utility functions for twill.
"""
import ClientForm, ClientCookie
import urllib2
import pullparser
from cStringIO import StringIO
import os
import tempfile
import mechanize
import base64
from ClientCookie._Util import getheaders, time
from mechanize import BrowserStateError

class FakeResponse:
    def __init__(self, data, url):
        self.fp = StringIO(data)
        self.url = url

    def read(self, *args):
        return self.fp.read(*args)

    def geturl(self):
        return self.url

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

def journey(func, *args, **kwargs):
    """
    Wrap 'func' so that HTTPErrors and other things are captured when
    'func' is executed as func(*args, **kwargs).  Convert result into
    a 'ResultWrapper'.
    
    Idea stolen straight from PBP, which used lambda functions waaaaay
    too much.
    """
    try:
        result = func(*args, **kwargs)
    except urllib2.HTTPError, e:
        result = e

    if result is None:
        return None

    try:
        result.seek(0)
    except AttributeError:
        pass
    
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
        print "## __Name__________________ __Type___ __ID________ __Value__________________"

    clickies = [c for c in f.controls if c.is_of_kind('clickable')]
    nonclickies = [c for c in f.controls if c not in clickies]

    for field in nonclickies:
        if hasattr(field, 'items'):
            items = [ i.name for i in field.items ]
            value_displayed = "%s of %s" % (field.value, items)
        else:
            value_displayed = "%s" % (field.value,)
        strings = ("  ",
                   "%-24s %-9s" % (trunc(str(field.name), 24),
                                   trunc(field.type, 9)),
                   "%-12s" % (trunc(field.id or "(None)", 12),),
                   trunc(value_displayed, 40),
                   )
        for s in strings:
            print s,
        print ''

    for n, field in enumerate(clickies):
        strings = ("%-2s" % (n+1,),
                   "%-24s %-9s" % (trunc(field.name, 24),
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
        try:
            v = control.get(name=val)
        except ClientForm.ItemNotFoundError:
            try:
                v = control.get(label=val)
            except ClientForm.AmbiguityError:
                raise ClientForm.ItemNotFoundError('multiple matches to value/label "%s" in list control' % (val,))
            except ClientForm.ItemNotFoundError:
                raise ClientForm.ItemNotFoundError('cannot find value/label "%s" in list control' % (val,))

        v.selected = 1
    else:
        control.value = val

#
# stuff to run 'tidy'...
#

_tidy_cmd = "tidy -q -ashtml -o %(output)s -f %(err)s %(input)s >& %(err)s"

def run_tidy(html):
    """
    Run the 'tidy' command-line program on the given HTML string.

    Return a 2-tuple (output, errors).  (None, None) will be returned if
    'tidy' doesn't exist or otherwise fails.
    """
    global _tidy_cmd

    from commands import _options
    require_tidy = _options.get('require_tidy')

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
    cmd = _tidy_cmd % dict(input=inp_filename, err=err_filename,
                           output=out_filename)

    #
    # run the command
    #
    
    success = False
    try:
        os.system(cmd)
        success = True
    except Exception:
        pass

    #
    # get the cleaned-up HTML
    #

    clean_html = None
    errors = None
    if success:
        try:
            clean_html = open(out_filename).read()
        except IOError:
            pass

        try:
            errors = open(err_filename).read().strip()
        except IOError:
            pass

        # complain if no output file: that means we couldn't run tidy...
        if clean_html is None and require_tidy:
            raise Exception("cannot run 'tidy'; \n\t%s\n" % (errors,))

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

#
# TidyAwareLinksParser
#

class TidyAwareLinksParser(pullparser.TolerantPullParser):
    def __init__(self, fh, *args, **kwargs):
        from twill.commands import _options
        use_tidy = _options.get('use_tidy')

        # use 'tidy' to tidy up the HTML, if desired.
        if use_tidy:
            html = fh.read()
            (clean_html, errors) = run_tidy(html)
            if clean_html:
                html = clean_html

            fh = StringIO(html)
            
        pullparser.TolerantPullParser.__init__(self, fh, *args, **kwargs)

###

#
# TidyAwareFormsFactory
#

class TidyAwareFormsFactory(mechanize._mechanize.FormsFactory):
    def parse_response(self, response, encoding):
        from twill.commands import _options
        use_tidy = _options.get('use_tidy')

        # use 'tidy' to tidy up the HTML, if desired.
        if use_tidy:
            data = response.read()
            (clean_html, errors) = run_tidy(data)
            if clean_html:
                data = clean_html

            url = response.geturl()
            fake = FakeResponse(data, url)
        else:
            fake = response

        return mechanize._mechanize.FormsFactory.parse_response(self, fake, encoding)

    def parse_file(self, file_obj, base_url):
        from twill.commands import _options
        use_tidy = _options.get('use_tidy')

        if use_tidy:
            data = file_obj.read()
            (clean_html, errors ) = run_tidy(data)
            if clean_html:
                data = clean_html

            file_obj = StringIO(data)
        return mechanize._mechanize.FormsFactory.parse_file(file_obj, base_url)

###

class FixedHTTPBasicAuthHandler(urllib2.HTTPBasicAuthHandler):
    """
    Fix a bug that exists through Python 2.4 (but NOT in 2.5!)
    """
    def retry_http_basic_auth(self, host, req, realm):
        user,pw = self.passwd.find_user_password(realm, req.get_full_url())
        # ----------------------------------------------^^^^^^^^^^^^^^^^^^ CTB
        if pw is not None:
            raw = "%s:%s" % (user, pw)
            auth = 'Basic %s' % base64.encodestring(raw).strip()
            if req.headers.get(self.auth_header, None) == auth:
                return None
            req.add_header(self.auth_header, auth)
            return self.parent.open(req)
        else:
            return None
    

###

class FunctioningHTTPRefreshProcessor(ClientCookie.HTTPRefreshProcessor):
    """
    Fix an issue where the 'content' component of the http-equiv=refresh
    tag may not contain 'url='.  CTB hack.
    """
    def http_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.info()

        if code == 200 and hdrs.has_key("refresh"):
            refresh = getheaders(hdrs, "refresh")[0]
            i = refresh.find(";")
            if i != -1:
                pause, newurl_spec = refresh[:i], refresh[i+1:]
                pause = int(pause)
                
                j = newurl_spec.find("=")
                if j != -1:
                    newurl = newurl_spec[j+1:]
                else:
                    newurl = newurl_spec
                    
                if (self.max_time is None) or (pause <= self.max_time):
                    if pause != 0 and 0:  # CTB hack! ==#  and self.honor_time:
                        time.sleep(pause)
                    hdrs["location"] = newurl
                    # hardcoded http is NOT a bug
                    response = self.parent.error(
                        "http", request, response,
                        "refresh", msg, hdrs)

        return response

    https_response = http_response
