"""
Test the utils.run_tidy function.

This doesn't test to see if tidy was actually run; all it does is make sure
that the function runs without error.
"""
import testlib
from twill import utils

def setup():
    pass

def test():
    bad_html = """<a href="test">you</a> <b>hello."""
    (output, errors) = utils.run_tidy(bad_html)

    print output
    print errors

def teardown():
    pass

if __name__ == '__main__':
    setup()
    test()
    teardown()
