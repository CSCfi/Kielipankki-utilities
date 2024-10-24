
"""
vrt_augment_name_attrs.py

The actual implementation of vrt-augment-name-attrs.

Please run "vrt-augment-name-attrs -h" for more information.
"""


# TODO:
# - Try to improve intra-name tag nesting in cases such as: "<tag>
#   nameword1 </tag> nameword2", now tagged as "<tag> <ne> nameword1
#   </tag> nameword2 </ne>", and "nameword1 <tag> nameword2 </tag>",
#   now tagged "<ne> nameword1 <tag> nameword2 </ne> </tag>"


import sys
import re

from collections import defaultdict

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
         '''positional attribute name for base form (lemma) is attr;
            if the input does not contain attr, use word forms in the
            place of lemmas (specify "" to suppress a warning)'''),
        ('--nertag = attr:encode_utf8 "nertag2"',
         '''positional attribute name for maximal NER tag is attr'''),
        ('--multi-nertag = attr:encode_utf8 "nertags2"',
         '''positional attribute name for multiple (nested, non-maximal) NER
            tags is attr'''),
        ('--maximal-only',
         '''enclose only maximal names, no nested ones'''),
    ]

    def __init__(self):
        # extra_types=... is needed for using module-level functions
        # as types in ARGSPECS (otherwise, type could be passed via a
        # dict)
        super().__init__(extra_types=globals())

    def check_args(self, args):
        """Check and modify `args` (parsed command line arguments)."""
        args.multi_nertag = args.multi_nertag.rstrip(b'/') + b'/'
        self.args = args

    def main(self, args, inf, ouf):
        """Read `inf`, write to `ouf`, with command-line arguments `args`."""

        # Index of the positional attribute for nertag, nertags, word
        # and lemma
        attrnum_nertag = attrnum_nertags = attrnum_word = attrnum_lemma = None
        # The type of a NER tag based on the last character of the
        # value
        NERTAG_NONE = b'_'[0]
        NERTAG_BEGIN = b'B'[0]
        NERTAG_END = b'E'[0]
        NERTAG_FULL = b'F'[0]
        # The names of ne attributes extracted from the NER tag, both
        # as str and bytes
        nertag_part_attrnames = tuple(
            (attrname, attrname.encode('utf-8'))
            for attrname in ('ex', 'type', 'subtype'))

        def split_nertag(nertag):
            """Return a dict containing `nertag` parts.

            If `nertag` value is not valid, that is, it does not match
            the NER tag regexp
            ``(Ena|Nu|Ti)mex[A-Z][a-z]+[A-Z][a-z]+-[BEF](-[0-9]+)?``,
            return `None`.
            """
            mo = re.match(rb'''(?P<fulltype>
                                 (?P<ex> (?: Ena|Nu|Ti ) mex )
                                 (?P<type> [A-Z] [a-z]+ )
                                 (?P<subtype> [A-Z] [a-z]+ )
                               )
                               - (?P<kind> [BEF] )
                               (?: - (?P<depth> [0-9]+ ) )?''',
                          nertag, re.X)
            return mo.groupdict() if mo else None

        def add_ne_tags(nertag_parts, namelines, name_tokens):
            """Return `namelines` surrounded by an <ne> structure.

            `nertag_parts` is a dict containing the parts of the NER
            tag and `name_tokens` is `namelines` split into
            attributes.
            """
            # print('add_ne_tags', nertag, namelines, name_tokens, file=sys.stderr)
            if not args.maximal_only:
                namelines = add_nested_ne_tags(namelines, name_tokens)
            return enclose_in_ne(nertag_parts, namelines, name_tokens)

        def add_nested_ne_tags(namelines, name_tokens):
            """Return `namelines` with nested names enclosed in <ne>.

            Enclose nested, non-maximal (non-top-level) names in
            `namelines` in <ne> structures. `name_tokens` is
            `namelines` split into positional attributes. The function
            uses the attribute ``nertags`` to get information on
            nested names.
            """
            # Names by nesting depth
            nested_names = defaultdict(list)
            maxdepth = 0
            for token_num, token in enumerate(name_tokens):
                nertags = token[attrnum_nertags].strip(b'|').split(b'|')
                for nertag in nertags:
                    if not nertag:
                        continue
                    nertag_parts = split_nertag(nertag)
                    if not nertag_parts or not nertag_parts['depth']:
                        warn('Invalid nested NER tag', nertag, linenum)
                        continue
                    depth = int(nertag_parts['depth'])
                    # Ignore depth 0 (top level)
                    if depth:
                        maxdepth = max(depth, maxdepth)
                        tagtype = nertag_parts['kind'][0]
                        if tagtype == NERTAG_FULL:
                            nested_names[depth - 1].append(
                                [nertag, nertag_parts, token_num,
                                 token_num + 1])
                        elif tagtype == NERTAG_BEGIN:
                            nested_names[depth - 1].append(
                                [nertag, nertag_parts, token_num])
                        elif tagtype == NERTAG_END:
                            nested_names[depth - 1][-1].append(token_num + 1)
                        else:
                            warn('Invalid nested NER tag', nertag, linenum)
            # nameline_index[i] is the number of the line in namelines
            # whose number was i in the input namelines but which may
            # be different after adding <ne> tags
            nameline_index = list(range(len(namelines) + 1))
            for depth in range(maxdepth, 0, -1):
                for nameinfo in nested_names[depth - 1]:
                    if len(nameinfo) < 4:
                        warn('No end tag for nested NER tag', nameinfo[0],
                             linenum)
                        continue
                    _, nertag_parts, start, end = nameinfo
                    nameline_start = nameline_index[start]
                    nameline_end = nameline_index[end]
                    namelines[nameline_start:nameline_end] = (
                        enclose_in_ne(nertag_parts,
                                      namelines[nameline_start:nameline_end],
                                      name_tokens[start:end]))
                    # Adjust nameline_index by the start tag
                    for i in range(start + 1, end):
                        nameline_index[i] += 1
                    # Adjust nameline_index by the start and end tag
                    for i in range(end, len(nameline_index)):
                        nameline_index[i] += 2
            return namelines

        def enclose_in_ne(nertag_parts, namelines, name_tokens):
            """Return `namelines` enclosed in <ne> with NER tag `nertag_parts`.

            `name_tokens` is `namelines` split into positional
            attributes.
            """
            return (
                [ml.starttag(
                    b'ne', make_ne_attrs(nertag_parts, name_tokens))]
                + namelines
                + [b'</ne>\n'])

        def make_ne_attrs(nertag_parts, name_tokens):
            """Return attribute (name, value) pairs for <ne> structure.

            Return structural attributes for `nertag_parts` and `name_tokens`
            """
            is_placename = nertag_parts['type'] == b'Loc'
            name = (make_name(name_tokens, nertag_parts['ex'])
                    .replace(b'"', b'&quot;'))
            return (
                (b'name', name),
                (b'fulltype', nertag_parts['fulltype']),
                *((attrname_b, nertag_parts[attrname].upper())
                  for attrname, attrname_b in nertag_part_attrnames),
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

        def warn(msg, nertag, linenum):
            """Output to stderr a warning with message `msg`.

            The warning message also includes the NER tag `nertag`,
            input file name (or ``<stdin>``) and input line number
            `linenum`.
            """
            self.warn(msg + ': "' + nertag.decode('utf-8') + '"',
                      filename=inf.name, linenr=linenum + 1)

        def set_attrnums(line):
            """Set `attrnum_*` variables from pos attrs comment `line`."""
            nonlocal attrnum_nertag, attrnum_nertags
            nonlocal attrnum_word, attrnum_lemma
            attrs = nl.parsenameline(line)
            attrnames_check = [args.nertag, args.word]
            if not args.maximal_only:
                attrnames_check.append(args.multi_nertag)
            for attrname in attrnames_check:
                if attrname not in attrs:
                    self.error_exit('No positional attribute \''
                                    + attrname.decode('utf-8') + '\' in input')
            attrnum_nertag = attrs.index(args.nertag)
            attrnum_word = attrs.index(args.word)
            if args.lemma in attrs:
                attrnum_lemma = attrs.index(args.lemma)
            else:
                if args.lemma:
                    self.warn('No positional attribute \''
                              + args.lemma.decode('utf-8') + '\' in input;'
                              ' using word forms in the place of lemmas')
                attrnum_lemma = attrnum_word
            if not args.maximal_only:
                attrnum_nertags = attrs.index(args.multi_nertag)

        # Input lines within a (multi-word) name
        namelines = []
        # namelines (tokens) split into attributes, to avoid to
        # splitting multiple times
        name_tokens = []
        # NER tag split into parts
        nertag_parts = {}
        for linenum, line in enumerate(inf):
            if ml.ismeta(line):
                # Structure or comment line
                if namelines:
                    # Inside a name
                    if ml.isendtag(line) and ml.element(line) == b'sentence':
                        # Names may not cross sentence boundaries
                        self.warn(f'No NER end tag for {nertag.decode("utf-8")}'
                                  ' within sentence',
                                  filename=inf.name, linenr=linenum + 1)
                        ouf.writelines(namelines)
                        ouf.write(line)
                        namelines = []
                        name_tokens = []
                        continue
                    else:
                        namelines.append(line)
                else:
                    # Outside a name
                    if attrnum_nertag is None:
                        # Positional-attributes comment not yet seen
                        if nl.isnameline(line):
                            set_attrnums(line)
                    ouf.write(line)
            elif attrnum_nertag is None:
                # Token line, no positional-attributes comment seen
                self.error_exit(
                    'No positional-attributes comment before the first token')
            else:
                # Token line
                attrs = line[:-1].split(b'\t')
                nertag = attrs[attrnum_nertag]
                if nertag and nertag != b'_':
                    nertag_parts = split_nertag(nertag)
                    if nertag_parts:
                        nertag_type = nertag_parts['kind'][0]
                    else:
                        warn('Invalid NER tag', nertag, linenum)
                        nertag_type = NERTAG_NONE
                else:
                    nertag_type = NERTAG_NONE
                if namelines:
                    # Within a multi-word name
                    namelines.append(line)
                    name_tokens.append(attrs)
                    if nertag_type == NERTAG_END:
                        # Last token of the name
                        ouf.writelines(
                            add_ne_tags(nertag_parts, namelines, name_tokens))
                        namelines = []
                        name_tokens = []
                    elif nertag_type != NERTAG_NONE:
                        warn('Invalid NER tag within name', nertag, linenum)
                elif nertag_type == NERTAG_NONE:
                    # Not a name
                    ouf.write(line)
                elif nertag_type == NERTAG_FULL:
                    # Single-word name
                    ouf.writelines(add_ne_tags(nertag_parts, [line], [attrs]))
                elif nertag_type == NERTAG_BEGIN:
                    # Begin a multi-word name
                    namelines.append(line)
                    name_tokens.append(attrs)
                elif nertag_type == NERTAG_END:
                    warn('NER end tag without start tag', nertag, linenum)
                    ouf.write(line)
                else:
                    warn('Invalid NER tag', nertag, linenum)
                    ouf.write(line)
        if namelines:
            # This means that a sentence is open, too, and the input
            # is incomplete
            self.warn('End of input at the middle of a name: '
                      + nertag.decode('utf-8')[:-1] + 'E expected',
                      filename=inf.name, linenr=linenum)
            ouf.writelines(namelines)
