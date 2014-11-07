#! /usr/bin/env python


import sys
import os
import re
import gc

from optparse import OptionParser
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
from collections import defaultdict
from os.path import basename


class Deprels(object):

    class SentInfo(object):

        __slots__ = ['id', 'sentences']

        id_counter = 0

        def __init__(self, id_=None):
            self.id = id_ if id_ is not None else self.id_counter
            self.__class__.id_counter += 1
            self.sentences = []

        def add_info(self, info):
            self.sentences += info

        def get_len(self):
            return len(self.sentences)

    relmap = {'advl': 'ADV',
              'attr': 'AT',
              'aux': 'IV',
              'comp': 'OP',
              'conjunct': 'UK',
              'idiom': 'XF',
              'idom': 'XF',
              'main': 'HD',
              'mod': 'ET',
              'modal': 'IV',
              'obj': 'OBJ',
              'phrm': 'XX',
              'phrv': 'PL',
              'scomp': 'SP',
              'subj': 'SS',
              'voc': 'TT',
              '_': 'XX'}

    def __init__(self, relmap=None, include_wordforms=False):
        self.relmap = relmap or self.__class__.relmap
        self._include_wordforms = include_wordforms
        self.freqs_rel = defaultdict(int)
        self.freqs_head_rel = defaultdict(int)
        self.freqs_rel_dep = defaultdict(int)
        self.sentences = defaultdict(self.SentInfo)

    def __iter__(self):
        for key in self.sentences:
            (head, rel, dep, wf) = key
            yield {'id': self.sentences[key].id,
                   'head': head,
                   'rel': rel,
                   'dep': dep,
                   'depextra': '',
                   'freq': self.sentences[key].get_len(),
                   'freq_rel': self.freqs_rel[rel],
                   'freq_head_rel': self.freqs_head_rel[(head, rel)],
                   'freq_rel_dep': self.freqs_rel_dep[(rel, dep)],
                   'wf': int(wf),
                   'sentences': ';'.join(':'.join(str(item) for item in sent)
                                         for sent
                                         in self.sentences[key].sentences)}

    def iter_freqs(self):
        for key in self.sentences:
            (head, rel, dep, wf) = key
            yield (str(self.sentences[key].id),  # id
                   head,
                   rel,
                   dep,
                   '',  # depextra
                   str(self.sentences[key].get_len()),  # freq
                   '3' if wf else '0')  # wf

    def iter_freqs_rel(self):
        for rel in self.freqs_rel:
            yield (rel,
                   str(self.freqs_rel[rel]))

    def iter_freqs_head_rel(self):
        for (head, rel) in self.freqs_head_rel:
            yield (head,
                   rel,
                   str(self.freqs_head_rel[(head, rel)]))

    def iter_freqs_rel_dep(self):
        for (rel, dep) in self.freqs_rel_dep:
            yield (dep,
                   '',  # depextra
                   rel,
                   str(self.freqs_rel_dep[(rel, dep)]))

    def iter_sentences(self):
        for key in self.sentences:
            for (sent_id, start, end) in self.sentences[key].sentences:
                yield (str(self.sentences[key].id),
                       str(sent_id),
                       str(start),
                       str(end))

    def add(self, sent_id, data):

        def add_info(rel, dep, head, depnr, headnr, is_wordform=False):
            self.freqs_head_rel[(head, rel)] += 1
            self.freqs_rel_dep[(rel, dep)] += 1
            self.sentences[(head, rel, dep, is_wordform)].add_info(
                [(sent_id, min(wordnr, headnr) + 1,
                  max(wordnr, headnr) + 1)])

        def get_lemgram_pos(lemgram):
            if lemgram[-6:-4] == '..':
                return '_' + lemgram[-4:-2].upper()
            else:
                return ''

        # print sent_id, len(data)
        for wordnr, word_info in enumerate(data):
            dep, deprel, dephead, wform = word_info
            if dephead == '_':
                continue
            try:
                headnr = int(dephead) - 1
            except ValueError:
                headnr = -1
            if headnr >= 0 and headnr < len(data):
                rel = self.relmap.get(deprel, 'XX')
                head = data[headnr][0]
                self.freqs_rel[rel] += 1
                add_info(rel, dep, head, wordnr, headnr)
                if self._include_wordforms:
                    add_info(rel, wform + get_lemgram_pos(dep),
                             data[headnr][-1] + get_lemgram_pos(head), wordnr,
                             headnr, True)

    def get_sizes(self):
        sizes = []
        for attr in ['freqs_rel', 'freqs_head_rel', 'freqs_rel_dep',
                     'sentences']:
            sizes.append((attr, sys.getsizeof(getattr(self, attr))))
        return sizes


class RelationExtractor(object):

    def __init__(self, opts):
        self._opts = opts
        relmap = None
        if opts.relation_map:
            relmap = self._read_relmap(opts.relation_map)
        self._deprels = Deprels(relmap, opts.include_word_forms)
        self._temp_fnames = {}
        if self._opts.input_fields:
            self._input_fieldnames = re.split(r'\s*[,\s]\s*',
                                              self._opts.input_fields)
            if 'lex' in self._input_fieldnames:
                lex_index = self._input_fieldnames.index('lex')
                self._input_fieldnames[lex_index] = 'lemgram';
        else:
            self._input_fieldnames = ['word', 'lemma', 'pos', 'msd', 'dephead',
                                      'deprel', 'lemgram']
            if self._opts.input_type == 'ftb3-extrapos':
                self._input_fieldnames.insert(3, 'pos_extra')
            if self._opts.input_type.startswith('ftb3'):
                self._input_fieldnames.insert(1, 'lemma_comp')
        self._fieldnrs = dict((fieldname,
                               (self._input_fieldnames.index(fieldname)
                                if fieldname in self._input_fieldnames
                                else None))
                              for fieldname in self._input_fieldnames)

    def _read_relmap(self, fname):
        relmap = {}
        with open(fname, 'r') as f:
            for line in f:
                if line.strip() == '' or line.startswith('#'):
                    continue
                (src_rels, trg_rel) = line[:-1].split('\t', 1)
                if self._opts.inverse_relation_map:
                    (src_rels, trg_rel) = (trg_rel, src_rels)
                relmap.update(dict([(src_rel, trg_rel)
                                    for src_rel in src_rels.split()]))
        return relmap

    def process_input(self, args):
        if isinstance(args, list):
            for arg in args:
                self.process_input(arg)
        elif isinstance(args, basestring):
            with open(args, 'r') as f:
                self._process_input_stream(f)
        else:
            self._process_input_stream(args)

    def _process_input_stream(self, f):
        sent_id_re = re.compile(r'<sentence\s+(?:.+\s)?id="(.*?)".*>')
        # Try to optimize by using local variables not requiring
        # attribute access
        has_lemgrams = bool(self._fieldnrs['lemgram'])
        fieldnr_lemgram_lemma = (self._fieldnrs['lemgram']
                                 or self._fieldnrs['lemma'])
        fieldnr_deprel = self._fieldnrs['deprel']
        fieldnr_dephead = self._fieldnrs['dephead']
        fieldnr_word = self._fieldnrs['word']
        min_num_fields = max(fieldnr_lemgram_lemma, fieldnr_deprel,
                             fieldnr_dephead, fieldnr_word) + 1
        data = []
        sentnr = 0
        # sys.stdout.write(str(sentnr) + ' ' + repr(self._deprels.get_sizes()) + '\n')
        for linenr, line in enumerate(f):
            line = line[:-1]
            if not line:
                continue
            elif line[0] != '<':
                fields = line.split('\t')
                if len(fields) < min_num_fields:
                    sys.stderr.write(
                        ('Warning: Ignoring line {linenr} with only {numfields}'
                         ' fields ({reqfields} required):\n{line}\n').format(
                            numfields=len(fields), reqfields=min_num_fields,
                            linenr=linenr, line=line))
                    continue
                if has_lemgrams:
                    # Remove leading and trailing vertical bars from
                    # the lemgram. FIXME: This assumes an unambiguous
                    # lemgram.
                    fields[fieldnr_lemgram_lemma] = (
                        fields[fieldnr_lemgram_lemma][1:-1])
                # Would we need this:
                # fields.append('')	# An empty lemgram by default
                data.append((fields[fieldnr_lemgram_lemma],
                             fields[fieldnr_deprel],
                             fields[fieldnr_dephead],
                             fields[fieldnr_word]))
            elif line.startswith('<sentence'):
                mo = sent_id_re.match(line)
                if len(data) > 0:
                    self._deprels.add(sent_id, data)
                    sentnr += 1
                    # if sentnr % 100000 == 0:
                    #     sys.stdout.write(
                    #         str(sentnr) + ' ' + repr(self._deprels.get_sizes()) + '\n')
                sent_id = mo.group(1)
                data = []
        if len(data) > 0:
            self._deprels.add(sent_id, data)
            # sys.stdout.write(str(sentnr) + ' ' + repr(self._deprels.get_sizes()) + '\n')

    def output_rels(self):
        if self._opts.output_type == 'old':
            self._output_rels_old()
        else:
            self._output_rels_new()

    def _output_rels_old(self):
        for data in self._deprels:
            print '\t'.join(map(lambda x: str(data[x]),
                                ['head', 'rel', 'dep', 'depextra', 'freq',
                                 'freq_rel', 'freq_head_rel', 'freq_rel_dep',
                                 'wf', 'sentences']))

    def _output_rels_new(self):
        output_rels = [('iter_freqs', '', True),
                       ('iter_freqs_rel', '_rel', False),
                       ('iter_freqs_head_rel', '_head_rel', False),
                       ('iter_freqs_rel_dep', '_dep_rel', False),
                       ('iter_sentences', '_sentences', True)]
        for output_rel in output_rels:
            self._output_rel(getattr(self._deprels, output_rel[0])(),
                             *output_rel[1:])
        if self._opts.temp_files:
            del self._deprels
            gc.collect()
            self._write_final_files(output_rels)

    def _output_rel(self, data, rel_suffix, numeric_sort=False):
        with self._open_output_file(self._make_output_filename(rel_suffix),
                                    numeric_sort, self._opts.temp_files) as f:
            for row in data:
                f.write('\t'.join(row) + '\n')
            if self._opts.temp_files:
                self._temp_fnames[rel_suffix] = f.name

    def _make_output_filename(self, rel_suffix):
        return self._opts.output_prefix + rel_suffix + '.tsv'

    def _open_output_file(self, fname, numeric_sort=False, temporary=False):
        if temporary:
            return NamedTemporaryFile(
                prefix=basename(sys.argv[0]) + '.' + basename(fname) + '.',
                dir=self._opts.temp_dir, delete=False)
        compress_cmd = None
        if self._opts.compress.startswith('gz'):
            fname += '.gz'
            compress_cmd = 'gzip'
        elif self._opts.compress.startswith('bz'):
            fname += '.bz2'
            compress_cmd = 'bzip2'
        f = open(fname, 'w')
        if self._opts.sort:
            sort_env = os.environ
            sort_env['LC_ALL'] = 'C'
            sort_cmd = ['sort']
            if numeric_sort:
                sort_cmd += ['-n']
            p1 = Popen(sort_cmd, stdin=PIPE,
                       stdout=(PIPE if compress_cmd else f), env=sort_env)
            if compress_cmd is not None:
                p2 = Popen([compress_cmd], stdin=p1.stdout, stdout=f)
                p1.stdout.close()
            return p1.stdin
        elif compress_cmd is not None:
            p2 = Popen([compress_cmd], stdin=PIPE, stdout=f)
            return p2.stdin
        else:
            return f

    def _write_final_files(self, output_rels_info):
        numeric_sort = dict([(relinfo[1], relinfo[-1])
                             for relinfo in output_rels_info])
        for (rel_suffix, temp_fname) in self._temp_fnames.iteritems():
            with open(temp_fname, 'r') as inf:
                with self._open_output_file(
                    self._make_output_filename(rel_suffix),
                    numeric_sort[rel_suffix], False) as outf:
                    for line in inf:
                        outf.write(line)
            os.remove(temp_fname)


def getopts():
    optparser = OptionParser()
    optparser.add_option('--input-type', '--mode', type='choice',
                         choices=['ftb2', 'ftb3', 'ftb3-extrapos'],
                         default='ftb2')
    optparser.add_option('--input-fields', '--input-field-names')
    optparser.add_option('--output-type', type='choice',
                         choices=['old', 'new'], default='new')
    optparser.add_option('--corpus-name', default=None)
    optparser.add_option('--output-prefix', default=None)
    optparser.add_option('--compress', type='choice',
                         choices=['none', 'gzip', 'gz', 'bzip2', 'bz', 'bz2'],
                         default='none')
    optparser.add_option('--sort', action='store_true', default=False)
    optparser.add_option('--temp-files', '--temporary-files',
                         action='store_true', default=False)
    optparser.add_option('--temp-dir', '--temporary-directory', default=None)
    optparser.add_option('--relation-map')
    optparser.add_option('--inverse-relation-map', action='store_true',
                         default=False)
    optparser.add_option('--include-word-forms', action='store_true')
    (opts, args) = optparser.parse_args()
    if opts.output_prefix is None and opts.corpus_name is not None:
        opts.output_prefix = 'relations_' + opts.corpus_name
    if opts.output_type == 'new' and opts.output_prefix is None:
        sys.stderr.write('--output-prefix=PREFIX or --corpus-name=NAME required'
                         + ' with --output-type=new\n')
        exit(1)
    if opts.compress == 'none' and not opts.sort:
        opts.temp_files = False
    return (opts, args)


def main():
    (opts, args) = getopts()
    extractor = RelationExtractor(opts)
    extractor.process_input(args or sys.stdin)
    extractor.output_rels()


if __name__ == '__main__':
    main()
