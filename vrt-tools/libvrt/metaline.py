'''Support library for vrt-tools.

Warning: this is not a validator.

'''

import re
import sys

from collections import OrderedDict

def attributes(line):
    return tuple(name for name, value in pairs(line))

def mapping(line):
    it = OrderedDict(pairs(line))
    return it

def pairs(line):
    return re.findall(br'(\S+)="([^""]*)"', line)

def element(line):
    '''Get start or end tag element name from line (bytes).'''
    mo = re.search(rb'\w+', line)
    return mo.group(0) if mo else None

def strelement(line):
    '''Get start or end tag element name from line (str).'''
    mo = re.search(r'\w+', line)
    return mo.group(0) if mo else None

def valuegetter(head, *,
                missing, # missing value mark (safe bytes)
                warn = True,
                prog = '(prog)', # for the warning message (str)
                many = None): # max number of warnings (int)
    '''Sigh.'''
    if warn:
        seen = 0
        def warner(line):
            nonlocal seen
            this = mapping(line)
            if many is None or seen < many:
                what = sorted(name for name in this if name not in head)
                miss = tuple(name for name in head if name not in this)
                if what or miss:
                    seen += 1
                    (
                        what and
                        print('{}: warning: not in head:'.format(prog),
                              *(repr(name.decode('utf-8')) for name in what),
                              file = sys.stderr)
                    )
                    (
                        miss and
                        print('{}: warning: missing:'.format(prog),
                              # no repr, trust head
                              *(name.decode('utf-8') for name in miss),
                              file = sys.stderr)
                    )
                    if many is not None and seen == many:
                        print('{}: warning: ...'.format(prog),
                              file = sys.stderr)

            return tuple(unescape(this.get(name, missing))
                         for name in head)
        return warner

    def getter(line):
        return tuple(unescape(mapping(line).get(name, missing))
                     for name in head)

    return getter

# ...

ENTITIES = {
    b'&lt;' : b'<',
    b'&gt;' : b'>',
    b'&amp;' : b'&',
    b'&quot;' : b'"',
    b'&apos;' : b"'",
    b'\t' : b'{TAB}' # tab is field separator
}

ENTITY_RE_NOTAB = b'&(lt|gt|amp|quot|apos);'
ENTITY_RE_TAB = ENTITY_RE_NOTAB + b'|\t'
ENTITY_RE = {
    # key: whether to encode tabs or not
    False: re.compile(ENTITY_RE_NOTAB),
    True: re.compile(ENTITY_RE_TAB),
}

def unentify(mo): return ENTITIES[mo.group()]
def unescape(value, tabs=True):
    '''Unescape the allowed character entities &lt; &gt; &amp; &quot; and
    &apos;. Should really warn of any other or something, or not? This
    is not a validator! But in that case html.unescape is good enough!
    Otherwise, there might even be bare ampersands, and who can tell
    which is which then.

    Also replace tabs with {TAB} unless tabs is False.

    '''

    return ENTITY_RE[tabs].sub(unentify, value)

def escape(value):
    '''Escape & < > " in value as &amp; &lt; &gt; &quot; respectively.'''
    return ( value
             .replace(b'&', b'&amp;')
             .replace(b'<', b'&lt;')
             .replace(b'>', b'&gt;')
             .replace(b'"', b'&quot;')
    )

STR_ENTITIES = dict((key.decode('utf-8'), val.decode('utf-8'))
                    for key, val in ENTITIES.items())

STR_ENTITY_RE_NOTAB = ENTITY_RE_NOTAB.decode('utf-8')
STR_ENTITY_RE_TAB = ENTITY_RE_TAB.decode('utf-8')
STR_ENTITY_RE = {
    # key: whether to encode tabs or not
    False: re.compile(STR_ENTITY_RE_NOTAB),
    True: re.compile(STR_ENTITY_RE_TAB),
}

def strunentify(mo): return STR_ENTITIES[mo.group()]
def strunescape(value, tabs=True):
    '''As unescape but for strings instead of bytes.'''

    return STR_ENTITY_RE[tabs].sub(strunentify, value)

def strescape(value):
    '''Escape & < > " in value (str) as &amp; &lt; &gt; &quot; respectively.'''
    return ( value
             .replace('&', '&amp;')
             .replace('<', '&lt;')
             .replace('>', '&gt;')
             .replace('"', '&quot;')
    )

def starttag(struct, attrs, sort=False):
    '''Start tag line for struct (bytes) with attrs (bytes, bytes).

    attrs can be either a dict or a list of pairs (name, value).
    attrs should be an OrderedDict to preserve attribute order for
    Python versions prior to 3.8.

    If sort == True, sort the attributes by name.

    This function does not escape attribute values in attrs nor check
    their escaping, so that should be done by the caller.

    '''

    attrstr = b' '.join(name + b'="' + val + b'"'
                        for name, val in _get_attrs(attrs, sort))
    return b'<' + struct + (b' ' + attrstr if attrstr else b'') + b'>\n'

def _get_attrs(attrs, sort=False):
    '''Return items from attrs (dict or list of pairs), sorted if sort.'''
    try:
        items = attrs.items()
    except AttributeError:
        items = attrs
    return sorted(items) if sort else items

def strstarttag(struct, attrs, sort=False):
    '''Start tag line for struct (str) with attrs (str, str).

    This works the same way for strings as starttag for bytes.

    '''

    attrstr = ' '.join(name + '="' + val + '"'
                       for name, val in _get_attrs(attrs, sort))
    return '<' + struct + (' ' + attrstr if attrstr else '') + '>\n'

def ismeta(line):
    '''line (bytes) is metaline.'''
    return line and line[0] in b'<'

def strismeta(line):
    '''line (str) is metaline.'''
    return line and line[0] == '<'

# Should the following functions call ismeta(line) (or
# strismeta(line)) or not? Currently they don't, to reduce overhead
# when ismeta is tested first by the caller.

def isstarttag(line):
    '''line (bytes) is a start tag, assuming ismeta(line).'''
    return line[1] not in b'/!'

def strisstarttag(line):
    '''line (str) is a start tag, assuming strismeta(line).'''
    return line[1] not in '/!'

def isendtag(line):
    '''line (bytes) is an end tag, assuming ismeta(line).'''
    # This is faster than line[1].startswith(b'/')
    return line[1] in b'/'

def strisendtag(line):
    '''line (str) is an end tag, assuming strismeta(line).'''
    return line[1] == '/'

def iscomment(line):
    '''line (bytes) is a comment, assuming ismeta(line).'''
    return line.startswith(b'<!--')

def striscomment(line):
    '''line (str) is a comment, assuming strismeta(line).'''
    return line.startswith('<!--')
