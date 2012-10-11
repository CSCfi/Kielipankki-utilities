#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs

from optparse import OptionParser


class AttributeFixer(object):

    def __init__(self, opts):
        self._opts = opts
        self._opts.angle_brackets = self._opts.angle_brackets.split(',', 1)
        self._split_lines = (self._opts.compound_boundaries != 'keep'
                             or self._opts.strip)

    def process_files(self, files):
        if isinstance(files, list):
            for file_ in files:
                self.process_files(file_)
        elif isinstance(files, basestring):
            with codecs.open(files, 'r', encoding='utf-8') as f:
                self._fix_input(f)
        else:
            self._fix_input(files)

    def _fix_input(self, f):
        for line in f:
            sys.stdout.write(self._make_fixed_line(line))

    def _make_fixed_line(self, line):
        if line.startswith('<') and line.endswith('>\n'):
            return line
        else:
            return self._fix_posattrs(line)

    def _fix_posattrs(self, line):
        if self._split_lines:
            attrs = line[:-1].split('\t')
            self._process_compound_lemmas(attrs)
            self._strip_attrs(attrs)
            line = '\t'.join(attrs) + '\n'
        if self._opts.space:
            line = line.replace(' ', self._opts.space)
        if self._opts.angle_brackets:
            line = (line.replace('<', self._opts.angle_brackets[0])
                    .replace('>', self._opts.angle_brackets[1]))
        return line

    def _process_compound_lemmas(self, attrs):
        if self._opts.compound_boundaries != 'keep':
            noncompound_lemma = attrs[self._opts.lemma_field] .replace('#', '')
            if self._opts.compound_boundaries == 'remove':
                attrs[self._opts.lemma_field] = noncompound_lemma
            elif self._opts.compound_boundaries == 'new':
                attrs.insert(self._opts.noncompound_lemma_field,
                             noncompound_lemma)

    def _strip_attrs(self, attrs):
        if self._opts.strip:
            for attrnr in xrange(0, len(attrs)):
                attrs[attrnr] = attrs[attrnr].strip()


def getopts():
    optparser = OptionParser()
    optparser.add_option('--space', '--space-replacement', default=':')
    optparser.add_option('--no-strip', action='store_false', dest='strip',
                         default=True)
    optparser.add_option('--angle-brackets', '--angle-bracket-replacement',
                         default='[,]')
    optparser.add_option('--compound-boundaries', '--lemma-compound-boundaries',
                         type='choice', choices=['keep', 'remove', 'new'],
                         default='keep')
    optparser.add_option('--lemma-field', type='int', default=2)
    optparser.add_option('--noncompound-lemma-field', '--noncompound-field',
                         '--removed-compound-boundary-field', type='int',
                         default=None)
    (opts, args) = optparser.parse_args()
    if opts.noncompound_lemma_field is None:
        opts.noncompound_lemma_field = opts.lemma_field
    opts.lemma_field -= 1
    opts.noncompound_lemma_field -= 1
    return (opts, args)


def main():
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    attr_fixer = AttributeFixer(opts)
    attr_fixer.process_files(args if args else sys.stdin)


if __name__ == "__main__":
    main()
