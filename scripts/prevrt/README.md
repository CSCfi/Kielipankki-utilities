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

    <!-- Positional attributes: word lemma pos -->

Field names facilitate further annotation of tokens regardless of what
previous annotations exist.

A minor innovation is the use of auxiliary formats to facilitate the
production of VRT from other formats and manipulation of large VRT
corpora in conveniently sized fragments.

Most of the tools transform an input document into an output document.
Such tools have a common set of options that allow them to compose
flexibly in different ways:
- read from a named file or from standard input;
- write to standard output, or
- write to a explicitly named file, or
- write to a sibling to the input file, or
- replace the input file with the output,
- with optional backup of the input file.

In case of failure, any partial output is left in a transparently
named temporary file.

## To be continued
