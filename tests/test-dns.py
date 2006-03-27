import twilltestlib
from tests import url

def test():
    twilltestlib.execute_twill_script('test-dns.twill', initial_url=url)
    
