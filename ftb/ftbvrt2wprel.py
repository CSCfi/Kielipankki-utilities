#! /usr/bin/env python


import sys
import re
import copy
import gzip
import bz2

from optparse import OptionParser


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
        self.ids = {}
        self.id = 0
        self.freqs = IncrDict()
        self.freqs_rel = IncrDict()
        self.freqs_head_rel = IncrDict()
        self.freqs_rel_dep = IncrDict()
        # Specifying [] is not enough because it would always use the
        # same list, whereas this returns a new list each time
        self.sentences = IncrDict(init_func=lambda: [])

    def __iter__(self):
        for key in self.ids.keys():
            (head, rel, dep) = key
            yield {'id': self.ids[key],
                   'head': head,
                   'rel': rel,
                   'dep': dep,
                   'depextra': '',
                   'freq': self.freqs[key],
                   'freq_rel': self.freqs_rel[rel],
                   'freq_head_rel': self.freqs_head_rel[(head, rel)],
                   'freq_rel_dep': self.freqs_rel_dep[(rel, dep)],
                   'wf': 0,
                   'sentences': ';'.join(':'.join(str(item) for item in sent)
                                         for sent in self.sentences[key])}

    def iter_freqs(self):
        for key in self.freqs.keys():
            (head, rel, dep) = key                       
            yield {'id': self.ids[key],
                   'head': head,
                   'rel': rel,
                   'dep': dep,
                   'depextra': '',
                   'freq': self.freqs[key],
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
            for (sent_id, start, end) in self.sentences[key]:
                yield {'id': self.ids[key],
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
                self.ids[head_rel_dep] = self.id
                self.id += 1
                self.freqs.incr(head_rel_dep)
                self.freqs_rel.incr(rel)
                self.freqs_head_rel.incr((head, rel))
                self.freqs_rel_dep.incr((rel, dep))
                self.sentences.incr(head_rel_dep,
                                    [(sent_id, min(wordnr, headnr) + 1,
                                      max(wordnr, headnr) + 1)])


def getopts():
    optparser = OptionParser()
    optparser.add_option('--input-type', '--mode', type='choice',
                         choices=['ftb2', 'ftb3', 'ftb3-extrapos'],
                         default='ftb2')
    optparser.add_option('--output-type', type='choice',
                         choices=['old', 'new'], default='new')
    optparser.add_option('--corpus-name', default=None)
    optparser.add_option('--output-prefix', default=None)
    optparser.add_option('--compress', type='choice',
                         choices=['none', 'gzip', 'gz', 'bzip2', 'bz', 'bz2'],
                         default='none')
    (opts, args) = optparser.parse_args()
    if opts.output_prefix is None and opts.corpus_name is not None:
        opts.output_prefix = 'relations_' + opts.corpus_name
    if opts.output_type == 'new' and opts.output_prefix is None:
        sys.stderr.write('--output-prefix=PREFIX or --corpus-name=NAME required'
                         + ' with --output-type=new\n')
        exit(1)
    return (opts, args)


def process_input(f, deprels, opts):
    sent_id_re = re.compile(r'<sentence\s+(?:.+\s)?id="(.*?)".*>')
    tag_re = re.compile(r'^<.*>$')
    fieldnames = ["word", "lemma", "pos", "msd", "dephead", "deprel", "lemgram"]
    if opts.input_type == 'ftb3-extrapos':
        fieldnames.insert(3, 'pos_extra')
    if opts.input_type.startswith('ftb3'):
        fieldnames.insert(1, "lemma_comp")
    data = []
    for line in f:
        line = line[:-1]
        if line.startswith('<sentence'):
            mo = sent_id_re.match(line)
            if len(data) > 0:
                deprels.add(sent_id, data)
            sent_id = mo.group(1)
            data = []
        elif not tag_re.match(line):
            fields = line.split('\t')
            if fields[-1].startswith('|') and fields[-1].endswith('|'):
                fields[-1] = fields[-1][1:-1]
            fields.append("")	# An empty lemgram by default
            data.append(dict(zip(fieldnames, fields)))
    if len(data) > 0:
        deprels.add(sent_id, data)


def output_rels_old(deprels):
    for data in deprels:
        print '\t'.join(map(lambda x: str(data[x]),
                            ['head', 'rel', 'dep', 'depextra', 'freq',
                             'freq_rel', 'freq_head_rel', 'freq_rel_dep', 'wf',
                             'sentences']))


def output_rels_new(deprels, opts):
    output_rel(deprels.iter_freqs(), '', opts,
               ['id', 'head', 'rel', 'dep', 'depextra', 'freq', 'wf'])
    output_rel(deprels.iter_freqs_rel(), '_rel', opts,
               ['rel', 'freq'])
    output_rel(deprels.iter_freqs_head_rel(), '_head_rel', opts,
               ['head', 'rel', 'freq'])
    output_rel(deprels.iter_freqs_rel_dep(), '_dep_rel', opts,
               ['dep', 'depextra', 'rel', 'freq'])
    output_rel(deprels.iter_sentences(), '_sentences', opts,
               ['id', 'sentence', 'start', 'end'])


def output_rel(data, rel_suffix, opts, fieldnames):
    with open_output_file(opts.output_prefix + rel_suffix + '.tsv', opts) as f:
        for row in data:
            f.write('\t'.join([str(row[fieldname])
                               for fieldname in fieldnames]) + '\n')
    

def open_output_file(fname, opts):
    if opts.compress.startswith('gz'):
        return gzip.open(fname + '.gz', 'w')
    elif opts.compress.startswith('bz'):
        return bz2.BZ2File(fname + '.bz2', 'w')
    else:
        return open(fname, 'w')


def main():
    deprels = Deprels()
    (opts, args) = getopts()
    process_input(sys.stdin, deprels, opts)
    if opts.output_type == 'old':
        output_rels_old(deprels)
    else:
        output_rels_new(deprels, opts)


if __name__ == '__main__':
    main()
