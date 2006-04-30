"""
Test the WSGI intercept code.
"""

import twill

_app_was_hit = False

def success():
    return _app_was_hit

def simple_app(environ, start_response):
    """Simplest possible application object"""
    status = '200 OK'
    response_headers = [('Content-type','text/plain')]
    start_response(status, response_headers)

    global _app_was_hit
    _app_was_hit = True
    
    return ['WSGI intercept successful!\n']

def test_intercept():
    global _app_was_hit

    twill.add_wsgi_intercept('localhost', 80, lambda: simple_app)
    assert not _app_was_hit
    twill.commands.go('http://localhost:80/')
    twill.commands.find("WSGI intercept successful")
    assert _app_was_hit
    twill.remove_wsgi_intercept('localhost', 80)
