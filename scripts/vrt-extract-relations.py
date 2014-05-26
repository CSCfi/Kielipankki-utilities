#! /usr/bin/env python


import sys
import os
import re
import gc

from optparse import OptionParser
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile


class IncrDict(dict):

    def __init__(self, init_val=0, init_func=None):
        dict.__init__(self)
        self.init_val = init_val
        self.init_func = init_func or (lambda: init_val)

    def incr(self, key, step=1):
        if key not in self:
            self[key] = self.init_func()
        self[key] += step


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

    def __init__(self):
        self.freqs_rel = IncrDict()
        self.freqs_head_rel = IncrDict()
        self.freqs_rel_dep = IncrDict()
        self.sentences = {}

    def __iter__(self):
        for key in self.ids.keys():
            (head, rel, dep) = key
            yield {'id': self.sentences[key].id,
                   'head': head,
                   'rel': rel,
                   'dep': dep,
                   'depextra': '',
                   'freq': self.sentences[key].get_len(),
                   'freq_rel': self.freqs_rel[rel],
                   'freq_head_rel': self.freqs_head_rel[(head, rel)],
                   'freq_rel_dep': self.freqs_rel_dep[(rel, dep)],
                   'wf': 0,
                   'sentences': ';'.join(':'.join(str(item) for item in sent)
                                         for sent
                                         in self.sentences[key].sentences)}

    def iter_freqs(self):
        for key in self.sentences.keys():
            (head, rel, dep) = key
            yield {'id': self.sentences[key].id,
                   'head': head,
                   'rel': rel,
                   'dep': dep,
                   'depextra': '',
                   'freq': self.sentences[key].get_len(),
                   'wf': 0}

    def iter_freqs_rel(self):
        for rel in self.freqs_rel.keys():
            yield {'rel': rel,
                   'freq': self.freqs_rel[rel]}

    def iter_freqs_head_rel(self):
        for (head, rel) in self.freqs_head_rel.keys():
            yield {'head': head,
                   'rel': rel,
                   'freq': self.freqs_head_rel[(head, rel)]}

    def iter_freqs_rel_dep(self):
        for (rel, dep) in self.freqs_rel_dep.keys():
            yield {'dep': dep,
                   'depextra': '',
                   'rel': rel,
                   'freq': self.freqs_rel_dep[(rel, dep)]}

    def iter_sentences(self):
        for key in self.sentences.keys():
            for (sent_id, start, end) in self.sentences[key].sentences:
                yield {'id': self.sentences[key].id,
                       'sentence': sent_id,
                       'start': start,
                       'end': end}

    def add(self, sent_id, data):
        # print sent_id, len(data)
        for wordnr in xrange(0, len(data)):
            word_info = data[wordnr]
            if word_info["dephead"] == '_':
                word_info["dephead"] = -1
            try:
                headnr = int(word_info["dephead"]) - 1
            except ValueError:
                headnr = -1
            if headnr >= 0 and headnr < len(data):
                dep = word_info["lemgram"] or word_info["lemma"]
                rel = self.relmap[word_info["deprel"]]
                head = data[headnr]["lemgram"] or data[headnr]["lemma"]
                head_rel_dep = (head, rel, dep)
                if head_rel_dep not in self.sentences:
                    self.sentences[head_rel_dep] = self.SentInfo()
                self.freqs_rel.incr(rel)
                self.freqs_head_rel.incr((head, rel))
                self.freqs_rel_dep.incr((rel, dep))
                self.sentences[head_rel_dep].add_info(
                    [(sent_id, min(wordnr, headnr) + 1,
                      max(wordnr, headnr) + 1)])

    def get_sizes(self):
        sizes = []
        for attr in ['freqs_rel', 'freqs_head_rel', 'freqs_rel_dep',
                     'sentences']:
            sizes.append((attr, sys.getsizeof(getattr(self, attr))))
        return sizes


class RelationExtractor(object):

    def __init__(self, opts):
        self._opts = opts
        self._deprels = Deprels()
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
        tag_re = re.compile(r'^<.*>$')
        data = []
        sentnr = 0
        # sys.stdout.write(str(sentnr) + ' ' + repr(self._deprels.get_sizes()) + '\n')
        for line in f:
            line = line[:-1]
            if line.startswith('<sentence'):
                mo = sent_id_re.match(line)
                if len(data) > 0:
                    self._deprels.add(sent_id, data)
                    sentnr += 1
                    # if sentnr % 100000 == 0:
                    #     sys.stdout.write(
                    #         str(sentnr) + ' ' + repr(self._deprels.get_sizes()) + '\n')
                sent_id = mo.group(1)
                data = []
            elif not tag_re.match(line):
                fields = line.split('\t')
                if fields[-1].startswith('|') and fields[-1].endswith('|'):
                    fields[-1] = fields[-1][1:-1]
                fields.append('')	# An empty lemgram by default
                data.append(dict(zip(self._input_fieldnames, fields)))
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
        output_rels = [('iter_freqs', '',
                        ['id', 'head', 'rel', 'dep', 'depextra', 'freq', 'wf'],
                        True),
                       ('iter_freqs_rel', '_rel', ['rel', 'freq'], False),
                       ('iter_freqs_head_rel', '_head_rel',
                         ['head', 'rel', 'freq'], False),
                       ('iter_freqs_rel_dep', '_dep_rel',
                         ['dep', 'depextra', 'rel', 'freq'], False),
                       ('iter_sentences', '_sentences',
                         ['id', 'sentence', 'start', 'end'], True)]
        for output_rel in output_rels:
            self._output_rel(getattr(self._deprels, output_rel[0])(),
                             *output_rel[1:])
        if self._opts.temp_files:
            del self._deprels
            gc.collect()
            self._write_final_files(output_rels)

    def _output_rel(self, data, rel_suffix, fieldnames, numeric_sort=False):
        with self._open_output_file(self._make_output_filename(rel_suffix),
                                    numeric_sort, self._opts.temp_files) as f:
            for row in data:
                f.write('\t'.join([str(row[fieldname])
                                   for fieldname in fieldnames]) + '\n')
            if self._opts.temp_files:
                self._temp_fnames[rel_suffix] = f.name

    def _make_output_filename(self, rel_suffix):
        return self._opts.output_prefix + rel_suffix + '.tsv'

    def _open_output_file(self, fname, numeric_sort=False, temporary=False):
        if temporary:
            return NamedTemporaryFile(prefix=sys.argv[0] + '.' + fname + '.',
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
