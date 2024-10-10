
"""
vrt_augment_name_attrs.py

The actual implementation of vrt-augment-name-attrs.

Please run "vrt-augment-name-attrs -h" for more information.
"""


# TODO:
# - Add nested ne tags for nested names (optionally?)
# - Try to improve intra-name tag nesting in cases such as: "<tag>
#   nameword1 </tag> nameword2", now tagged as "<tag> <ne> nameword1
#   </tag> nameword2 </ne>", and "nameword1 <tag> nameword2 </tag>",
#   now tagged "<ne> nameword1 <tag> nameword2 </ne> </tag>"


import sys
import re

from libvrt import metaline as ml
from libvrt import nameline as nl
from libvrt.argtypes import encode_utf8

from vrtargsoolib import InputProcessor


class VrtNameAttrAugmenter(InputProcessor):

    """Class implementing vrt-augment-name-attrs functionality."""

    DESCRIPTION = """
    Augment VRT input containing positional name attributes
    with <ne> structures with attributes.
    """
    ARGSPECS = [
        ('--word = attr:encode_utf8 "word"',
         '''positional attribute name for word form is attr'''),
        ('--lemma = attr:encode_utf8 "lemma"',
         '''positional attribute name for base form (lemma) is attr'''),
        ('--nertag = attr:encode_utf8 "nertag2"',
         '''positional attribute name for maximal NER tag is attr'''),
    ]

    def __init__(self):
        # extra_types=... is needed for using module-level functions
        # as types in ARGSPECS (otherwise, type could be passed via a
        # dict)
        super().__init__(extra_types=globals())

    def check_args(self, args):
        """Check and modify `args` (parsed command line arguments)."""
        self.args = args

    def main(self, args, inf, ouf):
        """Read `inf`, write to `ouf`, with command-line arguments `args`."""

        # Index of the positional attribute for nertag, word and lemma
        attrnum_nertag = attrnum_word = attrnum_lemma = None
        # The type of a NER tag based on the last character of the
        # value
        NERTAG_NONE = b'_'[0]
        NERTAG_BEGIN = b'B'[0]
        NERTAG_END = b'E'[0]
        NERTAG_FULL = b'F'[0]

        def add_ne_tags(nertag, namelines, name_tokens):
            """Return `namelines` surrounded by an <ne> structure.

            `nertag` is the tag for the name and `name_tokens` is
            `namelines` split into attributes.
            """
            # print('add_ne_tags', nertag, namelines, name_tokens, file=sys.stderr)
            return (
                [ml.starttag(
                    b'ne', make_ne_attrs(nertag, name_tokens))]
                + namelines
                + [b'</ne>\n'])

        def make_ne_attrs(nertag, name_tokens):
            """Return attribute (name, value) pairs for <ne> structure.

            Return structural attributes for `nertag` and `name_tokens`
            """
            mo = re.match(rb'((?:Ena|Nu|Ti)mex)(...)(...)', nertag)
            is_placename = mo.group(2) == b'Loc'
            name = make_name(name_tokens, mo.group(1)).replace(b'"', b'&quot;')
            return (
                (b'name', name),
                (b'fulltype', mo.group(0)),
                *((attrname, mo.group(group + 1).upper())
                  for group, attrname in enumerate(
                          (b'ex', b'type', b'subtype'))),
                (b'placename', name if is_placename else b''),
                (b'placename_source', b'ner' if is_placename else b''))

        def make_name(name_tokens, name_cat):
            """Return a name composed of `name_tokens`, of type `name_cat`."""
            if name_cat in (b'Timex', b'Numex'):
                # For temporal and numeric expressions, return a
                # concatenation of word forms
                return b' '.join(
                    token[attrnum_word] for token in name_tokens)
            else:
                # For name expressions proper, use lemma of the last
                # token and word forms of the preceding ones
                last_wordform = name_tokens[-1][attrnum_word]
                last_lemma = name_tokens[-1][attrnum_lemma]
                # If the last word form is capitalized or
                # all-uppercase, make the last lemma such, too
                if last_wordform.istitle():
                    last_lemma = last_lemma.title()
                elif last_wordform.isupper():
                    last_lemma = last_lemma.upper()
                return b' '.join([token[attrnum_word]
                                  for token in name_tokens[:-1]]
                                 + [last_lemma])

        # Input lines within a (multi-word) name
        namelines = []
        # namelines (tokens) split into attributes, to avoid to
        # splitting multiple times
        name_tokens = []
        for line in inf:
            if ml.ismeta(line):
                # Structure or comment line
                if namelines:
                    # Inside a name
                    namelines.append(line)
                else:
                    # Outside a name
                    if attrnum_nertag is None:
                        # Positional-attributes comment not yet seen
                        if nl.isnameline(line):
                            attrs = nl.parsenameline(line)
                            for attrname in [
                                    args.nertag, args.lemma, args.word]:
                                if attrname not in attrs:
                                    self.error_exit(
                                        'No positional attribute \''
                                        + attrname.decode('utf-8')
                                        + '\' in input')
                            attrnum_nertag = attrs.index(args.nertag)
                            attrnum_word = attrs.index(args.word)
                            attrnum_lemma = attrs.index(args.lemma)
                    ouf.write(line)
            elif attrnum_nertag is None:
                # Token line, no positional-attributes comment seen
                self.error_exit(
                    'No positional-attributes comment before the first token')
            else:
                # Token line
                attrs = line[:-1].split(b'\t')
                nertag = attrs[attrnum_nertag]
                nertag_type = nertag[-1]
                if namelines:
                    # Within a multi-word name
                    namelines.append(line)
                    name_tokens.append(attrs)
                    if nertag_type == NERTAG_END:
                        # Last token of the name
                        ouf.writelines(
                            add_ne_tags(nertag, namelines, name_tokens))
                        namelines = []
                        name_tokens = []
                elif nertag_type == NERTAG_NONE:
                    # Not a name
                    ouf.write(line)
                elif nertag_type == NERTAG_FULL:
                    # Single-word name
                    ouf.writelines(add_ne_tags(nertag, [line], [attrs]))
                elif nertag_type == NERTAG_BEGIN:
                    # Begin a multi-word name
                    namelines.append(line)
                    name_tokens.append(attrs)
