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

def print_form(n, f, OUT):
    """
    Pretty-print the given form, assigned # n.
    """
    if f.name:
        print>>OUT, 'Form name=%s' % (f.name,)
    else:
        print>>OUT, 'Form #%d' % (n + 1,)

    if f.controls:
        print>>OUT, "## __Name__________________ __Type___ __ID________ __Value__________________"

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
            print>>OUT, s,
        print>>OUT, ''

    for n, field in enumerate(clickies):
        strings = ("%-2s" % (n+1,),
                   "%-24s %-9s" % (trunc(field.name, 24),
                                   trunc(field.type, 9)),
                   "%-12s" % (trunc(field.id or "(None)", 12),),
                   trunc(field.value, 40),
                   )
        for s in strings:
            print>>OUT, s,
        print>>OUT, ''

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

class ConfigurableParsingFactory(mechanize.Factory):
    """
    A factory that listens to twill config options regarding parsing.

    First: clean up passed-in HTML using tidy?
    Second: parse using the regular parser, or BeautifulSoup?
    Third: should we fail on, or ignore, parse errors?
    """
    
    def __init__(self):
        ### create the two sets of factories to use.
        self.basic_ff = mechanize.FormsFactory()
        self.basic_lf = mechanize.LinksFactory()
        self.basic_gt = mechanize.pp_get_title

        self.bs_ff = mechanize.RobustFormsFactory()
        self.bs_lf = mechanize.RobustLinksFactory()
        self.bs_gt = mechanize.bs_get_title
        
        self.reset()

    def set_request_class(self, request_class):
        self.basic_ff.request_class = request_class
        self.bs_ff.request_class = request_class

    def reset(self):
        self._html = self._orig_html = self._url = None
        self._encoding = None
        
        self._links = self._forms = self._title = None

    def parse_html(self, response, encoding):
        self._url = response.geturl()
        self._orig_html = response.read()
        response.seek(0)
        self._encoding = encoding

        self._html = self._orig_html

        from twill.commands import _options
        use_tidy = _options.get('use_tidy')
        if use_tidy:
            (new_html, errors) = run_tidy(self._html)
            if new_html:
                self._html = new_html

    def use_BS(self):
        from twill.commands import _options
        flag = _options.get('use_BeautifulSoup')

        # try importing BeautifulSoup.
        try:
            import BeautifulSoupy
        except ImportError:
            require = _options.get('require_BeautifulSoup')
            if require:
                raise Exception("cannot import BeautifulSoup, but it's required!")
            return False                # don't use if we can't import!
        return flag

    def forms(self):
        if self._forms is None:
            response = FakeResponse(self._html, self._url)

            from twill.commands import _options
            if _options.get('allow_parse_errors'):
                ignore_errors = True
            else:
                ignore_errors = False

            if self.use_BS():
                parse_fn = self.bs_ff.parse_response
                self.bs_ff.ignore_errors = ignore_errors
            else:
                parse_fn = self.basic_ff.parse_response
                self.basic_ff.ignore_errors = ignore_errors
                
            self._forms = parse_fn(response, self._encoding)

        return self._forms

    def links(self):
        if self._links is None:
            if self.use_BS():
                parse_fn = self.bs_lf.links
            else:
                parse_fn = self.basic_lf.links
                
            self._links = parse_fn(StringIO(self._html), self._url,
                                   self._encoding)
            self._links = list(self._links)
            
        return self._links

    def title(self):
        if self._title is None:
            if self.use_BS():
                parse_fn = self.bs_gt
            else:
                parse_fn = self.basic_gt
            self._title = parse_fn(StringIO(self._html), self._encoding)

        return self._title

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
