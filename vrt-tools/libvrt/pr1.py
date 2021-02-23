# -*- mode: Python; -*-

'''Protocol for interfacing with external sentence-annotation tools,
with the following characteristics that might be different in an
alternative protocol.

0. Input is VRT, output is VRT. With field name comment before first
   sentence. With every token inside a <sentence> tags. At least one
   token inside every sentence.

1. An implementation is allowed to observe, in pr1_test, any meta
   outside sentences (outer meta) to decide whether to pass current
   sentence to the external tool or keep it. (Possibly observe a
   special _skip tag of each sentence.)

2. Any meta inside sentences (inner meta) is passed transparently
   through.

3. An implementation may provide pr1_join_meta to combine new
   annotations to the sentence start tag. Then pr1_read must yield a
   meta component for each sentence.

4. An implementation may provide pr1_join to combine new annotations
   to a token. Then pr1_read must yield a data component for each
   sentence, generating new token annotations.

5. An implementation may provide pr1_read_stderr. Then the external
   process must write its stderr to a PIPE and pr1_read_stderr must
   deal with it.

A particular tool is implemented as a module that provides the
tool-specific functionality.

'''

import sys
from itertools import filterfalse, groupby
from queue import Queue
from threading import Thread

from libvrt.bad import BadData, BadCode

NAMES, OUTER, INNER, TAGS, BEGIN, META, DATA, JOIN, KEEP = range(2, 11)

def transput(args, imp, proc, ins, ous):

    '''Set up a thread that pushes a (segmented) copy of ins to a queue
    and uses imp to feed proc with input sentences from ins. Combine
    the copy of ins with the output sentences from proc and write the
    combined result to ous.

    If there is imp.pr1_read_stderr, set it to read all of proc.stderr
    in yet another thread.

    '''

    matter = _segment(ins, imp)
    kind, head = next(matter)

    if kind in (TAGS, BEGIN):
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

    if hasattr(imp, 'pr1_read_stderr'):
        deal = Thread(target = _readerr,
                      args = (args, imp, proc),
                      name = 'Diagnostic Thread',
                      daemon = True)
        deal.start()

    _combinate(args, imp, copy, proc, ous)

    # proc should have run its course by now; the 30 second timeout
    # may or may not be either wildly excessive or sufficient
    code = proc.wait(timeout = 30)

    if not copy.empty():
        raise BadCode('copy queue is not empty')

    # feed should have run its course by now, but was sometimes
    # observed alive before the addition of the (probably excessive)
    # 5-second timeout; incidentally, documentation says the timeout
    # "should be a floating point number" but does not seem to mean it
    feed.join(5)
    if feed.is_alive():
        raise BadCode('separation thread is still alive')

    # proc is surely not writing anything to its stderr any more,
    # having been waited for, but let the stderr-reading thread have
    # five more seconds to finish, should it still be there
    if hasattr(imp, 'pr1_read_stderr'):
        deal.join(5)
        if deal.is_alive():
            raise BadCode('diagnostic thread is still alive')

    return code

def _segment(ins, imp):
    '''Yield non-empty input lines in classified groups.

    (TAGS, lines) is a succession of sentence tags (start or end);
    (BEGIN, lines) is same and ends with a start tag.

    (OUTER, lines) is a succession of meta lines outside sentence;
    (INNER, mix) consists of all lines inside a sentence.

    In (INNER, mix), in the mix:
    (META, line) is an inner meta line;
    (DATA, record) is a stripped-and-split data line (a record).

    There are three legitimate TAGS groups: a lone start tag, a lone
    end tag, and an end tag followed by a start tag. Two of these are
    also legitimate BEGIN groups.

    Both OUTER meta groups and INNER data/meta groups may consist of
    many lines, but any impractical length is considered impossible
    (an error, like a data set that does not use sentence tags, for
    example).

    It is very important to note that no unescaping of the few special
    characters is done.

    '''

    START = (BEGIN if hasattr(imp, 'pr1_join_meta') else TAGS)

    inside = False
    for k, g in groupby(filterfalse(bytes.isspace, ins), lambda line:
                        line.startswith((b'<sentence ',
                                         b'<sentence>',
                                         b'</sentence>'))):
        if k:
            lines = tuple(g)
            inside = lines[-1].startswith(b'<sentence')
            yield (START if inside else TAGS), lines
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
    '''Running in another thread, put all incoming matter (segmented ins)
    to copy (a queue of classified groups of lines) and send some of
    the sentences to proc according to imp. Finally put a sentinel in
    copy.

    Matter comes in as TAGS/BEGIN, OUTER, INNER (INNER containing DATA
    records, META lines).

    Matter goes to copy as TAGS/BEGIN, OUTER, JOIN (INNER sent to
    proc), KEEP (INNER not sent to PROC).

    Choice to skip a sentence is up to imp, with access to TAGS/BEGIN
    and OUTER.

    Only use BEGIN if there is imp.pr1_join_meta, and then
    imp.pr1_read produces a meta component for the sentence.

    Only use JOIN if there is imp.pr1_join, and then imp.pr1_read
    produces a data component for the sentence.

    '''

    # whether imp.pr1_read produces data components or not
    SENT = (JOIN if hasattr(imp, 'pr1_join') else KEEP)

    for kind, lines in matter:
        if kind == BEGIN:
            # imp.pr1_read produces meta components
            # for sent sentences (put to copy as BEGIN)
            # not for skipped (put to copy as TAGS)
            imp.pr1_test(tags = lines)
            copy.put((( BEGIN
                        if imp.pr1_test()
                        else TAGS ),
                      lines))
        elif kind == TAGS:
            copy.put((kind, lines))
            imp.pr1_test(tags = lines)
        elif kind == OUTER:
            copy.put((kind, lines))
            imp.pr1_test(meta = lines)
        elif imp.pr1_test():
            # kind == INNER
            copy.put((SENT, lines))
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
        elif kind == BEGIN:
            # there is a meta component for the sentence
            _write_join_meta(imp, old, next(news), ous)
        elif kind == JOIN:
            # there is a data component for the sentence
            _write_join(imp, old, next(news), ous)
        elif kind == KEEP:
            # there is no data component for the sentence
            _write_keep(imp, old, ous)
        elif kind == NAMES:
            # old is actually *new* names already
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

def _write_join_meta(imp, old, new, ous):
    '''Write a group of sentence tags, ending with a start tag, with new
    meta added to that start tag. (Either there is only the start
    tag, or there is an end tag followed by the start tag.

    '''

    for line in old:
        if line.startswith(b'</'):
            ous.write(line)
        else:
            # only imp knows what kind of thing new is
            # (imp.pr1_read, imp.pr1_join_meta)
            imp.pr1_join_meta(line, new, ous)

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

def _readerr(args, imp, proc):
    '''Running as another thread, have imp read the diagnostic (stderr)
    stream of proc.

    '''

    try:
        imp.pr1_read_stderr(args, proc.stderr)
    except Exception as exn:
        print(args.prog, ': stderr reader failed: ', exn,
              sep = '',
              file = sys.stderr)
        # should show stack trace of exn, need to remember how
        if proc.returncode is None:
            proc.terminate()
            proc.kill()
