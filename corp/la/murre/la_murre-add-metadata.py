#! /usr/bin/env python
# -*- coding: utf-8 -*-


# Extract and add extra metadata attributes to VRT text and paragraph
# elements from IMDI metadata files.
#
# Usage: $progname imdi_dir < input.vrt > output.vrt
#
# The script takes the metadata from the file imdi_dir/FILENAME.imdi
# for each <text> element in input.vrt containing the attribute
# filename="FILENAME". It adds to the <text> element values for
# attributes describing the whole text (interview): date,
# session_descr, project_descr, content_descr, source_id. If
# <paragraph> elements contain the attribute speaker="NN", the script
# adds to them speaker information attributes: speaker_name,
# speaker_age, speaker_sex, speaker_birthdate, speaker_descr,
# speaker_role.


import sys
import re
import codecs
import os.path
import lxml.etree as et

from xml.sax.saxutils import escape


class Metadata(object):

    _session_info_keys = [
        ('date', 'Date'),
        ('session_descr', 'Description'),
        ('project_descr', '/Project/Description'),
        ('content_descr', '/Content/Description'),
        ('source_id', '/Resources/Source/Id'),
    ]
    _actor_info_keys = [
        ('speaker_name', 'Name'),
        ('speaker_age', 'Age'),
        ('speaker_sex', 'Sex'),
        ('speaker_birthdate', 'BirthDate'),
        ('speaker_descr', 'Description'),
        ('speaker_role', 'Role')
    ]

    def __init__(self, fname=None):
        self._session_data = []
        self._actor_data = {}
        if fname:
            self._extract_from(fname)

    def _extract_from(self, fname):

        def extract_text(etr, path):
            return etr.findtext(add_any_ns(path)).strip()

        def add_any_ns(path):
            return re.sub(r'(^|/)(\w)', r'\1{*}\2', path)

        etr = et.parse(fname)
        for key, path in self._session_info_keys:
            value = extract_text(etr, '//Session/' + path)
            if key == 'session_descr':
                value = re.sub(r'\s+\(.*\)', '', value)
            self._session_data.append((key, value))
        for actor in etr.iterfind(add_any_ns('//Session//Actor')):
            this_actor_data = []
            for key, path in self._actor_info_keys:
                value = extract_text(actor, path)
                if value == 'Unspecified':
                    value = ''
                if path == 'Sex':
                    value = value.lower()
                this_actor_data.append((key, value))
            actor_name = extract_text(actor, 'Name')
            self._actor_data[actor_name] = this_actor_data

    def get_session_data(self):
        return self._session_data

    def get_actor_data_all(self):
        return self._actor_data

    def get_actor_data(self, actor_name):
        return self._actor_data.get(actor_name)


class MetadataAdder(object):

    _quote_escapes = {'"': '&quot;', '\'': '&apos;'}

    def __init__(self, metadata_dir=''):
        self._metadata_dir = metadata_dir

    def add_metadata(self, infile):
        filename = None
        speaker = None
        speaker_map = {}
        metadata = None
        for line in infile:
            if line.startswith('<text '):
                filename = self._find_attrval('filename', line)
                metadata = self._extract_metadata(filename)
                if metadata:
                    line = self._add_xml_attrs(
                        line, metadata.get_session_data())
                    speaker_map = self._make_speaker_map(
                        metadata, self._find_attrval('info', line))
            elif metadata and line.startswith('<paragraph '):
                speaker = self._find_attrval('speaker', line)
                actor_data = metadata.get_actor_data(speaker_map.get(speaker))
                if actor_data:
                    line = self._add_xml_attrs(line, actor_data)
            sys.stdout.write(line)

    def _extract_metadata(self, fname):
        return Metadata(os.path.join(self._metadata_dir, fname + '.imdi'))

    def _find_attrval(self, attrname, line):
        mo = re.search(r'\s' + attrname + r'\s*=\s*(".*?"|\'.*?\')', line)
        if mo:
            return mo.group(1)[1:-1]
        else:
            return None

    def _make_speaker_map(self, metadata, info):
        speaker_map = {}
        # print info
        if info:
            role_info = [[code for code in role.split(':')[-1].split(u'§')
                          if code != '0'] for role in info.split()]
            # print repr(role_info)
            speaker_map.update(dict(
                [(code, code.upper()) for role in role_info for code in role]))
            if len(role_info[0]) == 1:
                speaker_map['h'] = role_info[0][0]
            for inum, interviewer in enumerate(role_info[0]):
                speaker_map['h' + str(inum + 1)] = interviewer.upper()
        else:
            actors_data = metadata.get_actor_data_all()
            for actor_name, actor_data in actors_data.iteritems():
                speaker_map[actor_name.lower()] = actor_name
                if filter(lambda item: item == ('speaker_role', 'Interviewer'),
                          actor_data):
                    speaker_map['h'] = actor_name
        # print repr(speaker_map)
        return speaker_map

    def _add_xml_attrs(self, line, attrs):
        return re.sub(r'(>\s*)$', ' ' + self._make_xml_attrs(attrs) + r'\1',
                      line)

    def _make_xml_attrs(self, attrs):
        return u' '.join([name + '="' + escape(val, self._quote_escapes) + '"'
                          for name, val in attrs])


def main():
    sys.stdin = codecs.getreader('utf-8')(sys.stdin)
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    adder = MetadataAdder(sys.argv[1])
    adder.add_metadata(sys.stdin)


if __name__ == '__main__':
    main()
