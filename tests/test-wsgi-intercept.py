import testlib
import twill
from twill import myhttplib

###

simple_app_was_hit = False

def simple_app(environ, start_response):
    """Simplest possible application object"""
    status = '200 OK'
    response_headers = [('Content-type','text/plain')]
    start_response(status, response_headers)

    global simple_app_was_hit
    simple_app_was_hit = True
    
    return ['WSGI intercept successful!\n']

def create_simple_app():
    return simple_app

###

_saved_debuglevel = None

def setup():
    _saved_debuglevel, myhttplib.debuglevel = myhttplib.debuglevel, 1
    twill.add_wsgi_intercept('localhost', 80, create_simple_app)

def test():
    global simple_app_was_hit
    from twill.commands import go, code, find, show

    simple_app_was_hit = False
    go('http://localhost/')
    code(200)
    #show()
    find('WSGI intercept successful!')
    assert simple_app_was_hit

    # repeat, just to be sure that we can reset 'simple_app_was_hit'
    simple_app_was_hit = False
    go('http://localhost/')
    code(200)
    show()
    find('WSGI intercept successful!')
    assert simple_app_was_hit

    # clear & make sure it's clear...
    twill.remove_wsgi_intercept('localhost', 80)
    simple_app_was_hit = False

    go('http://localhost/')             # may or may not succeed!
    assert not simple_app_was_hit       # <-- but *this* is what's important.

def teardown():
    myhttplib.debuglevel = _saved_debuglevel

if __name__ == '__main__':
    setup()
    test()
    teardown()
