#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs
import re

import xml.etree.ElementTree as et

from optparse import OptionParser


class Converter(object):

    def __init__(self, opts, divtypemap={}, elem_extra_attrs={}):
        self._opts = opts
        self._divtypemap = divtypemap
        self._elem_extra_attrs = elem_extra_attrs

    def process_input(self, f):
        self._src_etr = et.parse(f)
        self._url_base = self._make_url_base()
        self._read_metadata(f)
        result_etr = self._convert()
        result_etr.write(sys.stdout, encoding='utf-8')

    def _make_url_base(self):
        if self._opts.kaino_urls:
            sourcedesc = self._get_source()
            # TODO: Make this more general
            return ('http://kaino.kotus.fi'
                    + (sourcedesc.replace('/meta/', '/teksti/')
                       .replace('_rdf.xml', '.xml')))
        else:
            return None

    def _read_metadata(self, fname):
        if self._opts.kotus_metadata:
            metadata_fname = self._make_metadata_filename(fname)
            # register_namespace does not seem to have an effect, so
            # make a namespace dict of our own
            self._metadata_namespaces = {
                'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                'dc': 'http://purl.org/dc/elements/1.1/',
                'dcterms': 'http://purl.org/dc/terms/',
                'kotus': 'http://www.kotus.fi/'}
            for prefix, uri in self._metadata_namespaces.iteritems():
                et.register_namespace(prefix, uri)
            self._metadata_etr = et.parse(metadata_fname)
        else:
            self._metadata_etr = None

    def _make_metadata_filename(self, f):
        if isinstance(f, basestring):
            fname = f
        else:
            fname = self._opts.filename or getattr(f, 'name', '')
        # FIXME: This is specific to Kotus corpora
        fname_parts = fname.partition('/teksti/')
        metadata_fname_parts = self._get_source().partition('/meta/')
        return (fname_parts[0] + metadata_fname_parts[1]
                + metadata_fname_parts[2])

    def _convert(self):
        text_e = et.Element("text")
        self._add_text_info(text_e)
        self._add_body(text_e)
        self._add_content_newlines(text_e)
        return et.ElementTree(text_e)

    def _add_text_info(self, text_e):
        text_e.set("title", self._get_title())
        text_e.set("distributor", self._get_distributor())
        text_e.set("source", self._get_source())
        if self._metadata_etr:
            # FIXME: Make this more general
            url_prefix = 'http://kaino.kotus.fi'
            author, author_birthyear, author_deathyear = self._get_author_info()
            text_e.set("author", author)
            text_e.set("author_birthyear", author_birthyear)
            text_e.set("author_deathyear", author_deathyear)
            text_e.set("date", self._get_coverage())
            text_e.set("url", url_prefix + self._get_source())
            text_e.set("original_url", self._get_external_link())
            text_e.set("collection_url", url_prefix + self._get_ispartof())
            text_e.set("modified_date", self._get_modified())
            text_e.set("tei_coding_responsible", self._get_tei_responsible())

    def _get_title(self):
        return (self._src_etr.find("teiHeader//title").text.strip()
                or ' '.join(head.text.strip() for head in
                            [self._src_etr.find(".//head[@id='h0']")]
                            + self._src_etr.findall(
                    ".//div[@id='d1']/head[@type='sub']")))

    def _get_distributor(self):
        return ' / '.join([distr.text.strip() for distr in
                           self._src_etr.findall("teiHeader//distributor")])

    def _get_tei_responsible(self):
        return self._src_etr.find("teiHeader//respStmt/name").text.strip()

    def _get_source(self):
        return self._src_etr.find("teiHeader//sourceDesc/p").text.strip()

    def _get_metainfo(self, elemname):
        return self._metadata_etr.find(
            './/' + elemname, namespaces=self._metadata_namespaces).text.strip()

    def _get_author_info(self):
        creator_info = self._metadata_etr.find(
            './/dc:creator', namespaces=self._metadata_namespaces).text.strip()
        name_mo = re.match(r'(.+?)(?: \(|$)', creator_info)
        name = name_mo.group(1) if name_mo else ''
        years_mo = re.search(r'\((\d+)(?:\D+)(\d*)\)', creator_info)
        birth_year, death_year = years_mo.group(1, 2) if years_mo else ('', '')
        return name, birth_year, death_year

    def _get_coverage(self):
        return self._get_metainfo('dc:coverage')

    def _get_language(self):
        return self._get_metainfo('dc:language').lower()

    def _get_modified(self):
        return self._get_metainfo('dcterms:modified')

    def _get_extent(self):
        return self._get_metainfo('dcterms:extent')

    def _get_external_link(self):
        elem = self._metadata_etr.find('.//*[@kotus:type="external_link"]',
                                       namespaces=self._metadata_namespaces)
        if elem is not None:
            return (elem.get('{' + self._metadata_namespaces['rdf'] + '}'
                             + 'resource', '')
                    or '')
        else:
            return ''

    def _get_ispartof(self):
        elem = self._metadata_etr.find('.//dcterms:isPartOf',
                                       namespaces=self._metadata_namespaces)
        if elem is not None:
            return (elem.get('{' + self._metadata_namespaces['kotus'] + '}'
                             + 'metalink', '')
                    or '')
        else:
            return ''

    def _add_body(self, text_e):
        body_roots = self._src_etr.findall(".//text/body")
        text_e.extend([subresult
                       for elem in body_roots
                       for subresult in self._process_body_elem(elem)])

    def _process_body_elem(self, body_e):

        def _process_subelems(result):
            result.text = result.text or ''
            subresults = self._process_subelems(body_e)
            if isinstance(subresults, basestring):
                result.text += subresults
            else:
                result.extend(subresults)

        def _extract_topic(text, key):
            mo = re.search(r' ' + key + '/(\S+)', text)
            return mo.group(1) if mo else ''

        result = None
        id_attr = body_e.get('id', '')
        # print '<' + body_e.tag + " id=" + id_attr
        if body_e.tag in ['s', 'title', 'dateline', 'signed']:
            result = self._make_sentence(body_e)
            if body_e.tag != 's':
                result.set('type', body_e.tag)
        elif body_e.tag == 'w':
            return self._make_word(body_e)
        elif body_e.tag in ['lb', 'pb', 'gap', 'xref']:
            return []
        elif body_e.tag in ['p', 'head', 'opener', 'closer']:
            if self._opts.para_as_sent:
                result = self._make_sentence(body_e)
            else:
                result = et.Element(self._opts.para_elem_name)
                _process_subelems(result)
            if body_e.get('type'):
                topic_and_span = body_e.get('type')
                result.set('topic', _extract_topic(topic_and_span, 'TOPIC'))
                result.set('span', _extract_topic(topic_and_span, 'SPAN'))
            result.set('type', body_e.tag)
        elif body_e.tag == 'div':
            type_ = body_e.get('type', '')
            subresults = self._process_subelems(body_e)
            if not type_:
                return subresults
            else:
                tag = self._divtypemap.get(type_, "div")
                if tag == '':
                    return subresults
                result = et.Element(tag)
                if tag == 'div':
                    result.set('type', type_)
                result.extend(subresults)
                self._add_extra_attrs(result, body_e)
                # print len(result)
        elif body_e.tag in ['body', 'hi']:
            return self._process_subelems(body_e)
        elif body_e.tag == 'entry' and self._opts.mode == 'dictionary':
            return [self._make_dict_entry_sentence(body_e)]
        elif body_e.tag == 'entry' and self._opts.mode == 'sayings':
            return [self._make_sayings_entry(body_e)]
        else:
            result = et.Element(body_e.tag)
            _process_subelems(result)
        result.set('id', id_attr)
        if self._url_base:
            result.set('url', self._url_base + '#' + id_attr)
        self._add_content_newlines(result)
        # print "<<" + result.text + ">>"
        # print '>' + body_e.tag + " id=" + id_attr + " " + result.get('id')
        return [result]

    def _make_sentence(self, elem):
        result = et.Element('sentence')
        if self._opts.words:
            self._process_word_elems(elem, result)
        else:
            self._process_mixed_content(elem, result)
        return result

    def _process_word_elems(self, elem, result):
        result.text = ''.join([self._make_word(subelem)
                               for subelem in elem
                               if subelem.tag == 'w'])

    def _make_word(self, elem):
        lemma_comp_bound = elem.get('lemma', '')
        lemma = ''.join(lemma_comp_bound.split('#'))
        pos = elem.get('type', '')
        msd = elem.get('msd', '').strip()
        msd = pos + (' ' + msd if msd else '')
        if self._opts.fix_msd_tags:
            msd = re.sub(r'\s+', self._opts.msd_separator, msd)
            if self._opts.enclosed_msd:
                msd = self._opts.msd_separator + msd + self._opts.msd_separator
        lemgram = ([self._make_lemgram(lemma, pos)]
                   if self._opts.lemgrams else [])
        return '\t'.join([elem.get('norm', ''), lemma, lemma_comp_bound,
                          pos, msd, elem.get('id', '')] + lemgram) + '\n'

    _lemgram_posmap = {'_': 'xx', # Unspecified
                       'A': 'jj',
                       # AN in the target is not PoS category but a feature,
                       # but we treat it as a category here.
                       'ABBR': 'an',
                       'AD-A': 'ab',
                       'ADV': 'ab',
                       'C': 'kn',
                       'N': 'nn',
                       'NUM': 'rg',
                       'PCP1': 'vb',
                       'PCP2': 'vb',
                       'PP': 'pp',
                       'PSP': 'pp',
                       'PRON': 'pn',
                       'REFL/PRON': 'pn',
                       'PUNCT': 'xx',
                       'V': 'vb'}

    def _make_lemgram(self, lemma, pos):
        return u'|{lemma}..{pos}.1|'.format(
            lemma=lemma, pos=self._lemgram_posmap.get(pos, 'xx'))

    def _process_subelems(self, elem):
        subresults = [subresult
                      for subelem in elem
                      for subresult in self._process_body_elem(subelem)]
        # sys.stderr.write(' '.join([repr(s) for s in subresults]) + '\n')
        subresult_strings = [isinstance(sr, basestring) for sr in subresults]
        if all(subresult_strings):
            return ''.join(subresults)
        elif any(subresult_strings):
            # This happens if w elements not within an s are followed
            # by an s (or vice versa).
            return self._combine_elems_and_text(subresults, 'sentence')
        else:
            return subresults

    def _combine_elems_and_text(self, children, elemtype='sentence'):

        def _add_str_children(elem_children, str_children):
            if str_children:
                new_elem = self._make_text_elem(elemtype, str_children)
                self._add_content_newlines(new_elem)
                elem_children.append(new_elem)

        elem_children = []
        str_children = ''
        for child in children:
            if isinstance(child, basestring):
                str_children += child
            else:
                _add_str_children(elem_children, str_children)
                str_children = ''
                # if str_children:
                #     elem_children.append(_make_text_elem(elemtype,
                #                                          str_children))
                #     str_children = ''
                elem_children.append(child)
        _add_str_children(elem_children, str_children)
        # if str_children:
        #     elem_children.append(_make_text_elem(elemtype, str_children))
        return elem_children

    def _make_text_elem(self, tag, text):
        result = et.Element(tag)
        result.text = text
        return result

    def _process_text(self, elem, result):
        result.text = self._tokenize(self._get_all_text(elem))

    def _process_mixed_content(self, elem, result):
        result.text = self._tokenize(elem.text)
        result.tail = self._tokenize(elem.tail)
        result.attrib = elem.attrib
        self._add_content_newlines(result)
        for subelem in elem:
            subresult = et.Element(subelem.tag)
            self._process_mixed_content(subelem, subresult)
            result.append(subresult)

    def _make_dict_entry_sentence(self, elem):
        result = et.Element('sentence')
        if self._opts.dict_entry_as_posattrs:
            result.text = self._make_dict_entry_as_posattrs(elem)
        else:
            self._make_dict_entry_as_elems(elem, result)
        # print result.text
        self._add_content_newlines(result)
        return result

    def _make_dict_entry_as_posattrs(self, elem):
        entry_info = self._get_dict_entry_info(elem)
        return '\t'.join([entry_info[key]
                          for key in ['form', 'example', 'pos', 'xref',
                                      'etym', 'etymlang', 'note',
                                      'notetype']])

    def _make_dict_entry_as_elems(self, elem, result):
        entry_info = self._get_dict_entry_info(elem)
        for subelem in elem:
            if len(subelem):
                for subsubelem in subelem:
                    if subsubelem.tag == 'q':
                        tag = subelem.tag
                        text = self._tokenize('"' + subsubelem.text.strip()
                                              + '"')
                    else:
                        tag = subsubelem.tag
                        text = self._tokenize(subsubelem.text)
                    add_elem = et.Element('item', subsubelem.attrib)
                    add_elem.set('itemtype', tag)
                    add_elem.text = text
                    self._add_content_newlines(add_elem)
                    result.append(add_elem)
            else:
                add_elem = et.Element('item', subelem.attrib)
                add_elem.set('itemtype', subelem.tag)
                add_elem.text = self._tokenize(subelem.text)
                self._add_content_newlines(add_elem)
                result.append(add_elem)
        if self._opts.dict_info_as_sent_attrs:
            for attr in ['form', 'example', 'pos', 'xref', 'etym', 'etymlang']:
                result.set(attr, entry_info.get(attr, ''))

    def _get_dict_entry_info(self, elem):
        entry_elems = {'form': './form/orth',
                       'example': './eg/q',
                       'pos': './gramGrp/pos',
                       'xref': './xr',
                       'etym': './etym',
                       'etymlang': ('./etym', 'lang'),
                       'note': './note',
                       'notetype': ('./note', 'type')}
        return self._get_entry_info(entry_elems, elem)

    def _get_entry_info(self, entry_elems, elem):
        return dict([(key, self._get_subelem_content(elem, entry_elems[key]))
                     for key in entry_elems.keys()])

    def _get_subelem_content(self, elem, item):
        if isinstance(item, tuple):
            return self._get_subelem_attrs(elem, item[0], item[1])
        else:
            return self._get_subelem_texts(elem, item)

    def _get_subelem_texts(self, elem, findpath):
        return '; '.join([self._get_all_text(subelem).strip()
                          for subelem in elem.findall(findpath)])

    def _get_subelem_attrs(self, elem, findpath, attrname):
        return '; '.join([subelem.get(attrname, '')
                          for subelem in elem.findall(findpath)])

    def _get_all_text(self, elem):
        return ((elem.text or '')
                + ''.join([self._get_all_text(subelem) + subelem.tail
                           for subelem in elem]))

    def _make_sayings_entry(self, elem):
        result = et.Element('entry')
        entry_info = self._get_saying_entry_info(elem)
        result.extend([self._make_sayings_entry_sentence(entry_info[item], item)
                       for item in 'standard', 'dialect', 'usage'
                       if entry_info[item]])
        for attr in entry_info:
            result.set(attr, entry_info[attr])
        self._add_content_newlines(result)
        return result

    def _get_saying_entry_info(self, elem):
        entry_map = {'standard': './form[@type=\'standard\']',
                     'dialect': './form[@type=\'dialect\']',
                     'usage': './usg',
                     'location': './note[@type=\'location\']',
                     'collector': './note[@type=\'collector\']',
                     'date': './note[@type=\'date\']'}
        return self._get_entry_info(entry_map, elem)

    def _make_sayings_entry_sentence(self, text, sent_type):
        result = et.Element('sentence')
        result.text = self._tokenize(text)
        result.set('type', sent_type)
        self._add_content_newlines(result)
        return result

    def _add_extra_attrs(self, result, elem):
        attrs = self._elem_extra_attrs.get(result.tag, {})
        for (attrname, path) in attrs.iteritems():
            result.set(attrname,
                       ' '.join(self._get_subelem_texts(elem, path).split()))

    def _tokenize(self, text):
        text = text or ''
        if self._opts.tokenize:
            text = re.sub(r'([.?!,:])(")', r'\1 \2', text)
            text = re.sub(r'(")([.?!,:])', r'\1 \2', text)
            text = re.sub(r'(\.\.\.)([,:;?!")])', r' \1 \2', text)
            text = re.sub(r'([.,:;?!")]|\.\.\.)([ \n]|\Z)', r' \1\2', text)
            text = re.sub(r'([ \n]|\A)(["(])', r'\1\2 ', text)
        return '\n'.join(text.split()) + '\n'

    def _add_content_newlines(self, elem):
        elem.text = self._add_lead_trail_newline(elem.text)
        elem.tail = self._add_lead_trail_newline(elem.tail)

    def _add_lead_trail_newline(self, s):
        s = (s.strip() or '\n') if s else '\n'
        if s[0] != '\n':
            s = '\n' + s
        if s[-1] != '\n':
            s += '\n'
        return s


def getopts():
    optparser = OptionParser()
    optparser.add_option('--mode', '-m', type='choice',
                         choices=['sentences', 'statute', 'dictionary',
                                  'stories', 'statute-modern', 'sayings'],
                         default='sentences')
    optparser.add_option('--words', action='store_true', default=False)
    optparser.add_option('--lemgrams', action='store_true', default=False)
    optparser.add_option('--tokenize', action='store_true', default=False)
    optparser.add_option('--para-as-sent', '--paragraph-as-sentence',
                         action='store_true', default=False)
    optparser.add_option('--dict-entry-as-posattrs',
                         '--dictionary-entry-as-positional-attributes',
                         action='store_true', default=False)
    optparser.add_option('--dict-info-as-sent-attrs',
                         '--dictionary-information-as-sentence-attributes',
                         action='store_true', default=False)
    optparser.add_option('--msd-separator', '--morpho-tag-separator',
                         default=u':')
    optparser.add_option('--enclosed-msd', '--enclosed-morpho-tags',
                         action='store_true', default=False)
    optparser.add_option('--para-elem-name', '--paragraph-element-name',
                         default=u'para')
    optparser.add_option('--no-fix-msd-tags', '--no-fix-morpho-tags',
                         action='store_false', dest='fix_msd_tags',
                         default=True)
    # FIXME: Make the following two option names more general
    optparser.add_option('--kaino-urls', action='store_true')
    optparser.add_option('--kotus-metadata', action='store_true')
    optparser.add_option('--filename')
    (opts, args) = optparser.parse_args()
    return (opts, args)


def main():
    divtypemaps = {'statute': {'artikla': 'article', u'pykälä': 'paragraph'},
                   'sentences': {'main': ''},
                   'dictionary': {},
                   'stories': {'collection': 'collection', 'story': 'story'},
                   'statute-modern': {'main': ''}}
    elem_extra_attrs = {'stories': {'collection': {'title': './head'},
                                    'story': {'title': './head'}}}
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    # ElementTree.XMLParser uses the encoding specified in the XML
    # header, so we should not modify it here.
    # sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    # sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    converter = Converter(opts, divtypemap=divtypemaps.get(opts.mode, {}),
                          elem_extra_attrs=elem_extra_attrs.get(opts.mode, {}))
    converter.process_input(args[0] if args else sys.stdin)


if __name__ == "__main__":
    main()
