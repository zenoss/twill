"""
@CTB: still need to find something that only BS (and not the intolerant
parser) can parse.
"""

import ClientForm

import twilltestlib
from tests import url
from twill import commands

def test_raw():
    """
    test parsing of raw, unfixed HTML.
    """
    b = commands.get_browser()

    commands.config('use_tidy', '0')
    commands.config('use_BeautifulSoup', '0')
    commands.config('allow_parse_errors', '0')

    commands.go(url)

    ###
    
    commands.go('/tidy_fixable_html')

    assert len(b._browser.forms()) == 0, \
           "there should be no correct forms on this page"

    ###

    commands.go('/BS_fixable_html')
    assert len(b._browser.forms()) == 1, \
           "there should be one mangled form on this page"

    ###

    commands.go('/unfixable_html')
    try:
        b._browser.forms()
        assert 0, "this page has a parse error."
    except ClientForm.ParseError:
        pass

def test_tidy():
    """
    test parsing of tidy-processed HTML.
    """
    b = commands.get_browser()

    commands.config('use_tidy', '1')
    commands.config('use_BeautifulSoup', '0')
    commands.config('allow_parse_errors', '0')

    commands.go(url)

    ###
    
    commands.go('/tidy_fixable_html')

    assert len(b._browser.forms()) == 1, \
           "there should be one correctable form on this page"

    ###

    commands.go('/BS_fixable_html')
    assert len(b._browser.forms()) == 1, \
           "there should be one mangled form on this page"

    ###

    commands.go('/unfixable_html')
    try:
        b._browser.forms()
        assert 0, "this page has a parse error."
    except ClientForm.ParseError:
        pass

def test_BeautifulSoup():
    """
    test parsing of BS-processed HTML.
    """
    b = commands.get_browser()

    commands.config('use_tidy', '0')
    commands.config('use_BeautifulSoup', '1')
    commands.config('allow_parse_errors', '0')

    commands.go(url)

    ###
    
    commands.go('/tidy_fixable_html')

    assert len(b._browser.forms()) == 0, \
           "there should be no correct forms on this page"

    ###

    commands.go('/BS_fixable_html')
    assert len(b._browser.forms()) == 1, \
           "there should be one mangled form on this page"

    ###

    commands.go('/unfixable_html')
    try:
        b._browser.forms()
        assert 0, "this page has a parse error."
    except ClientForm.ParseError:
        pass

def test_allow_parse_errors():
    """
    test nice parsing.
    """
    b = commands.get_browser()

    commands.config('use_tidy', '0')
    commands.config('use_BeautifulSoup', '1')
    commands.config('allow_parse_errors', '1')

    commands.go(url)

    commands.go('/unfixable_html')
    b._browser.forms()

def test_effed_up_forms():
    """
    @CTB should succeed, doesn't for now
    """
    b = commands.get_browser()
    commands.config('use_tidy', '0')

    commands.go(url)
    commands.go('/effed_up_forms')
    assert not b._browser.forms()       # @CTB shouldn't be 'not'
