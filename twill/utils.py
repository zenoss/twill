import ClientForm

class ResultWrapper:
    """
    Deal with mechanize/urllib2/whatever results, and present them in a
    unified form.  Returned by 'journey'-wrapped functions.

    get_url() and get_page() only work when code=200.
    """
    def __init__(self, http_code, url=None, page=None):
        self.http_code = int(http_code)
        self.url = url
        self.page = page

    def get_url(self):
        return self.url

    def get_http_code(self):
        return self.http_code

    def get_page(self):
        return self.page

def journey(func, *args, **kwargs):
    """
    Wrap 'func' so that HTTPErrors and other things are captured when
    'func' is executed as func(*args, **kwargs).  Convert result from
    the various confusing options (exceptions, etc.) into a 'ResultWrapper'.

    This function may be more than a bit ugly & confusing, my apologies.

    Idea stolen from PBP, which used lambda functions waaaaay too much.
    """
    result = func(*args, **kwargs)

    new_result = ResultWrapper(result.wrapped.code, # HTTP response code
                               result.geturl(), #  URL
                               result.read() # HTML
                               )

    return new_result

def trunc(s, length):
    """
    Truncate a string s to length length, by cutting off the last 
    (length-4) characters and replacing them with ' ...'
    """
    if not s:
        return ''
    
    if len(s) > length:
        return s[:length-4] + ' ...'
    
    return s

def print_form(n, f):
    """
    Pretty-print the given form, assigned # n.
    """
    if f.name:
        print 'Form name=%s' % (f.name,)
    else:
        print 'Form #%d' % (n + 1,)

    if f.controls:
        print "## __Name______ __Type___ __ID________ __Value__________________"

    clickies = [c for c in f.controls if c.is_of_kind('clickable')]
    nonclickies = [c for c in f.controls if c not in clickies]

    for field in nonclickies:
        if hasattr(field, 'possible_items'):
            value_displayed = "%s of %s" % (field.value,
                                            field.possible_items())
        else:
            value_displayed = "%s" % (field.value,)
        strings = ("  ",
                   "%-12s %-9s" % (trunc(str(field.name), 12),
                                   trunc(field.type, 9)),
                   "%-12s" % (trunc(field.id or "(None)", 12),),
                   trunc(value_displayed, 40),
                   )
        for s in strings:
            print s,
        print ''

    for n, field in enumerate(clickies):
        strings = ("%-2s" % (n+1,),
                   "%-12s %-9s" % (trunc(field.name, 12),
                                   trunc(field.type, 9)),
                   "%-12s" % (trunc(field.id or "(None)", 12),),
                   trunc(field.value, 40),
                   )
        for s in strings:
            print s,
        print ''

def set_form_control_value(control, val):
    """
    Helper function to deal with setting form values on lists etc.
    """
    if isinstance(control, ClientForm.ListControl):
        control.set(1, val)
    else:
        control.value = val
