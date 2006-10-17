import twilltestlib
from tests import url

import pkg_resources
pkg_resources.require('dnspython>=1.4')

def test():
    twilltestlib.execute_twill_script('test-dns.twill', initial_url=url)
    
