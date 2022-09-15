#! /usr/bin/env python3
# -*- coding: utf-8 -*-


# This script has been converted from Python 2 to Python 3.

# TODO:
# - Rewrite the script as a proper VRT tool.


import sys
import errno
import re
import unicodedata

from optparse import OptionParser
from os.path import basename

from korpimport3.util import unique, set_sys_stream_encodings


def warn(msg, kwdict):
    sys.stderr.write(('{progname}: Warning: ' + msg + '\n')
                     .format(progname=basename(sys.argv[0]), **kwdict))


def process_input(f, posmap, opts):
    if isinstance(f, str):
        with open(f, 'r', encoding='utf-8-sig') as fp:
            process_input_stream(fp, posmap, opts)
    else:
        process_input_stream(f, posmap, opts)


def process_input_stream(f, posmap, opts):
    for linenr, line in enumerate(f):
        if line.startswith('<') and line.endswith('>\n'):
            sys.stdout.write(line)
        elif line != '\n':
            sys.stdout.write(add_lemgram(line, posmap, opts))


def add_lemgram(line, posmap, opts):
    fields = line[:-1].split('\t')
    lemmas = split_set_value(get_field(fields, opts.lemma_field))
    if not lemmas or lemmas == [''] and not opts.skip_empty_lemmas:
        # Fall back to word form if no lemma
        lemmas = [get_field(fields, 0, '')]
    poses = split_set_value(get_field(fields, opts.pos_field, ''))
    lemgrams = []
    # If the number of lemmas and POSes is the same, assume that
    # lemma1 corresponds to pos1, lemma2 to pos2 and so on; otherwise,
    # add all possible combinations.
    if len(lemmas) == len(poses):
        for i in range(len(lemmas)):
            lemgrams.extend(make_lemgrams(posmap, lemmas[i], poses[i], opts))
    else:
        for lemma in lemmas:
            for pos in poses:
                lemgrams.extend(make_lemgrams(posmap, lemma, pos, opts))
    lemgram_str = ('|' + '|'.join(unique(lemgrams)) + '|') if lemgrams else '|'
    return line[:-1] + '\t' + lemgram_str + '\n'


def get_field(fields, num, default=None):
    try:
        return fields[num]
    except IndexError as e:
        return default


def split_set_value(field):
    if field == '|':
        return []
    if field and field[0] == '|' and field[-1] == '|':
        return field[1:-1].split('|')
    else:
        return [field]


def make_lemgrams(posmap, lemma, pos, opts):
    lemmas = [lemma]
    if opts.add_lowercase:
        lemma_lower = lemma.lower()
        if lemma_lower != lemma:
            lemmas.append(lemma_lower)
    if opts.add_non_diacritic:
        add_lemmas = []
        for lemma in lemmas:
            # CHECK: Would it be faster to check if lemma contains non-ASCII
            # characters?
            if opts.keep_letters:
                lemma_non_diacritic = opts.non_keep_letters_re.sub(
                    lambda mo: remove_diacritics(mo.group()), lemma)
            else:
                lemma_non_diacritic = remove_diacritics(lemma)
            if lemma_non_diacritic != lemma:
                add_lemmas.append(lemma_non_diacritic)
        lemmas.extend(add_lemmas)
    pos = posmap.get(pos, 'xx')
    return ['{lemma}..{pos}.1'.format(lemma=lemma, pos=pos)
            for lemma in lemmas]


def remove_diacritics(s):
    # Based on https://stackoverflow.com/a/517974
    return ''.join(c for c in unicodedata.normalize('NFKD', s)
                    if not unicodedata.combining(c))


def read_posmap(fname, opts):

    def warn_posmap(msg, kwdict):
        warn('PoS map file {fname}, line {linenum}: ' + msg, kwdict)

    posmap = {}
    pos_types = {(False, True): 'source',
                 (True, False): 'target',
                 (False, False): 'source and target'}
    # Supported file-specific options and their default values
    # The options may be set on a line beginning with "#:options: ".
    fileopts = {
        # Source parts of speech may contain spaces, so they do not split the
        # source field into multiple parts of speech mapped to the same target
        # PoS.
        'source-spaces': False,
    }
    with open(fname, 'r', encoding='utf-8-sig') as f:
        linenum = 0
        for line in f:
            linenum += 1
            if line.startswith('#:options:'):
                fileopt_list = line.split()[1:]
                for fileopt in fileopt_list:
                    if fileopt not in fileopts:
                        warn_posmap('unrecognized file option: {fileopt}',
                                    locals())
                    else:
                        fileopts[fileopt] = True
                continue
            elif line.strip() == '' or line.startswith('#'):
                continue
            fields = line[:-1].split('\t')
            fieldcount = len(fields)
            if fieldcount != 2:
                warn_msg_base = (
                    '{fieldcount} tab-separated fields instead of 2; skipping')
                if fieldcount < 2:
                    warn_posmap(warn_msg_base + '.', locals())
                    continue
                else:
                    warn_posmap(warn_msg_base + ' extra fields.', locals())
            (src_poses, trg_pos) = (fields[0].strip(), fields[1].strip())
            if not src_poses or not trg_pos:
                pos_type = pos_types[(bool(src_poses), bool(trg_pos))]
                warn_posmap('empty {pos_type}; skipping.', locals())
                continue
            if opts.inverse_pos_map:
                (src_poses, trg_pos) = (trg_pos, src_poses)
            src_pos_list = ([src_poses] if fileopts['source-spaces']
                            else src_poses.split())
            for src_pos in src_pos_list:
                if src_pos in posmap:
                    if posmap[src_pos] != trg_pos:
                        prev_src_pos = posmap[src_pos]
                        warn_posmap(
                            ('mapping "{src_pos}" to "{trg_pos}" overrides'
                             ' previous mapping to "{prev_src_pos}"'),
                            locals())
                    else:
                        warn_posmap(
                            'duplicate mapping "{src_pos}" to "{trg_pos}"',
                            locals())
                posmap[src_pos] = trg_pos
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
    optparser.add_option(
        '--add-lowercase-variants', action='store_true',
        dest='add_lowercase',
        help=('Add all-lower-case variants of lemgrams for lemmas containing'
              ' upper-case letters'))
    optparser.add_option(
        '--add-non-diacritic-variants', action='store_true',
        dest='add_non_diacritic',
        help=('Add variants of lemgrams without diacritics for lemmas'
              ' containing letters with diacritics'))
    optparser.add_option(
        '--keep-letters-with-diacritics', metavar='CHARS', dest='keep_letters',
        help=('Keep the letters with diacritics in CHARS intact even in'
              ' lemgram variants otherwise without diacritics. CHARS is a'
              ' string of characters that can be used inside a set of'
              ' characters in a regular expression (as [^CHARS]). CHARS are'
              ' retained regardless of their case.'))
    (opts, args) = optparser.parse_args()
    if opts.pos_map_file is None:
        sys.stderr.write('Please specify POS map file with --pos-map-file\n')
        exit(1)
    opts.lemma_field -= 1
    opts.pos_field -= 1
    if opts.keep_letters:
        # Kludge: Add attribute to opts to avoid a global variable
        setattr(opts, 'non_keep_letters_re',
                re.compile(r'([^' + opts.keep_letters + '])',
                           re.UNICODE | re.IGNORECASE))
    return (opts, args)


def main_main():
    input_encoding = 'utf-8-sig'
    output_encoding = 'utf-8'
    set_sys_stream_encodings(input_encoding, output_encoding, output_encoding)
    (opts, args) = getopts()
    posmap = read_posmap(opts.pos_map_file, opts)
    process_input(args[0] if args else sys.stdin, posmap, opts)


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


if __name__ == "__main__":
    main()
