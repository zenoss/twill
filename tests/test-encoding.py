import twilltestlib
import ClientForm
from cStringIO import StringIO

def test_form_parse():
    content = "&rsaquo;"
    fp = StringIO(content)

    # latin-1 should fail...
    try:
        ClientForm.ParseFile(fp, "<test-encoding.py fp>", encoding='latin-1',
                             backwards_compat=False)
        assert 0, "should fail"
    except UnicodeEncodeError:
        pass


    # ...but the default (utf-8) should succeed.
    fp.seek(0)
    ClientForm.ParseFile(fp, "<test-encoding.py fp>", backwards_compat=False)
