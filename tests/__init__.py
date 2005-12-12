import twilltestlib
import twilltestserver

url = None

def setup(package):
    twilltestlib.cd_testdir()
    package.url = twilltestlib.run_server(twilltestserver.create_publisher)
    print "Started twilltestserver at %s" % package.url
    
def teardown(package):
    twilltestlib.kill_server()
    twilltestlib.pop_testdir()
