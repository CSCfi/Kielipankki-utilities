#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs

from optparse import OptionParser


def process_input(f, posmap, opts):
    if isinstance(f, basestring):
        with codecs.open(f, 'r', encoding='utf-8') as fp:
            process_input_stream(fp, posmap, opts)
    else:
        process_input_stream(f, posmap, opts)


def process_input_stream(f, posmap, opts):
    for linenr, line in enumerate(f):
        if line.startswith('<') and line.endswith('>\n'):
            sys.stdout.write(line)
        else:
            sys.stdout.write(add_lemgram(line, posmap, opts))


def add_lemgram(line, posmap, opts):
    fields = line[:-1].split('\t')
    lemma = get_field(fields, opts.lemma_field)
    if not lemma and not opts.skip_empty_lemmas:
        # Fall back to word form if no lemma
        lemma = get_field(fields, 0, '')
    lemgram = (make_lemgram(posmap, lemma,
                            get_field(fields, opts.pos_field, ''))
               if lemma else '|')
    return line[:-1] + '\t' + lemgram + '\n'


def get_field(fields, num, default=None):
    try:
        return fields[num]
    except IndexError as e:
        return default


def make_lemgram(posmap, lemma, pos):
    return u'|{lemma}..{pos}.1|'.format(lemma=lemma, pos=posmap.get(pos, 'xx'))


def read_posmap(fname, opts):
    posmap = {}
    with codecs.open(fname, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() == '' or line.startswith('#'):
                continue
            (src_poses, trg_pos) = line[:-1].split('\t', 1)
            if opts.inverse_pos_map:
                (src_poses, trg_pos) = (trg_pos, src_poses)
            posmap.update(dict([(src_pos, trg_pos)
                                for src_pos in src_poses.split()]))
    return posmap


def getopts():
    optparser = OptionParser()
    optparser.add_option('--pos-map-file', '--map-file')
    optparser.add_option('--inverse-pos-map', action='store_true',
                         default=False)
    optparser.add_option('--lemma-field', type='int', default=2)
    optparser.add_option('--skip-empty-lemmas', action='store_true',
                         default=False)
    optparser.add_option('--pos-field', type='int', default=3)
    (opts, args) = optparser.parse_args()
    opts.lemma_field -= 1
    opts.pos_field -= 1
    return (opts, args)


def main():
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    posmap = read_posmap(opts.pos_map_file, opts)
    process_input(args[0] if args else sys.stdin, posmap, opts)


if __name__ == "__main__":
    main()
