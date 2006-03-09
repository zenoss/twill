"""Stateful programmatic WWW navigation, after Perl's WWW::Mechanize.

Copyright 2003-2006 John J. Lee <jjl@pobox.com>
Copyright 2003 Andy Lester (original Perl code)

This code is free software; you can redistribute it and/or modify it under
the terms of the BSD License (see the file COPYING included with the
distribution).

"""

# XXXX
# test referer bugs (frags and don't add in redirect unless orig req had Referer)

# XXX
# The stuff on web page's todo list.
# Moof's emails about response object, .back(), etc.

from __future__ import generators

import urllib2, socket, urlparse, urllib, re, sys, copy

import ClientCookie
from ClientCookie._Util import response_seek_wrapper
from ClientCookie._HeadersUtil import split_header_words, is_html

from _useragent import UserAgent
from _html import _find_links, DefaultFactory

__version__ = (0, 0, 12, "a", None)  # 0.0.12a

class BrowserStateError(Exception): pass
class FormNotFoundError(Exception): pass

class History:
    """

    Though this will become public, the implied interface is not yet stable.

    """
    def __init__(self):
        self._history = []  # LIFO
    def add(self, request, response):
        self._history.append((request, response))
    def back(self, n, _response):
        response = _response  # XXX move Browser._response into this class?
        while n > 0 or response is None:
            try:
                request, response = self._history.pop()
            except IndexError:
                raise BrowserStateError("already at start of history")
            n -= 1
        return request, response
    def clear(self):
        del self._history[:]
    def close(self):
        for request, response in self._history:
            if response is not None:
                response.close()
        del self._history[:]
    def __len__(self):
        return len(self._history)
    def __getitem__(self, i):
        return self._history[i]


if sys.version_info[:2] >= (2, 4):
    from ClientCookie._Opener import OpenerMixin
else:
    class OpenerMixin: pass

class Browser(UserAgent, OpenerMixin):
    """Browser-like class with support for history, forms and links.

    BrowserStateError is raised whenever the browser is in the wrong state to
    complete the requested operation - eg., when .back() is called when the
    browser history is empty, or when .follow_link() is called when the current
    response does not contain HTML data.

    Public attributes:

    request: last request (ClientCookie.Request or urllib2.Request)
    form: currently selected form (see .select_form())
    default_encoding: character encoding used if no encoding is found in the
     response (you should turn on HTTP-EQUIV handling if you want the best
     chance of getting this right without resorting to this default)

    """

    def __init__(self, default_encoding="utf-8",
                 factory=None,
                 history=None,
                 request_class=None,
                 forms_factory=None,  # deprecated
                 links_factory=None,  # deprecated
                 get_title=None,  # deprecated
                 ):
        """

        Only named arguments should be passed to this constructor.

        default_encoding: See class docs.
        request_class: Request class to use.  Defaults to ClientCookie.Request
         by default for Pythons older than 2.4, urllib2.Request otherwise.
        factory: mechanize.Factory

        Note that the supplied factory's request_class is overridden by this
        constructor, to ensure only one Request class is used.
        """
        self.default_encoding = default_encoding
        if history is None:
            history = History()
        self._history = history
        self.request = self._response = None
        self.form = None

        if request_class is None:
            if not hasattr(urllib2.Request, "add_unredirected_header"):
                request_class = ClientCookie.Request
            else:
                request_class = urllib2.Request  # Python 2.4

        if factory is None:
            factory = DefaultFactory()
        factory.set_request_class(request_class)
        self._factory = factory
        self.request_class = request_class

        UserAgent.__init__(self)  # do this last to avoid __getattr__ problems

    def close(self):
        if self._response is not None:
            self._response.close()    
        UserAgent.close(self)
        if self._history is not None:
            self._history.close()
            self._history = None
            
        self._factory.reset()
        self.request = self._response = None

    def open(self, url, data=None):
        if self._response is not None:
            self._response.close()
        return self._mech_open(url, data)

    def _mech_open(self, url, data=None, update_history=True):
        try:
            url.get_full_url
        except AttributeError:
            # string URL -- convert to absolute URL if required
            scheme, netloc = urlparse.urlparse(url)[:2]
            if not scheme:
                # relative URL
                assert not netloc, "malformed URL"
                if self._response is None:
                    raise BrowserStateError(
                        "can't fetch relative URL: not viewing any document")
                url = urlparse.urljoin(self._response.geturl(), url)

        if self.request is not None and update_history:
            self._history.add(self.request, self._response)
        self._response = None
        # we want self.request to be assigned even if UserAgent.open fails
        self.request = self._request(url, data)
        self._previous_scheme = self.request.get_type()

        success = True
        try:
            self._response = UserAgent.open(self, self.request, data)
        except urllib2.HTTPError, error:
            success = False
            self._response = error
##         except (IOError, socket.error, OSError), error:
##             # Yes, urllib2 really does raise all these :-((
##             # See test_urllib2.py in stdlib and in ClientCookie for examples
##             # of socket.gaierror and OSError, plus note that FTPHandler raises
##             # IOError.
##             # XXX I don't seem to have an example of exactly socket.error being
##             #  raised, only socket.gaierror...
##             # I don't want to start fixing these here, though, since this is a
##             # subclass of OpenerDirector, and it would break old code.  Even in
##             # Python core, a fix would need some backwards-compat. hack to be
##             # acceptable.
##             raise
        if not hasattr(self._response, "seek"):
            self._response = response_seek_wrapper(self._response)
        self._parse_html(self._response)
        if not success:
            raise error
        return copy.copy(self._response)

    def response(self):
        """Return last response (as return value of urllib2.urlopen())."""
        return copy.copy(self._response)

    def geturl(self):
        """Get URL of current document."""
        if self._response is None:
            raise BrowserStateError("not viewing any document")
        return self._response.geturl()

    def reload(self):
        """Reload current document, and return response object."""
        if self.request is None:
            raise BrowserStateError("no URL has yet been .open()ed")
        if self._response is not None:
            self._response.close()
        return self._mech_open(self.request, update_history=False)

    def back(self, n=1):
        """Go back n steps in history, and return response object.

        n: go back this number of steps (default 1 step)

        """
        if self._response is not None:
            self._response.close()
        self.request, self._response = self._history.back(n, self._response)
        self._parse_html(self._response)
        return self._response

    def clear_history(self):
        self._history.clear()

    def links(self, **kwds):
        """Return iterable over links (mechanize.Link objects)."""
        if not self.viewing_html():
            raise BrowserStateError("not viewing HTML")

        all_links = self._factory.links()
        if kwds:
            return _find_links(all_links, False, **kwds)
        else:    
            return all_links

    def forms(self):
        """Return iterable over forms.

        The returned form objects implement the ClientForm.HTMLForm interface.

        """
        if not self.viewing_html():
            raise BrowserStateError("not viewing HTML")
        return self._factory.forms()

    def viewing_html(self):
        """Return whether the current response contains HTML data."""
        if self._response is None:
            raise BrowserStateError("not viewing any document")
        ct_hdrs = self._response.info().getheaders("content-type")
        url = self._response.geturl()
        return is_html(ct_hdrs, url)

    def title(self):
        """Return title, or None if there is no title element in the document.

        Tags are stripped or textified as described in docs for
        PullParser.get_text() method of pullparser module.

        """
        if not self.viewing_html():
            raise BrowserStateError("not viewing HTML")

        return self._factory.title()

    def select_form(self, name=None, predicate=None, nr=None):
        """Select an HTML form for input.

        This is a bit like giving a form the "input focus" in a browser.

        If a form is selected, the Browser object supports the HTMLForm
        interface, so you can call methods like .set_value(), .set(), and
        .click().

        At least one of the name, predicate and nr arguments must be supplied.
        If no matching form is found, mechanize.FormNotFoundError is raised.

        If name is specified, then the form must have the indicated name.

        If predicate is specified, then the form must match that function.  The
        predicate function is passed the HTMLForm as its single argument, and
        should return a boolean value indicating whether the form matched.

        nr, if supplied, is the sequence number of the form (where 0 is the
        first).  Note that control 0 is the first form matching all the other
        arguments (if supplied); it is not necessarily the first control in the
        form.

        """
        if not self.viewing_html():
            raise BrowserStateError("not viewing HTML")
        if (name is None) and (predicate is None) and (nr is None):
            raise ValueError(
                "at least one argument must be supplied to specify form")

        orig_nr = nr
        for form in self.forms():
            if name is not None and name != form.name:
                continue
            if predicate is not None and not predicate(form):
                continue
            if nr:
                nr -= 1
                continue
            self.form = form
            break  # success
        else:
            # failure
            description = []
            if name is not None: description.append("name '%s'" % name)
            if predicate is not None:
                description.append("predicate %s" % predicate)
            if orig_nr is not None: description.append("nr %d" % orig_nr)
            description = ", ".join(description)
            raise FormNotFoundError("no form matching "+description)

    def _add_referer_header(self, request, origin_request=True):
        if self.request is None:
            return request
        scheme = request.get_type()
        original_scheme = self.request.get_type()
        if scheme not in ["http", "https"]:
            return request
        if not origin_request and not self.request.has_header("Referer"):
            return request

        if (self._handle_referer and
            original_scheme in ["http", "https"] and
            not (original_scheme == "https" and scheme != "https")):
            # strip URL fragment (RFC 2616 14.36)
            parts = urlparse.urlparse(self.request.get_full_url())
            parts = parts[:-1]+("",)
            referer = urlparse.urlunparse(parts)
            request.add_unredirected_header("Referer", referer)
        return request

    def click(self, *args, **kwds):
        """See ClientForm.HTMLForm.click for documentation."""
        if not self.viewing_html():
            raise BrowserStateError("not viewing HTML")
        request = self.form.click(*args, **kwds)
        return self._add_referer_header(request)

    def submit(self, *args, **kwds):
        """Submit current form.

        Arguments are as for ClientForm.HTMLForm.click().

        Return value is same as for Browser.open().

        """
        return self.open(self.click(*args, **kwds))

    def click_link(self, link=None, **kwds):
        """Find a link and return a Request object for it.

        Arguments are as for .find_link(), except that a link may be supplied
        as the first argument.

        """
        if not self.viewing_html():
            raise BrowserStateError("not viewing HTML")
        if not link:
            link = self.find_link(**kwds)
        else:
            if kwds:
                raise ValueError(
                    "either pass a Link, or keyword arguments, not both")
        request = self.request_class(link.absolute_url)
        return self._add_referer_header(request)

    def follow_link(self, link=None, **kwds):
        """Find a link and .open() it.

        Arguments are as for .click_link().

        Return value is same as for Browser.open().

        """
        return self.open(self.click_link(link, **kwds))

    def find_link(self, **kwds):
        """Find a link in current page.

        Links are returned as mechanize.Link objects.

        # Return third link that .search()-matches the regexp "python"
        # (by ".search()-matches", I mean that the regular expression method
        # .search() is used, rather than .match()).
        find_link(text_regex=re.compile("python"), nr=2)

        # Return first http link in the current page that points to somewhere
        # on python.org whose link text (after tags have been removed) is
        # exactly "monty python".
        find_link(text="monty python",
                  url_regex=re.compile("http.*python.org"))

        # Return first link with exactly three HTML attributes.
        find_link(predicate=lambda link: len(link.attrs) == 3)

        Links include anchors (<a>), image maps (<area>), and frames (<frame>,
        <iframe>).

        All arguments must be passed by keyword, not position.  Zero or more
        arguments may be supplied.  In order to find a link, all arguments
        supplied must match.

        If a matching link is not found, mechanize.LinkNotFoundError is raised.

        text: link text between link tags: eg. <a href="blah">this bit</a> (as
         returned by pullparser.get_compressed_text(), ie. without tags but
         with opening tags "textified" as per the pullparser docs) must compare
         equal to this argument, if supplied
        text_regex: link text between tag (as defined above) must match the
         regular expression object passed as this argument, if supplied
        name, name_regex: as for text and text_regex, but matched against the
         name HTML attribute of the link tag
        url, url_regex: as for text and text_regex, but matched against the
         URL of the link tag (note this matches against Link.url, which is a
         relative or absolute URL according to how it was written in the HTML)
        tag: element name of opening tag, eg. "a"
        predicate: a function taking a Link object as its single argument,
         returning a boolean result, indicating whether the links
        nr: matches the nth link that matches all other criteria (default 0)

        """
        if not self.viewing_html():
            raise BrowserStateError("not viewing HTML")

        return _find_links(self._factory.links(), True, **kwds)

    def __getattr__(self, name):
        # pass through ClientForm / DOMForm methods and attributes
        form = self.__dict__.get("form")
        if form is None:
            raise AttributeError(
                "%s instance has no attribute %s (perhaps you forgot to "
                ".select_form()?)" % (self.__class__, name))
        return getattr(form, name)

#---------------------------------------------------
# Private methods.


    def _encoding(self, response):
        # HTTPEquivProcessor may be in use, so both HTTP and HTTP-EQUIV
        # headers may be in the response.  HTTP-EQUIV headers come last,
        # so try in order from first to last.
        for ct in response.info().getheaders("content-type"):
            for k, v in split_header_words([ct])[0]:
                if k == "charset":
                    return v
        return self.default_encoding

    def _parse_html(self, response):
        self.form = None

        self._factory.reset()
        if self.viewing_html():
            self._factory.parse_html(response, self._encoding(response))
