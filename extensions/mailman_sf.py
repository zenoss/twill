import twill, twill.utils
import re

# export:
__all__ = ['discard_all_messages',
           ]

def discard_all_messages(*noargs):
    formvalue_by_regexp_setall("1", "^\d+$", "3")

def formvalue_by_regexp_setall(formname, fieldname, value):
    state = twill.get_browser_state()
    
    form = state.get_form(formname)
    if not form:
        print 'no such form', formname
        return

    regexp = re.compile(fieldname)

    matches = [ ctl for ctl in form.controls if regexp.search(str(ctl.name)) ]

    if matches:
        print '-- matches %d' % (len(matches),)

        n = 0
        for control in matches:
            state.clicked(form, control)
            if control.readonly:
                continue

            n += 1
            twill.utils.set_form_control_value(control, value)

        print 'set %d values total' % (n,)
