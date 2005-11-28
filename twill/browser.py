"""
Python classes for proper browser behavior.

Contains both `PatchedMechanizeBrowser`, which contains twill-specific
fixes/patches/overrides for mechanize behavior, and `TwillBrowser`, a
more stateful browser with a somewhat simpler interface.  `TwillBrowser`
is what is used directly by `commands.py`.
"""

# Python imports
import urllib2
import re
import urlparse

# wwwsearch imports
import mechanize
from mechanize import Browser as MechanizeBrowser
from mechanize._mechanize import BrowserStateError, LinkNotFoundError
from mechanize._useragent import UserAgent
import ClientCookie, ClientForm
from ClientCookie._Util import response_seek_wrapper

# twill package imports
from twill import myhttplib
from utils import trunc, print_form, journey, TidyAwareLinksParser, \
     TidyAwareFormsFactory

class PatchedMechanizeBrowser(MechanizeBrowser):
    """
    A patched version of the mechanize browser class.  Currently only
    installs the WSGI intercept handler.
    """
    def __init__(self, *args, **kwargs):
        # install WSGI intercept handler.
        self.handler_classes['http'] = myhttplib.get_my_handler()
        
        MechanizeBrowser.__init__(self, *args, **kwargs)
        
#    def title(self):
#        return MechanizeBrowser.title(self)

#
# TwillBrowser
#

class TwillBrowser:
    """
    Wrap mechanize behavior in a simple stateful way.
    """
    def __init__(self):
        links_factory = mechanize._mechanize.LinksFactory(link_parser_class=TidyAwareLinksParser)

        forms_factory = TidyAwareFormsFactory()
        
        b = PatchedMechanizeBrowser(links_factory=links_factory,
                                    forms_factory=forms_factory)
        self._browser = b
        
        self._last_result = None
        self._last_submit = None

        # create & set a cookie jar.
        policy = ClientCookie.DefaultCookiePolicy(rfc2965=True)
        cj = ClientCookie.LWPCookieJar(policy=policy)
        self._browser.set_cookiejar(cj)
        self.cj = cj

        # Ask for MIME type 'text/html' by preference.
        self._browser.addheaders = [("Accept", "text/html; */*")]

        # ignore robots.txt
        self._browser.set_handle_robots(None)

        # create an HTTP auth handler
        creds = urllib2.HTTPPasswordMgr()
        self.creds = creds
        self._browser.set_credentials(creds)

        # do handle HTTP-EQUIV properly.
        self._browser.set_handle_equiv(True)

    def _new_page(self):
        """
        Reset various things.
        """
        self._last_submit = None
        
    def url(self):
        if self._last_result is None:
            return " *empty page* "

        return self.get_url()

    def go(self, url):
        """
        Visit given URL.
        """
        url = url.replace(' ', '%20')

        try_urls = [ url, ]

        # if this is an absolute URL that is just missing the 'http://' at
        # the beginning, try fixing that.
        
        if url.find('://') == -1:
            full_url = 'http://%s' % (url,)  # mimic browser behavior
            try_urls.append(full_url)

        success = False

        for u in try_urls:
            try:
                self._last_result = journey(self._browser.open, u)
                self._new_page()
                success = True
                break
            except Exception, e:
                pass

        if success:
            print '==> at', self.get_url()
        else:
            raise BrowserStateError("cannot go to '%s'" % (url,))

    def reload(self):
        """
        Tell the browser to reload the current page.
        """
        self._last_result = journey(self._browser.reload)
        self._new_page()
        print '==> reloaded'

    def back(self):
        """
        Return to previous page, if possible.
        """
        back_url = self._browser.back
        try:
            self._last_result = journey(back_url)
            self._new_page()
        except BrowserStateError, e:
            self._last_result = None

        if self._last_result is not None:
            print '==> back to', self.get_url()
        else:
            print '==> back at empty page.'
            
    def get_code(self):
        """
        Get the HTTP status code received for the current page.
        """
        if self._last_result:
            return self._last_result.get_http_code()
        return None

    def get_html(self):
        """
        Get the HTML for the current page.
        """
        if self._last_result:
            return self._last_result.get_page()
        return None

    def get_title(self):
        """
        Get content of the HTML title element for the current page.
        """
        return self._browser.title()

    def get_url(self):
        """
        Get the URL of the current page.
        """
        if self._last_result:
            return self._last_result.get_url()
        return None

    def find_link(self, pattern):
        """
        Find the first link with a URL, link text, or name matching the
        given pattern.
        """

        #
        # first, try to find a link matching that regexp.
        #
        
        try:
            l = self._browser.find_link(url_regex=pattern)
        except LinkNotFoundError:

            #
            # then, look for a text match.
            #
            
            try:
                l = self._browser.find_link(text_regex=pattern)
            except LinkNotFoundError:
                
                #
                # finally, look for a name match.
                #
                
                try:
                    l = self._browser.find_link(name_regex=pattern)
                except LinkNotFoundError:
                    l = None

        return l

    def follow_link(self, link):
        """
        Follow the given link.
        """
        self._last_result = journey(self._browser.follow_link, link)
        self._new_page()
        print '==> at', self.get_url()

    def set_agent_string(self, agent):
        """
        Set the agent string to the given value.
        """
        # currently doesn't work.
        for i in xrange(len(self._browser.addheaders)):
            if self._browser.addheaders[i][0] == "User-agent":
                del self._browser.addheaders[i]
                break
        self._browser.addheaders += [("User-agent", agent)]

    def showforms(self):
        """
        Pretty-print all of the forms.
        """
        for n, f in enumerate(self._browser.forms()):
            print_form(n, f)

    def showlinks(self):
        """
        Pretty-print all of the links.
        """
        print 'Links:\n'
        for n, link in enumerate(self._browser.links()):
            print "%d. %s ==> %s" % (n, link.text, link.url,)
        print ''

    def showhistory(self):
        """
        Pretty-print the history of links visited.
        """
        print ''
        print 'History: (%d pages total) ' % (len(self._browser._history))

        n = 1
        for (req, resp) in self._browser._history:
            if req and resp:            # only print those that back() will go
                print "\t%d. %s" % (n, resp.geturl())
                n += 1
            
        print ''

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
        except ValueError:              # int() failed
            pass
        except IndexError:              # formnum was incorrect
            pass

        return None

    def get_form_field(self, form, fieldname):
        """
        Return the control that matches 'fieldname'.  Must be
        a *unique* regexp/exact string match.
        """
        found = None
        
        matches = [ c for c in form.controls if str(c.name) == fieldname ]

        if matches and len(matches) == 1:
            found = matches[0]

        if found is None:
            regexp = re.compile(fieldname)

            matches = [ ctl for ctl in form.controls \
                        if regexp.search(str(ctl.name)) ]

            if matches and len(matches) == 1:
                found = matches[0]
                
        if found is None:
            # try num
            clickies = [c for c in form.controls if c.is_of_kind('clickable')]
            try:
                fieldnum = int(fieldname)
                found = clickies[fieldnum]
            except ValueError:          # int() failed
                pass
            except IndexError:          # fieldnum was incorrect
                pass

        if found is None:
            # try value, for readonly controls like submit keys
            clickies = [ c for c in form.controls if c.value == fieldname \
                         and c.readonly ]
            if len(clickies) == 1:
                found = clickies[0]

        return found

    def clicked(self, form, control):

        if self._browser.form != form:
            # construct a function to choose a particular form; select_form
            # can use this to pick out a precise form.

            def choose_this_form(test_form, this_form=form):
                if test_form is this_form:
                    return True

                return False

            self._browser.select_form(predicate=choose_this_form)
            self._last_submit = None

        # record the last submit button clicked.
        if isinstance(control, ClientForm.SubmitControl):
            self._last_submit = control

    def submit(self, fieldname):
        if not self._browser.forms():
            raise Exception("no forms on this page!")
        
        ctl = None
        
        form = self._browser.form
        if form is None:
            if len(self._browser.forms()) == 1:
                form = self._browser.forms()[0]
            else:
                raise Exception("more than one form; you must select one (use 'fv') before submitting")

        # no fieldname?  see if we can use the last submit button clicked...
        if not fieldname:
            if self._last_submit:
                ctl = self._last_submit
            else:
                # get first submit button in form.
                submits = [ c for c in form.controls \
                            if isinstance(c, ClientForm.SubmitControl) ]

                if len(submits):
                    ctl = submits[0]
                
        else:
            # fieldname given; find it.
            ctl = self.get_form_field(form, fieldname)

        #
        # now set up the submission:
        #
        
        if ctl:
            # submit w/button
            print 'Note: submit is using submit button: name="%s", value="%s"' % \
                  (ctl.name, ctl.value)
            
            if isinstance(ctl, ClientForm.ImageControl):
                control = ctl._click(form, (1,1), urllib2.Request)
            else:
                control = ctl._click(form, True, urllib2.Request)
                
        else:
            # submit w/o submit button.
            control = form._click(None, None, None, None, 0, None, urllib2.Request)

        # now actually GO.
        self._last_result = journey(self._browser.open, control)
        self._new_page()

    def save_cookies(self, filename):
        self.cj.save(filename, ignore_discard=True, ignore_expires=True)

    def load_cookies(self, filename):
        self.cj.load(filename, ignore_discard=True, ignore_expires=True)

    def clear_cookies(self):
        self.cj.clear()

    def show_cookies(self):
        print '\nThere are %d cookie(s) in the cookiejar.\n' % (len(self.cj,))
        if len(self.cj):
            for cookie in self.cj:
                print '\t', cookie

            print ''
