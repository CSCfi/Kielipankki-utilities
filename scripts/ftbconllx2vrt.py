#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import re
import codecs

from optparse import OptionParser


def zip_longer(list1, list2, defaultvalue=''):
    lendiff = len(list1) - len(list2)
    if lendiff >= 0:
        return zip(list1, list2 + lendiff * [defaultvalue])
    else:
        return zip(list1 + (- lendiff) * [defaultvalue], list2)


class FtbConllxToVrtConverter(object):

    _lemgram_posmap = {'_': 'xx', # Unspecified
                        'A': 'jj',
                        # AN in the target is not PoS category but a feature,
                        # but we treat it as a category here.
                        'Abbr': 'an',
                        'Adp': 'pp',
                        'Adv': 'ab',
                        'CC': 'kn',
                        u'CC V': 'kn',
                        'Con': 'kn',
                        'CS': 'sn',
                        'Interj': 'in',
                        'Noun': 'nn',
                        'N': 'nn',
                        'Num': 'rg',
                        'Adp Po': 'pp',
                        'Pron': 'pn',
                        'Pun': 'xx',
                        'V': 'vb'}

    def __init__(self, opts):
        self._opts = opts

    def process_input(self, f):

        def fix_msd_cond(msd):
            return (self._fix_msd(msd, self._opts.msd_separator)
                    if self._opts.fix_msd_tags else msd)

        prev_corp = ''
        prev_fname = ''
        infields = ['wnum', 'word', 'lemma', 'pos', 'pos2', 'msd', 'head',
                    'rel', 'f9', 'f10']
        outfields = ['word', 'lemma0', 'lemma', 'pos', 'msd', 'head', 'rel']
        if self._opts.pos_type.startswith('original'):
            outfields[3] = 'pos_orig'
            if self._opts.pos_type.endswith('clean'):
                outfields[4:4] = ['pos']
        elif self._opts.pos_type == 'clean-original':
            outfields[4:4] = ['pos_orig']
        if self._opts.lemgrams:
            outfields.append('lemgram')
        sentnr = 0
        for line in f:
            if line.startswith('<s>'):
                if sentnr > 0:
                    sys.stdout.write('</sentence>\n')
                (corp, fname, linenr) = self._extract_info(line)
                if fname != prev_fname and prev_fname != '':
                    sys.stdout.write('</file>\n')
                if self._opts.subcorpora and corp != prev_corp:
                    if prev_corp != '':
                        sys.stdout.write('</subcorpus>\n')
                    sys.stdout.write(
                        '<subcorpus name="{corp}">\n'.format(corp=corp))
                    prev_corp = corp
                if fname != prev_fname:
                    sys.stdout.write(
                        '<file name="{fname}">\n'.format(fname=fname))
                    prev_fname = fname
                sentnr += 1
                sys.stdout.write('<sentence id="{sentnr}" line="{linenr}">\n'
                                 .format(sentnr=sentnr, linenr=linenr))
            elif not line.startswith('</s>'):
                fields = self._set_fields(line, infields)
                fields['lemma0'] = self._remove_markers(fields['lemma'])
                fields['pos_orig'] = fix_msd_cond(fields['pos'].strip())
                fields['pos'] = self._extract_pos(fields['pos'])
                fields['msd'] = fix_msd_cond(fields['msd'])
                if self._opts.lemgrams:
                    fields['lemgram'] = self._make_lemgram(fields['lemma0'],
                                                           fields['pos'])
                sys.stdout.write('\t'.join(self._get_fields(fields, outfields))
                                 + '\n')
        sys.stdout.write('</sentence>\n</file>\n')
        if self._opts.subcorpora:
            sys.stdout.write('</subcorpus>\n')

    def _extract_info(self, line):
        mo = re.search(ur'<loc\s+file="((.+?)\s+.+?)"\s+line="(.*?)"\s*/>',
                       line)
        if mo is None:
            sys.stderr.write("warning: invalid location: " + line)
            return ('', '', '')
        return (mo.group(2), mo.group(1), mo.group(3))

    def _set_fields(self, line, fieldnames):
        fields = line[:-1].split('\t')
        return dict(zip_longer(fieldnames, fields))

    def _get_fields(self, fields, fieldnames):
        return [fields[fldname] for fldname in fieldnames]

    def _remove_markers(self, lemma):
        return ''.join(lemma.split('#'))

    def _extract_pos(self, pos):
        pos = pos.strip()
        pos = re.sub(r'\s{2,}', ' ', pos)
        pos = re.sub(r'(\s(\d+|<HEUR.?>|TrunCo|>>>)|</s>)+$', '', pos)
        pos = re.sub(r'(\s(Nom|Gen|Par|Ill|Sg|Pl|(kO|pA|Foc_)\w*)|INF5)+$', '',
                     pos)
        pos = re.sub(r'(<.*?>|Forgn|Roman|Pr[sf]Prc\w*)\s|D[ANV]-\w+?\s'
                     + r'|\sD[ANV]-\w+?', '', pos)
        pos = re.sub(r'Pron Pron', 'Pron', pos)
        pos = re.sub(r'Abbr Abbr', 'Abbr', pos)
        pos = re.sub(r'Punct .*', 'Punct', pos)
        pos = self._fix_msd(pos)
        return pos

    def _fix_msd(self, msd, separator=u':'):
        return re.sub(r'\s+', separator,
                      re.sub(r'<', '[', re.sub(r'>', ']', msd)))

    def _make_lemgram(self, lemma, pos):
        return (u'|{lemma}..{pos}.1|'
                .format(lemma=lemma, pos=self._lemgram_posmap.get(pos, 'xx')))


def test_pos_conv(f):
    posfreqs = {}
    for line in f:
        mo = re.search(r'^\s*(\d+)\s(.*)', line[:-1])
        if mo:
            (freq, pos) = (mo.group(1), mo.group(2))
        else:
            (freq, pos) = (1, line)
        pos = extract_pos(pos)
        if pos not in posfreqs:
            posfreqs[pos] = 0
        posfreqs[pos] += int(freq)
    for pos in posfreqs:
        sys.stdout.write(u'{freq:8d} {pos}\n'.format(freq=posfreqs[pos],
                                                     pos=pos))


def getopts():
    optparser = OptionParser()
    optparser.add_option('--lemgrams', action='store_true', default=False)
    optparser.add_option('--pos-type', type='choice',
                         choices=['original', 'clean',
                                  'original-clean', 'original+clean', 
                                  'clean-original', 'clean+original'],
                         default='clean')
    optparser.add_option('--msd-separator', '--morpho-tag-separator',
                         default=u':')
    optparser.add_option('--test-pos-conv', action='store_true', default=False)
    optparser.add_option('--no-fix-msd-tags', '--no-fix-morpho-tags',
                         action='store_false', dest='fix_msd_tags',
                         default=True)
    optparser.add_option('--no-subcorpora', action='store_false',
                         dest='subcorpora', default=True)
    (opts, args) = optparser.parse_args()
    opts.pos_type = opts.pos_type.replace('+', '-')
    return (opts, args)


def main():
    encoding = 'utf-8'
    sys.stdin = codecs.getreader(encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(encoding)(sys.stdout)
    sys.stderr = codecs.getwriter(encoding)(sys.stderr)
    (opts, args) = getopts()
    if opts.test_pos_conv:
        test_pos_conv(sys.stdin)
    else:
        converter = FtbConllxToVrtConverter(opts)
        converter.process_input(sys.stdin)


if __name__ == '__main__':
    main()
