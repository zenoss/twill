# wwwsearch imports
import mechanize
from mechanize import Browser as MechanizeBrowser
from mechanize._mechanize import BrowserStateError, LinkNotFoundError
from mechanize._useragent import UserAgent
import ClientCookie, ClientForm
from ClientCookie._Util import response_seek_wrapper

import wsgi_intercept
from utils import run_tidy, StringIO, \
     FixedHTTPBasicAuthHandler, FunctioningHTTPRefreshProcessor

def build_http_handler():
    from ClientCookie import HTTPHandler

    class MyHTTPHandler(HTTPHandler):
        def http_open(self, req):
            return self.do_open(wsgi_intercept.WSGI_HTTPConnection, req)

    return MyHTTPHandler

class PatchedMechanizeBrowser(MechanizeBrowser):
    """
    A patched version of the mechanize browser class.  Currently
    installs the WSGI intercept handler & fixes a problem with
    urllib2 Basic Authentication.
    """
    def __init__(self, *args, **kwargs):
        # install WSGI intercept handler.
        self.handler_classes['http'] = build_http_handler()

        # fix basic auth.
        self.handler_classes['_authen'] = FixedHTTPBasicAuthHandler

        # make refresh work even for somewhat mangled refresh directives.
        self.handler_classes['_refresh'] = FunctioningHTTPRefreshProcessor

        MechanizeBrowser.__init__(self, *args, **kwargs)

    def title(self):
        import pullparser
        if not self.viewing_html():
            raise BrowserStateError("not viewing HTML")
        if self._title is None:
            from twill.commands import _options
            do_run_tidy = _options.get('do_run_tidy')
            
            self._response.seek(0)
            if do_run_tidy:
                data = self._response.read()
                (clean_html, errors) = run_tidy(data)
                if clean_html:
                    data = clean_html
                fp = StringIO(data)
            else:
                fp = self._response

            p = pullparser.TolerantPullParser(fp,
                                      encoding=self._encoding(self._response))
            try:
                p.get_tag("title")
            except pullparser.NoMoreTokensError:
                pass
            else:
                title = p.get_text()

                # replace newlines with spaces.
                title = title.replace("\n", " ") # @CTB fix this tidy bug.
                title = title.replace("\r", " ")
                
                self._title = title
        return self._title
