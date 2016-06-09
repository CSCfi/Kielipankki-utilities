#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""
Convert ELFA TEI data to VRT
"""


import sys
import re

from lxml import etree

import korpimport.util


class VrtData(list):

    def __init__(self):
        super(VrtData, self).__init__()
        self._struct_stack = []

    def open_struct(self, name, attrs):
        self._struct_stack.append(name)
        self.append([self.make_starttag(name, attrs)])

    def make_starttag(self, name, attrs):
        try:
            attrs = attrs.iteritems()
        except AttributeError:
            pass
        return ('<' + name + ' '
                + ' '.join(u'{0}="{1}"'
                           .format(attrname,
                                   re.sub(r'\s+', ' ',
                                          attrval.replace('"', '&quot;')))
                           for attrname, attrval in attrs)
                + '>')

    def close_struct(self, name=None):
        if name and self._struct_stack and name != self._struct_stack[-1]:
            return
        name = self._struct_stack.pop()
        self.append([self.make_endtag(name)])

    def make_endtag(self, name):
        return '</' + name + '>'

    def close_all_structs(self):
        while self._struct_stack:
            self.close_struct()

    def serialize(self):
        for line in self:
            # print line
            yield '\t'.join(line) + '\n'


class ElfaToVrtConverter(korpimport.util.InputProcessor):

    _xml_ns = 'http://www.w3.org/XML/1998/namespace'
    _xml_id = '{' + _xml_ns + '}id'
    _namespaces = {'t': 'http://www.tei-c.org/ns/1.0',
                   'xml': _xml_ns}
    _text_attr_xpath = [
        ('id', '/t:TEI/@xml:id'),
        ('title', '//t:titleStmt/t:title/text()'),
        ('publisher', '//t:publicationStmt/t:publisher/text()'),
        ('notes', '//t:notesStmt/t:note/text()'),
        ('duration_iso', '//t:sourceDesc//t:recording/@dur'),
        ('date', '//t:creation/t:date/@when'),
        ('event_type', '//t:textDesc/t:channel/text()'),
        ('domain', '//t:textDesc/t:domain/@type'),
        ('discipline', '//t:textDesc/t:domain/text()'),
        ('interaction_degree', '//t:textDesc/t:interaction/@type'),
        ('num_participants',
         '//t:textDesc/t:interaction/t:num[@type="participants"]/text()'),
        ('num_speakers',
         '//t:textDesc/t:interaction/t:num[@type="speakers"]/text()'),
        ('preparedness', '//t:textDesc/t:preparedness/@type'),
        ('event_purpose', '//t:textDesc/t:purpose/@type'),
    ]
    _speaker_attr_xpath = [
        ('speaker_id', '@xml:id'),
        ('speaker_role', '@role'),
        ('speaker_sex', 't:sex/text()'),
        ('speaker_age', 't:age/text()'),
        ('speaker_l1', './/t:langKnown/@tag'),
        ('speaker_type', 't:p/text()'),
    ]
    _speaker_type_map = {
        '' : 'identified',
        'several simultaneous speakers' : 'several',
        'unidentified speaker' : 'unidentified',
    }
    _file_id_expansion = {
        'recording_type': {
            'U': 'university degree programme',
            'C': 'conference',
        },
        'event_type': {
            'SEMP': 'seminar presentation',
            'SEMD': 'seminar discussion',
            'LEC': 'monologic lecture',
            'LECD': 'lecture discussion',
            'DEFP': 'doctoral thesis defence presentation',
            'DEFD': 'doctoral thesis defence discussion',
            'PRE': 'conference presentation',
            'DIS': 'discussion following paper',
            'PLE': 'conference plenary',
            'OTH': 'other event',
        }
    }

    def __init__(self):
        super(ElfaToVrtConverter, self).__init__()
        # TODO: Add an option to enable or disable this
        self._break_utterances = True
        if self._break_utterances:
            self._sentence_break = ['<SENTENCE_BREAK>']
            self._utterance_struct = 'paragraph'
        else:
            self._sentence_break = []
            self._utterance_struct = 'sentence'

    def process_input_stream(self, stream, filename=None):
        # print 'FILE', filename
        self._filename = filename
        self._tei_tree = etree.parse(stream).getroot()
        self._text_id = None
        self._utterance_id = ''
        self._text_attrs = []
        self._speakers = {}
        self._incident_count = 0
        self._pause_count = 0
        self._elemstack = []
        self._mode = 'speaking'
        self._voice = 'normal'
        self._vrt = VrtData()
        self._construct_vrt()
        self._output_vrt()

    def _construct_vrt(self):
        self._extract_text_attrs()
        self._vrt.open_struct('text', self._text_attrs)
        self._extract_participants()
        self._extract_utterances()
        self._vrt.close_all_structs()

    def _xpath(self, xpath, root=None):
        if root is None:
            root = self._tei_tree
        return root.xpath(xpath, namespaces=self._namespaces)

    def _xpath_str(self, xpath, root=None, joiner='; '):
        return joiner.join(val.strip() for val in self._xpath(xpath, root))

    def _xpath_text(self, xpath, root=None, default=''):
        elems = self._xpath(xpath, root)
        if elems:
           return ''.join(elem.text + elem.tail for elem in elems)
        else:
            return default

    def _xpath_first(self, xpath, root=None, default=None):
        elems = self._xpath(xpath, root)
        return elems[0] if elems else default

    def _tagname(self, elem):
        return elem.tag.rpartition('}')[2]

    def _extract_text_attrs(self):
        duration_iso = ''
        for attr, xpath in self._text_attr_xpath:
            self._text_attrs.append((attr, self._xpath_str(xpath)))
            if attr == 'id':
                self._text_id = self._text_attrs[-1][1]
            if attr == 'duration_iso':
                duration_iso = self._text_attrs[-1][1]
        for attrname, formatspec in [('duration_minsec', '{min}:{minsec:02d}'),
                                     ('duration_sec', '{sec}')]:
            self._text_attrs.append(
                (attrname, self._convert_duration(duration_iso, formatspec)))
        self._expand_file_id_attrs(self._text_id)

    def _expand_file_id_attrs(self, fileid):
        mo = re.match(r'([CU])([A-Z]+)([0-9][0-9])([0A-Z])$', fileid)
        if mo:
            # Event type is taken from the file header
            for groupnum, attrname in [(1, 'recording_type'),
                                       # (2, 'event_type'),
                                       (3, 'event_num'),
                                       (4, 'event_part')]:
                val = mo.group(groupnum)
                if attrname in self._file_id_expansion:
                    attrval = self._file_id_expansion[attrname].get(val, val)
                else:
                    attrval = val
                self._text_attrs.append((attrname, attrval))

    def _convert_duration(self, iso_duration, formatspec):
        mo = re.match(r'PT(?:(?P<min>\d+)M)?(?P<minsec>\d+)S', iso_duration)
        valdict = mo.groupdict(default='0')
        for key in valdict:
            valdict[key] = int(valdict[key])
        valdict['sec'] = valdict['min'] * 60 + valdict['minsec']
        return formatspec.format(**valdict)

    def _extract_participants(self):
        for person in self._xpath('//t:listPerson/t:person'):
            speaker = {}
            for attr, xpath in self._speaker_attr_xpath:
                speaker[attr] = self._xpath_str(xpath, person, joiner='|')
                if '|' in speaker[attr]:
                    speaker[attr] = '|' + speaker[attr] + '|'
                if attr == 'speaker_type':
                    speaker[attr] = self._speaker_type_map.get(speaker[attr],
                                                               '')
                if speaker[attr] == '':
                    speaker[attr] = 'unknown'
            self._speakers[speaker['speaker_id']] = speaker

    def _extract_utterances(self):
        elem_handlers = {
            'u': self._append_utterance,
            'incident': self._append_incident,
            'pause': self._append_pause,
        }
        for utterance in self._xpath('//t:text/t:body/*'):
            tagname = self._tagname(utterance)
            if tagname in elem_handlers:
                elem_handlers[tagname](utterance)
            else:
                sys.stderr.write('Unrecognized element in body: {0}\n'
                                 .format(tagname))

    def _append_utterance(self, utterance):
        speaker_id = utterance.get('who', '').strip('#')
        tokens = []
        self._utterance_id = utterance.get(self._xml_id, '')
        attrs = {'id': self._utterance_id, 'type': 'utterance'}
        attrs.update(self._speakers.get(speaker_id, {}))
        tokens = self._make_fragment_tokens(utterance)
        self._append_sentence(tokens, attrs)

    def _make_fragment_tokens(self, fragment, **kwargs):
        # print fragment, fragment.attrib
        tokens = []
        tokens.extend(self._make_tokens(fragment.text, **kwargs))
        for elem in fragment:
            # print '  ', elem, elem.attrib
            self._elemstack.append(self._tagname(elem))
            tokens.extend(self._make_elem_tokens(elem))
            self._elemstack.pop()
            tokens.extend(self._make_tokens(elem.tail, **kwargs))
        return tokens

    def _make_tokens(self, text, **kwargs):
        text = (text or '').strip()
        if text:
            return [self._make_token(token, **kwargs)
                    for token in text.split()]
        else:
            return []

    def _make_token(self, token, token_type='word', token_subtype='',
                    span_id=''):
        if token_type == 'word':
            if token in ['er', 'erm', 'mhm', 'ah']:
                token_type = 'hesitation'
            elif token in ['mhm-hm', 'uh-huh']:
                token_type = 'backchannel'
            elif token[-1] == '-':
                token_subtype = 'unfinished'
        span_id = span_id or self._utterance_id
        voice = self._voice if token_type in ['word', 'voice_shift'] else ''
        return [token, token_type, token_subtype, span_id, self._mode, voice,
                (('|' + '|'.join(self._elemstack) + '|') if self._elemstack
                 else '|' )]

    def _make_elem_tokens(self, elem):
        tagname = self._tagname(elem)
        return getattr(self, '_make_elem_tokens_' + tagname,
                       self._make_elem_tokens_default)(elem)

    def _make_elem_tokens_default(self, elem):
        tagname = self._tagname(elem)
        if elem.text:
            return (
                [self._make_token(self._make_tag_text(tagname),
                                  token_type=tagname, token_subtype='begin')]
                + self._make_fragment_tokens(elem, token_subtype=tagname)
                + [self._make_token(self._make_endtag_text(tagname),
                                    token_type=tagname, token_subtype='end')])
        else:
            return [self._make_token(self._make_tag_text(tagname),
                                     token_type=tagname)]

    def _make_tag_text(self, text, *attrs):
        return '<' + ' '.join([text.upper()] + list(attrs)) + '>'

    def _make_endtag_text(self, text):
        return '</' + text.upper() + '>'

    def _make_tagged_text(self, text, content, *attrs):
        return ('<' + ' '.join([text.upper()] + list(attrs)) + '>'
                + content + '</' + text.upper() + '>')

    def _make_elem_tokens_pause(self, elem, breaks=True):
        pause_length = elem.get('type') or elem.get('dur')
        sent_break = ([self._sentence_break]
                      if self._break_utterances and breaks else [])
        maybe_sent_break = []
        if pause_length == 'P2-3sec':
            token_text = ','
        elif pause_length == 'P3-4sec':
            token_text = '.'
            maybe_sent_break = sent_break
        else:
            mo = re.match('PT(\d+)S', pause_length)
            if mo:
                pause_length = mo.group(1)
            token_text = self._make_tag_text('P:', pause_length)
            maybe_sent_break = sent_break
        # Should we also add a break before the pause?
        return [self._make_token(token_text, 'pause')] + maybe_sent_break

    def _make_elem_tokens_gap(self, elem):
        return [self._make_token('(xx)', 'unclear')]

    def _make_elem_tokens_name(self, elem):
        name = elem.get('ref', 'unknown').strip('#')
        return [self._make_token(self._make_tag_text('NAME', name), 'name',
                                 token_subtype='anonymized_name')]

    def _make_elem_tokens_anchor(self, elem):
        synch_info = self._get_synch_info(elem)
        synch_info['type'] = 'anchor'
        return [[self._vrt.make_starttag('synch', synch_info)],
                self._make_token(
                    self._make_tagged_text(
                        synch_info['speaker_id'].split('_')[1],
                        synch_info['content']),
                    'backchannel'),
                [self._vrt.make_endtag('synch')]]

    def _get_synch_info(self, elem):
        id_ = elem.get(self._xml_id)
        # print id_
        synch_cond = '@synch="#' + id_ + '"'
        synch_attr = elem.get('synch')
        if synch_attr:
            synch_cond = (
                '@xml:id="' + synch_attr.strip('#')
                + '" or (@synch="' + synch_attr + '"'
                + ' and @xml:id!="' + id_ + '")')
        else:
            synch_cond = '@synch="#' + id_ + '"'
        synch_elems = self._xpath('//t:body//*[' + synch_cond + ']')
        # print '//t:body//*[' + synch_cond + ']', synch_elems
        # print synch_elem.tag, repr(synch_elem.text.strip()), synch_elem.attrib
        speaker_id = (
            ' | '.join(
                self._xpath_first('ancestor-or-self::t:u/@who',
                                  synch_elem).strip('#')
                for synch_elem in synch_elems))
        # print self._xpath('.//t:seg', synch_elem)
        synch_content = (
            ' | '.join(
                ' '.join(token[0] for token in
                         self._make_fragment_tokens(synch_elem)
                         if token != self._sentence_break)
                for synch_elem in synch_elems))
        # FIXME: For the first overlapping span (without a synch
        # attribute), the synch id should contain the ids of the seg
        # elements referring to it in their synch attributes
        return {'id': id_,
                'speaker_id': speaker_id,
                'content': synch_content}

    def _make_elem_tokens_seg(self, elem):
        synch_info = self._get_synch_info(elem)
        synch_info['type'] = 'overlap'
        tokens = ([[self._vrt.make_starttag('synch', synch_info)],
                   self._make_token('[', token_type='overlap_begin')]
                  + self._make_fragment_tokens(elem, token_subtype='overlap',
                                               span_id=synch_info['id'])
                  + [self._make_token(']', token_type='overlap_end'),
                     [self._vrt.make_endtag('synch')]])
        # print 'seg', tokens
        return tokens

    def _make_elem_tokens_shift(self, elem):
        voice_text_map = {'laugh': '@',
                          'whisp': 'whispering',
                          'mutter': 'muttering'}
        prev_voice = self._voice
        new_voice = elem.get('new') or 'normal'
        shift_type = 'begin' if new_voice != 'normal' else 'end'
        # if new_voice == 'laugh' or prev_voice == 'laugh':
        #     token_text = '@'
        if shift_type == 'begin':
            token_text = self._make_tag_text(
                voice_text_map.get(new_voice, new_voice))
        else:
            token_text = self._make_endtag_text(
                voice_text_map.get(prev_voice, prev_voice))
        if shift_type == 'begin':
            self._voice = new_voice
        token = [self._make_token(token_text, token_type='voice_shift',
                                  token_subtype=shift_type)]
        self._voice = new_voice
        return token

    def _make_elem_tokens_unclear(self, elem):
        return (
            [self._make_token('(', token_type='unclear', token_subtype='begin')]
            + self._make_fragment_tokens(elem, token_subtype='unclear')
            + [self._make_token(')', token_type='unclear',
                                token_subtype='end')])

    def _make_elem_tokens_vocal(self, elem):
        descr = elem[0].text
        if descr == 'LAUGH':
            token_text = '@@'
        else:
            token_text = self._make_tag_text(descr)
        return [self._make_token(token_text, descr.lower())]

    def _make_elem_tokens_writing(self, elem):
        prev_mode = self._mode
        self._mode = elem.get('type')
        tokens = (
            [self._make_token(self._make_tag_text(self._mode),
                              token_type='mode_shift', token_subtype='begin')]
            + self._make_fragment_tokens(elem)
            + [self._make_token(self._make_endtag_text(self._mode),
                                token_type='mode_shift', token_subtype='end')])
        self._mode = prev_mode
        return tokens

    def _make_elem_tokens_incident(self, elem, breaks=True):
        descr = self._xpath_first('t:desc/text()', elem)
        sent_break = ([self._sentence_break]
                      if self._break_utterances and breaks else [])
        return (sent_break
                + [self._make_token(self._make_tag_text(descr), 'incident')]
                + sent_break)

    def _append_incident(self, incident):
        self._incident_count += 1
        self._append_sentence(
            self._make_elem_tokens_incident(incident, breaks=False),
            {'id': (self._text_id + '_i{0:03d}'.format(self._incident_count)),
             'type': 'incident'})

    def _append_pause(self, pause):
        self._pause_count += 1
        self._append_sentence(
            self._make_elem_tokens_pause(pause, breaks=False),
            {'id': (self._text_id + '_p{0:03d}'.format(self._pause_count)),
             'type': 'pause'})

    def _append_sentence(self, tokens, attrs):
        self._vrt.open_struct(self._utterance_struct,
                              self._make_sentence_attrs(attrs))
        self._append_sentence_tokens(tokens, attrs)
        self._vrt.close_struct(self._utterance_struct)

    def _make_sentence_attrs(self, attrs):
        return attrs

    def _append_sentence_tokens(self, tokens, attrs):

        def open_sentence(sentnr):
            self._vrt.open_struct(
                'sentence', {'id': attrs['id'] + '_s{0:d}'.format(sentnr)})

        if self._break_utterances:
            last_tokennr = len(tokens) - 1
            sentnr = 1
            in_synch = False
            open_sentence(sentnr)
            prev_is_break = True
            # print tokens
            for tokennr, token in enumerate(tokens):
                if token == self._sentence_break:
                    if prev_is_break or tokennr == last_tokennr or in_synch:
                        continue
                    if tokennr != 0:
                        self._vrt.close_struct('sentence')
                    open_sentence(sentnr)
                    prev_is_break = True
                    sentnr += 1
                else:
                    if token[0].startswith('<synch'):
                        in_synch = True
                    elif token[0] == '</synch>':
                        in_synch = False
                    self._vrt.append(token)
                    prev_is_break = False
            self._vrt.close_struct('sentence')
        else:
            self._vrt.extend(token for token in tokens
                             if token != self._sentence_break)

    def _output_vrt(self):
        for line in self._vrt.serialize():
            sys.stdout.write(line)


if __name__ == "__main__":
    ElfaToVrtConverter().run()
