#! /usr/bin/env python2.4

# export:
__all__ = ['go',
           'code',
           'follow',
           'find',
           'notfind',
           'back',
           'show',
           'echo',
           'agent',
           'showform',
           'submit']

import re
from mechanize import Browser

def trunc(s, length, end=1):
    """Truncate a string s to length length, by cutting off the last 
    (length-4) characters and replacing them with ' ...'
    With end=0, truncate from the front instead.
    """
    if not s:
        return ''
    if len(s) > length:
        if end:
            return s[:length-4] + ' ...'
        return '... ' + s[len(s)-length+4:]
    return s

#
# _BrowserState
#

_state_init = 0
class _BrowserState:
    """
    Wrap mechanize behavior in a simple stateful way.
    """
    def __init__(self):
        global _state_init
        if _state_init:
            raise "error, can only create one of me"

        _state_init = 1
        
        self._browser = Browser()
        self._last_res = None

    def go(self, url):
        """
        Visit given URL.
        """
        self._last_res = self._browser.open(url)
        print '==> at', self._last_res.geturl()

    def back(self):
        """
        Return to previous page, if possible.
        """
        self._last_res = self._browser.back()

    def get_code(self):
        """
        Get the HTTP status code received for the current page.
        """
        return self._last_res.wrapped.code

    def get_html(self):
        """
        Get the HTML for the current page.
        """
        self._last_res.seek(0)
        return self._last_res.read()

    def get_url(self):
        """
        Get the URL of the current page.
        """
        return self._last_res.geturl()

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
        self._last_res = self._browser.follow_link(link)
        print '==> at', self._last_res.geturl()

    def set_agent_string(self, agent):
        """
        Set the agent string to the given value.
        """
        # currently doesn't work.
        # self._browser.set_persistent_headers([("User-agent", agent)])

    def showforms(self):
        for n, f in enumerate(self._browser.forms()):
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
                    
            for n, field in enumerate(clickies):
                strings = ("%-2s" % (n+1,),
                           "%-12s %-9s" % (trunc(field.name, 12),
                                           trunc(field.type, 9)),
                           "%-12s" % (trunc(field.id or "(None)", 12),),
                           trunc(field.value, 40),
                           )
                for s in strings:
                    print s,
        

    def submit(self):
        self._last_res = self._browser.submit()
        
state = _BrowserState()

###

def go(url):
    """
    Visit the URL given.
    """
    state.go(url)

def code(should_be):
    """
    Check to make sure the response code for the last page is what it should be.
    """
    assert state.get_code() == int(should_be)

def follow(what):
    """
    Find the first matching link on the page & visit it.
    """
    regexp = re.compile(what)
    links = state.find_link(regexp)

    if links:
        state.follow_link(links)
        return

    assert 0, "no links match '%s'" % (what,)

def find(what):
    regexp = re.compile(what)
    page = state.get_html()

    assert regexp.search(page)

def notfind(what):
    regexp = re.compile(what)
    page = state.get_html()

    assert not regexp.search(page)

def back():
    state.back()

def show():
    print state.get_html()

def echo(*strs):
    for s in strs:
        print s,

def agent(what):
    what = what.strip()
    agent = agent_map.get(what, what)
    state.set_agent_string(agent)

def submit(*nada):
    state.submit()

###

def formvalue():
    pass

fv = formvalue

def showform(*nada):
    state.showforms()

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

