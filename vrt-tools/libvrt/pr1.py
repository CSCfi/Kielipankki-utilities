# -*- mode: Python; -*-

'''Protocol for interfacing with external sentence-annotation tools,
with the following characteristics that might be different in an
alternative protocol.

0. Input is VRT, output is VRT. With field name comment before first
   sentence. With every token inside a sentence. At least one token
   inside every sentence.

1. Any meta outside sentences (outer meta) is observed to decide
   whether to pass current sentence to the external tool or keep it.

2. Any meta inside sentences (inner meta) is passed transparently
   through.

A particular tool is implemented as a module that provides the
tool-specific functionality.

'''

from itertools import filterfalse, groupby
from queue import Queue
from threading import Thread

from libvrt.bad import BadData, BadCode

NAMES, OUTER, INNER, TAGS, META, DATA, JOIN, KEEP = range(2, 10)

def transput(args, imp, proc, ins, ous):

    '''Set up a thread that pushes a (segmented) copy of ins to a queue
    and uses imp to feed proc with input sentences from ins. Combine
    the copy of ins with the output sentences from proc and write the
    combined result to ous.

    '''

    matter = _segment(ins)
    kind, head = next(matter)

    if kind == TAGS:
        raise BadData('no name comment before first sentence')

    names = imp.pr1_init(args, _extract(head))

    copy = Queue()
    copy.put((NAMES, names))
    copy.put((OUTER, head))

    imp.pr1_test(meta = head)
    feed = Thread(target = _separate,
                  args = (args, imp, matter, copy, proc),
                  name = 'Separation Thread',
                  daemon = True)
    feed.start()

    _combinate(args, imp, copy, proc, ous)

    # proc should have run its course by now;
    # the 30 second timeout may or may not be
    # either excessive or sufficient
    code = proc.wait(timeout = 30)

    if not copy.empty():
        raise BadCode('copy queue is not empty')

    # feed should have run its course by now,
    # but was sometimes observed alive before
    # the addition of the (probably excessive)
    # timeout; incidentally, documentation says
    # the timeout "should be a floating point
    # number" but does not seem to mean it
    feed.join(5)
    if feed.is_alive():
        raise BadCode('separation thread is still alive')

    return code

def _segment(ins):
    '''Yield non-empty input lines in classified groups.

    (TAGS, lines) is a succession of sentence tags (start or end);
    (OUTER, lines) is a succession of meta lines outside sentence;
    (INNER, mix) consists of all lines inside a sentence.

    In (INNER, mix), in the mix:
    (META, line) is an inner meta line;
    (DATA, record) is a stripped-and-split data line (a record).

    There are three legitimate TAGS groups: a lone start tag, a lone
    end tag, and an end tag followed by a start tag.

    Both meta groups and data groups may consist of many lines, but
    any impractical numbers are considered impossible (an error, like
    a data set that does not use sentence tags, for example).

    It is very important to note that no unescaping of the few special
    characters is done.

    '''
    inside = False
    for k, g in groupby(filterfalse(bytes.isspace, ins), lambda line:
                        line.startswith((b'<sentence ',
                                         b'<sentence>',
                                         b'</sentence>'))):
        if k:
            lines = tuple(g)
            yield TAGS, lines
            inside = lines[-1].startswith(b'<sentence')
        elif inside:
            yield INNER, tuple(((META, line)
                                if line.startswith(b'<') else
                                (DATA, line.rstrip(b'\r\n').split(b'\t')))
                               for line in g)
        else:
            yield OUTER, tuple(g)

def _extract(head):
    '''Extract and return the field names from a comment in the first
    group of lines. Raise a BadData exception if the comment is not
    there.

    '''
    line = next((line for line in head
                 if line.startswith(b'<!-- #vrt positional-attributes: ')
                 if line.rstrip(b'\r\n').endswith(b' -->')),
                None)
    if line is None:
        raise BadData('no name comment before first sentence')

    names = line.split()[3:-1]
    return names

def _separate(args, imp, matter, copy, proc):
    '''In another thread, put all incoming matter (segmented ins) to copy
    (a queue of classified groups of lines) and some of the sentences
    to proc according to imp. Finally put a sentinel in copy.

    Matter coming in as TAGS, OUTER, INNER (DATA records, META lines).
    Matter going to copy as TAGS, OUTER, JOIN (with proc), KEEP.
    Choice to JOIN or KEEP is up to imp, with access to TAGS and OUTER.

    '''
    def ismeta(line):
        '''Whether an INNER line is META (or DATA).'''
        kind, content = line
        return kind == META

    for kind, lines in matter:
        if kind == TAGS:
            copy.put((kind, lines))
            imp.pr1_test(tags = lines)
        elif kind == OUTER:
            copy.put((kind, lines))
            imp.pr1_test(meta = lines)
        elif imp.pr1_test():
            # kind == INNER
            copy.put((JOIN, lines))
            imp.pr1_send((line for kind, line in lines
                          if kind == DATA),
                         proc)
        else:
            # kind == INNER
            copy.put((KEEP, lines))
    else:
        copy.put((None, ()))
        proc.stdin.close()

def _combinate(args, imp, copy, proc, ous):
    '''In the main thread.'''

    news = imp.pr1_read(proc.stdout)

    kind, old = copy.get(block = False)
    while kind is not None:
        if kind in (OUTER, TAGS):
            _write_meta(old, ous)
        elif kind == JOIN:
            _write_join(imp, old, next(news), ous)
        elif kind == KEEP:
            _write_keep(imp, old, ous)
        elif kind == NAMES:
            # actually *new* names
            _write_names(old, ous)
        else:
            raise BadCode('broken protocol')

        # 5 * 60 == 300 (five minutes is 300 seconds)
        kind, old = copy.get(block = True, timeout = 300)

def _write_names(names, ous):
    '''Write names as name comment to ous.'''
    ous.write(b' '.join((b'<!-- #vrt positional-attributes:',
                         *names, b'-->\n')))

def _write_meta(old, ous):
    '''Write meta lines out, other than old name comments.'''
    for line in old:
        ( line.startswith(b'<!-- #vrt positional-attributes:') or
          ous.write(line)
        )

def _write_join(imp, old, new, ous):
    '''Write data lines out with new annotations by imp.'''
    try:
        for what, line in old:
            if what == META:
                ous.write(line)
            else:
                imp.pr1_join(line, next(new), ous)
    except StopIteration:
        raise BadData('too few newly annotated tokens')

    if next(new, None) is not None:
        raise BadData('too many newly annotated tokens')

def _write_keep(imp, old, ous):
    '''Write data lines out with dummy new annotations by imp.'''
    for what, line in old:
        if what == META:
            ous.write(line)
        else:
            imp.pr1_keep(line, ous)