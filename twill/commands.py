#! /usr/bin/env python2.4

# export:
__all__ = ['go',
           'reload',
           'code',
           'follow',
           'find',
           'notfind',
           'back',
           'show',
           'echo',
           'agent',
           'showform',
           'submit',
           'formvalue',
           'fv',
           'formclear']

import re

import urllib2

from mechanize import Browser
import ClientCookie
from errors import TwillAssertionError
from utils import trunc, print_form, set_form_control_value, journey

#
# _BrowserState
#

class _BrowserState:
    """
    Wrap mechanize behavior in a simple stateful way.
    """
    def __init__(self):
        self._browser = Browser()
        self._last_result = None

        # create & set a cookie jar.
        policy = ClientCookie.DefaultCookiePolicy(rfc2965=True)
        cj = ClientCookie.LWPCookieJar(policy=policy)
        self._browser.set_cookiejar(cj)
        
        # browser.set_cookiejar(cj) is broken; need to call
        # browser._set_handler directly.  the problem is that bool(cj)
        # returns false (?!).
        #self._browser._set_handler("_cookies", handle=True, obj=cj)
        self.cj = cj
        

    def go(self, url):
        """
        Visit given URL.
        """
        self._last_result = journey(self._browser.open, url)
        print '==> at', self._last_result.get_url()

    def reload(self):
        self._last_result = journey(self._browser.reload)
        print '==> reloaded'

    def back(self):
        """
        Return to previous page, if possible.
        """
        self._last_result = journey(self._browser.back)
        if self._last_result:
            print '==> at', self._last_result.get_url()
        else:
            print '(no current URL)'
            
    def get_code(self):
        """
        Get the HTTP status code received for the current page.
        """
        return self._last_result.get_http_code()

    def get_html(self):
        """
        Get the HTML for the current page.
        """
        return self._last_result.get_page()

    def get_url(self):
        """
        Get the URL of the current page.
        """
        return journey(self._last_result.get_url)

    def find_link(self, pattern):
        """
        Find the first link with a URL, link text, or name matching the
        given pattern.
        """
        l = self._browser.find_link(url_regex=pattern)
        if not l:
            l = self._browser.find_link(text_regex=pattern)
        if not l:
            l = self._browser.find_link(name_regex=pattern)

        return l

    def follow_link(self, link):
        """
        Follow the given link.
        """
        try:
            self._last_result = journey(self._browser.follow_link, link)
            print '==> at', self._last_result.get_url()
        except urllib2.HTTPError, e:
            raise

    def set_agent_string(self, agent):
        """
        Set the agent string to the given value.
        """
        # currently doesn't work.
        # self._browser.set_persistent_headers([("User-agent", agent)])

    def showforms(self):
        """
        Pretty-print all of the forms.
        """
        for n, f in enumerate(self._browser.forms()):
            print_form(n, f)

    def get_form(self, formname):
        """
        Return the first form that matches 'formname'.
        """
        # first try regexps
        regexp = re.compile(formname)
        for f in self._browser.forms():
            if f.name and regexp.search(f.name):
                return f

        # ok, try number
        try:
            formnum = int(formname)
            return self._browser.forms()[formnum - 1]
        except ValueError:
            pass
        except IndexError:
            pass

        return None

    def get_form_field(self, form, fieldname):
        """
        Return the control that matches 'fieldname'.  Must be
        a *unique* regexp/exact string match.
        """
        found = None
        
        regexp = re.compile(fieldname)

        matches = [ ctl for ctl in form.controls \
                    if regexp.search(str(ctl.name)) ]

        if matches:
            if len(matches) == 1:
                found = matches[0]
            else:
                #print '-- -- fieldname "%s" matches multiple controls' % \
                #      (fieldname,)
                found = None

        if found is None:
            # try num
            clickies = [c for c in form.controls if c.is_of_kind('clickable')]
            try:
                fieldnum = int(fieldname)
                found = clickies[fieldnum]
            except ValueError:
                pass
            except IndexError:
                pass

        #print '-- -- found form control:', found.name, found.type, found.value
        
        return found

    def clicked(self, form, field):
        def choose_this_form(test_form, this_form=form):
            if test_form is this_form:
                return True
            
            return False

        self._browser.select_form(predicate=choose_this_form)

    def submit(self, fieldname):
        assert self._browser.form
        
        ctl = self.get_form_field(self._browser.form, fieldname)
        
        #### @CTB ARGH.  There's no way, currently, to select a specific
        #### control if you've already got one in mind, because the
        #### 'predicate' function doesn't get passed through Browser.click().
        
        control = ctl._click(self._browser.form, None, urllib2.Request)
        self._last_result = journey(self._browser.open, control)
        
state = _BrowserState()

###

def go(url):
    """
    Visit the URL given.
    """
    state.go(url)

def reload(*noargs):
    """
    Reload the current URL.
    """
    state.reload()

def code(should_be):
    """
    Check to make sure the response code for the last page is what it should be.
    """
    should_be = int(should_be)
    if state.get_code() != int(should_be):
        raise TwillAssertionError("code is %d, != %d" % (state.get_code(),
                                                         should_be))

def follow(what):
    """
    Find the first matching link on the page & visit it.
    """
    regexp = re.compile(what)
    links = state.find_link(regexp)

    if links:
        state.follow_link(links)
        return

    raise TwillAssertionError("no links match to '%s'" % (what,))

def find(what):
    """
    Succeed if the regular expression is on the page.
    """
    regexp = re.compile(what)
    page = state.get_html()

    if not regexp.search(page):
        raise TwillAssertionError("no match to '%s'" % (what,))

def notfind(what):
    """
    Fail if the regular expression is on the page.
    """
    regexp = re.compile(what)
    page = state.get_html()

    if regexp.search(page):
        raise TwillAssertionError("match to '%s'" % (what,))

def back(*noargs):
    """
    Return to the previous page.
    """
    state.back()

def show(*noargs):
    """
    Show the HTML for the current page.
    """
    print state.get_html()

def echo(*strs):
    """
    Echo the arguments to the screen.
    """
    for s in strs:
        print s,

def agent(what):
    """
    Set the agent string -- does nothing, currently.
    """
    what = what.strip()
    agent = agent_map.get(what, what)
    state.set_agent_string(agent)

def submit(submit_button):
    """
    Submit.
    """
    state.submit(submit_button)

def showform(*noargs):
    """
    Show all of the forms on the current page.
    """
    state.showforms()

def formclear(formname):
    """
    Run 'clear' on all of the controls in this form.
    """
    form = state.get_form(formname)
    for control in form.controls:
        if control.readonly:
            continue

        control.clear()

def formvalue(formname, fieldname, value):
    """
    formvalue <formname> <field> <value>   -- set value.

    There are some ambiguities in the way formvalue deals with lists:
    'set' will *add* the given value to a multilist.

    Formvalue ignores read-only fields completely; if they're readonly,
    nothing is done.
    """
    print formname, fieldname, value
    if value:
        print value

    form = state.get_form(formname)
    control = state.get_form_field(form, fieldname)
    print '-- got form field', control.name

    state.clicked(form, control)

    if control.readonly:
        return

    set_form_control_value(control, value)

fv = formvalue

####

agent_map = dict(
    ie5='Mozilla/4.0 (compatible; MSIE 5.0; Windows NT 5.1)',
    ie55='Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.1)',
    ie6='Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    moz17='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7) Gecko/20040616',
    opera7='Opera/7.0 (Windows NT 5.1; U) [en]',
    konq32='Mozilla/5.0 (compatible; Konqueror/3.2.3; Linux 2.4.14; X11; i686)',
    saf11='Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en-us) AppleWebKit/100 (KHTML, like Gecko) Safari/100',
    aol9='Mozilla/4.0 (compatible; MSIE 5.5; AOL 9.0; Windows NT 5.1)',)

