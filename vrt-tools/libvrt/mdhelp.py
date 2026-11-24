
"""
Module libvrt.mdhelp

Support for usage messages and documentation written in a subset of
Markdown with marked detail levels, so that a short usage message
(--help), full help (--help-full) and documentation in Markdown
(--help-markdown) can be generated from the same source: the
description, argument help texts and epilog of an
`argparse.ArgumentParser`.

To enable the facility for a parser, call `enable_markdown_help`.
(With `vrtargsoolib`, set `markdown_help = True` in the class
`OPTIONS` of a tool class instead.)

Detail levels are marked with Pandoc-style fenced divs and bracketed
spans with class "long" (only in full help and documentation) or
"short" (only in the short usage message):

    Always shown.

    ::: long
    Shown only in full help and documentation.
    :::

    ::: short
    Shown only in the short usage message.
    :::

    Inline: always shown[, only in full help]{.long}.

The div markers may also be written as "::: {.long}". Divs may be
nested, and divs with other classes are kept as they are. Spans may
not contain square brackets.

The Markdown subset supported by the plain-text help formatter
`MarkdownHelpFormatter` consists of paragraphs, bulleted and numbered
lists (an item continues up to the next item or a blank line), fenced
and indented code blocks, ATX headings ("# Heading"), hard line breaks
(a trailing backslash) and inline code, emphasis and links. Precede
a list with a blank line: Pandoc (unlike CommonMark) does not
otherwise recognize it. The indentation of texts is normalized as with
`inspect.cleandoc`.

Literal structure tags such as <ne> should be written as inline code
(`<ne>`), as otherwise they are treated as HTML tags in Markdown
output; the plain-text formatter removes the backquotes around such
code spans. The plain-text formatter also removes the backquotes
around code spans followed by "{.plain}" (as in `` `"x"`{.plain} ``),
which is used for default values; "{.plain}" is removed from the
Markdown output. Similarly, characters such as "*" and "_" in literal
values should be within inline code to avoid their being interpreted
as emphasis. As in argparse in general, a literal "%" in argument help
texts needs to be written as "%%".

In the Markdown documentation, the description should use level-3
headings ("###") for subsections and the epilog level-2 headings
("##") for sections of their own, such as "## Examples".

When the help is written to a terminal, `MarkdownHelpFormatter`
renders inline code, strong emphasis, headings and option names
(such as --option) in the help texts in bold and emphasis underlined,
as in man pages, removing the Markdown markup. The environment
variables PYTHON_COLORS, NO_COLOR and FORCE_COLOR can be used to
disable or force this (see `can_style`). (The parts of help formatted
by argparse itself are coloured by Python 3.14 and later.)
"""


from __future__ import annotations

import argparse
import functools
import os
import re
import sys

# typing (and inspect) are not imported at run time, as this module is
# imported by every tool using vrtargsoolib, and importing them would
# slow down the start-up of every tool by 10-30 milliseconds
TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence
    from typing import Any, TextIO


DETAIL_SHORT = 'short'
"""Detail level of the short usage message"""
DETAIL_FULL = 'full'
"""Detail level of full help and documentation"""

_DETAIL_CLASS_DROP = {
    DETAIL_SHORT: 'long',
    DETAIL_FULL: 'short',
}
"""The class of fenced divs and spans dropped at each detail level"""
_DETAIL_CLASSES = ('long', 'short')
"""The classes of fenced divs and spans marking detail levels"""

_DIV_OPEN_RE = re.compile(
    r'^ {0,3}:{3,}\s*(?:\{\s*\.(?P<cls1>[\w-]+)\s*\}|(?P<cls2>[\w-]+))'
    r'\s*:*\s*$')
_DIV_CLOSE_RE = re.compile(r'^ {0,3}:{3,}\s*$')
_SPAN_RE = re.compile(r'\[(?P<text>[^\[\]]*)\]\{\s*\.(?P<cls>long|short)\s*\}')
_FENCE_RE = re.compile(r'^(?P<indent> *)(?P<fence>`{3,}|~{3,})')
_LIST_ITEM_RE = re.compile(
    r'^(?P<indent> *)(?P<marker>[-*+]|\d{1,9}[.)])(?: +(?P<text>.*))?$')
_HEADING_RE = re.compile(r'^ {0,3}#{1,6}\s+(?P<text>.*?)(?:\s+#+)?\s*$')

_SGR_RE = re.compile(r'\x1b\[(?P<params>[0-9;]*)m')
"""ANSI SGR (Select Graphic Rendition) escape sequence"""
_SGR_OFF = {'1': '22', '3': '23', '4': '24'}
"""Map from SGR codes for bold, italics and underline to the
corresponding codes for turning them off"""
_BOLD = ('\x1b[1m', '\x1b[22m')
"""ANSI SGR escape sequences for turning bold on and off"""
_UNDERLINE = ('\x1b[4m', '\x1b[24m')
"""ANSI SGR escape sequences for turning underline on and off"""
_ESCAPE_RE = re.compile(r'\\([\\`*_{}\[\]()#+.!<>|-])')
"""Backslash-escaped character in Markdown"""
_LINK_RE = re.compile(r'\[([^\[\]]+)\]\(([^()\s]+)\)')
"""Markdown inline link [text](url)"""
_PROTECTED_RE = re.compile('[\uE000-\uE07F]')
"""ASCII character protected from being treated as markup by mapping it
to the Unicode private use area (code point + `_PROTECT_BASE`)"""
_PROTECT_BASE = 0xE000
"""The offset of protected ASCII characters in the private use area"""

_GROUP_TITLES = {
    'optional arguments': 'Options',
    'options': 'Options',
    'positional arguments': 'Positional arguments',
}
"""Normalized titles of argparse default argument groups (the title of
optional arguments depends on the Python version)"""


def _cleandoc(text: str) -> str:
    """Normalize the indentation of text as `inspect.cleandoc`.

    Expand tabs, remove leading whitespace from the first line and the
    common indentation from the rest, and remove leading and trailing
    blank lines. (`inspect` is not imported, as it is slow to import.)

    Args:
        text: The text to normalize.

    Returns:
        `text` with indentation normalized.
    """
    lines = text.expandtabs().split('\n')
    indents = [len(line) - len(line.lstrip()) for line in lines[1:]
               if line.strip()]
    margin = min(indents, default=0)
    lines[0] = lines[0].lstrip()
    lines[1:] = [line[margin:] for line in lines[1:]]
    while lines and not lines[-1]:
        lines.pop()
    while lines and not lines[0]:
        lines.pop(0)
    return '\n'.join(lines)


def select_detail(text: str, detail: str) -> str:
    """Select the content for a detail level from Markdown text.

    Normalize the indentation of `text` as `inspect.cleandoc` and
    remove the fenced divs and bracketed spans of the class not
    belonging to `detail` and the markers of those belonging to it.
    Divs and spans are not recognized in code blocks and code spans.

    Args:
        text: Markdown text with marked detail levels.
        detail: The detail level: `DETAIL_SHORT` or `DETAIL_FULL`.

    Returns:
        `text` with the content for `detail` selected.
    """
    drop_cls = _DETAIL_CLASS_DROP[detail]

    def replace_span(mo: re.Match[str]) -> str:
        """Return the text of the span in `mo` or "" if dropped."""
        return '' if mo.group('cls') == drop_cls else mo.group('text')

    def replace_spans(lines: list[str]) -> list[str]:
        """Replace the spans in `lines`, not in code spans in them."""
        if not lines:
            return []
        code_spans: list[str] = []

        def hide(mo: re.Match[str]) -> str:
            """Replace the code span in `mo` with a placeholder."""
            code_spans.append(mo.group())
            return f'\uE100{len(code_spans) - 1}\uE101'

        text = _CODE_SPAN_RE.sub(hide, '\n'.join(lines))
        text = _SPAN_RE.sub(replace_span, text)
        text = re.sub('\uE100(\\d+)\uE101',
                      lambda mo: code_spans[int(mo.group(1))], text)
        return text.split('\n')

    result: list[str] = []
    # Lines of text outside code blocks not yet added to result
    pending: list[str] = []
    # Stack of the classes of open divs
    divs: list[str] = []
    # The fence of the code block being read, if any
    fence: str | None = None
    # Whether the previous line was blank (or a div marker) or in an
    # indented code block
    prev_blank = True
    in_indented_code = False
    for line in _cleandoc(text).split('\n'):
        dropping = drop_cls in divs
        is_code = True
        if fence:
            if line.lstrip().startswith(fence):
                fence = None
        elif mo := _FENCE_RE.match(line):
            fence = mo.group('fence')
        elif (line.startswith('    ')
              and (prev_blank or in_indented_code)):
            in_indented_code = True
        else:
            is_code = False
            in_indented_code = in_indented_code and not line.strip()
            if mo := _DIV_OPEN_RE.match(line):
                cls = mo.group('cls1') or mo.group('cls2')
                divs.append(cls)
                prev_blank = True
                if cls in _DETAIL_CLASSES:
                    continue
            elif divs and _DIV_CLOSE_RE.match(line):
                prev_blank = True
                if divs.pop() in _DETAIL_CLASSES:
                    continue
            else:
                prev_blank = not line.strip()
        if dropping:
            continue
        if is_code:
            # Detail level spans are not recognized in code blocks
            result.extend(replace_spans(pending))
            pending = []
            result.append(line)
            prev_blank = False
        else:
            pending.append(line)
    result.extend(replace_spans(pending))
    text = '\n'.join(result)
    # Remove extra blank lines possibly left by removed divs
    return re.sub(r'\n{3,}', '\n\n', text).strip('\n')


def insert_in_first_paragraph(text: str, addition: str) -> str:
    """Append text to the first paragraph of Markdown text.

    Normalize the indentation of `text` as `inspect.cleandoc`. Skip
    code blocks and the content of fenced divs of the detail level
    classes, so that `addition` is shown at all detail levels. If a
    div marker follows the paragraph without a blank line in between,
    insert `addition` before it.

    Args:
        text: Markdown text with marked detail levels.
        addition: The text to append, typically beginning with a
            space.

    Returns:
        `text` with `addition` appended to its first paragraph, or
        appended as a paragraph of its own if `text` has no paragraph
        outside detail level divs and code blocks.
    """
    lines = _cleandoc(text).split('\n')
    # Stack of the classes of open divs
    divs: list[str] = []
    # The fence of the code block being read, if any
    fence: str | None = None
    prev_blank = True
    in_indented_code = False
    # The index of the last line of the first paragraph found so far
    last: int | None = None
    for i, line in enumerate(lines):
        is_text = False
        if fence:
            if line.lstrip().startswith(fence):
                fence = None
        elif mo := _FENCE_RE.match(line):
            fence = mo.group('fence')
        elif line.startswith('    ') and (prev_blank or in_indented_code):
            in_indented_code = True
        elif mo := _DIV_OPEN_RE.match(line):
            divs.append(mo.group('cls1') or mo.group('cls2'))
        elif divs and _DIV_CLOSE_RE.match(line):
            divs.pop()
        elif line.strip():
            in_indented_code = False
            is_text = not any(cls in _DETAIL_CLASSES for cls in divs)
        if is_text:
            last = i
        elif last is not None:
            break
        prev_blank = not line.strip() or bool(
            not fence and (_DIV_OPEN_RE.match(line)
                           or _DIV_CLOSE_RE.match(line)))
    if last is None:
        return '\n'.join(lines) + '\n\n' + addition.strip()
    lines[last] += addition
    return '\n'.join(lines)


_CODE_SPAN_RE = re.compile(
    r'(?<!`)(?P<ticks>`+)(?!`)(?P<code>(?:(?!\n[ \t]*\n).)+?)(?<!`)'
    r'(?P=ticks)(?!`)(?P<attr>\{\.plain\})?', re.DOTALL)
"""Markdown code span, delimited by backquote strings of equal length
(not spanning paragraphs), possibly followed by attribute "{.plain}"
(shown without backquotes in plain-text help)"""
_PLAIN_ATTR = '{.plain}'
"""Attribute of a code span shown without backquotes in plain-text
help"""


def code_span(text: str, plain: bool = False) -> str:
    """Return text as a Markdown code span.

    Use a backquote string longer than any in `text` as the delimiter,
    and add spaces inside the delimiters if needed to keep backquotes
    or spaces at the ends of `text`.

    Args:
        text: The text of the code span; may not be empty.
        plain: Whether to add attribute "{.plain}", so that the code
            span is shown without backquotes in plain-text help.

    Returns:
        `text` as a code span.
    """
    ticks = '`' * (max(map(len, re.findall('`+', text)), default=0) + 1)
    pad = (' ' if (text[:1] == '`' or text[-1:] == '`'
                   or (text[:1] == text[-1:] == ' ' and text.strip()))
           else '')
    return ticks + pad + text + pad + ticks + (_PLAIN_ATTR if plain else '')


def _strip_plain_attrs(text: str) -> str:
    """Remove attributes "{.plain}" of code spans from Markdown text.

    Args:
        text: Markdown text.

    Returns:
        `text` without "{.plain}" after code spans.
    """
    return ''.join(part.removesuffix(_PLAIN_ATTR) if i % 2 else part
                   for i, part in enumerate(_split_code_spans(text)))


def _split_code_spans(text: str) -> list[str]:
    """Split Markdown text to code spans and other text.

    Args:
        text: Markdown text.

    Returns:
        The parts of `text`: other text at even indices and code spans
        (including their delimiters and a possible attribute "{.plain}")
        at odd indices.
    """
    parts: list[str] = []
    pos = 0
    for mo in _CODE_SPAN_RE.finditer(text):
        parts.extend([text[pos:mo.start()], mo.group()])
        pos = mo.end()
    parts.append(text[pos:])
    return parts


def _style(text: str, style: tuple[str, str]) -> str:
    """Enclose text in escape sequences turning a style on and off.

    Args:
        text: The text to style.
        style: The escape sequences turning the style on and off, such
            as `_BOLD`.

    Returns:
        `text` enclosed in the escape sequences of `style`.
    """
    return style[0] + text + style[1]


def _render_inline(text: str, styled: bool = False) -> str:
    """Convert Markdown inline markup to plain or styled text.

    Convert links to "text <url>" and remove backslash escapes outside
    code spans. If `styled`, render code spans, strong emphasis and
    option names (such as --option or -o) in bold and emphasis
    underlined with ANSI escape sequences, removing the Markdown
    markup. Otherwise, remove backquotes only around code spans
    looking like structure tags (`<...>`) or followed by "{.plain}"
    and keep other markup (emphasis, other code spans) as is, as it
    reads well enough as plain text. Remove "{.plain}" in both cases.

    Args:
        text: Markdown text without block-level markup.
        styled: Whether to render the markup with styles.

    Returns:
        `text` converted to plain or styled text.
    """

    def protect(mo: re.Match[str]) -> str:
        """Return the escaped character in `mo` as a private-use one.

        This prevents the character from being treated as markup.
        """
        return chr(_PROTECT_BASE + ord(mo.group(1)))

    def unprotect(mo: re.Match[str]) -> str:
        """Return the protected character in `mo` as the original one."""
        return chr(ord(mo.group()) - _PROTECT_BASE)

    def bold(mo: re.Match[str]) -> str:
        """Return the first group of `mo` in bold."""
        return _style(mo.group(1), _BOLD)

    def underline(mo: re.Match[str]) -> str:
        """Return the first group of `mo` underlined."""
        return _style(mo.group(1), _UNDERLINE)

    parts = _split_code_spans(text)
    for i, part in enumerate(parts):
        if i % 2:
            plain = part.endswith(_PLAIN_ATTR)
            part = part.removesuffix(_PLAIN_ATTR)
            # The content of a code span neither begins nor ends with
            # a backquote
            code = part.strip('`')
            # As in CommonMark, strip one space from both sides
            if code.startswith(' ') and code.endswith(' ') and code.strip():
                code = code[1:-1]
            if styled:
                parts[i] = _style(code, _BOLD)
            elif plain or re.fullmatch(r'<[^`]+>', code):
                parts[i] = code
            else:
                parts[i] = part
        else:
            part = _ESCAPE_RE.sub(protect, part)
            part = _LINK_RE.sub(r'\1 <\2>', part)
            if styled:
                part = re.sub(r'\*\*(?=\S)(.+?)(?<=\S)\*\*', bold, part)
                part = re.sub(
                    r'(?<![\w*])\*(?=[^\s*])(.+?)(?<=[^\s*])\*(?![\w*])',
                    underline, part)
                part = re.sub(r'(?<!\w)_(?=\S)(.+?)(?<=\S)_(?!\w)',
                              underline, part)
                part = re.sub(
                    r'(?<![\w-])(--[A-Za-z][\w-]*|-[A-Za-z](?![\w-]))',
                    bold, part)
            parts[i] = _PROTECTED_RE.sub(unprotect, part)
    return ''.join(parts)


def can_style(file: TextIO | None = None) -> bool:
    """Return whether text written to a file may be styled.

    Follow the conventions of Python 3.13+ (`_colorize.can_colorize`):
    if environment variable PYTHON_COLORS is "0" or "1", disable or
    enable styling; otherwise, if NO_COLOR is non-empty, disable it,
    and if FORCE_COLOR is non-empty, enable it. Otherwise, style only
    if `file` is a terminal and TERM is not "dumb".

    Args:
        file: The file to which text is written (default:
            `sys.stdout`).

    Returns:
        `True` if text written to `file` may be styled with ANSI
        escape sequences.
    """
    if file is None:
        file = sys.stdout
    if not sys.flags.ignore_environment:
        python_colors = os.environ.get('PYTHON_COLORS')
        if python_colors in ('0', '1'):
            return python_colors == '1'
    if os.environ.get('NO_COLOR'):
        return False
    if os.environ.get('FORCE_COLOR'):
        return True
    if os.environ.get('TERM') == 'dumb':
        return False
    try:
        return file is not None and os.isatty(file.fileno())
    except (AttributeError, OSError, ValueError):
        return False


def _iter_blocks(lines: list[str]) -> Iterator[tuple[str, list[str], str]]:
    """Split the lines of Markdown text to blocks.

    Args:
        lines: The lines of Markdown text.

    Yields:
        Tuples (kind, block, marker), where kind is "blank", "code",
        "heading" or "para" (a paragraph or a list item); block
        contains the lines of the block without code fences, the
        indentation of code blocks, heading markers and list item
        markers (empty for "blank"); and marker is the indentation and
        marker of a list item followed by a space (such as "- "), or
        "" for other blocks.
    """

    def is_para_end(line: str, in_item: bool) -> bool:
        """Return `True` if `line` ends a paragraph or a list item.

        As in CommonMark, any list item ends a list item, but only a
        non-empty bulleted list item or a numbered one beginning with
        1 ends (interrupts) a paragraph.
        """
        if not line.strip() or _FENCE_RE.match(line) or _HEADING_RE.match(line):
            return True
        if not (mo := _LIST_ITEM_RE.match(line)):
            return False
        return in_item or bool(
            mo.group('text')
            and mo.group('marker').rstrip('.)') in ('-', '*', '+', '1'))

    i = 0
    prev_blank = True
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            yield 'blank', [], ''
            prev_blank = True
            i += 1
            continue
        if mo := _FENCE_RE.match(line):
            fence = mo.group('fence')
            indent = len(mo.group('indent'))
            block: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].lstrip().startswith(fence):
                block.append(lines[i][indent:]
                             if not lines[i][:indent].strip()
                             else lines[i].lstrip())
                i += 1
            i += 1
            yield 'code', block, ''
        elif prev_blank and line.startswith('    '):
            block = []
            while i < len(lines) and (lines[i].startswith('    ')
                                      or not lines[i].strip()):
                block.append(lines[i][4:])
                i += 1
            # Leave trailing blank lines to be yielded as blanks
            while block and not block[-1].strip():
                block.pop()
                i -= 1
            yield 'code', block, ''
        elif mo := _HEADING_RE.match(line):
            yield 'heading', [mo.group('text')], ''
            i += 1
        else:
            # A paragraph or a list item
            marker = ''
            if mo := _LIST_ITEM_RE.match(line):
                marker = mo.group('indent') + mo.group('marker') + ' '
                line = mo.group('text') or ''
            block = [line]
            i += 1
            while i < len(lines) and not is_para_end(lines[i], bool(marker)):
                block.append(lines[i])
                i += 1
            yield 'para', block, marker
        prev_blank = False


def visible_len(text: str) -> int:
    """Return the visible length of text.

    Args:
        text: Text possibly containing ANSI SGR escape sequences.

    Returns:
        The length of `text` excluding ANSI SGR escape sequences.
    """
    return len(_SGR_RE.sub('', text))


def _update_styles(active: list[str], text: str) -> None:
    """Update a list of active SGR codes with the codes in text.

    Args:
        active: The SGR codes of the active styles (keys of
            `_SGR_OFF`), modified in place.
        text: Text possibly containing ANSI SGR escape sequences.
    """
    for mo in _SGR_RE.finditer(text):
        code = mo.group('params')
        if code in ('', '0'):
            active.clear()
        elif code in _SGR_OFF:
            if code not in active:
                active.append(code)
        else:
            for on_code, off_code in _SGR_OFF.items():
                if code == off_code and on_code in active:
                    active.remove(on_code)


def wrap_text(text: str, width: int, initial_indent: str = '',
              subsequent_indent: str = '') -> list[str]:
    """Wrap text to lines of at most a given width.

    Break lines only at whitespace (keeping hyphenated words intact),
    and put words longer than `width` on lines of their own. ANSI SGR
    escape sequences for bold, italics and underline (and resetting
    them) are not counted in the line width, and styles continuing
    over a line break are turned off at the end of the line and back
    on after the indentation of the next line.

    Without escape sequences, the result is the same as that of
    `textwrap.wrap` with `break_on_hyphens=False` and
    `break_long_words=False`.

    Args:
        text: The text to wrap.
        width: The maximum width of lines, including indentation.
        initial_indent: The indentation of the first line.
        subsequent_indent: The indentation of the other lines.

    Returns:
        The wrapped lines of `text`, without newlines.
    """
    # Only ASCII whitespace, as in textwrap, so that a no-break space
    # does not allow a line break
    text = re.sub(r'[\n\x0b\x0c\r]', ' ', text.expandtabs())
    chunks = [chunk for chunk in re.split(r'( +)', text) if chunk]
    # The wrapped lines as (indent, line)
    lines: list[tuple[str, str]] = []
    i = 0
    while i < len(chunks):
        if lines and not chunks[i].strip():
            # Drop whitespace at the beginning of a line (except the
            # first one)
            i += 1
            continue
        indent = subsequent_indent if lines else initial_indent
        avail = width - len(indent)
        line_chunks: list[str] = []
        line_len = 0
        while i < len(chunks):
            chunk_len = visible_len(chunks[i])
            if line_len + chunk_len > avail:
                break
            line_chunks.append(chunks[i])
            line_len += chunk_len
            i += 1
        if not line_chunks:
            # A word longer than width
            line_chunks.append(chunks[i])
            i += 1
        if not line_chunks[-1].strip():
            line_chunks.pop()
        if line_chunks:
            lines.append((indent, ''.join(line_chunks)))
    # Turn off styles at the end of each line and on at the beginning
    # of the next one
    result: list[str] = []
    # The SGR codes of the styles active at the end of the line
    active: list[str] = []
    for indent, line in lines:
        prefix = ''.join(f'\x1b[{code}m' for code in active)
        _update_styles(active, line)
        suffix = ''.join(f'\x1b[{_SGR_OFF[code]}m'
                         for code in reversed(active))
        result.append(indent + prefix + line + suffix)
    return result


def _wrap_inline(lines: list[str], width: int, first_indent: str = '',
                 indent: str = '', styled: bool = False) -> list[str]:
    """Wrap the lines of a Markdown paragraph, honouring hard breaks.

    Args:
        lines: The lines of a paragraph or list item.
        width: The maximum width of output lines.
        first_indent: The indentation of the first output line.
        indent: The indentation of the other output lines.
        styled: Whether to render inline markup with styles (bold,
            underline) instead of as plain text.

    Returns:
        The wrapped lines.
    """
    # Split at hard line breaks (trailing backslash)
    segments: list[list[str]] = [[]]
    for line in lines:
        line = line.rstrip()
        if line.endswith('\\') and not line.endswith('\\\\'):
            segments[-1].append(line[:-1])
            segments.append([])
        else:
            segments[-1].append(line)
    result: list[str] = []
    for segment in segments:
        if not segment:
            continue
        text = _render_inline(' '.join(line.strip() for line in segment),
                              styled)
        result.extend(
            wrap_text(text, width,
                      initial_indent=(indent if result else first_indent),
                      subsequent_indent=indent)
            or [first_indent.rstrip()])
    return result


def markdown_to_plain_lines(text: str, width: int,
                            styled: bool = False) -> list[str]:
    """Convert Markdown text to wrapped plain-text lines.

    See the module docstring for the supported Markdown subset.

    Args:
        text: Markdown text, with indentation normalized.
        width: The maximum width of output lines (except for code
            blocks and words longer than `width`).
        styled: Whether to render headings and inline markup with
            styles (bold, underline) using ANSI escape sequences.

    Returns:
        The lines of `text` converted to plain text.
    """
    result: list[str] = []
    for kind, block, marker in _iter_blocks(text.split('\n')):
        if kind == 'blank':
            if result and result[-1]:
                result.append('')
        elif kind == 'code':
            result.extend(('    ' + line).rstrip() for line in block)
        elif kind == 'heading':
            heading = _render_inline(block[0])
            if heading[-1:].isalnum():
                heading += ':'
            result.append(_style(heading, _BOLD) if styled else heading)
        else:
            result.extend(_wrap_inline(block, width, marker,
                                       ' ' * len(marker), styled))
    while result and not result[-1]:
        result.pop()
    return result


class MarkdownHelpFormatter(argparse.HelpFormatter):

    """Help formatter for Markdown texts with marked detail levels.

    Select the content for detail level `detail` (by default,
    `DETAIL_SHORT`) from the description, epilog, group descriptions
    and argument help texts, and render them as plain text, styled
    if standard output allows it (see `can_style`). Unlike
    `argparse.HelpFormatter`, keep paragraph breaks, list items and
    code blocks, wrapping paragraphs and list items separately.
    """

    detail = DETAIL_SHORT
    """Detail level of help texts"""

    @functools.cached_property
    def _styled(self) -> bool:
        """`True` if help texts are to be styled."""
        return can_style()

    def _split_lines(self, text: str, width: int) -> list[str]:
        """Convert an argument help text to lines (see `_fill_text`).

        Return `[""]` if the help text is empty at the detail level, as
        argparse requires at least one line.
        """
        return markdown_to_plain_lines(select_detail(text, self.detail),
                                       width, self._styled) or ['']

    def _fill_text(self, text: str, width: int, indent: str) -> str:
        """Convert a description or epilog to wrapped plain text.

        Args:
            text: Markdown text with marked detail levels.
            width: The maximum width of lines, including `indent`.
            indent: The indentation of each line.

        Returns:
            The content of `text` for detail level `detail` as wrapped
            plain text, styled if `_styled`.
        """
        return '\n'.join(
            (indent + line).rstrip()
            for line in self._split_lines(text, width - len(indent)))

    def format_help(self) -> str:
        """Return the help message, without trailing whitespace on lines."""
        # argparse indents also the empty lines between paragraphs in
        # argument help texts
        return re.sub(r'[ \t]+\n', '\n', super().format_help())


class FullMarkdownHelpFormatter(MarkdownHelpFormatter):

    """Help formatter for Markdown texts at full detail level."""

    detail = DETAIL_FULL


def _make_doc_formatter(parser: argparse.ArgumentParser
                        ) -> argparse.HelpFormatter:
    """Make a help formatter for generating Markdown documentation.

    Use a fixed width to make the output reproducible and disable
    colours (Python 3.14+).

    Args:
        parser: The parser to be documented.

    Returns:
        An instance of the formatter class of `parser`.
    """
    # Any, as the constructor arguments vary by Python version
    formatter_class: Any = parser.formatter_class
    try:
        return formatter_class(prog=parser.prog, width=80, color=False)
    except TypeError:
        return formatter_class(prog=parser.prog, width=80)


def _format_invocation(formatter: argparse.HelpFormatter,
                       action: argparse.Action) -> list[str]:
    """Format the ways to invoke an argument for Markdown documentation.

    The format does not depend on the Python version, unlike that of
    `HelpFormatter._format_action_invocation`.

    Args:
        formatter: The help formatter of the parser.
        action: The argument (action) to be documented.

    Returns:
        The ways to invoke `action`, such as ["--out file", "-o file"]
        for an option or ["file"] for a positional argument.
    """
    if not action.option_strings:
        default = formatter._get_default_metavar_for_positional(action)
        return [formatter._metavar_formatter(action, default)(1)[0]]
    if action.nargs == 0:
        return list(action.option_strings)
    default = formatter._get_default_metavar_for_optional(action)
    args_string = formatter._format_args(action, default)
    return [f'{option} {args_string}' for option in action.option_strings]


def _format_text(text: str | None, prog: str) -> str:
    """Format a description or epilog for Markdown documentation.

    Args:
        text: Markdown text with marked detail levels, or `None`.
        prog: The program name, to replace `%(prog)s` in `text`.

    Returns:
        `text` at full detail level, with `%(prog)s` expanded, or ""
        if `text` is empty or `None`.
    """
    if not text:
        return ''
    if '%(prog)' in text:
        text = text % dict(prog=prog)
    return _strip_plain_attrs(select_detail(text, DETAIL_FULL))


def format_markdown_doc(parser: argparse.ArgumentParser) -> str:
    """Format documentation for an argument parser as Markdown.

    The output contains the full detail level of the texts in
    `parser`. It begins with a level-1 heading with the program name,
    followed by sections "Synopsis", "Description" and "Arguments",
    and finally the epilog, preceded by heading "Notes" unless it
    begins with a heading of its own.
    Under "Arguments", each argument group has a level-3 heading and
    each argument a level-4 heading containing the ways to invoke it
    as inline code. The output is intended to render properly both on
    GitHub and with Pandoc.

    Args:
        parser: The parser to be documented.

    Returns:
        The documentation for `parser` in Markdown.
    """
    formatter = _make_doc_formatter(parser)
    usage = formatter._format_usage(parser.usage, parser._actions,
                                    parser._mutually_exclusive_groups,
                                    prefix='')
    parts = [
        f'# {parser.prog}',
        '## Synopsis',
        '```\n' + usage.strip('\n') + '\n```',
    ]
    if description := _format_text(parser.description, parser.prog):
        parts.extend(['## Description', description])
    parts.append('## Arguments')
    for group in parser._action_groups:
        actions = [action for action in group._group_actions
                   if action.help is not argparse.SUPPRESS]
        if not actions:
            continue
        title = group.title or ''
        title = _GROUP_TITLES.get(title, title[:1].upper() + title[1:])
        parts.append(f'### {title}')
        if group_description := _format_text(group.description, parser.prog):
            parts.append(group_description)
        for action in actions:
            invocation = ', '.join(
                f'`{inv}`' for inv in _format_invocation(formatter, action))
            parts.append(f'#### {invocation}')
            if action.help and (help_text := _strip_plain_attrs(
                    select_detail(formatter._expand_help(action),
                                  DETAIL_FULL))):
                parts.append(help_text)
    if epilog := _format_text(parser.epilog, parser.prog):
        # Without a heading of its own, the epilog would appear to
        # belong to the description of the last argument
        if not _HEADING_RE.match(epilog.split('\n', 1)[0]):
            parts.append('## Notes')
        parts.append(epilog)
    return '\n\n'.join(parts) + '\n'


class _HelpAction(argparse.Action):

    """Base class for actions printing help and exiting."""

    def __init__(self, option_strings: Sequence[str],
                 dest: str = argparse.SUPPRESS,
                 default: Any = argparse.SUPPRESS,
                 help: str | None = None):
        """Initialize the action, taking no arguments.

        Args:
            option_strings: The option strings of the action.
            dest: The attribute of the namespace for the action (not
                used).
            default: The default value (not used).
            help: The help text of the action.
        """
        super().__init__(option_strings=option_strings, dest=dest,
                         default=default, nargs=0, help=help)


class FullHelpAction(_HelpAction):

    """Action printing full help as plain text and exiting."""

    def __call__(self, parser: argparse.ArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: str | None = None) -> None:
        """Print full help for `parser` and exit."""
        parser.formatter_class = FullMarkdownHelpFormatter
        parser.print_help()
        parser.exit()


class MarkdownDocAction(_HelpAction):

    """Action printing documentation in Markdown and exiting."""

    def __call__(self, parser: argparse.ArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: str | None = None) -> None:
        """Print Markdown documentation for `parser` and exit."""
        print(format_markdown_doc(parser), end='')
        parser.exit()


def uses_markdown_help(parser: argparse.ArgumentParser) -> bool:
    """Return whether Markdown help is enabled for a parser.

    Args:
        parser: The parser to check.

    Returns:
        `True` if `enable_markdown_help` has been called for `parser`
        (its formatter class is `MarkdownHelpFormatter` or a subclass).
    """
    formatter_class = parser.formatter_class
    return (isinstance(formatter_class, type)
            and issubclass(formatter_class, MarkdownHelpFormatter))


def enable_markdown_help(
        parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Enable Markdown help texts with detail levels for a parser.

    Set the formatter class of `parser` to `MarkdownHelpFormatter`
    and add the options --help-full for printing full help and the
    hidden --help-markdown for printing documentation in Markdown.

    The description, epilog, group descriptions and argument help
    texts of `parser` are then treated as Markdown with marked detail
    levels (see the module docstring), regardless of whether they are
    added before or after calling this function.

    Args:
        parser: The parser for which to enable Markdown help.

    Returns:
        `parser`, modified in place.
    """
    parser.formatter_class = MarkdownHelpFormatter
    parser.add_argument('--help-full', action=FullHelpAction,
                        help='show full help message and exit')
    parser.add_argument('--help-markdown', action=MarkdownDocAction,
                        help=argparse.SUPPRESS)
    return parser
