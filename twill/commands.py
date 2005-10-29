"""
Implementation of all of the individual 'twill' commands.
"""

# export:
__all__ = ['reset_state',
           'extend_with',
           'go',
           'reload',
           'code',
           'follow',
           'find',
           'notfind',
           'back',
           'show',
           'echo',
           'save_html',
           'sleep',
           'agent',
           'showforms',
           'submit',
           'formvalue',
           'fv',
           'formclear',
           'formfile',
           'getinput',
           'getpassword',
           'save_cookies',
           'load_cookies',
           'clear_cookies',
           'show_cookies',
           'add_auth',
           'run',
           'runfile',
           'setglobal',
           'setlocal',
           'debug',
           'title',
           ]

import re, getpass, time

from browser import TwillBrowser

from errors import TwillAssertionError
from utils import set_form_control_value
from namespaces import get_twill_glocals

        
state = TwillBrowser()

def reset_state():
    """
    >> reset_state

    Reset the browser completely.
    """
    global state
    state = TwillBrowser()

###

def go(url):
    """
    >> go <url>
    
    Visit the URL given.
    """
    state.go(url)

def reload():
    """
    >> reload
    
    Reload the current URL.
    """
    state.reload()

def code(should_be):
    """
    >> code <int>
    
    Check to make sure the response code for the last page is as given.
    """
    should_be = int(should_be)
    if state.get_code() != int(should_be):
        raise TwillAssertionError("code is %d, != %d" % (state.get_code(),
                                                         should_be))

def follow(what):
    """
    >> follow <regexp>
    
    Find the first matching link on the page & visit it.
    """
    regexp = re.compile(what)
    links = state.find_link(regexp)

    if links:
        state.follow_link(links)
        return

    raise TwillAssertionError("no links match to '%s'" % (what,))

def find(what):
    """
    >> find <regexp>
    
    Succeed if the regular expression is on the page.
    """
    regexp = re.compile(what)
    page = state.get_html()

    if not regexp.search(page):
        raise TwillAssertionError("no match to '%s'" % (what,))

def notfind(what):
    """
    >> notfind <regexp>
    
    Fail if the regular expression is on the page.
    """
    regexp = re.compile(what)
    page = state.get_html()

    if regexp.search(page):
        raise TwillAssertionError("match to '%s'" % (what,))

def back():
    """
    >> back
    
    Return to the previous page.
    """
    state.back()

def show():
    """
    >> show
    
    Show the HTML for the current page.
    """
    print state.get_html()

def echo(*strs):
    """
    >> echo <list> <of> <strings>
    
    Echo the arguments to the screen.
    """
    strs = map(str, strs)
    s = " ".join(strs)
    print s

def save_html(filename):
    """
    >> save_html <filename>
    
    Save the HTML for the current page into <filename>
    """
    html = state.get_html()

    f = open(filename, 'w')
    f.write(html)
    f.close()

def sleep(interval=1):
    """
    >> sleep [<interval>]

    Sleep for the specified amount of time.
    If no interval is given, sleep for 1 second.
    """
    time.sleep(float(interval))

def agent(what):
    """
    >> agent <agent>
    
    Set the agent string -- does nothing, currently.
    """
    what = what.strip()
    agent = agent_map.get(what, what)
    state.set_agent_string(agent)

def submit(submit_button=None):
    """
    >> submit [<buttonspec>]
    
    Submit the current form (the one last clicked on) by clicking on the
    n'th submission button.  If no "buttonspec" is given, submit the current
    form by using the last clicked submit button.
    """
    state.submit(submit_button)

def showforms():
    """
    >> showforms
    
    Show all of the forms on the current page.
    """
    state.showforms()

def formclear(formname):
    """
    >> formclear <formname>
    
    Run 'clear' on all of the controls in this form.
    """
    form = state.get_form(formname)
    for control in form.controls:
        if control.readonly:
            continue

        control.clear()

def formvalue(formname, fieldname, value):
    """
    >> formvalue <formname> <field> <value>

    Set value of a form field.

    There are some ambiguities in the way formvalue deals with lists:
    'fv' will *add* the given value to a multilist.

    Formvalue ignores read-only fields completely; if they're readonly,
    nothing is done.

    Available as 'fv' as well.
    """
    form = state.get_form(formname)
    control = state.get_form_field(form, fieldname)

    if control:
        state.clicked(form, control)
        if control.readonly:
            return

        set_form_control_value(control, value)
    else:
        print 'NO SUCH FIELD FOUND / MULTIPLE MATCHES TO NAME'
        assert 0

fv = formvalue

def formfile(formname, fieldname, filename, content_type=None):
    """
    >> formfile <form> <field> <filename> [ <content_type> ]

    Upload a file via an "upload file" form field.
    """
    form = state.get_form(formname)
    control = state.get_form_field(form, fieldname)

    if control:
        if not control.is_of_kind('file'):
            print 'ERROR: field is not a file upload field!'
            assert 0
            
        state.clicked(form, control)
        fp = open(filename)
        control.add_file(fp, content_type, filename)

        print '\nAdded file "%s" to file upload field "%s"\n' % (filename,
                                                                 control.name,)
    else:
        print 'NO SUCH FIELD FOUND / MULTIPLE MATCHES TO NAME'
        assert 0

def extend_with(module_name):
    """
    >> extend_with <module>
    
    Import contents of given module.
    """
    global_dict, local_dict = get_twill_glocals()
    
    exec "from %s import *" % (module_name,) in global_dict, local_dict

def getinput(prompt):
    """
    >> getinput <prompt>
    Get input, store it in '__input__'.
    """
    global_dict, local_dict = get_twill_glocals()

    inp = raw_input(prompt)

    local_dict['__input__'] = inp

def getpassword(prompt):
    """
    >> getpassword <prompt>
    
    Get a password ("invisible input"), store it in '__password__'.
    """
    global_dict, local_dict = get_twill_glocals()

    inp = getpass.getpass(prompt)

    local_dict['__password__'] = inp

def save_cookies(filename):
    """
    >> save_cookies <filename>

    Save all of the current cookies to the given file.
    """
    state.save_cookies(filename)

def load_cookies(filename):
    """
    >> load_cookies <filename>

    Clear the cookie jar and load cookies from the given file.
    """
    state.load_cookies(filename)

def clear_cookies():
    """
    >> clear_cookies

    Clear the cookie jar.
    """
    state.clear_cookies()

def show_cookies():
    """
    >> show_cookies

    Show all of the cookies in the cookie jar.
    """
    state.show_cookies()

def add_auth(realm, uri, user, passwd):
    """
    >> add_auth <realm> <uri> <user> <passwd>

    Add HTTP Basic Authentication information for the given realm/uri.
    """
    creds = state.creds
    creds.add_password(realm, uri, user, passwd)

    print "Added auth info: realm '%s' / URI '%s' / user '%s'" % (realm,
                                                                  uri,
                                                                  user,)

def debug(what, level):
    """
    >> debug <what> <level>

    <what> can be:
       * http (any level >= 1), to display the HTTP transactions.
    """
    if what == "http":
        state._browser.set_debug_http(int(level))

def run(cmd):
    """
    >> run <command>

    <command> can be any valid python command; 'exec' is used to run it.
    """
    # @CTB: use pyparsing to grok the command?  make sure that quoting works...
    
    # execute command.
    import commands
    global_dict, local_dict = get_twill_glocals()

    # set __url__
    local_dict['__cmd__'] = cmd
    local_dict['__url__'] = commands.state.url()

    exec(cmd, global_dict, local_dict)

def runfile(files):
    """
    >> runfile <file1> [ <file2> ... ]

    """
    # @CTB: use pyparsing to separate out the files, so that quoted
    # filenames with spaces in them can be used, e.g.
    #     runfile "test 1" "test 2"

    import parse, sys
    global_dict, local_dict = get_twill_glocals()

    filenames = files.split(' ')
    for f in filenames:
        parse.execute_file(f)

def setglobal(name, value):
    """
    setglobal <name> <value>

    Sets the variable <name> to the value <value> in the global namespace.
    """
    global_dict, local_dict = get_twill_glocals()
    global_dict[name] = value

def setlocal(name, value):
    """
    setlocal <name> <value>

    Sets the variable <name> to the value <value> in the local namespace.
    """
    global_dict, local_dict = get_twill_glocals()
    local_dict[name] = value

def title(what):
    """
    >> title <regexp>
    
    Succeed if the regular expression is in the page title.
    """
    regexp = re.compile(what)
    title = state.get_title()

    if not regexp.search(title):
        raise TwillAssertionError("title does not contain '%s'" % (what,))

#### doesn't really work just yet.

agent_map = dict(
    ie5='Mozilla/4.0 (compatible; MSIE 5.0; Windows NT 5.1)',
    ie55='Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.1)',
    ie6='Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    moz17='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7) Gecko/20040616',
    opera7='Opera/7.0 (Windows NT 5.1; U) [en]',
    konq32='Mozilla/5.0 (compatible; Konqueror/3.2.3; Linux 2.4.14; X11; i686)',
    saf11='Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en-us) AppleWebKit/100 (KHTML, like Gecko) Safari/100',
    aol9='Mozilla/4.0 (compatible; MSIE 5.5; AOL 9.0; Windows NT 5.1)',)

