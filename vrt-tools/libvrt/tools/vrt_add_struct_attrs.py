#! /usr/bin/env python3
# -*- mode: Python; -*-


"""
vrt_add_struct_attrs.py

The actual implementation of vrt-add-struct-attrs.

Please run "vrt-add-struct-attrs -h" for more information.
"""


import re
import sys

from collections import OrderedDict

from libvrt.metaline import mapping, starttag
from vrtargsoolib import InputProcessor


class TsvReader:

    """Read from a binary tab-separated values file, optionally with a
    column headers.

    By default, convert the characters <>&" to the corresponding XML
    predefined entities.

    This tries to be somewhat compatible with csv.DictReader, which does
    not support reading from a binary file, which is faster.
    """

    entities = dict((spec[0].encode(), ('&' + spec[1:] + ';').encode())
                    for spec in '<lt >gt &amp "quot'.split())

    def __init__(self, infile, fieldnames=None, entities=True):
        self._infile = infile
        self.fieldnames = fieldnames
        self._entities = entities
        self.line_num = 0

    def __next__(self):
        if self.fieldnames is None:
            self.fieldnames = self._read_fields()
        fieldvals = self._read_fields()
        return OrderedDict(zip(self.fieldnames, fieldvals))

    def _read_fields(self):

        def encode_entities(line):
            return re.sub(rb'([<>"]|&(?!(?:lt|gt|amp|quot);))',
                          lambda mo: self.entities[mo.group(1)],
                          line)

        line = self._infile.readline()
        if not line:
            raise StopIteration
        self.line_num += 1
        if self._entities:
            line = encode_entities(line)
        return line[:-1].split(b'\t')

    def read_fieldnames(self):
        if self.fieldnames is None:
            try:
                self.fieldnames = self._read_fields()
            except StopIteration:
                pass
        return self.fieldnames


class StructAttrAdder(InputProcessor):

    DESCRIPTION = """
    Add structural attribute annotations to VRT data from a TSV file.
    Either (1) the TSV file can have the same number of data rows as the VRT
    data has structural attributes of the specified kind, in which case
    values for the nth structural attribute are added from the nth data row of
    the data file, or (2) one or more attributes may be specified as a key,
    in which case values are added from the last data row matching the key
    attribute values in the structural attribute.
    """

    ARGSPECS = [
        ('--structure|element|e=STRUCT "text" -> struct_name',
         'Add attributes (annotations) to structures STRUCT.'),
        ('--data-file=FILENAME',
         'Add annotations from the TSV data file FILENAME.',
         dict(required=True)),
        ('--attributes=ATTRLIST -> attr_names',
         """Add attributes (annotations) listed in space-separated ATTRLIST,
         corresponding to the columns (fields) of the TSV data file. If not
         specified, the first row of the TSV file is considered as a heading
         listing the attribute names. If an attribute named in ATTRLIST
         already exists in the VRT, check that its value is the same than in
         the TSV file, unless --overwrite lists the attribute.
         """),
        ('--overwrite=ATTRLIST -> overwrite_attrs',
         """Overwrite the possibly existing values of attributes listed in
         space-separated ATTRLIST, instead of warning if their values differ
         and keeping the existing value.
         """),
        ('--key=ATTRLIST -> key_attrs',
         """Use the attributes listed in space-separated ATTRLIST as a key:
         when their values in a VRT structure match those of a row in a data
         file, add the remaining attributes in the data file to the VRT.
         If the data file does not contain values for a key in the VRT, empty
         strings are added as attribute values.
         Note that this option implies reading the entire data file into
         memory, so use with caution for very large data files.
         """),
    ]

    def __init__(self):
        super().__init__()

    def main(self, args, inf, ouf):

        LESS_THAN = '<'.encode()[0]
        overwrite_attrs = set(name.encode()
                              for name in (args.overwrite_attrs or '').split())
        key_attrs = args.key_attrs
        if key_attrs:
            key_attrs = tuple(name.encode() for name in key_attrs.split())
        if args.attr_names:
            args.attr_names = [name.encode()
                               for name in args.attr_names.split()]
        struct_name = args.struct_name.encode()
        struct_begin_alts = tuple(b'<' + struct_name + endchar
                                  for endchar in [b' ', b'>'])
        new_attr_names = None
        new_attr_values = {}

        def read_keyed_data(tsv_reader):
            missing_key_attrs = [attr for attr in key_attrs
                                 if attr not in new_attr_names]
            if missing_key_attrs:
                plural = len(missing_key_attrs) > 1
                self.error_exit(
                    ('Key attribute{s} {attrs} {do} not exist in'
                     ' {datafile}').format(
                         s='s' if plural else '',
                         attrs=', '.join(attr.decode()
                                         for attr in missing_key_attrs),
                         do='do' if plural else 'does',
                         datafile=args.data_file))
            attrs = {}
            while attrs is not None:
                attrs = next(tsv_reader, None)
                if attrs is None:
                    break
                key = tuple(attrs[attrname] for attrname in key_attrs)
                if key in new_attr_values:
                    self.warn(
                        ('Duplicate value for key {key} on line {dataline} of'
                         ' {datafile} overrides previous value on line'
                         ' {dataline_prev}').format(
                             key=tuple(val.decode() for val in key),
                             dataline=tsv_reader.line_num,
                             datafile=args.data_file,
                             dataline_prev=new_attr_values[key][1]))
                new_attr_values[key] = (attrs, tsv_reader.line_num)

        def get_add_attrs_ordered(tsv_reader, line, attrs, linenr):
            add_attrs = next(tsv_reader, None)
            if add_attrs is None:
                # If the data file is too short, output the rest of the
                # VRT as is and exit with error
                ouf.write(line)
                for line in inf:
                    ouf.write(line)
                self.error_exit(
                    ('Data file {datafile} has fewer data lines'
                     ' ({numlines}) than the input VRT has {struct}'
                     ' structures').format(
                         datafile=args.data_file,
                         numlines=(tsv_reader.line_num -
                                   int(args.attr_names is None)),
                         struct=args.struct_name))
            return add_attrs, tsv_reader.line_num

        def get_add_attrs_keyed(tsv_reader, line, attrs, linenr):
            try:
                key = tuple(attrs[key_attr] for key_attr in key_attrs)
            except KeyError:
                missing_keys = tuple(
                    key_attr.decode() for key_attr in key_attrs
                    if key_attr not in attrs)
                self.warn(
                    ('No key attribute{s} {missing_keys} on line {vrtline} of'
                     ' VRT input').format(
                         s=('s' if len(missing_keys) > 1 else ''),
                         missing_keys=', '.join(missing_keys),
                         vrtline=linenr))
                return (None, None)
            add_attrs = None
            if key in new_attr_values:
                return new_attr_values[key]
            else:
                self.warn(
                    ('No data for key {key} in {datafile} on VRT line'
                     ' {vrtline}; using empty values').format(
                         key=tuple(val.decode() for val in key),
                         datafile=args.data_file,
                         vrtline=linenr))
                return (OrderedDict((attrname, attrs[attrname]
                                     if attrname in key_attrs else b'')
                                    for attrname in tsv_reader.fieldnames),
                        -1)

        def add_attributes(line, attrs, add_attrs, linenr, tsv_line_num,
                           check_overlap_attrs):
            if tsv_line_num != -1:
                for overlap_attr in check_overlap_attrs:
                    if (overlap_attr in attrs.keys()
                            and add_attrs[overlap_attr] != attrs[overlap_attr]):
                        self.warn(
                            ('Values for attribute {attr} differ on'
                             ' line {dataline} of {datafile} and'
                             ' line {vrtline} of VRT input').format(
                                 attr=overlap_attr.decode(),
                                 dataline=tsv_line_num,
                                 datafile=args.data_file,
                                 vrtline=linenr))
                        # In case of conflict, the existing value is kept
                        add_attrs[overlap_attr] = attrs[overlap_attr]
            for attrname, attrval in add_attrs.items():
                # This is redundant for the attributes that are for checking
                # value equality only, but is this faster anyway?
                attrs[attrname] = attrval
            return starttag(struct_name, attrs)

        def process_input(inf, get_add_attrs, tsv_reader, new_attr_names):
            """Process VRT input from inf.

            Use function get_add_attrs to get the attributes to be
            added, reading TSV data with tsv_reader, with new
            attribute names new_attr_names.
            """
            check_overlap_attrs = new_attr_names - overwrite_attrs
            linenr = 0
            for line in inf:
                linenr += 1
                if line[0] == LESS_THAN and line.startswith(struct_begin_alts):
                    attrs = mapping(line)
                    add_attrs, tsv_linenr = get_add_attrs(
                        tsv_reader, line, attrs, linenr)
                    if add_attrs:
                        line = add_attributes(
                            line, attrs, add_attrs, linenr, tsv_linenr,
                            check_overlap_attrs)
                ouf.write(line)

        get_add_attrs = (
            get_add_attrs_keyed if key_attrs else get_add_attrs_ordered)
        with open(args.data_file, 'rb') as attrf:
            tsv_reader = TsvReader(attrf, fieldnames=args.attr_names,
                                   entities=True)
            if not args.attr_names:
                tsv_reader.read_fieldnames()
            new_attr_names = set(tsv_reader.fieldnames or [])
            if key_attrs:
                read_keyed_data(tsv_reader)
            process_input(inf, get_add_attrs, tsv_reader, new_attr_names)
