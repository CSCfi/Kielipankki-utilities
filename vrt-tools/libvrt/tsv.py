
"""
Module libvrt.tsv

This module contains utilities for processing TSV data, in particular,
a class for reading TSV data as binary, each row as an OrderedDict.
"""


# TODO:
# - Handle lines with fewer or more fields than field names.
# - Handle duplicate field names (error?).


import re

from collections import OrderedDict
from enum import Enum

from libvrt.metaline import escape


class EncodeEntities(Enum):
    """Specify when to encode characters as XML predefined entities."""
    # Do not encode
    NEVER = 0
    # Encode all others except & beginning an entity, that is,
    # followed by one of lt;, gt;, quot;, amp;
    NON_ENTITIES = 1
    # Always encode, even & beginning an entity
    ALWAYS = 2


class TsvReader:

    """Read from a binary tab-separated values file, optionally with a
    column heading row.

    When iterated over, return `OrderedDict` instances with field
    (column) names as keys.

    By default, convert the characters ``<>&"`` to the corresponding
    XML predefined entities (``&`` only if not followed by ``lt;``,
    ``gt;``, ``quot;`` or ``amp;``).

    This tries to be somewhat compatible with `csv.DictReader`, which
    does not support reading from a binary file, which is faster.
    """

    # Dictionary mapping characters and the corresponding XML
    # predefined entities
    entities = dict((spec[0].encode(), ('&' + spec[1:] + ';').encode())
                    for spec in '<lt >gt &amp "quot'.split())

    def __init__(self, infile, fieldnames=None, entities=None):
        """Initialize for reading from `infile` with field names `fieldnames`.

        If `fieldnames` is `None` (default), treat the first line of
        `infile` as a column heading row containing the names of the
        fields; otherwise, `fieldnames` should be a sequence of
        `bytes` to be used as field names.

        `entities` controls whether to encode the special characters
        ``<>"&`` to XML predefined entities. Its value can be one of
        the following:
        - `EncodeEntities.NEVER`: Preserve the characters as they are.
        - `EncodeEntities.ALWAYS`: Always encode the characters.
        - `None` or `EncodeEntities.NON_ENTITIES` (default): Encode
           ``&`` only if not followed by ``lt;``, ``gt;``, ``quot;``
           or ``amp;``; always encode the ``<>"``.
        """
        self._infile = infile
        self.fieldnames = fieldnames
        # self._encode_entities is a function to convert <>&" in a
        # bytes string to XML predefined entities; None if they are
        # not to be converted
        if entities == EncodeEntities.NEVER:
            self._encode_entities = None
        elif entities == EncodeEntities.ALWAYS:
            self._encode_entities = escape
        else:
            # Default if entities is None or EncodeEntities.NON_ENTITIES
            entities_re = re.compile(rb'([<>"]|&(?!(?:lt|gt|amp|quot);))')
            subst_fn = lambda mo: self.entities[mo.group(1)]
            self._encode_entities = (
                lambda line: entities_re.sub(subst_fn, line))
        self.line_num = 0

    def __next__(self):
        """Return `OrderedDict` corresponding to the next input line.

        If `fieldnames` was not set when creating instance, read the
        first input line as a column heading row and set
        `self.fieldnames` accordingly.
        """
        if self.fieldnames is None:
            self.fieldnames = self._read_fields()
        fieldvals = self._read_fields()
        return OrderedDict(zip(self.fieldnames, fieldvals))

    def _read_fields(self):
        """Read the next line from input, split by tabs and return as `list`.

        Raise `StopIteration` if the input is exhausted.
        """
        line = self._infile.readline()
        if not line:
            raise StopIteration
        self.line_num += 1
        if self._encode_entities:
            line = self._encode_entities(line)
        return line[:-1].split(b'\t')

    def read_fieldnames(self):
        """Return field (column) names, reading from input if needed.

        If `self.fieldnames` is not set, read field names from the
        input (the first input line) and set `self.fieldnames`. If the
        input is empty, return `None`.
        """
        if self.fieldnames is None:
            try:
                self.fieldnames = self._read_fields()
            except StopIteration:
                pass
        return self.fieldnames
