#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import codecs
import sqlite3
import os
import os.path
import errno
import re

import cStringIO as strio

from optparse import OptionParser


# FIXME: Even if the output files may go to several different
# directories (corpora), in particular when using --all-database-docs
# and a parse database containing multiple corpora, they still have a
# single sentence id sequence. Maybe we should have an option
# controlling if each directory should have its own id sequence
# starting from 0 or not.


class ParseAdder(object):

    def __init__(self, opts):
        self._opts = opts
        self._sentnr = 0
        if opts.lemgram_pos_map_file:
            self._lemgram_posmap = self._read_posmap(opts.lemgram_pos_map_file)

    def _read_posmap(self, fname):
        posmap = {}
        with codecs.open(fname, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() == '' or line.startswith('#'):
                    continue
                (src_poses, trg_pos) = line[:-1].split('\t', 1)
                if self._opts.lemgram_inverse_pos_map:
                    (src_poses, trg_pos) = (trg_pos, src_poses)
                posmap.update(dict([(src_pos, trg_pos)
                                    for src_pos in src_poses.split()]))
        return posmap

    def process_files(self, files):
        if isinstance(files, list):
            for file_ in files:
                self.process_files(file_)
        elif isinstance(files, basestring):
            with codecs.open(files, 'r', encoding='utf-8') as f:
                self._add_parses(f)
        else:
            self._add_parses(files)

    def _add_parses(self, infile):
        file_sentnr = 0
        sent_line = None
        tokens = []
        parses = self._get_sentence_parses(infile.name)
        self._infile_name = infile.name
        with codecs.open(self._make_outfilename(infile.name), 'w',
                         encoding='utf-8') as outfile:
            for line in infile:
                if line.startswith('<'):
                    if line.startswith('<sentence '):
                        sent_line = line
                    elif line.startswith('</sentence>'):
                        self._add_sentence_parse(tokens, parses[file_sentnr][0],
                                                 file_sentnr)
                        if self._opts.lemgram_pos_map_file:
                            self._add_sentence_lemgrams(tokens)
                        self._write_sentence(outfile, sent_line, tokens,
                                             parses[file_sentnr][1])
                        tokens = []
                        file_sentnr += 1
                        self._sentnr += 1
                    elif not tokens:
                        outfile.write(line)
                        if not line.endswith('\n'):
                            outfile.write('\n')
                else:
                    tokens.append(line[:-1].split('\t'))

    def _get_sentence_parses(self, vrt_fname):
        parses = []
        with sqlite3.connect(self._opts.database) as con:
           cur = con.cursor()
           sens = cur.execute(
               '''select tok, stt from doc, sen
                  where doc.nme = :nme and sen.yno = doc.yno
                        and sen.dno = doc.dno
                  order by sno''',
               {'nme': self._make_filename_key(vrt_fname)})
           for sen, stt in sens:
               parses.append((self._split_sentence(sen), stt))
        # print repr(parses)
        return parses

    def _make_filename_key(self, vrt_fname):
        dirname, fname = os.path.split(vrt_fname)
        _, lastdir = os.path.split(dirname)
        return os.path.join(lastdir, fname)

    def _split_sentence(self, sen):
        return [[attr for attr in token.split('\t') if attr]
                for token in sen[:-1].split('\n')]

    def _make_outfilename(self, infilename):
        outfilename = self._make_filename_key(infilename)
        dirname = os.path.dirname(outfilename)
        # http://stackoverflow.com/questions/273192/check-if-a-directory-exists-and-create-it-if-necessary
        try:
            os.makedirs(os.path.join(self._opts.output_dir, dirname))
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        return os.path.join(self._opts.output_dir, outfilename)

    def _add_sentence_parse(self, tokens, parsed_tokens, file_sentnr):
        for tokennr, token_fields in enumerate(tokens):
            parsed_token = self._add_parse(
                token_fields, parsed_tokens[tokennr], file_sentnr)
            if (self._opts.lemma_without_compound_boundary
                and len(parsed_token) > 1):
                self._add_lemma_without_boundaries(parsed_token)
            tokens[tokennr] = parsed_token

    def _add_parse(self, token_fields, parsed_token_fields, file_sentnr):
        if token_fields[0] != parsed_token_fields[1]:
            if token_fields[0] == '' and len(token_fields) == 1:
                return []
            sys.stderr.write(
                u'Warning: parse does not match original: "{0}" != "{1}", '
                u'file {2}, sentence {3:d}\n'.format(
                    token_fields[0], parsed_token_fields[1],
                    self._infile_name, file_sentnr))
            # print >>sys.stderr, repr(token_fields)
            # print >>sys.stderr, repr(parsed_token_fields)
        return ([parsed_token_fields[fieldnum]
                 for fieldnum in [1, 3, 5, 7, 9, 11, 0]]
                + [field for field in token_fields[1:] if field])

    def _add_lemma_without_boundaries(self, parsed_token):
        if '|' not in parsed_token[1]:
            lemma_without_boundaries = parsed_token[1]
        elif '-' not in parsed_token[0]:
            lemma_without_boundaries = parsed_token[1].replace('|', '')
        else:
            # In some cases, the lemma has - replaced with a |; in
            # other cases not
            wordform_parts = parsed_token[0].split('-')
            lemma_parts = parsed_token[1].split('|')
            if (len(wordform_parts) == len(lemma_parts)
                and '-' not in parsed_token[1]):
                lemma_without_boundaries = parsed_token[1].replace('|', '-')
            else:
                lemma_without_boundaries = [lemma_parts[0]]
                lemma_prefix_len = len(lemma_parts[0])
                wf_prefix_len = len(wordform_parts[0])
                wf_partnr = 1
                for lemma_part in lemma_parts[1:]:
                    if wf_partnr >= len(wordform_parts):
                        lemma_without_boundaries.append(lemma_part)
                    elif (lemma_part[:2] == wordform_parts[wf_partnr][:2]
                          and abs(wf_prefix_len - lemma_prefix_len) <= 2):
                        # FIXME: Devise a better heuristic
                        lemma_without_boundaries.extend(['-', lemma_part])
                        wf_prefix_len += len(wordform_parts[wf_partnr])
                        wf_partnr += 1
                    else:
                        lemma_without_boundaries.append(lemma_part)
                    lemma_prefix_len += len(lemma_part)
                lemma_without_boundaries = ''.join(lemma_without_boundaries)
        parsed_token[1:1] = [lemma_without_boundaries]

    def _add_sentence_lemgrams(self, tokens):
        for token_fields in tokens:
            if len(token_fields) > 1:
                token_fields.append(self._make_lemgram(token_fields[1],
                                                       token_fields[3]))

    def _make_lemgram(self, lemma, pos):
        return '|' + lemma + '..' + self._lemgram_posmap.get(pos, 'xx') + '.1|'

    def _write_sentence(self, outfile, sent_line, tokens, parse_state):
        outfile.write(''.join([sent_line[:-2].replace(' id=', ' local_id='),
                               ' id="', str(self._sentnr),
                               '" parse_state="', parse_state, '">\n']))
        for token_fields in tokens:
            outfile.write('\t'.join(token_fields) + '\n')
        outfile.write('</sentence>\n')


def read_input_files_list(list_filename):
    skip_line_re = re.compile(r'^\s*(#.*)?$')
    with open(list_filename) as f:
        return [line.strip() for line in f if not skip_line_re.match(line)]


def list_files_in_directory(dirname):
    """Recursively list files in dirname and its subdirs."""
    full_filenames = []
    for dirpath, dirnames, filenames in os.walk(dirname):
        full_filenames.extend(
            sorted(os.path.join(dirpath, fname) for fname in filenames))
    return full_filenames


def list_database_docs(database, input_root):
    with sqlite3.connect(database) as con:
       cur = con.cursor()
       fnames = sorted(os.path.join(input_root, fname)
                       for (fname,)
                       in cur.execute('''select distinct nme from doc;'''))
    return fnames


def getopts():
    optparser = OptionParser()
    optparser.add_option('--database')
    optparser.add_option('--output-dir', default='.')
    optparser.add_option('--input-files-list')
    optparser.add_option('--input-dir')
    optparser.add_option('--input-root')
    optparser.add_option('--all-database-docs', action='store_true')
    optparser.add_option('--no-lemma-without-compound-boundary',
                         action='store_false', default=True,
                         dest='lemma_without_compound_boundary')
    optparser.add_option('--lemgram-pos-map-file')
    optparser.add_option('--lemgram-inverse-pos-map')
    (opts, input_filenames) = optparser.parse_args()
    if opts.all_database_docs:
        input_filenames.append(list_database_docs(opts.database,
                                                  opts.input_root or ''))
    else:
        if opts.input_files_list:
            input_filenames.append(read_input_files_list(opts.input_files_list))
        if opts.input_dir:
            input_filenames.append(list_files_in_directory(opts.input_dir))
    return (opts, input_filenames)


def main():
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, input_filenames) = getopts()
    parse_adder = ParseAdder(opts)
    parse_adder.process_files(input_filenames)


if __name__ == "__main__":
    main()
