"""
A small extension function to check all of the links on a page.

Usage:

   check_links [ <pattern> ]

Make sure that all of the HTTP links on the current page can be visited
successfully.  If 'pattern' is given, check only URLs that match that
regular expression.
"""

__all__ = ['check_links']

DEBUG=True

import re
from twill import commands
from errors import TwillAssertionError

def check_links(pattern = '', visited={}):
    """
    >> check_links [ <pattern> ]

    Make sure that all of the HTTP links on the current page can be visited
    with an HTTP response 200 (success).  If 'pattern' is given, interpret
    it as a regular expression that link URLs must contain in order to be
    tested, e.g.

        check_links http://.*\.google\.com

    would check only links to google URLs.  Note that because 'follow'
    is used to visit the pages, the referrer URL is properly set on the
    visit.
    """
    OUT = commands.OUT
    browser = commands.browser

    #
    # compile the regexp
    #
    
    regexp = None
    if pattern:
        regexp = re.compile(pattern)

    #
    # iterate over all links, collecting those that match.
    #
    # note that in the case of duplicate URLs, only one of the
    # links is actually followed!
    #

    collected_urls = {}
    for link in browser._browser.links():
        url = link.absolute_url
        url = url.split('#', 1)[0]      # get rid of subpage pointers

        if not (url.startswith('http://') or url.startswith('https://')):
            if DEBUG:
               print>>OUT, "url '%s' is not an HTTP link; ignoring" % (url,)
            continue

        if regexp:
            if regexp.search(url):
                collected_urls[url] = link
                if DEBUG:
                    print>>OUT, "Gathered URL %s -- matched regexp" % (url,)
        else:
            collected_urls[url] = link
            if DEBUG:
                print>>OUT, "Gathered URL %s." % (url,)

    #
    # now, for each unique URL, follow the link. Trap ALL exceptions
    # as failures.
    #

    failed = []
    for link in collected_urls.values():
        went = False
        try:
            if DEBUG:
                print>>OUT, "Trying %s" % (link.absolute_url,),
                
            if not visited.has_key(link.absolute_url):
                browser.follow_link(link)
                went = True
                
                code = browser.get_code()
                assert code == 200

                visited[link.absolute_url] = 1
                
                if DEBUG:
                    print>>OUT, '...success!'
            else:
                if DEBUG:
                    print>>OUT, ' (already visited successfully)'
        except:
            failed.append(link.absolute_url)
            if DEBUG:
                print>>OUT, '...failure ;('

        if went:
            browser.back()
        
                

    if failed:
        print>>OUT, '\nCould not follow %d links' % (len(failed),)
        print>>OUT, '\t%s\n' % '\n\t'.join(failed)
        raise TwillAssertionError("broken links on page")
