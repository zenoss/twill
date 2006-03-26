"""
Extension functions to help query/assert name service information.

Functions:

  * dns_resolves -- assert that a host resolves to a specific IP address.
  * dns_a -- assert that a host directly resolves to a specific IP address
  * dns_cname -- assert that a host is an alias for another hostname.
  * dnx_mx -- assert that a given host is a mail exchanger for the given name.
  * dns_ns -- assert that a given hostname is a name server for the given name.
"""

from twill.errors import TwillAssertionError

try:
    import dns.resolver
except ImportError:
    raise Exception("ERROR: must have dnspython installed to use the DNS extension module")

def dns_a(host, ipaddress, server=None):
    """
    >> dns_a <name> <ipaddress> [<name server>]

    Assert that <name> resolves to <ipaddress> (and is an A record).
    Optionally use the given name server.
    """
    if not is_ip_addr(ipaddress):
        raise Exception("<ipaddress> parameter must be an IP address, not a hostname")

    for answer in _query(host, 'A', server):
        if _compare_hostnames(ipaddress, str(answer)):
            return True

    raise TwillAssertionError

def dns_cname(host, cname, server=None):
    """
    >> dns_cname <name> <alias_for> [<name server>]

    Assert that <name> is a CNAME alias for <alias_for>  Optionally use
    <name server>.
    """
    if is_ip_addr(cname):
        raise Exception("<alias_for> parameter must be a hostname, not an IP address")
    
    for answer in _query(host, 'CNAME', server):
        if _compare_hostnames(cname, str(answer)):
            return True

    raise TwillAssertionError

def dns_resolves(host, ipaddress, server=None):
    """
    >> dns_resolves <name> <name2/ipaddress> [<name server>]
    
    Assert that <name> ultimately resolves to the given IP address (or
    the same IP address that 'name2' resolves to).  Optionally use the
    given name server.
    """
    if not is_ip_addr(ipaddress):
        ipaddress = _resolve_name(ipaddress, server)
        
    for answer in _query(host, 1, server):
        if _compare_hostnames(ipaddress, str(answer)):
            return True

    raise TwillAssertionError

def dns_mx(host, mailserver, server=None):
    """
    >> dns_mx <name> <mailserver> [<name server>]

    Assert that <mailserver> is a mailserver for <name>.
    """
    for rdata in _query(host, 'MX', server):
        (pref, n) = str(rdata).split()

        if _compare_hostnames(n, mailserver):
            return True

    raise TwillAssertionError

def dns_ns(host, query_ns, server=None):
    """
    >>> dns_ns <domain> <nameserver> [<name server to use>]

    Assert that <nameserver> is a mailserver for <domain>.
    """
    for answer in _query(host, 'NS', server):
        if _compare_hostnames(query_ns, str(answer)):
            return True

###

def _compare_hostnames(a, b):
    """
    Normalize two hostnames for string comparison.  (basically strip off
    '.'s ;)
    """
    a = a.strip('.')
    b = b.strip('.')
    return (a == b)

def is_ip_addr(name):
    """
    Check the 'name' to see if it's just an IP address.  Probably should use
    a regexp to do this... @CTB
    """
    name = name.replace('.', '')
    for i in range(0, 10):
        i = str(i)
        name = name.replace(i, '')

    if name:
        return False
    return True

def _resolve_name(name, server):
    """
    Resolve the given name to an IP address.
    """
    if is_ip_addr(name):
        return name
    
    r = dns.resolver.Resolver()
    if server:
        r.nameservers = [_resolve_name(server)]

    answers = r.query(name)

    answer = None
    for answer in answers:              # @CTB !?
        break

    assert answer
    return str(answer)

def _query(query, query_type, server):
    """
    Query, perhaps via the given name server.  (server=None to use default).
    """
    r = dns.resolver.Resolver()
    if server:
        r.nameservers = [_resolve_name(server)]

    return r.query(query, query_type)
