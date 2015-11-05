#! /usr/bin/env python
# -*- coding: utf-8 -*-


# TODO: Metadata from TSV, single translation

import sys
import re
import codecs
import os.path

from collections import OrderedDict
from lxml import etree

import korpimport.util
from korpimport import vrt
from korpimport import eaf


# EafToVrtConverter should be a general-purpose EAF-to-VRT converter
# but it is very incomplete and would probably need a lot of
# rethinking.

class EafToVrtConverter(korpimport.util.InputProcessor):

    def __init__(self):
        super(EafToVrtConverter, self).__init__()
        self._eaf_tree = None
        self._tiers = {}
        self._tier_pos_attrs = [ur'word@.*']
        self._tier_stuct_attrs = [
            (u'sentence', [(ur'ref@.*', u'ref'),
                          (ur'orth(orig)@.*', u'orth_orig'),
                          (ur'ft-eng(orig)@.*', u'transl')]),
        ]
        self._vrt = None

    def process_input_stream(self, stream, filename=None):
        # print 'FILE', filename
        self._filename = filename
        self._eaf_tree = etree.parse(stream).getroot()
        self._tiers = {}
        self._extract_tiers()
        self._vrt = vrt.VrtData()
        self._construct_vrt()
        self._output_vrt()

    def _extract_tiers(self):
        for tier_et in self._eaf_tree.iterdescendants('TIER'):
            tier = eaf.EafTier(tier_et)
            if (self._opts.participant is None
                or tier.participant == self._opts.participant):
                self._tiers[tier.id_] = tier

    def _constuct_vrt(self):
        pass

    def _output_vrt(self):
        for line in self._vrt.serialize():
            sys.stdout.write(line)


class EafRiesslerToVrtConverter(EafToVrtConverter):

    """Converter for Michael Rießler's EAF data."""

    def __init__(self):
        super(EafRiesslerToVrtConverter, self).__init__()
        self._text_metadata = {}
        if self._opts.metadata_file:
            self._read_metadata_file()

    def _read_metadata_file(self):
        with codecs.open(self._opts.metadata_file, encoding='utf-8') as mdf:
            heading = True
            headings = []
            for line in mdf:
                fields = line[:-1].split('\t')
                if not len(fields):
                    continue
                if heading:
                    headings = [re.sub(ur'(\(.*\)|\d)$', '', field_name.lower())
                                for field_name in fields]
                    heading = False
                else:
                    metadata = OrderedDict()
                    for fieldnr, field in enumerate(fields):
                        if headings[fieldnr] == 'actor':
                            mo = re.match(ur'(.*?)\((.*?)\)', field)
                            if mo:
                                actor, actor_type = mo.group(1), mo.group(2)
                                if actor_type in metadata:
                                    metadata[actor_type] += ' & ' + actor
                                else:
                                    metadata[actor_type] = actor
                        else:
                            metadata[headings[fieldnr]] = field
                        if headings[fieldnr] == 'session_name':
                            mo = re.match(ur'sjd([12]\d{3})', field)
                            if mo:
                                metadata['year'] = mo.group(1)
                    self._text_metadata[fields[0]] = metadata

    def _construct_vrt(self):
        self._simplify_tiers()
        words = []
        sentences = []
        sent_start = 0
        ref_id = None
        ref_id_prev = None
        para_bounds = []
        para_begin = False
        for tokennr, annot in enumerate(self._tiers['word']):
            words.append(annot.value)
            ref_id = annot.annot_ref
            if ref_id != ref_id_prev:
                if ref_id_prev is not None:
                    sentences.append((sent_start, tokennr - 1))
                ref_id_prev = ref_id
                sent_start = tokennr
                if annot.value == '#':
                    if len(para_bounds):
                        if para_bounds[-1] == 'begin':
                            para_bounds[-1] = 'begin+end'
                        else:
                            para_bounds[-1] = 'end'
                    para_bounds.append('')
                    para_begin = True
                else:
                    para_bounds.append('begin' if para_begin else '')
                    para_begin = False
        para_bounds[0] = 'begin' + ('+' + para_bounds[0]
                                    if para_bounds[0] else '')
        para_bounds[-1] = ((para_bounds[-1] + '+' if para_bounds[-1] else '')
                           + 'end')
        sentences.append((sent_start, len(self._tiers['word']) - 1))
        self._vrt.add_tokens(words)
        self._vrt.add_struct('text', [(0, len(words) - 1)])
        self._vrt.add_struct('sentence', sentences)
        # for tier in self._tiers:
        #     print tier, len(self._tiers[tier])
        if 'transl' in self._tiers:
            self._vrt.add_struct_attr(
                'sentence', 'transl',
                (annot.value for annot in self._tiers['transl']))
            self._vrt.add_struct_attr('sentence', 'transl_lang',
                                      [self._transl_lang] * len(sentences))
        if 'orth(orig)' in self._tiers:
            self._vrt.add_struct_attr(
                'sentence', 'orth_orig',
                (annot.value for annot in self._tiers['orth(orig)']))
        self._vrt.add_struct_attr(
            'sentence', 'id', (unicode(x) for x in xrange(len(sentences))))
        self._vrt.add_struct_attr('sentence', 'paragraph_boundary', para_bounds)
        self._add_text_metadata()

    def _simplify_tiers(self):
        extra_tier_refs = {}
        for tier in self._tiers:
            extra_tier_refs[re.sub(ur'@.*', r'', tier)] = self._tiers[tier]
        self._tiers.update(extra_tier_refs)
        for lang in ['eng', 'rus', 'sms', 'kpv']:
            tier_id = 'ft-' + lang
            if tier_id in self._tiers and len(self._tiers[tier_id]):
                self._tiers['transl'] = self._tiers[tier_id]
                self._transl_lang = lang
                break

    def _add_text_metadata(self):
        file_basename = os.path.splitext(os.path.basename(self._filename))[0]
        # print self._filename, file_basename, repr(self._text_metadata)
        metadata = self._text_metadata.get(file_basename, {})
        for key, value in metadata.iteritems():
            self._vrt.add_struct_attr('text', key, [value])

    def getopts(self):
        self.getopts_basic(
            dict(usage="%progname [options] [input] > output"),
            ['--original-words', '--orig-words', dict(action='store_true')],
            ['--participant'],
            ['--metadata-file'],
        )


if __name__ == "__main__":
    EafRiesslerToVrtConverter().run()
