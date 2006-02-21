import sys, os
import twilltestlib
from twill import commands
from twill import namespaces
from twill.errors import TwillAssertionError
import twill.parse
from cStringIO import StringIO
from tests import url

def setup_module():
    global _save_print
    _save_print = twill.parse._print_commands
    twill.parse.debug_print_commands(True)

def test():
    # from file
    twilltestlib.execute_twill_script('test-go.twill', initial_url=url)

    # from stdin
    filename = os.path.join(twilltestlib.testdir, 'test-go.twill')
    old_in, sys.stdin = sys.stdin, open(filename)
    try:
        twilltestlib.execute_twill_script('-', initial_url=url)
    finally:
        sys.stdin = old_in

    # from parse.execute_file
    twill.parse.execute_file('test-go-exit.twill', initial_url=url)
    
    # also test some failures.

    old_err, sys.stderr = sys.stderr, StringIO()
    try:
        #
        # failed assert in a script
        #
        try:
            twill.parse.execute_file('test-go-fail.twill', initial_url=url)
            assert 0
        except TwillAssertionError:
            pass

        commands.go(url)
        try:
            commands.code(400)
            assert 0
        except TwillAssertionError:
            pass

        #
        # no such command (NameError)
        #

        try:
            twill.parse.execute_file('test-go-fail2.twill', initial_url=url)
            assert 0
        except NameError:
            pass
    finally:
        sys.stderr = old_err

    namespaces.new_local_dict()
    gd, ld = namespaces.get_twill_glocals()

    commands.go(url)
    try:
        twill.parse.execute_command('url', ('not this',), gd, ld, "anony")
        assert 0, "shouldn't get here"
    except TwillAssertionError:
        pass

    try:
        commands.follow('no such link')
        assert 0, "shouldn't get here"
    except TwillAssertionError:
        pass

    try:
        commands.find('no such link')
        assert 0, "shouldn't get here"
    except TwillAssertionError:
        pass

    try:
        commands.notfind('Hello')
        assert 0, "shouldn't get here"
    except TwillAssertionError:
        pass

    try:
        twill.parse.execute_command('exit', ('0',), gd, ld, "anony")
        assert 0, "shouldn't get here"
    except SystemExit:
        pass
    
def teardown_module():
    twill.parse.debug_print_commands(_save_print)
