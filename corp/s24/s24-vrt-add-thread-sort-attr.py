#! /usr/bin/env python3


import re

# libpaths adds local library paths to sys.path (VRT Tools)
import libpaths

import vrtargsoolib



class ThreadSortKeyAdder(vrtargsoolib.InputProcessor):

    DESCRIPTION = """
    Add sort key attributes to text elements (corresponding to
    messages) in Suomi24 VRT input for sorting messages within threads
    in the thread hierarchy order (messages under their parents in
    time order), as on the Suomi24 Web site.

    The input is assumed to be already sorted by thread and within
    each thread so that the comments to a message follow the parent
    message. Messages with no parents in the input are ordered in the
    order of their timestamps.
    """
    ARGSPECS = [
        ('--sort-key-attribute=ATTR "sort_key" -> sort_key_attr',
         'add the sort key value to the attribute ATTR of structure text'),
        ('--add-mode=MODE (*prepend|append|replace)',
         'add the sort key to an existing attribute value using MODE, one of:'
         ' "prepend" (default), "append" or "replace"'),
        ('--value-separator=SEP " + " -> value_sep',
         'when MODE is "prepend" or "append", separate the new key from the'
         ' the existing value of the sort key by SEP; this can be used to'
         ' affect sort order'),
    ]

    def __init__(self):
        super().__init__()

    def main(self, args, inf, ouf):
        msg_keys = {}
        sort_key_attr = args.sort_key_attr.encode()
        sort_key_attr_sign = b' ' + sort_key_attr + b'="'
        value_sep = args.value_sep.encode()
        add_attr_fn = {
            'prepend': lambda old, key: key + value_sep + old,
            'append': lambda old, key: old + value_sep + key,
            'replace': lambda old, key: key,
            }[args.add_mode]
        thread_first_datetime = None

        def append_attr(line, attrname, attrval):
            # This assumes that the line ends in ">\n", with no trailing
            # whitespace nor \r.
            return (line[:-2] + b' ' + attrname + b'="' + attrval + b'"'
                    + line[-2:])

        def get_attr_values(line):
            # Note that this assumes that the order of the attributes is as
            # below.
            mo = re.search(
                (b' comment="(?P<comment>.*?)".*'
                 b' datetime="(?P<datetime>.*?)".*'
                 b' parent="(?P<parent>.*?)".*'
                 b' thread="(?P<thread>.*?)"'),
                line)
            return mo.groupdict() if mo else {}

        def make_key(attrvals):
            key = attrvals['datetime']
            # ouf.write(b'>> attrvals = ' + repr(attrvals).encode() + b'\n')
            # ouf.write(b'>> key(1) = ' + key + b'\n')
            if attrvals['comment'] == b'0':
                # ouf.write(b'>> branch1\n')
                key = append_thread_id(key, attrvals['thread'])
                # ouf.write(b'>> key(2) = ' + key + b'\n')
            else:
                # ouf.write(b'>> branch2\n')
                key = ((msg_keys.get(attrvals['parent'])
                        or (append_thread_id(thread_first_datetime or key,
                                            attrvals['thread'])))
                       + b' ' + key)
                # ouf.write(b'>> parent_key = ' + msg_keys.get(attrvals['parent'], b'[None]') + b'\n')
                # ouf.write(b'>> key(3) = ' + key + b'\n')
            # ouf.write(repr((attrvals, key)).encode() + b'\n')
            return key

        def append_thread_id(val, thread_id):
            return val + b' ' + (b'0' * (8 - len(thread_id))) + thread_id

        def add_key_attr(line, key):
            if sort_key_attr_sign in line:
                return re.sub(
                    b'(' + sort_key_attr_sign + b')(.*?)"',
                    lambda mo: (
                        mo.group(1) + add_attr_fn(mo.group(2), key) + b'"'),
                    line)
            else:
                return append_attr(line, sort_key_attr, key)

        prev_thread_id = None
        for line in inf:
            if line.startswith(b'<text '):
                attrvals = get_attr_values(line)
                if attrvals['thread'] != prev_thread_id:
                    msg_keys = {}
                    thread_first_datetime = attrvals['datetime']
                    prev_thread_id = attrvals['thread']
                key = make_key(attrvals)
                msg_keys[attrvals['comment']] = key
                # ouf.write(repr(msg_keys).encode() + b'\n')
                line = add_key_attr(line, key)
            ouf.write(line)


if __name__ == '__main__':
    ThreadSortKeyAdder().run()
