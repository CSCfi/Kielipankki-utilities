#! /usr/bin/env python3


import sys
import os
import re
import gc
import errno

from optparse import OptionParser
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
from collections import defaultdict
from os.path import basename

from korpimport3.util import set_sys_stream_encodings


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

    class IdDict(dict):

        def __init__(self):
            dict.__init__(self)

        def get_id(self, key):
            return self.setdefault(key, len(self))

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

    # (R1, POS): R2: Map relation R1 to R2 if the head POS is POS.
    # FIXME: This is ad hoc for the TDT; add a facility for reading
    # the data from the relation map file.
    rel_pos_map = {
        ('ADV', 'JJ'): 'ET',
        ('ADV', 'NN'): 'ET',
        ('AT', 'VB'): 'ADV',
        ('ET', 'VB'): 'ADV',
        ('CPL', 'JJ'): 'ET',
        ('CPL', 'NN'): 'ET',
    }

    def __init__(self, relmap=None, wordform_pairtypes=None, output_type=None,
                 ignore_unknown_rels=False, **kwargs):
        self.relmap = relmap or self.__class__.relmap
        self._wordform_pairtypes = wordform_pairtypes or set()
        self._output_type = output_type
        self._ignore_unknown_rels = ignore_unknown_rels
        iter_suffix = ('_stringids' if output_type == 'new-strings'
                       else '_strings')
        for iter_type in ['freqs', 'freqs_head_rel', 'freqs_rel_dep']:
            setattr(self, 'iter_' + iter_type,
                    getattr(self, 'iter_' + iter_type + iter_suffix))
        self.strings = self.IdDict()
        self.freqs_rel = defaultdict(int)
        self.freqs_head_rel = defaultdict(int)
        self.freqs_rel_dep = defaultdict(int)
        self.sentences = defaultdict(self.SentInfo)

    def _get_string_type(self, lemgram_or_wordpos):
        if len(lemgram_or_wordpos) > 6 and lemgram_or_wordpos[-6:-4] == '..':
            return 'lemgram'
        elif len(lemgram_or_wordpos) > 3 and lemgram_or_wordpos[-3] == '_':
            return 'wordpos'
        else:
            return 'word'

    def _get_pos(self, lemgram_or_wordpos):
        string_type = self._get_string_type(lemgram_or_wordpos)
        if string_type == 'lemgram':
            return lemgram_or_wordpos[-4:-2].upper()
        elif string_type == 'wordpos':
            return lemgram_or_wordpos[-2:]
        else:
            return ''

    def _get_lemgram_or_lemma(self, lemgram_or_wordpos):
        string_type = self._get_string_type(lemgram_or_wordpos)
        if string_type == 'wordpos':
            return lemgram_or_wordpos[:-3]
        else:
            return lemgram_or_wordpos

    def _get_string_id(self, lemgram_or_wordpos):
        pos = self._get_pos(lemgram_or_wordpos)
        word = self._get_lemgram_or_lemma(lemgram_or_wordpos)
        return str(self.strings.get_id((word, '', pos)))

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

    def iter_strings(self):
        for key, id_ in self.strings.items():
            string, stringextra, pos = key
            yield (str(id_),
                   string,
                   stringextra,
                   pos)

    def iter_freqs_strings(self):
        for key in self.sentences:
            (head, rel, dep, wf) = key
            yield (str(self.sentences[key].id),  # id
                   head,
                   rel,
                   dep,
                   '',  # depextra
                   str(self.sentences[key].get_len()),  # freq
                   '3' if wf else '0')  # wf

    def iter_freqs_stringids(self):
        for key in self.sentences:
            (head, rel, dep, wf_head, wf_dep) = key
            yield (str(self.sentences[key].id),  # id
                   self._get_string_id(head),
                   rel,
                   self._get_string_id(dep),
                   str(self.sentences[key].get_len()),  # freq
                   str(int(not wf_head)),  # bfhead
                   str(int(not wf_dep)),   # bfdep
                   str(int(wf_head)),      # wfhead
                   str(int(wf_dep)))       # wfdep

    def iter_freqs_rel(self):
        for rel in self.freqs_rel:
            yield (rel,
                   str(self.freqs_rel[rel]))

    def iter_freqs_head_rel_strings(self):
        for (head, rel) in self.freqs_head_rel:
            yield (head,
                   rel,
                   str(self.freqs_head_rel[(head, rel)]))

    def iter_freqs_head_rel_stringids(self):
        for (head, rel) in self.freqs_head_rel:
            yield (self._get_string_id(head),
                   rel,
                   str(self.freqs_head_rel[(head, rel)]))

    def iter_freqs_rel_dep_strings(self):
        for (rel, dep) in self.freqs_rel_dep:
            yield (dep,
                   '',  # depextra
                   rel,
                   str(self.freqs_rel_dep[(rel, dep)]))

    def iter_freqs_rel_dep_stringids(self):
        for (rel, dep) in self.freqs_rel_dep:
            yield (self._get_string_id(dep),
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
                rel = self.relmap.get(deprel, '')
                if rel in ['', '-', '_', 'XX'] and self._ignore_unknown_rels:
                    continue
                head = data[headnr][0]
                headpos = self._get_pos(head)
                # sys.stderr.write(rel + ' ' + headpos)
                rel = self.rel_pos_map.get((rel, headpos), rel)
                # sys.stderr.write(' ' + rel + '\n')
                if rel in ['', '-', '_', 'XX'] and self._ignore_unknown_rels:
                    continue
                self.freqs_rel[rel] += 1
                self._add_info(sent_id, rel, head, dep, headnr, wordnr)
                if self._wordform_pairtypes:
                    head_wform = data[headnr][-1] +  '_' + self._get_pos(head)
                    dep_wform = wform + '_' + self._get_pos(dep)
                    if 'wf' in self._wordform_pairtypes:
                        self._add_info(sent_id, rel, head_wform, dep_wform,
                                       headnr, wordnr, True, True)
                    if 'bf' in self._wordform_pairtypes:
                        self._add_info(sent_id, rel, head_wform, dep, headnr,
                                       wordnr, True, False)
                        self._add_info(sent_id, rel, head, dep_wform, headnr,
                                       wordnr, False, True)

    def _add_info(self, sent_id, rel, head, dep, headnr, depnr, wf_head=False,
                  wf_dep=False):
        self.freqs_head_rel[(head, rel)] += 1
        self.freqs_rel_dep[(rel, dep)] += 1
        self.sentences[(head, rel, dep, wf_head, wf_dep)].add_info(
            [(sent_id, min(depnr, headnr) + 1,
              max(depnr, headnr) + 1)])

    def get_sizes(self):
        sizes = []
        for attr in ['freqs_rel', 'freqs_head_rel', 'freqs_rel_dep',
                     'sentences']:
            sizes.append((attr, sys.getsizeof(getattr(self, attr))))
        return sizes


class DeprelsDirectWrite(Deprels):

    """Write relation data directly to output files to reduce RAM usage.

    Write "raw", unsorted and uncounted relations data directly to
    output files to be counted in postprocessing (sort | uniq -c). In
    this way, only string ids need to be kept in memory. (Maybe even
    that would not be strictly necessary, but it simplifies
    postprocessing.)

    Relation type frequencies are counted as in Deprels, since the
    number of relations is small.
    """

    def __init__(self, filenames=None, **kwargs):
        # FIXME: Deprels constructor creates attributes that
        # DeprelsDirectWrite does not need.
        super(DeprelsDirectWrite, self).__init__(**kwargs)
        self._outfiles = dict((reltype, open(fname, 'w', encoding='utf-8'))
                              for reltype, fname in filenames.items())

    def _add_info(self, sent_id, rel, head, dep, headnr, depnr, wf_head=False,
                  wf_dep=False):
        head_id = str(self._get_string_id(head))
        dep_id = str(self._get_string_id(dep))
        triplet_id = head_id + '|' + rel + '|' + dep_id
        self._write('head_rel', (head_id, rel))
        self._write('dep_rel', (dep_id, rel))
        self._write('head_dep_rel',
                    (triplet_id, head_id, rel, dep_id,
                     str(int(not wf_head)), str(int(not wf_dep)),
                     str(int(wf_head)), str(int(wf_dep))))
        self._write('sentences',
                    (triplet_id, sent_id,
                     str(min(depnr, headnr) + 1),
                     str(max(depnr, headnr) + 1)))

    def _write(self, reltype, fields):
        self._outfiles[reltype].write('\t'.join(fields) + '\n')

    def close_files(self):
        for f in self._outfiles.values():
            f.close()


class RelationExtractor(object):

    # TODO: Add an option for this
    _str_maxlen = 100

    def __init__(self, opts):
        self._opts = opts
        relmap = None
        if opts.relation_map:
            relmap = self._read_relmap(opts.relation_map)
        self._temp_fnames = {}
        if self._opts.input_fields:
            # Strip slashes to allow "lex/"
            self._input_fieldnames = re.split(
                r'\s*[,\s]\s*', self._opts.input_fields.replace('/', ''))
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
        output_new_strings = (self._opts.output_type == 'new-strings')
        self._output_rels = [
            ('iter_freqs', '', True),
            ('iter_freqs_rel', '_rel', False),
            ('iter_freqs_head_rel', '_head_rel', output_new_strings),
            ('iter_freqs_rel_dep', '_dep_rel', output_new_strings),
            ('iter_sentences', '_sentences', True)]
        if output_new_strings:
            self._output_rels.append(('iter_strings', '_strings', True))
        deprels_common_args = {
            'relmap': relmap,
            'wordform_pairtypes': opts.word_form_pair_type,
            'ignore_unknown_rels': opts.ignore_unknown_relations,
        }
        if self._opts.raw_output:
            filenames = {}
            for _, rel_suffix, _ in self._output_rels:
                if rel_suffix in ['_rel', '_strings']:
                    continue
                elif rel_suffix == '':
                    rel_name = 'head_dep_rel'
                else:
                    rel_name = rel_suffix.lstrip('_')
                filenames[rel_name] = self._make_output_filename(rel_suffix,
                                                                 '.raw')
            self._deprels = DeprelsDirectWrite(filenames=filenames,
                                               **deprels_common_args)
        else:
            self._deprels = Deprels(output_type=opts.output_type,
                                    **deprels_common_args)

    def _read_relmap(self, fname):
        relmap = {}
        with open(fname, 'r', encoding='utf-8-sig') as f:
            for line in f:
                line_strip = line.strip()
                if line_strip == '' or line_strip.startswith('#'):
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
        elif isinstance(args, str):
            with open(args, 'r', encoding='utf-8-sig') as f:
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
                    if len(fields[fieldnr_lemgram_lemma]) > self._str_maxlen:
                        # Keep the lemgram POS code and sense number
                        parts = fields[fieldnr_lemgram_lemma].rpartition('..')
                        fields[fieldnr_lemgram_lemma] = (
                            parts[0][:self._str_maxlen - len(parts[2]) - 2]
                            + '..' + parts[2])
                # Would we need this:
                # fields.append('')	# An empty lemgram by default
                data.append((fields[fieldnr_lemgram_lemma],
                             fields[fieldnr_deprel],
                             fields[fieldnr_dephead],
                             fields[fieldnr_word][:self._str_maxlen]))
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
        elif self._opts.raw_output:
            self._output_rels_raw()
        else:
            self._output_rels_new()

    def _output_rels_old(self):
        for data in self._deprels:
            print('\t'.join([str(data[x]) for x in ['head', 'rel', 'dep', 'depextra', 'freq',
                                 'freq_rel', 'freq_head_rel', 'freq_rel_dep',
                                 'wf', 'sentences']]))

    def _output_rels_new(self):
        for rel_iter_name, rel_suffix, numeric_sort in self._output_rels:
            self._output_rel_iter(rel_iter_name, rel_suffix, numeric_sort)
        if self._opts.temp_files:
            del self._deprels
            gc.collect()
            self._write_final_files(self._output_rels)

    def _output_rel_iter(self, rel_iter_name, *args):
        self._output_rel(getattr(self._deprels, rel_iter_name)(), *args)

    def _output_rel(self, data, rel_suffix, numeric_sort=False):
        with self._open_output_file(self._make_output_filename(rel_suffix),
                                    numeric_sort, self._opts.temp_files) as f:
            for row in data:
                f.write('\t'.join(row) + '\n')
            if self._opts.temp_files:
                self._temp_fnames[rel_suffix] = f.name

    def _output_rels_raw(self):
        self._deprels.close_files()
        self._output_named_rel('_rel')
        self._output_named_rel('_strings')

    def _output_named_rel(self, suffix):
        for rel_iter_name, rel_suffix, numeric_sort in self._output_rels:
            if rel_suffix == suffix:
                self._output_rel_iter(rel_iter_name, rel_suffix, numeric_sort)

    def _make_output_filename(self, rel_suffix, extra_suffix=''):
        return self._opts.output_prefix + rel_suffix + extra_suffix + '.tsv'

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
        f = open(fname, 'w', encoding='utf-8')
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
        for (rel_suffix, temp_fname) in self._temp_fnames.items():
            with open(temp_fname, 'r') as inf:
                with self._open_output_file(
                    self._make_output_filename(rel_suffix),
                    numeric_sort[rel_suffix], False) as outf:
                    for line in inf:
                        outf.write(line)
            os.remove(temp_fname)


def getopts():
    optparser = OptionParser()
    word_form_pair_types = {'none': set(),
                            'wf': set(['wf']),
                            'bf': set(['bf']),
                            'wf+bf': set(['wf', 'bf'])}
    for val, aliases in [('none', [None]),
                         ('wf', ['wordform', 'word-form']),
                         ('bf', ['baseform', 'base-form', 'lemma', 'lemgram']),
                         ('wf+bf', ['both'])]:
        for alias in aliases:
            word_form_pair_types[alias] = word_form_pair_types[val]
    optparser.add_option('--input-type', '--mode', type='choice',
                         choices=['ftb2', 'ftb3', 'ftb3-extrapos'],
                         default='ftb2')
    optparser.add_option('--input-fields', '--input-field-names')
    optparser.add_option('--output-type', type='choice',
                         choices=['old', 'new', 'new-strings'], default='new')
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
    optparser.add_option('--word-form-pair-type', type='choice',
                         choices=list(word_form_pair_types.keys()))
    optparser.add_option('--raw-output', '--optimize-memory',
                         action='store_true')
    # --include-word-forms superseded by --word-form-pair-type=wordform;
    # retained for backward compatibility
    optparser.add_option('--include-word-forms', action='store_true')
    optparser.add_option('--ignore-unknown-relations',
                         '--skip-unknown-relations', action='store_true')
    (opts, args) = optparser.parse_args()
    if opts.output_prefix is None and opts.corpus_name is not None:
        opts.output_prefix = 'relations_' + opts.corpus_name
    if opts.output_type == 'new' and opts.output_prefix is None:
        sys.stderr.write('--output-prefix=PREFIX or --corpus-name=NAME required'
                         + ' with --output-type=new\n')
        exit(1)
    if opts.compress == 'none' and not opts.sort:
        opts.temp_files = False
    if opts.include_word_forms and not opts.word_form_pair_type:
        opts.word_form_pair_type = 'wordform'
    opts.word_form_pair_type = word_form_pair_types[opts.word_form_pair_type]
    return (opts, args)


def main_main():
    input_encoding = 'utf-8-sig'
    output_encoding = 'utf-8'
    set_sys_stream_encodings(input_encoding, output_encoding, output_encoding)
    (opts, args) = getopts()
    extractor = RelationExtractor(opts)
    extractor.process_input(args or sys.stdin)
    extractor.output_rels()


def main():
    try:
        main_main()
    except IOError as e:
        if e.errno == errno.EPIPE:
            sys.stderr.write('Broken pipe\n')
        else:
            sys.stderr.write(str(e) + '\n')
        exit(1)
    except KeyboardInterrupt as e:
        sys.stderr.write('Interrupted\n')
        exit(1)
    except:
        raise


if __name__ == '__main__':
    main()
