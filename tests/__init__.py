import twilltestlib
import twilltestserver

url = None

def setup(package):
    twilltestlib.cd_testdir()
    package.url = twilltestlib.run_server(twilltestserver.create_publisher)
    
def teardown(package):
    twilltestlib.kill_server()
    twilltestlib.pop_testdir()
