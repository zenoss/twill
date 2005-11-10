#! /usr/local/bin/python2.3
"""
Quixote test app for twill.
"""
import sys
import os

from quixote.publish import Publisher
from quixote.errors import AccessError
from quixote.session import Session, SessionManager
from quixote.directory import Directory, AccessControlled
from quixote import get_user, get_session, get_session_manager, get_path, \
     redirect, get_request
from quixote.form import widget
import base64

class AlwaysSession(Session):
    def __init__(self, session_id):
        Session.__init__(self, session_id)
        self.n = 0
        
    def has_info(self):
        """
        Always save.
        """
        return True

    is_dirty = has_info

from quixote.errors import AccessError
class UnauthorizedError(AccessError):
    """
    The request requires user authentication.
    This subclass of AccessError sends a 401 instead of a 403,
    hinting that the client should try again with authentication.

    (from http://www.quixote.ca/qx/HttpBasicAuthentication)
    """
    status_code = 401
    title = "Unauthorized"
    description = "You are not authorized to access this resource."

    def __init__(self, realm='Protected', public_msg=None, private_msg=None):
        self.realm = realm
        AccessError.__init__(self, public_msg, private_msg)
        
    def format(self):
        request = get_request()
        request.response.set_header('WWW-Authenticate',
                                    'Basic realm="%s"' % self.realm)
        return AccessError.format(self)

def create_publisher():
    """
    Create a publisher for TwillTest, with session management added on.
    """
    session_manager = SessionManager(session_class=AlwaysSession)
    return Publisher(TwillTest(),
                     session_manager=session_manager)

def message(session):
        return """\
Hello, world!
<p>
Your session ID is %s; this is visit #%d.
<p>
You are logged in as "%s".
<p>
<a href="./increment">increment</a> | <a href="./incrementfail">incrementfail</a>
<p>
<a href="logout">log out</a>
<p>
(<a href="test spaces">test spaces</a> / <a href="test_spaces">test spaces2</a>)
""" % (session.id, session.n, session.user)

class TwillTest(Directory):
    """
    Do some simple session manipulations.
    """
    _q_exports = ['logout', 'increment', 'incrementfail', "", 'restricted',
                  'login', ('test spaces', 'test_spaces'), 'test_spaces',
                  'simpleform', 'upload_file', 'http_auth', 'formpostredirect',
                  'exit', 'multisubmitform']

    def __init__(self):
        self.restricted = Restricted()
        self.http_auth = HttpAuthRestricted()

    def _q_index(self):
        session = get_session()
        return message(session)

    def test_spaces(self):
        return "success"

    def increment(self):
        session = get_session()

        session.n += 1

        return message(session)

    def incrementfail(self):
        session = get_session()

        session.n += 1

        raise Exception(message(session))

    def login(self):
        request = get_request()

        username_widget = widget.StringWidget(name='username',
                                              value='')
        submit_widget = widget.SubmitWidget(name='submit',
                                            value='submit me')
        submit_widget2 = widget.SubmitWidget(name='nosubmit2',
                                             value="don't submit")
        
        if request.form:
            assert not submit_widget2.parse(request)
            username = username_widget.parse(request)
            if username:
                session = get_session()
                session.set_user(username)
                return redirect('./')

        image_submit = '''<input type=image name='submit you' src=DNE.gif>'''
                
        return "<form method=POST>Log in: %s<p>%s<p>%s<p>%s</form>" % \
               (username_widget.render(),
                submit_widget2.render(),
                submit_widget.render(),
                image_submit)

    def simpleform(self):
        """
        no submit button...
        """
        request = get_request()
        
        w1 = widget.StringWidget(name='n', value='')
        w2 = widget.StringWidget(name='n2', value='')
        
        return "%s %s <form method=POST><input type=text name=n><input type=text name=n2></form>" % (w1.parse(request), w2.parse(request),)

    def multisubmitform(self):
        request = get_request()
        
        submit1 = widget.SubmitWidget('sub_a', value='sub_a')
        submit2 = widget.SubmitWidget('sub_b', value='sub_b')

        s = ""
        if request.form:
            used = False
            if submit1.parse(request):
                used = True
                s += "used_sub_a"
            if submit2.parse(request):
                used = True
                s += "used_sub_b"

            if not used:
                assert 0

        return "<form method=POST>%s %s %s</form>" % (s,
                                                      submit1.render(),
                                                      submit2.render())

    def formpostredirect(self):
        request = get_request()

        if not request.form:
            return """\
<form method=POST enctype=multipart/form-data>
<input type=text name=test>
<input type=submit value=submit name=submit>
</form>
"""
        redirect(get_path(1) + '/')

    def logout(self):
        # expire session
        session_manager = get_session_manager()
        session_manager.expire_session()

        # redirect to index page.
        return redirect(get_path(1) + '/')

    def upload_file(self):
        request = get_request()
        if request.form:
            contents = request.form['upload'].fp.read()
            return contents
        else:
            return "<form enctype=multipart/form-data method=POST> <input type=file name=upload> <input type=submit value=submit> </form>"

    def exit(self):
        os._exit(0)

class Restricted(AccessControlled, Directory):
    _q_exports = [""]

    def _q_access(self):
        session = get_session()
        if not session.user:
            raise AccessError("you must have a username")

    def _q_index(self):
        return "you made it!"

class HttpAuthRestricted(AccessControlled, Directory):
    _q_exports = [""]

    def _q_access(self):
        r = get_request()

        print '======================== NEW REQUEST'
        for k, v in r.environ.items():
            print '***', k, ':', v

        ha = r.get_environ('HTTP_AUTHORIZATION', None)
        print 'ACCESS'
        if ha:
            print 'HA'
            auth_type, auth_string = ha.split()
            login, passwd = base64.decodestring(auth_string).split(':')

            print 'YO', login, passwd
            if login == 'test' and passwd == 'password':
                return
            
        raise UnauthorizedError

    def _q_index(self):
        return "you made it!"

####

if __name__ == '__main__':
    from quixote.server.simple_server import run
    run(create_publisher, port=8080)
