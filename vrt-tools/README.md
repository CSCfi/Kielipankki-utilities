# FIN-CLARIN VRT Tools

These command-line tools implement composable manipulations of
segmented and annotated text in a VRT format aka *verticalized text*,
related to Corpus WorkBench that is used in the backend to the Korp
concordance enginge.

The VRT tools proper include (or are planned to include)
- generic and special format manipulations
- tokenization to produce VRT from a preliminary format (initially
  UDPipe tokenizers, soon also HFST tokenizers)
- morphosyntactic annotators (initially Finnish pipeline from Turku NLP)
- name recognition (FiNER planned soon)
- report generation (sentence length already implemented)
- conversion to other formats (to be planned)

Some tools depend on separate programs and models that are installed
in the Taito command-line environment. These are typically free
software, available for installation elsewhere.

## Highlights

The basic function of the VRT tools is to **preserve previous
annotations**, including structural markup that may contain valuable
information about the text units, without the underlying tools even
knowing that their input sentences are extracted from such context.
New annotations from an underlying tool are **added to their proper
place in the input document**.

The major innovation in FIN-CLARIN VRT is the use of **names** for the
fields that are only positional in basic format. In the basic format
the declaration of names is only a **comment** but these VRT tools use
it extensively.

    <!-- #vrt positional-attributes: word lemma pos -->

Field names facilitate further annotation of tokens regardless of what
previous annotations exist.

(Please note that the format of the attribute name comment was changed
slightly for VRT tools version 0.7.2 (2019-04-05). The old-format
comment with ``Positional attributes`` instead of ``#vrt
positional-attributes`` is still recognized by the tools.)

A minor innovation is the use of auxiliary formats to facilitate the
production of VRT from other formats and manipulation of large VRT
corpora in conveniently sized fragments.

Most of the tools transform an input document into an output document.
Such tools have a common set of options that allow them to compose
flexibly in different ways:
- read from a named file or from standard input;
- write to standard output, or
- write to an explicitly named file, or
- write to a sibling to the input file, or
- replace the input file with the output,
- with an optional backup file.

In case of failure, any partial output is left in a transparently
named temporary file.

## Documentation

Run a tool with `-h` for a short usage message. Tools using Markdown
help (see below) also have `--help-full` for full help, and their
documentation is available in Markdown in [`docs/tools/`](docs/tools/).

### Markdown help texts with detail levels

The description, epilog, argument group descriptions and argument
help texts of a tool can be written in a subset of Markdown with
marked detail levels. The short usage message (`-h`), the full help
(`--help-full`) and the Markdown documentation (`--help-markdown`,
not shown in the usage message) are then all generated from them.

Content shown only in the full help and documentation is marked as
`::: long` … `:::` and content shown only in the short usage message
as `::: short` … `:::`, or inline as `[…]{.long}` and `[…]{.short}`:

    add missing attributes with value str, to all attributes or only
    to those matching attr-regex-list

    ::: long
    attr-regex-list is a list of attribute name regular expressions,
    separated by spaces or commas. ...
    :::

The supported Markdown consists of paragraphs, lists, code blocks,
headings and inline markup. Precede a list with a blank line, as
Pandoc does not otherwise recognize it. Literal structure tags must
be written as inline code (`` `<ne>` ``), and characters such as `*`
and `_` in literal values should be within inline code.

In plain-text help, inline code keeps its backquotes, except for
structure tags and inline code followed by `{.plain}`, as in
`` `"_"`{.plain} ``; `{.plain}` is removed from the Markdown
documentation. `vrtargsoolib` uses it for the default value that it
appends to the first paragraph of an argument help text, as in
“(default: `` `"_"`{.plain} ``)”, unless the help text contains the
word “default” anywhere, also in content marked `long`.

When the help is written to a terminal, inline code, option names and
headings are shown in bold and emphasis (`*arg*`) underlined, as in
man pages; set `NO_COLOR=1` (or `PYTHON_COLORS=0`) to disable this.
See the docstring of [`libvrt/mdhelp.py`](libvrt/mdhelp.py) for
details.

To enable Markdown help for a tool:

- with `vrtargsoolib`: set `markdown_help = True` in the class
  `OPTIONS` of the tool class:

      class OPTIONS(InputProcessor.OPTIONS):
          markdown_help = True

- with `libvrt.args` or plain `argparse`: call
  `libvrt.mdhelp.enable_markdown_help(parser)` after creating the
  parser, for example, after `parser = transput_args(...)`.

### Generating documentation

After changing the help texts of a tool using Markdown help, or
enabling or disabling Markdown help for a tool, run
`docs/make-tool-docs` to update the Markdown documentation and its
index in `docs/tools/`; do not edit the generated files by hand. A
test (`tests/test_tool_docs.py`) checks that they are up to date.

Without arguments, `docs/make-tool-docs` documents all tools using
Markdown help and removes the documentation of other tools; with tool
names as arguments, it updates only their documentation and the
index. In a Git working tree, it finds the tools among the scripts
tracked by Git, so run `git add` for the script of a new tool first:
otherwise, its documentation is removed, and the test reports it as
obsolete.

`docs/make-tool-docs --html DIR` and `--man DIR` also generate HTML
and man pages with [Pandoc](https://pandoc.org/), for example, to
`docs/build/` (not version-controlled). To view a man page, run
`man -l DIR/man1/tool.1`.

## To be continued
