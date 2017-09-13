#! /usr/bin/env python


import sys
import re

from collections import defaultdict
from xml.sax.saxutils import escape

import korpimport.util as korputil
import korpimport.xmlutil as xmlutil


class LemmieToVrtConverter(korputil.InputProcessor):

    _output_fields = ['w', 'lemma', 'pos', 'msd'];
    _elem_map = {
        's': 'sentence',
        'p': 'paragraph',
        # 'div': None,
        # 'body': None,
    }
    _docinfo_attrs = [
        ('lemmie_id', 'id'),
        'title',
        'creator',
        'type',
        'subject',
        'publisher',
        'contributor',
        'date',
        'source',
        ('lang', 'language'),
        'rights',
        ('wordcount', 'sizeWords'),
        ('lemmie_corpus', 'inCorpus'),
        ('filename', 'path'),
    ]
    _docinfo_lang_map = {'FI': 'fin', 'SE': 'swe', 'EN': 'eng'}

    def __init__(self, args=None):
        super(LemmieToVrtConverter, self).__init__()
        self._elem_ids = defaultdict(int)
        self._elem_reader = self._get_elem_reader()
        self._docinfo_reader = self._get_docinfo_reader()
        self._docinfo_cache = {}

    def process_input_stream(self, stream, filename=None):
        reader = korputil.tsv_dictreader(stream)
        text_lines = []
        prev_textid = ''
        textid = ''
        for line in reader:
            # print repr(line)
            textid = line['textid']
            if textid == '0':
                continue
            if textid != prev_textid and prev_textid:
                self._write_vrt(text_lines, prev_textid)
                text_lines = []
            text_lines.append(line)
            prev_textid = textid
        if text_lines and prev_textid != '0':
            self._write_vrt(text_lines, prev_textid)

    def _write_vrt(self, token_lines, textid):

        def write_starttag(elemname, attrdict, attrnames=None):
            self._elem_ids[elemname] += 1
            attrdict.update({'new_id': str(self._elem_ids[elemname])})
            sys.stdout.write(
                xmlutil.make_starttag(elemname,
                                      [('id', 'new_id')]
                                      + (attrnames or sorted(attrs.keys())),
                                      attrdict)
                + '\n')

        # sys.stderr.write('make_vrt ' + str(textid) + '\n')
        elems = self._read_elems(textid)
        if not elems:
            sys.stderr.write(
                'Warning: Could not find elements for text id ' + textid + '\n')
            return
        self._modify_elems(elems)
        docinfo = self._get_docinfo(textid)
        if not docinfo:
            sys.stderr.write(
                'Warning: Could not find document info for text id ' + textid
                + '\n')
            return
        elemstack = []
        linenr = 0
        elemnr = 0
        in_para = False
        # print repr(docinfo)
        write_starttag('text', docinfo, self._docinfo_attrs)
        for line in token_lines:
            # print repr(line)
            corpos = line['corpos']
            # print 'corpos', corpos, 'elemnr', elemnr
            # print "STACK 0", repr(elemstack)
            while (elemnr < len(elems) and elems[elemnr]['tagstart'] < corpos
                   and elems[elemnr]['tagend'] <= corpos):
                elemnr += 1
            # print 'STACK 1', repr(elemstack), 'elemnr', elemnr
            while elemnr < len(elems) and elems[elemnr]['tagstart'] <= corpos:
                elem = elems[elemnr]
                elemname = self._get_elemname(elem)
                if elemname:
                    # No nested paragraphs and no elements within
                    # sentences
                    if ((elemname == 'paragraph' and in_para)
                        or (elemstack and elemstack[-1]['tagname'] == 's')):
                        elemnr += 1
                        continue
                    attrs = {'id': str(self._elem_ids[elemname])}
                    if elemname == 'paragraph':
                        in_para = True
                        write_starttag('paragraph', {'type': 'p'}, ['type'])
                    elif elemname == 'sentence':
                        within = ' '.join(elem['tagname'] for elem in elemstack)
                        if not in_para:
                            if elemstack:
                                para_elem = elemstack[-1].copy()
                                para_type = elemstack[-1]['tagname']
                            else:
                                para_elem = elem.copy()
                                para_type = ''
                            para_elem['tagname'] = 'p'
                            write_starttag('paragraph', {'type': para_type},
                                           ['type'])
                            elemstack.append(para_elem)
                            in_para = True
                        write_starttag('sentence', {'within': within},
                                       ['within'])
                elemstack.append(elem)
                elemnr += 1
            # print 'STACK 2', repr(elemstack)
            sys.stdout.write(
                '\t'.join(line[field] for field in self._output_fields) + '\n')
            while elemstack and elemstack[-1]['tagend'] <= corpos:
                elem = elemstack.pop()
                elemname = self._get_elemname(elem)
                if elemname in ['sentence', 'paragraph']:
                    sys.stdout.write('</' + elemname + '>\n')
                    if elemname == 'paragraph':
                        in_para = False
            # print 'STACK 3', repr(elemstack)
        if elemstack and elemstack[-1]['tagname'] == 's':
            sys.stdout.write('</sentence>\n')
        if in_para:
            sys.stdout.write('</paragraph>\n')
        sys.stdout.write('</text>\n')

    def _get_elem_reader(self):
        reader = korputil.tsv_dictreader(self._opts.elem_file)
        elems = []
        prev_textid = ''
        for line in reader:
            if line['textid'] != prev_textid and prev_textid:
                yield elems
                elems = []
            elems.append(line)
            prev_textid = line['textid']
        if elems:
            yield elems

    def _read_elems(self, textid):
        try:
            elems = self._elem_reader.next()
            # print 'read_elems', textid, elems
            while elems and elems[0]['textid'] < textid:
                elems = self._elem_reader.next()
        except StopIteration:
            elems = None
        return elems

    def _modify_elems(self, elems):
        result = []
        within = [('paragraph', False), ('sentence', False)]
        in_sent = False
        in_para = False
        for elemnr, elem in enumerate(elems):
            if elemnr > 0 and elem['tagstart'] > elems[elemnr - 1]['tagstart']:
                if not in_para:
                    para_elem = elems[elemnr - 1].copy()
            result.append(elem)
        elems = result
        return elems

    def _get_elemname(self, elem):
        old_name = elem['tagname']
        new_elem = self._elem_map.get(old_name, old_name)
        if new_elem:
            return new_elem
        else:
            return None

    def _get_docinfo_reader(self):
        return korputil.tsv_dictreader(self._opts.doc_info_file)

    def _get_docinfo(self, textid):
        try:
            # sys.stderr.write('_get_docinfo ' + textid + '\n')
            if textid in self._docinfo_cache:
                info = self._docinfo_cache[textid]
                # sys.stderr.write('use cached info\n')
            else:
                info = self._docinfo_reader.next()
                # sys.stderr.write('read info ' + info['id'] + '\n')
                # Assumes that the info file is sorted by text id
                while info and int(info['id']) < int(textid):
                    # sys.stderr.write('_get_docinfo skip ' + info['id'] + '\n')
                    info = self._docinfo_reader.next()
            # If we read a value for a larger textid than requested,
            # cache the value for later use. This probably indicates a
            # missing value in the document info file.
            if info['id'] != textid:
                self._docinfo_cache[info['id']] = info
                # sys.stderr.write('cache info ' + info['id'] + '\n')
                info = {}
            elif 'language' in info:
                info['language'] = self._docinfo_lang_map.get(info['language'],
                                                              info['language'])
        except StopIteration:
            info = {}
        return info

    def getopts(self, args=None):
        self.getopts_basic(
            dict(usage="%prog [options] [input] > output"),
            args,
            ['--doc-info-file', '--document-info-file'],
            ['--elem-file', '--element-file'],
        )
        if not self._opts.elem_file:
            sys.stderr.write('Please specify an element file with'
                             ' --element-file\n')
            exit(1)
        elif not self._opts.doc_info_file:
            sys.stderr.write('Please specify a document information file'
                             ' with --document-info-file\n')
            exit(1)


if __name__ == "__main__":
    LemmieToVrtConverter().run()
