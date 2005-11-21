import sys
import testlib
import twill, twill.browser, twill.commands
from mechanize import BrowserStateError
from cStringIO import StringIO

def setup():
    pass

def test():
    # get the current browser obj.
    browser = twill.get_browser_state()
    assert browser is twill.commands.browser

    try:
        browser._browser.viewing_html()
        assert 0, "shouldn't get here"
    except BrowserStateError:
        pass

    old_err, sys.stderr = sys.stderr, StringIO()
    try:
        try:
            browser.go('example') # what's a good "nowhere"?!?
            assert 0, "shouldn't get here"
        except BrowserStateError:
            pass
    finally:
        sys.stderr = old_err
    
    try:
        twill.commands.exit()
        assert 0, "shouldn't get here"
    except SystemExit:
        pass

def teardown():
    pass
