import twilltestlib
import twilltestserver

url = None

def setup(package):
    twilltestlib.cd_testdir()
    package.url = twilltestlib.run_server(twilltestserver.create_publisher)

    from twill.commands import go, find
    try:
        go(url)
        find("These are the twill tests")
    except:
        raise Exception("\n\n***\n\nHello! The twill test server is not running or cannot be reached; please free port 8080 (or set TWILL_TEST_PORT to something else), and clear your proxy settings too!\n\n***\n\n")
    
def teardown(package):
    twilltestlib.kill_server()
    twilltestlib.pop_testdir()
