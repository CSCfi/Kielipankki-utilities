#! /usr/bin/env python


# vrt-break-structs.py
#
# Insert structure breaks to VRT input at positions with the specified
# contexts.
#
# Jyrki Niemi 2018-01-12


import sys
import re
import codecs

import korpimport.util as korputil


class VrtStructBreaker(korputil.InputProcessor):

    def __init__(self, args=None, **kwargs):
        self._contexts_re = None
        super(VrtStructBreaker, self).__init__(args=args, **kwargs)

    def process_input_stream(self, stream, filename=None):
        self._make_contexts_re()
        text = ''.join(line for line in stream)
        text = self._insert_breaks(text)
        sys.stdout.write(text)

    def _make_contexts_re(self):

        def make_context_re(context):
            left, right = context.split('|', 1)
            # print repr(r'(' + make_tokens_re(left) + r'(?:</.+?>\s*\n)*)'
            #        + r'((?:<[^/].+?>\s*\n)*' + make_tokens_re(right) + r')')
            return re.compile(
                '(' + make_tokens_re(left) + '(?:</.+?>\\s*\n)*)'
                + '((?:<[^/].+?>\\s*\n)*' + make_tokens_re(right) + ')',
                re.UNICODE | re.MULTILINE)

        def make_tokens_re(s):
            tokens = s.split()
            return (u'(?:<.+?>\\s*\n)*'.join(
                u'^{tok}(?:\t.*?)?\n'.format(tok=re.escape(token))
                for token in tokens))

        if self._opts.context_file:
            contexts = self._read_context_file()
        else:
            contexts = [context.decode(self._input_encoding)
                     for context in self._opts.context]
        self._contexts_re = [make_context_re(context) for context in contexts]

    def _read_context_file(self):
        contexts = []
        with codecs.open(self._opts.context_file,
                         encoding=self._input_encoding) as pf:
            for line in pf:
                # Test for # before stripping, so that a literal # may
                # be represented by prepending a space
                if line[0] == '#':
                    continue
                line = line.strip()
                if line and line[0] != '#':
                    contexts.append(line)
        return contexts

    def _insert_breaks(self, text):
        repl_patt = ((ur'\1</{struct}>\n<{struct}>\n\2')
                     .format(struct=self._opts.struct))
        for context_re in self._contexts_re:
            # print context_re.context
            text = context_re.sub(repl_patt, text)
        return text

    def getopts(self, args=None):
        self.getopts_basic(
            dict(usage="""%prog [options] [input] > output

Insert structure (structural attribute) breaks (</STRUCT> <STRUCT>) to VRT
input at positions with the specified contexts. Each context is of the form
LEFT|RIGHT where LEFT and RIGHT are space-sparated lists of word forms (the
first positional attribute in the VRT input) preceding and following the
structure break to be inserted.

The structure break is inserted after the end tags and before the start tags
between LEFT and RIGHT. Note that any other possibly open structures are not
closed and reopened."""),
                 args,
                 ['struct|element=STRUCT',
                  dict(help='insert structure (element) STRUCT')],
                 ['context=CONTEXT',
                  dict(action='append',
                       help='insert at position specified by CONTEXT')],
                 ['context-file=FILE',
                  dict(help=('read contexts from FILE, one per line;'
                             ' empty lines and lines beginning with a #'
                             ' are ignored'))])
        if self._opts.struct is None:
            self.error('Please specify --struct', show_fileinfo=False)
        if self._opts.context is None and self._opts.context_file is None:
            self.error('Please specify either --context or --context-file',
                       show_fileinfo=False)


if __name__ == '__main__':
    VrtStructBreaker().run()
