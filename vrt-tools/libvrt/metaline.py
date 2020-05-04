'''Support library for vrt-tools.

Warning: this is not a validator.

'''

import re
import sys

def attributes(line):
    return tuple(name for name, value in pairs(line))

def mapping(line):
    it = dict(pairs(line))
    return it

def pairs(line):
    return re.findall(br'(\S+)="([^""]*)"', line)

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

def unentify(mo): return ENTITIES[mo.group()]
def unescape(value):
    '''Unescape the allowed character entities &lt; &gt; &amp; &quot; and
    &apos;. Should really warn of any other or something, or not? This
    is not a validator! But in that case html.unescape is good enough!
    Otherwise, there might even be bare ampersands, and who can tell
    which is which then.

    '''

    return re.sub(b'&(lt|gt|amp|quot|apos);|\t', unentify, value)
