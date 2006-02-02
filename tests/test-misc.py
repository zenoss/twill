import sys
import twilltestlib
import twill, twill.browser, twill.commands
from cStringIO import StringIO
from twill.errors import TwillAssertionError
import urllib2

def setup_module():
    pass

def test():
    # get the current browser obj.
    browser = twill.get_browser()
    assert browser is twill.commands.browser

    old_err, sys.stderr = sys.stderr, StringIO()
    try:
        try:
            browser.go('http://') # what's a good "nowhere"?!?
            assert 0, "shouldn't get here"
        except:
            pass
    finally:
        sys.stderr = old_err

    try:
        twill.commands.exit()
        assert 0, "shouldn't get here"
    except SystemExit:
        pass

    try:
        twill.commands.reset_browser()
        twill.commands.showhistory()
        twill.commands.tidy_ok()
        twill.commands.show()
        assert 0, "shouldn't get here!" # no page!
    except TwillAssertionError:
        pass

    twill.commands.debug('http', '1')
    twill.commands.debug('commands', '0')
    twill.commands.debug('commands', '1')
    try:
        twill.commands.debug('nada', '1')
        assert 0
    except:
        pass

    twill.commands.config()
    twill.commands.config('nada')
    twill.commands.config('readonly_controls_writeable')
    twill.commands.config('do_run_tidy')
    twill.commands.config('tidy_should_exist')
    
    twill.commands.config('readonly_controls_writeable', 1)
    twill.commands.config('do_run_tidy', 1)
    twill.commands.config('tidy_should_exist', 0)
    
    twill.commands.config('tidy_should_exist', "on")

    twill.commands.run("print 'hello'")

def teardown_module():
    pass
