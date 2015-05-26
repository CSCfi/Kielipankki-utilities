#! /usr/bin/env python


# Extract information for the Korp MySQL name database tables from VRT
# input.


import sys
import os
import re
import codecs
import gc

from optparse import OptionParser
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
from collections import defaultdict
from os.path import basename


class Names(object):

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

    class IdDict(dict):

        def __init__(self):
            dict.__init__(self)

        def get_id(self, key):
            return self.setdefault(key, len(self))

    def __init__(self):
        self._names = self.IdDict()
        self._freqs = defaultdict(int)
        self._sents = defaultdict(self.SentInfo)

    def _get_name_id(self, name, cat):
        return str(self._names.get_id((name, cat)))

    def iter_names(self):
        for name, cat in self._names:
            yield (str(self._get_name_id(name, cat)), name, cat)

    def iter_freqs(self):
        for key, freq in self._freqs.iteritems():
            name_id, text_id = key
            yield (str(name_id), text_id, str(freq))

    def iter_sents(self):
        for name_id, sents in self._sents.iteritems():
            for sent_info in sents.sentences:
                sent_id, start, end = sent_info
                yield (str(name_id), str(sent_id), str(start), str(end))

    def add(self, name, cat, text_id, sent_id, start, end):
        name_id = self._names.get_id((name, cat))
        self._freqs[(name_id, text_id)] += 1
        self._sents[name_id].add_info([(sent_id, start, end)])


class NameExtractor(object):

    def __init__(self, opts):
        self._opts = opts
        self._names = Names()
        text_id_structname, text_id_attrname = self._opts.id_attribute.split(
            '_', 1)
        self._text_id_re = self._make_struct_attr_extract_regex(
            text_id_structname, text_id_attrname)
        self._sent_id_re = self._make_struct_attr_extract_regex(
            "sentence", "id")

    def _make_struct_attr_extract_regex(self, structname, attrname):
        return re.compile(r'<' + structname
                          + r'\s+(?:.+\s)?' + attrname
                          + r'="(.*?)".*>')

    def process_input(self, args):
        if isinstance(args, list):
            for arg in args:
                self.process_input(arg)
        elif isinstance(args, basestring):
            with codecs.open(args, 'r', encoding='utf-8') as f:
                self._process_input_stream(f)
        else:
            self._process_input_stream(args)

    def _process_input_stream(self, f):

        def _get_fieldnr(fieldnr):
            return fieldnr if fieldnr <= 0 else fieldnr - 1

        nametag_fieldnr = _get_fieldnr(self._opts.name_tag_field_number)
        lemma_fieldnr = _get_fieldnr(self._opts.lemma_field_number)
        namedata = []
        nametag = None
        sentnr = 0
        text_id = None
        sent_id = None
        token_nr = 0
        for linenr, line in enumerate(f):
            line = line[:-1]
            if not line:
                continue
            elif line[0] != '<':
                fields = line.split('\t')
                nametag_new = fields[nametag_fieldnr]
                if namedata and nametag_new != nametag:
                    self._add_name(namedata, nametag, text_id, sent_id,
                                   token_nr)
                    namedata = []
                nametag = nametag_new
                if nametag and nametag != '_':
                    namedata.append((fields[0], fields[lemma_fieldnr]))
                token_nr += 1
            else:
                if namedata:
                    self._add_name(namedata, nametag, text_id, sent_id,
                                   token_nr)
                namedata = []
                nametag = None
                mo = self._text_id_re.match(line)
                if mo:
                    text_id = mo.group(1)
                    token_nr = 0
                else:
                    mo = self._sent_id_re.match(line)
                    if mo:
                        sent_id = mo.group(1)
                        token_nr = 0
        if namedata:
            self._add_name(namedata, nametag, text_id, sent_id, token_nr)

    def _add_name(self, namedata, nametag, text_id, sent_id, last_token_nr):
        if nametag.startswith('Timex') or nametag.startswith('Numex'):
            name = ' '.join(token[0] for token in namedata)
        else:
            if len(namedata) > 1:
                name = ' '.join(token[0] for token in namedata[:-1]) + ' '
            else:
                name = ''
            last_wordform, last_lemma = namedata[-1]
            if last_wordform.istitle():
                name += last_lemma.title()
            elif last_wordform.isupper():
                name += last_lemma.upper()
            else:
                name += last_lemma
        self._names.add(name, nametag, text_id, sent_id,
                        last_token_nr - len(namedata) + 1, last_token_nr)

    # The following methods have been copied directly (output_rels
    # slightly modified) from vrt-extract-relations.py. We probably
    # should put them to a common library module.

    def output_rels(self):
        output_rels = [('iter_freqs', '', True),
                       ('iter_names', '_strings', True),
                       ('iter_sents', '_sentences', True)]
        for rel_iter_name, rel_suffix, numeric_sort in output_rels:
            self._output_rel(getattr(self._names, rel_iter_name)(),
                             rel_suffix, numeric_sort)
        if self._opts.temp_files:
            del self._names
            gc.collect()
            self._write_final_files(output_rels)

    def _output_rel(self, data, rel_suffix, numeric_sort=False):
        with self._open_output_file(self._make_output_filename(rel_suffix),
                                    numeric_sort, self._opts.temp_files) as f:
            for row in data:
                f.write((u'\t'.join(row) + '\n').encode('utf-8'))
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
        f = codecs.open(fname, 'w')
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
    optparser.add_option('--id-attribute', default='text_id')
    optparser.add_option('--lemma-field-number', type='int', default=2)
    optparser.add_option('--name-tag-field-number', '--ner-tag-field-number',
                         type='int', default=-2)
    optparser.add_option('--corpus-name')
    optparser.add_option('--output-prefix')
    optparser.add_option('--compress', type='choice',
                         choices=['none', 'gzip', 'gz', 'bzip2', 'bz', 'bz2'],
                         default='none')
    optparser.add_option('--sort', action='store_true', default=False)
    optparser.add_option('--temp-files', '--temporary-files',
                         action='store_true', default=False)
    optparser.add_option('--temp-dir', '--temporary-directory', default=None)
    (opts, args) = optparser.parse_args()
    if opts.output_prefix is None and opts.corpus_name is not None:
        opts.output_prefix = 'names_' + opts.corpus_name
    if opts.compress == 'none' and not opts.sort:
        opts.temp_files = False
    return (opts, args)


def main():
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    extractor = NameExtractor(opts)
    extractor.process_input(args or sys.stdin)
    extractor.output_rels()


if __name__ == '__main__':
    main()
