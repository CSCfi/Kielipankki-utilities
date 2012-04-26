#! /usr/bin/env python


import sys
import re
import copy


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

    sep = '\0x01'
    relmap = {'advl': 'AA',
              'attr': 'AT',
              'aux': 'IV',
              'comp': 'OP',
              'conjunct': 'UK',
              'idiom': 'XF',
              'idom': 'XF',
              'main': 'HD',
              'mod': 'ET',
              'modal': 'IV',
              'obj': 'EO',
              'phrm': 'XX',
              'phrv': 'PL',
              'scomp': 'SP',
              'subj': 'ES',
              'voc': 'TT',
              '_': 'XX'}

    def __init__(self):
        self.freqs = IncrDict()
        self.freqs_rel = IncrDict()
        self.freqs_head_rel = IncrDict()
        self.freqs_rel_dep = IncrDict()
        # Specifying [] is not enough because it would always use the
        # same list, whereas this returns a new list each time
        self.sentences = IncrDict(init_func=lambda: [])

    def __iter__(self):
        for key in self.freqs.keys():
            (head, rel, dep) = key.split(self.sep)
            yield {'head': head,
                   'rel': rel,
                   'dep': dep,
                   'depextra': '',
                   'freq': self.freqs[key],
                   'freq_rel': self.freqs_rel[rel],
                   'freq_head_rel': self.freqs_head_rel[head + self.sep + rel],
                   'freq_rel_dep': self.freqs_rel_dep[rel + self.sep + dep],
                   'wf': 0,
                   'sentences': ';'.join(self.sentences[key])}

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
                head_rel_dep = head + self.sep + rel + self.sep + dep
                self.freqs.incr(head_rel_dep)
                self.freqs_rel.incr(rel)
                self.freqs_head_rel.incr(head + self.sep + rel)
                self.freqs_rel_dep.incr(rel + self.sep + dep)
                self.sentences.incr(head_rel_dep,
                                    [':'.join([sent_id,
                                               str(min(wordnr, headnr) + 1),
                                               str(max(wordnr, headnr) + 1)])])


def process_input(f, deprels):
    sent_id_re = re.compile(r'<sentence\s+id="(.*?)">')
    tag_re = re.compile(r'^<.*>$')
    fieldnames = ["word", "lemma", "pos", "msd", "dephead", "deprel", "lemgram"]
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


def output_rels(deprels):
    for data in deprels:
        print '\t'.join(map(lambda x: str(data[x]),
                            ['head', 'rel', 'dep', 'depextra', 'freq',
                             'freq_rel', 'freq_head_rel', 'freq_rel_dep', 'wf',
                             'sentences']))


def main():
    deprels = Deprels()
    process_input(sys.stdin, deprels)
    output_rels(deprels)


if __name__ == '__main__':
    main()
