'''Support library for vrt-tools.

Warning: this is not a validator.

'''

from itertools import chain
import re
import sys

def record(line):
    return line.rstrip(b'\r\n').split(b'\t')

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
            this = record(line)
            if many is None or seen < many:
                if not len(this) == len(head):
                    seen += 1
                    (
                        len(this) > len(head) and
                        print('{}: warning: too many fields: ignoring {}'
                              .format(prog, len(this) - len(head)),
                              file = sys.stderr)
                    )
                    (
                        len(this) < len(head) and
                        print('{}: warning: missing fields:'.format(prog),
                              # no repr, trust head
                              *(name.decode('utf-8')
                                for name in head[len(this):]),
                              file = sys.stderr)
                    )
                    if many is not None and seen == many:
                        print('{}: warning: ...'.format(prog),
                              file = sys.stderr)

            if len(this) == len(head):
                return tuple(map(unescape, this))

            if len(this) < len(head):
                rest = (missing for k in range(len(this), len(head)))
                return tuple(map(unescape, chain(this, rest)))

            return tuple(map(unescape, this[:len(head)]))

        return warner

    def getter(line):
        return tuple(map(unescape, record(line)))

    return getter

# ...

ENTITIES = {
    b'&lt;' : b'<',
    b'&gt;' : b'>',
    b'&amp;' : b'&',
    b'&quot;' : b'"',
    b'&apos;' : b"'",
    b'\t' : b'{TAB}' # tab is field separator
    # why is \t here?
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

def escape(value):
    '''Escape & < > in value as &amp; &lt; &gt; respectively.'''
    return ( value
             .replace(b'&', b'&amp;')
             .replace(b'<', b'&lt;')
             .replace(b'>', b'&gt;')
    )
