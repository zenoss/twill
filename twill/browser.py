"""
Implements TwillBrowser, a simple stateful wrapper for mechanize.Browser.

See _browser.py for mechanize code.
"""

# Python imports
import urllib2
import re
import urlparse

# wwwsearch imports
import mechanize, ClientCookie, ClientForm
from mechanize._mechanize import BrowserStateError, LinkNotFoundError

# twill package imports
from _browser import PatchedMechanizeBrowser
from utils import trunc, print_form, journey, TidyAwareLinksParser, \
     TidyAwareFormsFactory

#
# TwillBrowser
#

class TwillBrowser:
    """
    Wrap mechanize behavior in a simple stateful way.
    """
    def __init__(self):
        #
        # create special link/forms parsing code to run tidy on HTML first.
        #
        
        links_factory = mechanize._mechanize.LinksFactory(link_parser_class=TidyAwareLinksParser)
        forms_factory = TidyAwareFormsFactory(ignore_errors=False)

        factory = mechanize._mechanize.RobustFactory()

        #
        # Create the mechanize browser.
        #
        
        b = PatchedMechanizeBrowser(links_factory=links_factory,
                                    forms_factory=forms_factory)
#        b = PatchedMechanizeBrowser(factory=factory)

        self._browser = b
        
        self._last_result = None
        self._last_submit = None

        #
        # create & set a cookie jar.
        #
        
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
        Reset page-specific stuff -- to be called when visiting a new page.
        """
        self._last_submit = None
        
    def go(self, url):
        """
        Visit given URL.
        """
        try_urls = [ url, ]

        # if this is an absolute URL that is just missing the 'http://' at
        # the beginning, try fixing that.
        
        if url.find('://') == -1:
            full_url = 'http://%s' % (url,)  # mimic browser behavior
            try_urls.append(full_url)

        # if this is a '?' URL, then assume that we want to tack it onto
        # the end of the current URL.

        if url.startswith('?'):
            current_url = self.get_url()
            current_url = current_url.split('?')[0]
            try_urls = [ current_url + url, ]

        success = False

        for u in try_urls:
            try:
                self._last_result = journey(self._browser.open, u)
                self._new_page()
                success = True
                break
            except Exception:
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
        except BrowserStateError:
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

    def _all_the_same_checkbox(self, matches):
        """
        Check whether all these controls are actually the the same
        checkbox.

        Hidden controls can combine with checkboxes, to allow form
        processors to ensure a False value is returned even if user
        does not check the checkbox. Without the hidden control, no
        value would be returned.
        """
        name = None
        for match in matches:
            if match.type not in ['checkbox', 'hidden']:
                return False
            if name is None:
                name = match.name
            else:
                if match.name != name:
                    return False
        return True

    def _all_the_same_submit(self, matches):
        """
        Utility function to check to see if a list of controls all really
        belong to the same control: for use with checkboxes, hidden, and
        submit buttons.
        """
        name = None
        value = None
        for match in matches:
            if match.type not in ['submit', 'hidden']:
                return False
            if name is None:
                name = match.name
                value = match.value
            else:
                if match.name != name or match.value!= value:
                    return False
        return True

    def get_form_field(self, form, fieldname):
        """
        Return the control that matches 'fieldname'.  Must be
        a *unique* regexp/exact string match.
        """
        found = None
        found_multiple = False
        
        matches = [ c for c in form.controls if str(c.name) == fieldname ]

        # test exact match.
        if matches:
            if (len(matches) == 1
                or (self._all_the_same_checkbox(matches)
                    or self._all_the_same_submit(matches))):
                found = matches[0]
            else:
                found_multiple = True   # record for error reporting.

        # test index.
        if found is None:
            # try num
            clickies = [c for c in form.controls]
            try:
                fieldnum = int(fieldname) - 1
                found = clickies[fieldnum]
            except ValueError:          # int() failed
                pass
            except IndexError:          # fieldnum was incorrect
                pass

        # test regexp match
        if found is None:
            regexp = re.compile(fieldname)

            matches = [ ctl for ctl in form.controls \
                        if regexp.search(str(ctl.name)) ]

            if matches:
                if (len(matches) == 1
                    or (self._all_the_same_checkbox(matches)
                        or self._all_the_same_submit(matches))):
                    found = matches[0]
                else:
                    found_multiple = True # record for error

        if found is None:
            # try value, for readonly controls like submit keys
            clickies = [ c for c in form.controls if c.value == fieldname \
                         and c.readonly ]
            if clickies:
                if len(clickies) == 1:
                    found = clickies[0]
                else:
                    found_multiple = True   # record for error

        # error out?
        if found is None:
            if not found_multiple:
                raise Exception('no field matches "%s"' % (fieldname,))
            else:
                raise Exception('multiple matches to "%s"' % (fieldname,))

        return found

    def clicked(self, form, control):
        """
        Record a 'click' in a specific form.
        """
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
        """
        Submit the currently clicked form using the given field.
        """
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
        # now set up the submission by building the request object that
        # will be sent in the form submission.
        #
        
        if ctl:
            # submit w/button
            print 'Note: submit is using submit button: name="%s", value="%s"' % \
                  (ctl.name, ctl.value)
            
            if isinstance(ctl, ClientForm.ImageControl):
                request = ctl._click(form, (1,1), "", ClientCookie.Request)
            else:
                request = ctl._click(form, True, "", ClientCookie.Request)
                
        else:
            # submit w/o submit button.
            request = form._click(None, None, None, None, 0, None,
                                  "", ClientCookie.Request)

        #
        # add referer information.  this may require upgrading the
        # request object to have an 'add_unredirected_header' function.
        #

        upgrade = self._browser._ua_handlers.get('_http_request_upgrade')
        if upgrade:
            request = upgrade.http_request(request)
            request = self._browser._add_referer_header(request)

        #
        # now actually GO.
        #
        
        self._last_result = journey(self._browser.open, request)
        self._new_page()

    def save_cookies(self, filename):
        """
        Save cookies into the given file.
        """
        self.cj.save(filename, ignore_discard=True, ignore_expires=True)

    def load_cookies(self, filename):
        """
        Load cookies from the given file.
        """
        self.cj.load(filename, ignore_discard=True, ignore_expires=True)

    def clear_cookies(self):
        """
        Delete all of the cookies.
        """
        self.cj.clear()

    def show_cookies(self):
        """
        Pretty-print all of the cookies.
        """
        print '\nThere are %d cookie(s) in the cookiejar.\n' % (len(self.cj,))
        if len(self.cj):
            for cookie in self.cj:
                print '\t', cookie

            print ''
