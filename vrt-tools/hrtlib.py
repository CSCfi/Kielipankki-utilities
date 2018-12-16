from itertools import groupby
from queue import Queue
from random import choice
from string import ascii_letters
from threading import Thread

from vrtargslib import BadData
from vrtdatalib import binunescape

def tokenize(inf, proc, combine, ouf):
    '''Sends sentinel-headed, line-separeted, unescaped text blocks from
    inf to proc, which should be an external tokenizer process; puts
    each markup-line group from inf to a Queue (call it 'meta'),
    ensuring a (possibly empty) markup-line group before the first and
    after the last text block.

    Runs combine(proc, meta, sentinel, ouf) as a Thread that is
    supposed to combine and format to ouf the tokenized output of proc
    and the original markup lines.

    '''

    # sentinel does not occur in inf, probably;
    # sentinel is not split by proc, hopefully
    sent = bytes(map(ord, (choice(ascii_letters) for k in range(16))))

    meta = Queue()

    def send(group):
        # start with the sentinel: when combine can read a sentinel
        # group from proc, the preceding meta is available in copy
        # because the meta group was put in copy before the data group
        # was sent to proc
        proc.stdin.write(sent)
        proc.stdin.write(b'\n\n')
        for line in map(binunescape, group): proc.stdin.write(line)
        proc.stdin.write(b'\n')

    Thread(target=combine, args=[proc, meta, sent, ouf]).start()

    def issome(line): return not line.isspace()
    def ismeta(line): return line.startswith(b'<')
    def checked(meta):
        if any(line.startswith((b'<sentence ',
                                b'<sentence>',
                                b'</sentence>'))
               for line in meta):
            raise BadData('sentence tag not allowed')
        else:
            return meta

    todo = groupby(filter(issome, inf), ismeta)

    # ensure meta group before first data group;
    # default empty meta group is for empty inf
    kind, group = next(todo, (True, ()))
    if kind:
        meta.put(checked(tuple(group)))
    else:
        meta.put(())
        send(group)

    # meta and data alternate
    for kind, group in todo:
        if kind:
            meta.put(checked(tuple(group)))
        else:
            send(group)

    # ensure meta group after last data group
    if not kind: meta.put(())

    proc.stdin.close()
    meta.join()
