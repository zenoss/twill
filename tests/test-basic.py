import os
import twilltestlib
from tests import url

def test():
    inp = "unique1\nunique2\n"
    
    twilltestlib.execute_twill_script('test-basic.twill', inp, initial_url=url)
    
def teardown_module():
    try:
        os.unlink(os.path.join(twilltestlib.testdir, 'test-basic.cookies'))
    except OSError:
        pass
