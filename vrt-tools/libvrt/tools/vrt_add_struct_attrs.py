#! /usr/bin/env python3
# -*- mode: Python; -*-


"""
vrt_add_struct_attrs.py

The actual implementation of vrt-add-struct-attrs.

Please run "vrt-add-struct-attrs -h" for more information.
"""


# TODO:
# - Support specifying attribute-specific default values for the case
#   when no key is found in the input


import re
import sys

from collections import OrderedDict

from libvrt.argtypes import attrlist, attr_value
from libvrt.iterutils import find_duplicates
from libvrt.metaline import mapping, starttag
from libvrt.tsv import TsvReader, EncodeEntities
from vrtargsoolib import InputProcessor


class StructAttrAdder(InputProcessor):

    DESCRIPTION = """
    Add structural attribute annotations to VRT data from a TSV file (with
    --data-file) or with a fixed value (--fixed) or both.
    When using --data-file, either (1) the TSV file can have the same number
    of data rows as the VRT
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
         'Add attributes (annotations) from the TSV data file FILENAME.'),
        ('--fixed=ATTR:attr_value',
         """Add attribute ATTR with the same fixed value VALUE for all
         structures. If also --data-file is used, ATTR may not be one
         of the attributes in the TSV file. ATTR and VALUE may be
         separated by either "=" or ":"; spaces around ATTR are
         removed but kept around VALUE. This option can be repeated
         with different ATTRs.
         """,
         dict(action='append',
              metavar='ATTR=VALUE')),
        ('--attributes=ATTRLIST:attrlist -> attr_names',
         """Add attributes (annotations) listed in ATTRLIST (separated by
         spaces or commas),
         corresponding to the columns (fields) of the TSV data file. If not
         specified, the first row of the TSV file is considered as a heading
         listing the attribute names. If an attribute named in ATTRLIST
         already exists in the VRT, check that its value is the same than in
         the TSV file, unless --overwrite lists the attribute.
         """),
        ('--overwrite=ATTRLIST:attrlist -> overwrite_attrs',
         """Overwrite the possibly existing values of attributes listed in
         ATTRLIST (separated by spaces or commas), instead of warning if
         their values differ and keeping the existing value.
         """),
        ('--key=ATTRLIST:attrlist -> key_attrs',
         """Use the attributes listed in ATTRLIST (separated by spaces or
         commas) as a key:
         when their values in a VRT structure match those of a row in a data
         file, add the remaining attributes in the data file to the VRT.
         If the data file does not contain values for a key in the VRT,
         existing attribute values are preserved and the values for new
         attributes are empty strings.
         Note that this option implies reading the entire data file into
         memory, so use with caution for very large data files.
         """),
    ]

    def __init__(self):
        # extra_types=... is needed for using module-level functions
        # as types in ARGSPECS (otherwise, type could be passed via a
        # dict)
        super().__init__(extra_types=globals())

    def check_args(self, args):

        def check_fixed(fixed):
            fixed = fixed or []
            dupls = find_duplicates(name.decode('utf-8') for name, val in fixed)
            if dupls:
                self.error_exit('Multiple --fixed values for attributes: '
                                + ', '.join(dupls),
                                exitcode=2)
            return OrderedDict(fixed)

        super().check_args(args)
        if args.data_file is None and args.fixed is None:
            self.error_exit(
                'Please specify at least one of --data-file or --fixed.',
                exitcode=2)
        args.fixed = check_fixed(args.fixed)

    def main(self, args, inf, ouf):

        LESS_THAN = '<'.encode()[0]
        overwrite_attrs = set(args.overwrite_attrs or [])
        fixed_vals = args.fixed
        key_attrs = args.key_attrs
        if key_attrs:
            key_attrs = tuple(key_attrs)
        struct_name = args.struct_name.encode()
        struct_begin_alts = tuple(b'<' + struct_name + endchar
                                  for endchar in [b' ', b'>'])
        new_attr_names = None
        new_attr_values = {}
        # True if an ordered TSV file does not contain lines for all
        # structures in VRT
        tsv_exhausted = False
        # Attributes from the TSV file with empty values; set and used
        # when tsv_exhausted = True
        tsv_attrs_empty = None

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
            nonlocal tsv_exhausted, tsv_attrs_empty
            if tsv_exhausted:
                return tsv_attrs_empty, -1
            add_attrs = next(tsv_reader, None)
            if add_attrs is None:
                # If the data file is too short, add empty attribute
                # values to the rest of the VRT
                numlines = tsv_reader.line_num - int(args.attr_names is None)
                self.warn(
                    f'Data file {args.data_file} has fewer data lines'
                    f' ({numlines}) than the input VRT has {args.struct_name}'
                    ' structures; adding empty attribute values for the rest'
                    ' of the structures')
                tsv_exhausted = True
                tsv_attrs_empty = OrderedDict(
                    (attrname, b'') for attrname in tsv_reader.fieldnames)
                return tsv_attrs_empty, -1
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
                     ' {vrtline}; using empty values for new attributes')
                    .format(key=tuple(val.decode() for val in key),
                            datafile=args.data_file,
                            vrtline=linenr))
                return (
                    OrderedDict(
                        (attrname,
                         attrs[attrname] if attrname in attrs else b'')
                        for attrname in tsv_reader.fieldnames),
                    -1)

        def add_attributes(line, attrs, add_attrs, linenr, tsv_line_num,
                           check_overlap_attrs):
            # Check if attributes to be added (and not listed in
            # --overwrite) already exist in the input
            for overlap_attr in check_overlap_attrs:
                if (overlap_attr in attrs.keys()
                        and add_attrs[overlap_attr] != attrs[overlap_attr]):
                    attrname = overlap_attr.decode()
                    if overlap_attr in fixed_attrs:
                        msg_other = 'specified with --fixed'
                    else:
                        msg_other = (
                            f'on line {tsv_line_num} of {args.data_file}')
                    self.warn(
                        f'Value for attribute {overlap_attr.decode()}'
                        f' on line {linenr} of VRT input differs from'
                        f' that {msg_other}; keeping the existing one')
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
                    if get_add_attrs is not None:
                        add_attrs, tsv_linenr = get_add_attrs(
                            tsv_reader, line, attrs, linenr)
                        if fixed_vals:
                            add_attrs.update(fixed_vals)
                    else:
                        # If get_add_attrs is None, no data file, so
                        # fixed values only
                        add_attrs = fixed_vals
                        tsv_linenr = -1
                    if add_attrs:
                        line = add_attributes(
                            line, attrs, add_attrs, linenr, tsv_linenr,
                            check_overlap_attrs)
                ouf.write(line)

        fixed_attrs = set(fixed_vals.keys())
        new_attr_names = fixed_attrs.copy()
        if args.data_file is None:
            process_input(inf, None, None, new_attr_names)
        else:
            get_add_attrs = (
                get_add_attrs_keyed if key_attrs else get_add_attrs_ordered)
            with open(args.data_file, 'rb') as attrf:
                tsv_reader = TsvReader(attrf, fieldnames=args.attr_names,
                                       entities=EncodeEntities.NON_ENTITIES)
                if not args.attr_names:
                    tsv_reader.read_fieldnames()
                tsv_attr_names = set(tsv_reader.fieldnames or [])
                if new_attr_names & tsv_attr_names:
                    self.error_exit(
                        'Same attributes specified both in a data file and'
                        ' with a fixed value: '
                        + ', '.join(attrname.decode('utf-8') for attrname in
                                    sorted(new_attr_names & tsv_attr_names)))
                new_attr_names |= tsv_attr_names
                if key_attrs:
                    read_keyed_data(tsv_reader)
                process_input(inf, get_add_attrs, tsv_reader, new_attr_names)
