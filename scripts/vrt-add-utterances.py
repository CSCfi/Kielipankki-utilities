#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import re
import csv

from optparse import OptionParser


class UtteranceAdder(object):

    _field_names = ['Annotation',
                    'AnnotationBeginTime',
                    'TierParticipant']

    def __init__(self, opts):
        self._opts = opts
        self._skip_pos_re = re.compile(opts.skip_pos_regexp)
        self._skip_word_re = re.compile(opts.skip_word_regexp)
        self._skip_utt_word_re = re.compile(opts.skip_utterance_word_regexp)
        self._utterance_start_format = (
            '<utterance id="{id}" participant="{participant}" annex_link="'
            + opts.url_template + '">\n')
        self._utterances = []
        self._read_utterance_file(opts.utterance_file)
        self._make_multiword_alignments()

    def _read_utterance_file(self, fname):
        field_nums = []
        with open(fname, 'rb') as f:
            reader = csv.reader(f, delimiter=';')
            for fields in reader:
                if not field_nums:
                    field_nums = [fields.index(field_name)
                                  for field_name in self._field_names]
                else:
                    self._utterances.append([fields[field_num]
                                             for field_num in field_nums])
        # Sort by AnnotationBeginTime
        self._utterances.sort(key=lambda elem: int(elem[1]))

    def _make_multiword_alignments(self):
        self._multiword_skip_words = {}
        for align_info in self._opts.multi_word_alignment:
            wordcount, _, words = align_info.partition(':')
            wordcount = int(wordcount)
            if wordcount < 2:
                sys.stderr.write(
                    'The number of aligned words in multi-word alignment'
                    ' should be at least 2')
                continue
            wordlist = re.split(r'\s*[,|\s]\s*', words)
            for word in wordlist:
                self._multiword_skip_words[word] = wordcount - 1

    def process_input(self, file_):
        if isinstance(file_, basestring):
            with open(file_) as f:
                self._process_input(f)
        else:
            self._process_input(file_)

    def _process_input(self, file_):

        # Use utt as a namespace so that the inner function
        # next_utterance can assign to the variables
        class utt:
            data = None
            num = -1
            words = []
            word_num = 0
            words_aligned = False
            start_tag = ''

        def next_utterance():
            utt.words_aligned = False
            utt.num += 1
            utt.word_num = 0
            if utt.num < len(self._utterances):
                utt.data = self._utterances[utt.num]
                utt.start_tag = self._utterance_start_format.format(
                    id=str(utt.num + 1),
                    participant=utt.data[2],
                    begintime=utt.data[1])
                utt.words = utt.data[0].split()
            else:
                utt.data = None
                utt.words = []

        skip_sent_words = 0
        # print self._utt.datas
        for line in file_:
            if line[0] == '<':
                if line.strip() == '</sentence>' and utt.words_aligned:
                    sys.stdout.write('</utterance>\n')
                    next_utterance()
                sys.stdout.write(line)
            else:
                line_fields = line.strip().split('\t')
                word = line_fields[self._opts.word_field_number]
                pos = line_fields[self._opts.pos_field_number]
                # print word, pos
                if skip_sent_words:
                    line_fields.append('[]')
                    skip_sent_words -= 1
                    # print 'ALIGN', word, '[]'
                elif (utt.num >= len(self._utterances)
                    or self._skip_pos_re.match(pos)
                    or self._skip_word_re.match(word)):
                    line_fields.append('')
                    # print 'NOALIGN', word, '-'
                else:
                    while utt.num < len(self._utterances):
                        # print utt.num
                        while (utt.word_num < len(utt.words)
                               and (self._skip_utt_word_re.match(
                                    utt.words[utt.word_num]))):
                            # print 'NOALIGN -', utt.words[utt.word_num]
                            # print utt.word_num, utt.words[utt.word_num]
                            utt.word_num += 1
                        if utt.word_num < len(utt.words):
                            break
                        else:
                            if utt.words_aligned:
                                sys.stdout.write('</utterance>\n')
                            next_utterance()
                    if utt.num < len(self._utterances):
                        if not utt.words_aligned:
                            sys.stdout.write(utt.start_tag)
                            utt.words_aligned = True
                        line_fields.append(utt.words[utt.word_num])
                        skip_sent_words = self._multiword_skip_words.get(
                            utt.words[utt.word_num], 0)
                        # print 'ALIGN', word, utt.words[utt.word_num]
                        utt.word_num += 1
                    else:
                        line_fields.append('')
                sys.stdout.write('\t'.join(line_fields) + '\n')
        if utt.words_aligned:
            sys.stdout.write('</utterance>\n')


def getopts():
    optparser = OptionParser()
    optparser.add_option('--utterance-file')
    optparser.add_option('--add-links', action='store_true')
    optparser.add_option('--add-participants', action='store_true')
    optparser.add_option('--url-template',
                         default='http://lat.example.com/?time={begintime}')
    optparser.add_option('--word-field-number', type='int', default=1)
    optparser.add_option('--pos-field-number', type='int', default=3)
    optparser.add_option('--skip-pos-regexp', default=r'^$')
    optparser.add_option('--skip-word-regexp', default=r'^$')
    optparser.add_option('--skip-utterance-word-regexp',
                         default=r'^(\..*|.*-)$')
    optparser.add_option('--multi-word-alignment', action='append',
                         default=[])
    opts, args = optparser.parse_args()
    if not opts.utterance_file:
        sys.stderr.write(
            'Please specify un utterance file with --utterance-file\n')
        sys.exit(1)
    opts.word_field_number -= 1
    opts.pos_field_number -= 1
    return opts, args


def main():
    opts, args = getopts()
    utt_adder = UtteranceAdder(opts)
    if args:
        for fname in args:
            utt_adder.process_input(fname)
    else:
        utt_adder.process_input(sys.stdin)


if __name__ == '__main__':
    main()
