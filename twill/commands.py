"""
Implementation of all of the individual 'twill' commands available through
twill-sh.
"""

# export:
__all__ = ['reset_browser',
           'extend_with',
           'exit',
           'go',
           'reload',
           'url',
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
           'showlinks',
           'showhistory',
           'submit',
           'formvalue',
           'fv',
           'formaction',
           'fa',
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
           'exit',
           'config',
           'tidy_ok'
           ]

import re, getpass, time

from browser import TwillBrowser

from errors import TwillAssertionError
from utils import set_form_control_value, run_tidy
from namespaces import get_twill_glocals
        
browser = TwillBrowser()

def reset_browser():
    """
    >> reset_browser

    Reset the browser completely.
    """
    global browser
    browser = TwillBrowser()

    global _options
    _options = {}
    _options.update(_orig_options)

###

def exit(code="0"):
    """
    exit [<code>]

    Exits twill, with the given exit code (defaults to 0, "no error").
    """
    raise SystemExit(int(code))

def go(url):
    """
    >> go <url>
    
    Visit the URL given.
    """
    browser.go(url)

def reload():
    """
    >> reload
    
    Reload the current URL.
    """
    browser.reload()

def code(should_be):
    """
    >> code <int>
    
    Check to make sure the response code for the last page is as given.
    """
    should_be = int(should_be)
    if browser.get_code() != int(should_be):
        raise TwillAssertionError("code is %s != %s" % (browser.get_code(),
                                                        should_be))

def tidy_ok():
    """
    >> tidy_ok

    Assert that 'tidy' produces no warnings or errors when run on the current
    page.

    If 'tidy' cannot be run, will fail silently (unless 'tidy_should_exist'
    option is true; see 'config' command).
    """
    page = browser.get_html()
    if page is None:
        raise TwillAssertionError("not viewing HTML!")
        
    (clean_page, errors) = run_tidy(page)
    if clean_page is None:              # tidy doesn't exist...
        if _options.get('tidy_should_exist'):
            raise TwillAssertionError("cannot run 'tidy'")
    elif errors:
        raise TwillAssertionError("tidy errors:\n====\n%s\n====\n" % (errors,))

    # page is fine.

def url(should_be):
    """
    >> url <regexp>

    Check to make sure that the current URL matches the regexp.  The local
    variable __match__ is set to the matching part of the URL.
    """
    regexp = re.compile(should_be)
    current_url = browser.get_url()

    m = None
    if current_url is not None:
        m = regexp.search(current_url)

    if not m:
        raise TwillAssertionError("url does not match '%s'" % (should_be,))

    global_dict, local_dict = get_twill_glocals()
    local_dict['__match__'] = m.group()

def follow(what):
    """
    >> follow <regexp>
    
    Find the first matching link on the page & visit it.
    """
    regexp = re.compile(what)
    links = browser.find_link(regexp)

    if links:
        browser.follow_link(links)
        return

    raise TwillAssertionError("no links match to '%s'" % (what,))

def find(what):
    """
    >> find <regexp>
    
    Succeed if the regular expression is on the page.  Sets the local
    variable __match__ to the matching text.
    """
    regexp = re.compile(what)
    page = browser.get_html()

    m = regexp.search(page)
    if not m:
        raise TwillAssertionError("no match to '%s'" % (what,))

    global_dict, local_dict = get_twill_glocals()
    local_dict['__match__'] = m.group()

def notfind(what):
    """
    >> notfind <regexp>
    
    Fail if the regular expression is on the page.
    """
    regexp = re.compile(what)
    page = browser.get_html()

    if regexp.search(page):
        raise TwillAssertionError("match to '%s'" % (what,))

def back():
    """
    >> back
    
    Return to the previous page.
    """
    browser.back()

def show():
    """
    >> show
    
    Show the HTML for the current page.
    """
    print browser.get_html()

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
    html = browser.get_html()

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

_agent_map = dict(
    ie5='Mozilla/4.0 (compatible; MSIE 5.0; Windows NT 5.1)',
    ie55='Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.1)',
    ie6='Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    moz17='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7) Gecko/20040616',
    opera7='Opera/7.0 (Windows NT 5.1; U) [en]',
    konq32='Mozilla/5.0 (compatible; Konqueror/3.2.3; Linux 2.4.14; X11; i686)',
    saf11='Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en-us) AppleWebKit/100 (KHTML, like Gecko) Safari/100',
    aol9='Mozilla/4.0 (compatible; MSIE 5.5; AOL 9.0; Windows NT 5.1)',)

def agent(what):
    """
    >> agent <agent>
    
    Set the agent string (identifying the browser brand).

    Some convenient shortcuts:
      ie5, ie55, ie6, moz17, opera7, konq32, saf11, aol9.
    """
    what = what.strip()
    agent = _agent_map.get(what, what)
    browser.set_agent_string(agent)

def submit(submit_button=None):
    """
    >> submit [<buttonspec>]
    
    Submit the current form (the one last clicked on) by clicking on the
    n'th submission button.  If no "buttonspec" is given, submit the current
    form by using the last clicked submit button.

    The form to submit is the last form clicked on with a 'formvalue' command.

    The button used to submit is chosen based on 'buttonspec'.  If 'buttonspec'
    is given, it's matched against buttons using the same rules that
    'formvalue' uses.  If 'buttonspec' is not given, submit uses the last
    submit button clicked on by 'formvalue'.  If none can be found,
    submit submits the form with no submit button clicked.
    """
    browser.submit(submit_button)

def showforms():
    """
    >> showforms
    
    Show all of the forms on the current page.
    """
    browser.showforms()

def showlinks():
    """
    >> showlinks
    
    Show all of the links on the current page.
    """
    browser.showlinks()

def showhistory():
    """
    >> showhistory

    Show the browser history (what URLs were visited).
    """
    browser.showhistory()

def formclear(formname):
    """
    >> formclear <formname>
    
    Run 'clear' on all of the controls in this form.
    """
    form = browser.get_form(formname)
    for control in form.controls:
        if control.readonly:
            continue

        control.clear()

def formvalue(formname, fieldname, value):
    """
    >> formvalue <formname> <field> <value>

    Set value of a form field.

    There are some ambiguities in the way formvalue deals with lists:
    'formvalue' will *add* the given value to a list of multiple selection,
    for lists that allow it.

    Forms are matched against 'formname' as follows:
      1. regexp match to actual form name;
      2. if 'formname' is an integer, it's tried as an index.

    Form controls are matched against 'fieldname' as follows:
      1. unique exact match to control name;
      2. unique regexp match to control name;
      3. if fieldname is an integer, it's tried as an index;
      4. unique & exact match to submit-button values.

    Formvalue ignores read-only fields completely; if they're readonly,
    nothing is done, unless the config options ('config' command) are
    changed.

    'formvalue' is vailable as 'fv' as well.
    """
    form = browser.get_form(formname)
    if not form:
        raise TwillAssertionError("no matching forms!")

    control = browser.get_form_field(form, fieldname)

    browser.clicked(form, control)

    if _options['readonly_controls_writeable']:
        print 'forcing read-only control to writeable'
        control.readonly = False
        
    if control.readonly:
        print 'control is read-only; nothing done.'
        return

    set_form_control_value(control, value)

fv = formvalue

def formaction(formname, action):
    """
    >> formaction <formname> <action_url>

    Sets action parameter on form to action_url
    """
    form = browser.get_form(formname)
    form.action = action

fa = formaction

def formfile(formname, fieldname, filename, content_type=None):
    """
    >> formfile <form> <field> <filename> [ <content_type> ]

    Upload a file via an "upload file" form field.
    """
    form = browser.get_form(formname)
    control = browser.get_form_field(form, fieldname)

    if control:
        if not control.is_of_kind('file'):
            print 'ERROR: field is not a file upload field!'
            assert 0
            
        browser.clicked(form, control)
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
    browser.save_cookies(filename)

def load_cookies(filename):
    """
    >> load_cookies <filename>

    Clear the cookie jar and load cookies from the given file.
    """
    browser.load_cookies(filename)

def clear_cookies():
    """
    >> clear_cookies

    Clear the cookie jar.
    """
    browser.clear_cookies()

def show_cookies():
    """
    >> show_cookies

    Show all of the cookies in the cookie jar.
    """
    browser.show_cookies()

def add_auth(realm, uri, user, passwd):
    """
    >> add_auth <realm> <uri> <user> <passwd>

    Add HTTP Basic Authentication information for the given realm/uri.
    """
    creds = browser.creds
    creds.add_password(realm, uri, user, passwd)

    print "Added auth info: realm '%s' / URI '%s' / user '%s'" % (realm,
                                                                  uri,
                                                                  user,)

def debug(what, level):
    """
    >> debug <what> <level>

    <what> can be:
       * http (any level >= 1), to display the HTTP transactions.
       * commands (any level >= 1), to display the commands being executed.
    """
    import parse
    
    if what == "http":
        browser._browser.set_debug_http(int(level))
    elif what == 'twill':
        if level > 0:
            parse.debug_print_commands(True)
        else:
            parse.debug_print_commands(False)

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
    local_dict['__url__'] = commands.browser.url()

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
    title = browser.get_title()

    m = regexp.search(title)
    if not m:
        raise TwillAssertionError("title does not contain '%s'" % (what,))

    global_dict, local_dict = get_twill_glocals()
    local_dict['__match__'] = m.group()

### options

_orig_options = dict(readonly_controls_writeable=False,
                     do_run_tidy=True,
                     tidy_should_exist=False)
_options = {}
_options.update(_orig_options)           # make a copy

def config(key=None, value=None):
    """
    >> config [<key> [<int value>]]

    Configure/report various options.  If no <value> is given, report
    the current key value; if no <key> given, report current settings.

    So far:

     * 'readonly_controls_writeable', default 0;
     * 'do_run_tidy', default 1;
     ' 'tidy_should_exist', default 0;
    """
    if key is None:
        keys = _options.keys()
        keys.sort()

        print 'current configuration:'
        for k in keys:
            print '\t%s : %s' % (k, _options[k])
        print ''
    else:
        v = _options.get(key)
        if v is None:
            print '*** no such configuration key', key
            print 'valid keys are:', ";".join(_options.keys())
        elif value is None:
            print ''
            print 'key %s: value %s' % (key, v)
            print ''
        else:
            try:
                value = int(value)
            except ValueError:
                pass

            _options[key] = value
