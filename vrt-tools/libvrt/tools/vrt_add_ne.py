
"""
vrt_add_ne.py

The actual implementation of vrt-add-ne.

Please run "vrt-add-ne -h" for more information.
"""


# TODO:
# - Try to improve intra-name tag nesting in cases such as: "<tag>
#   nameword1 </tag> nameword2", now tagged as "<tag> <ne> nameword1
#   </tag> nameword2 </ne>", and "nameword1 <tag> nameword2 </tag>",
#   now tagged "<ne> nameword1 <tag> nameword2 </ne> </tag>"


import re

from collections import defaultdict
from dataclasses import dataclass, field

from libvrt import metaline as ml
from libvrt import nameline as nl
from libvrt.argtypes import encode_utf8

from vrtargsoolib import InputProcessor


# NER tag, possibly with a nesting depth suffix
_NERTAG_RE = re.compile(rb'''(?P<fulltype>
                               (?P<ex> (?: Ena|Nu|Ti ) mex )
                               (?P<type> [A-Z] [a-z]+ )
                               (?P<subtype> [A-Z] [a-z]+ )
                             )
                             - (?P<kind> [BEF] )
                             (?: - (?P<depth> [0-9]+ ) )?''',
                        re.X)


@dataclass(slots=True)
class _Name:

    """A name with its lines, as collected from the input."""

    # Parts of the NER tag of the maximal name (see `split_nertag`)
    nertag_parts: dict[str, bytes]
    # Input lines within the name: tokens and intra-name meta lines
    lines: list[bytes] = field(default_factory=list)
    # Token lines split into positional attributes
    tokens: list[list[bytes]] = field(default_factory=list)
    # Index in `lines` of each token
    token_lineidxs: list[int] = field(default_factory=list)
    # Zero-based input line number of each token
    token_linenums: list[int] = field(default_factory=list)
    # Structure nesting depth of the boundary structure of the name:
    # an end tag at this depth or lower ends the name if it has not
    # ended at a NER end tag (0 = no structure)
    boundary_depth: int = 0

    def add_token(self, line: bytes, attrs: list[bytes], linenum: int):
        """Add token `line`, split into `attrs`, at input line `linenum`."""
        self.token_lineidxs.append(len(self.lines))
        self.token_linenums.append(linenum)
        self.lines.append(line)
        self.tokens.append(attrs)


def _unescape(value: bytes) -> str:
    """Decode and unescape a VRT attribute value.

    Args:
        value: The value as in the input, possibly with character
            entity references.

    Returns:
        `value` decoded from UTF-8 (undecodable bytes as surrogate
        escapes) and with the predefined entity references (&lt;
        &gt; &amp; &quot; &apos;) replaced with the characters.
    """
    value_str = value.decode('utf-8', 'surrogateescape')
    return (ml.strunescape(value_str, tabs=False) if '&' in value_str
            else value_str)


class VrtNeAdder(InputProcessor):

    """Class implementing vrt-add-ne functionality."""

    DESCRIPTION = """
    Augment VRT input containing positional name attributes with <ne>
    structures with attributes. The tool expects a positional
    attribute to contain NER tags for maximal names, matching the
    regular expression "(Ena|Nu|Ti)mex[A-Z][a-z]+[A-Z][a-z]+-[BEF]",
    as produced by vrt-finnish-nertag. Another attribute can contain a
    set of NER tags for possible nested names, with "-N" appended
    where N is the nesting level. Maximal names are enclosed in <ne>
    and nested names in <neN>, where N is the nesting level (1, 2,
    ...), unless --recursive-nested is specified.
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
        ('--recursive-nested',
         '''enclose nested names in recursively embedded <ne> structures
            instead of numbered <ne1>, <ne2>, ... by nesting level'''),
        ('--sentence = struct:encode_utf8 "sentence"',
         '''sentence structure name is struct: a name may not cross the
            end of a struct structure'''),
    ]

    def __init__(self):
        # extra_types=... is needed for using module-level functions
        # as types in ARGSPECS (otherwise, type could be passed via a
        # dict)
        super().__init__(extra_types=globals())

    def check_args(self, args):
        """Check and modify `args` (parsed command line arguments)."""
        args.multi_nertag = args.multi_nertag.rstrip(b'/') + b'/'
        super().check_args(args)

    def main(self, args, inf, ouf):
        """Read `inf`, write to `ouf`, with command-line arguments `args`."""

        # Index of the positional attribute for nertag, nertags, word
        # and lemma
        attrnum_nertag = attrnum_nertags = attrnum_word = attrnum_lemma = None
        # Values of the kind group of a NER tag (see _NERTAG_RE):
        # beginning, end and full (single-word) name
        NERTAG_NONE = None
        NERTAG_BEGIN = b'B'
        NERTAG_END = b'E'
        NERTAG_FULL = b'F'

        def split_nertag(nertag):
            """Return a dict containing `nertag` parts.

            The keys of the dict are ``fulltype`` (the NER tag without
            the suffixes), its parts ``ex``, ``type`` and ``subtype``,
            ``kind`` (``B``, ``E`` or ``F``) and ``depth`` (the nesting
            level, or `None` if `nertag` has no nesting level suffix).
            If `nertag` is not valid, that is, it does not match the
            NER tag regexp
            ``(Ena|Nu|Ti)mex[A-Z][a-z]+[A-Z][a-z]+-[BEF](-[0-9]+)?``,
            return `None`.
            """
            mo = _NERTAG_RE.fullmatch(nertag)
            return mo.groupdict() if mo else None

        def add_ne_tags(name: _Name) -> list[bytes]:
            """Return the lines of `name` enclosed in <ne> structures.

            Enclose the maximal name in <ne> and, unless
            `args.maximal_only`, nested names in <neN> (or <ne>).
            """
            nested_names = [] if args.maximal_only else find_nested_names(name)
            if nested_names:
                lines = add_nested_ne_tags(name, nested_names)
            else:
                lines = name.lines
            starttag, endtag = make_ne_tags(name.nertag_parts, name.tokens)
            return [starttag] + lines + [endtag]

        def find_nested_names(
                name: _Name) -> list[tuple[int, int, int, dict[str, bytes]]]:
            """Return the nested, non-maximal names within `name`.

            Get the nested names from the attribute ``nertags`` of the
            tokens of `name`. Warn of invalid and unmatched NER tags.

            Returns:
                A list of tuples (depth, start, end, nertag_parts),
                where depth is the nesting level (> 0), start and end
                are the indices of the first token and the token
                following the last token of the nested name in
                `name.tokens`, and nertag_parts are the parts of its
                NER tag.
            """
            # Names whose end tag has not yet been seen, by depth:
            # (nertag, nertag_parts, start)
            open_names: dict[int, tuple[bytes, dict[str, bytes], int]] = {}
            nested_names: list[tuple[int, int, int, dict[str, bytes]]] = []
            for token_num, token in enumerate(name.tokens):
                token_linenum = name.token_linenums[token_num]
                nertags = token[attrnum_nertags].strip(b'|').split(b'|')
                for nertag in nertags:
                    if not nertag:
                        continue
                    nertag_parts = split_nertag(nertag)
                    if not nertag_parts or not nertag_parts['depth']:
                        warn('Invalid nested NER tag', nertag, token_linenum)
                        continue
                    depth = int(nertag_parts['depth'])
                    # Ignore depth 0 (top level)
                    if not depth:
                        continue
                    tagtype = nertag_parts['kind']
                    open_name = open_names.get(depth)
                    if tagtype == NERTAG_FULL:
                        nested_names.append(
                            (depth, token_num, token_num + 1, nertag_parts))
                    elif tagtype == NERTAG_BEGIN:
                        if open_name is None:
                            open_names[depth] = (
                                nertag, nertag_parts, token_num)
                        else:
                            warn('Nested NER tag '
                                 + open_name[0].decode('utf-8')
                                 + f' already open at level {depth}',
                                 nertag, token_linenum)
                    elif open_name is None:
                        # tagtype == NERTAG_END
                        warn('Nested NER end tag without start tag',
                             nertag, token_linenum)
                    elif (nertag_parts['fulltype']
                          == open_name[1]['fulltype']):
                        del open_names[depth]
                        nested_names.append(
                            (depth, open_name[2], token_num + 1,
                             open_name[1]))
                    else:
                        warn('Nested NER end tag does not match start'
                             ' tag ' + open_name[0].decode('utf-8'),
                             nertag, token_linenum)
            for depth in sorted(open_names, reverse=True):
                nertag, _, start = open_names[depth]
                warn('No end tag for nested NER tag', nertag,
                     name.token_linenums[start])
            return nested_names

        def add_nested_ne_tags(
                name: _Name,
                nested_names: list[tuple[int, int, int, dict[str, bytes]]]
        ) -> list[bytes]:
            """Return the lines of `name` with `nested_names` enclosed.

            Enclose `nested_names` (as returned by `find_nested_names`)
            in <neN> structures, where N is the nesting level, or in
            <ne> if `args.recursive_nested`. Insert start tags
            immediately before the first token of a nested name and
            end tags immediately after its last token, so that
            intra-name meta lines remain outside nested names
            beginning or ending at them.
            """
            # Start and end tags to be added before and after each
            # token, by token index; an outer name (lower depth, or
            # longer at the same depth) is opened first and closed
            # last
            starttags: defaultdict[int, list[bytes]] = defaultdict(list)
            endtags: defaultdict[int, list[bytes]] = defaultdict(list)
            for depth, start, end, nertag_parts in sorted(
                    nested_names, key=lambda n: (n[1], n[0], -n[2])):
                starttag, endtag = make_ne_tags(
                    nertag_parts, name.tokens[start:end], depth)
                starttags[start].append(starttag)
                endtags[end - 1].insert(0, endtag)
            lines: list[bytes] = []
            line_tokens: dict[int, int] = dict(
                zip(name.token_lineidxs, range(len(name.tokens))))
            for lineidx, line in enumerate(name.lines):
                token_num = line_tokens.get(lineidx)
                if token_num is None:
                    lines.append(line)
                else:
                    lines.extend(starttags.get(token_num, ()))
                    lines.append(line)
                    lines.extend(endtags.get(token_num, ()))
            return lines

        def make_ne_tags(nertag_parts: dict[str, bytes],
                         name_tokens: list[list[bytes]],
                         depth: int = 0) -> tuple[bytes, bytes]:
            """Return start and end tag of <ne> with NER tag `nertag_parts`.

            `name_tokens` is the tokens of the name split into
            positional attributes. If `depth` > 0 and not
            `args.recursive_nested`, use structure <neN>, where N is
            `depth`.
            """
            struct = (b'ne' if depth == 0 or args.recursive_nested
                      else f'ne{depth}'.encode())
            return (ml.starttag(struct,
                                make_ne_attrs(nertag_parts, name_tokens)),
                    b'</' + struct + b'>\n')

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
                (b'ex', nertag_parts['ex'].upper()),
                (b'type', nertag_parts['type'].upper()),
                (b'subtype', nertag_parts['subtype'].upper()),
                (b'placename', name if is_placename else b''),
                (b'placename_source', b'ner' if is_placename else b''))

        def make_name(name_tokens: list[list[bytes]],
                      name_cat: bytes) -> bytes:
            """Make the value of the name attribute of <ne>.

            Args:
                name_tokens: The tokens of the name split into
                    positional attributes.
                name_cat: The category of the name: ``Enamex``,
                    ``Numex`` or ``Timex``.

            Returns:
                The name, with character entity references as in the
                input, except possibly in a last lemma changed by
                `adjust_case`, and double quotation marks not encoded.
            """
            if name_cat in (b'Timex', b'Numex'):
                # For temporal and numeric expressions, return a
                # concatenation of word forms
                return b' '.join(
                    token[attrnum_word] for token in name_tokens)
            else:
                # For name expressions proper, use lemma of the last
                # token and word forms of the preceding ones
                return b' '.join(
                    [token[attrnum_word] for token in name_tokens[:-1]]
                    + [adjust_case(name_tokens[-1][attrnum_lemma],
                                   name_tokens[-1][attrnum_word])])

        def adjust_case(lemma: bytes, wordform: bytes) -> bytes:
            """Capitalize or upper-case a lemma like its word form.

            Test and change the case on unescaped strings, so that
            non-ASCII letters and letters adjacent to character entity
            references are handled correctly.

            Args:
                lemma: The lemma (escaped, as in the input).
                wordform: The word form (escaped, as in the input).

            Returns:
                `lemma` capitalized if `wordform` is capitalized, in
                upper case if `wordform` is in upper case, otherwise
                `lemma` as is.
            """
            wordform_str = _unescape(wordform)
            if wordform_str.istitle():
                change_case = str.title
            elif wordform_str.isupper():
                change_case = str.upper
            else:
                return lemma
            # ml.strescape does not escape apostrophes, so an &apos; in
            # the lemma becomes a literal apostrophe; that is valid in
            # a double-quoted attribute value
            return ml.strescape(change_case(_unescape(lemma))).encode(
                'utf-8', 'surrogateescape')

        def warn(msg, nertag, linenum):
            """Output to stderr a warning with message `msg`.

            The warning message also includes the NER tag `nertag`,
            input file name (or ``<stdin>``) and input line number
            `linenum`.
            """
            self.warn(msg + ': ' + nertag.decode('utf-8'),
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

        def begin_name(nertag_parts: dict[str, bytes]) -> _Name:
            """Begin a new multi-word name.

            Set the boundary structure of the name to the innermost
            open sentence structure or, if none is open, to the
            innermost open structure.

            Args:
                nertag_parts: The parts of the NER tag of the name.

            Returns:
                The new name, with no lines yet.
            """
            return _Name(nertag_parts,
                         boundary_depth=(sentence_depths[-1] if sentence_depths
                                         else struct_depth))

        # The multi-word name being collected, or None outside names
        name: _Name | None = None
        # The nesting depth of structures
        struct_depth = 0
        # The nesting depths of the open sentence structures
        sentence_depths: list[int] = []
        # Prefixes of sentence start tags
        sentence_starts = (b'<' + args.sentence + b' ',
                           b'<' + args.sentence + b'>')
        for linenum, line in enumerate(inf):
            # The same as ml.ismeta(line) but faster, as this is
            # tested for every line
            if line and line[0] == 60:  # b'<'
                # Structure or comment line
                if line.startswith(b'</'):
                    # End tag
                    if name and struct_depth <= name.boundary_depth:
                        # Names may not cross the end of a sentence. The
                        # warning mentions a sentence even if the
                        # boundary is another structure, but that
                        # happens only if tokens are not in sentences.
                        warn('NER start tag without end tag within sentence',
                             name.tokens[0][attrnum_nertag],
                             name.token_linenums[0])
                        ouf.writelines(name.lines)
                        name = None
                    if sentence_depths and sentence_depths[-1] == struct_depth:
                        sentence_depths.pop()
                    struct_depth -= 1
                elif not line.startswith(b'<!'):
                    # Start tag
                    struct_depth += 1
                    if line.startswith(sentence_starts):
                        sentence_depths.append(struct_depth)
                if name:
                    # Inside a name
                    name.lines.append(line)
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
                attrs = line.rstrip(b'\r\n').split(b'\t')
                nertag = attrs[attrnum_nertag]
                nertag_parts: dict[str, bytes] | None = None
                # "_" (as output by vrt-finnish-nertag --max) and an
                # empty value mean no name
                if nertag and nertag != b'_':
                    nertag_parts = split_nertag(nertag)
                    # A maximal NER tag may not have a depth suffix
                    if not nertag_parts or nertag_parts['depth']:
                        nertag_parts = None
                        warn('Invalid NER tag', nertag, linenum)
                nertag_type = (nertag_parts['kind'] if nertag_parts
                               else NERTAG_NONE)
                if name:
                    # Within a multi-word name
                    name.add_token(line, attrs, linenum)
                    if nertag_type == NERTAG_END:
                        if (nertag_parts['fulltype']
                                == name.nertag_parts['fulltype']):
                            # Last token of the name
                            ouf.writelines(add_ne_tags(name))
                            name = None
                        else:
                            warn('NER end tag does not match start tag '
                                 + name.nertag_parts['fulltype']
                                 .decode('utf-8')
                                 + '-B',
                                 nertag, linenum)
                    elif nertag_type != NERTAG_NONE:
                        warn('Invalid NER tag within name', nertag, linenum)
                elif nertag_type == NERTAG_NONE:
                    # Not a name
                    ouf.write(line)
                elif nertag_type == NERTAG_FULL:
                    # Single-word name
                    ouf.writelines(add_ne_tags(
                        _Name(nertag_parts, [line], [attrs], [0], [linenum])))
                elif nertag_type == NERTAG_BEGIN:
                    # Begin a multi-word name
                    name = begin_name(nertag_parts)
                    name.add_token(line, attrs, linenum)
                else:
                    # nertag_type == NERTAG_END
                    warn('NER end tag without start tag', nertag, linenum)
                    ouf.write(line)
        if name:
            # Neither a NER end tag nor a structure end tag ended the
            # name, so the input is incomplete (or has tokens outside
            # structures)
            self.warn('End of input in the middle of a name: '
                      + name.nertag_parts['fulltype'].decode('utf-8')
                      + '-E expected',
                      filename=inf.name, linenr=name.token_linenums[0] + 1)
            ouf.writelines(name.lines)
