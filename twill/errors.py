class TwillAssertionError(AssertionError):
    """
    AssertionError to raise upon failure of some twill command.
    Subclassed so that such errors can be caught separately from
    normal AssertionErrors (from e.g. mechanize).
    """
    pass
