# -*- coding: utf-8 -*-


"""
Module korpimport.xmlutil

Common utility functions and classes for processing XML in Korp/CWB
importing and VRT processing scripts.
"""


from xml.sax.saxutils import escape, unescape


def make_starttag(elemname, attrnames=None, attrdict=None, attrs=None):
    """Make an XML start tag for element elemname, with given attributes.

    The start tag will contain the attributes listed in attrnames with
    their values in the dictionary attrdict, or alternatively,
    the name-value pairs in attrs. See get_attr for more information on
    the values of attrnames and attrdict.
    """
    return ('<' + elemname
            + (' ' + make_attrs(attrnames or [], attrdict or {},
                                attrs or [], elemname)
               if attrnames or attrs else '')
            + '>')


def make_attrs(attrnames=None, attrdict=None, attrs=None, elemname=''):
    """Make a formatted attribute list for an element (also see get_attr).

    If attrs is specified (an iterable of name-value pairs), it is
    used instead of attrnames and attrdict.
    """
    if not attrs:
        attrnames = attrnames or []
        attrdict = attrdict or {}
        attrs = (get_attr(attrname, attrdict, elemname)
                 for attrname in attrnames)
    return ' '.join(make_attr(name, value) for name, value in attrs)


def make_attr(name, value):
    """Make name="value", with the appropriate characters in value escaped."""
    return u'{name}="{value}"'.format(
        name=name,
        value=escape(unescape(value,
                              {'&quot;': '"', '&apos;': '\''}),
                     {'"': '&quot;'}))


def get_attr(attrname, attrdict, elemname=''):
    """Return attribute name and value in attrdict for attrname (in elemname).

    attrname may be either a string or a pair of strings containing
    the input and output attribute name: the input name is the key for
    attrdict and the output name is the name to return. For a simple
    string, the output name is the same as the input name.

    The keys of attrdict may be either plain attribute names or
    attribute names prefixed with the element name and an underscore.
    The latter takes precedence if one exists for elemname.

    The return value is a pair of attribute name and value.
    """
    if isinstance(attrname, tuple):
        (attrname_output, attrname_input) = attrname
    else:
        attrname_output = attrname_input = attrname
    attrval = attrdict.get(elemname + '_' + attrname_input,
                           attrdict.get(attrname_input, ''))
    return (attrname_output, attrval)


def make_elem(elemname, content='', attrnames=None, attrdict=None, attrs=None,
              indent=0, newlines=False):
    """Make an XML element for elemname with the given content and attributes.

    The parameters elemname, attrnames, attrdict and attrs are as for
    make_starttag; content is the content of the element or None for
    an empty element; indent is the indentation depth (number of space
    characters) to be prepended to each line of content; if newlines
    is True, add a newline after the start tag and before the end tag
    (unless content ends in a newline).
    """
    starttag = make_starttag(elemname, attrnames, attrdict, attrs)
    if content is None:
        return starttag[:-1] + u'/>'
    content_end = ''
    if content and content[-1] == '\n':
        content_end = '\n'
        content = content[:-1]
    if indent > 0:
        content = content.replace(u'\n', u'\n' + (u' ' * indent)).rstrip(' ')
    newline1 = u'\n' + (u' ' * indent) if newlines else ''
    newline2 = u'\n' if newlines and content and content_end != '\n' else ''
    return (starttag + newline1 + content + content_end + newline2
            + u'</' + elemname + u'>')
