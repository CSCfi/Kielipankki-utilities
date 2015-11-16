#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""
Transform VRT input using XSLT.

The VRT input needs to be valid XML with no crossing elements but
without an XML declaration.
"""


# TODO:
# - Maybe add a default transformation to fulltext HTML to be used if
#   --xslt-stylesheet is not specified.


import sys
import re
import io

from lxml import etree

import korpimport.util as korputil
import korpimport.vrtxml as vrtxml


class VrtTransformer(korputil.InputProcessor):

    def __init__(self, args=None):
        self._transform = None
        super(VrtTransformer, self).__init__(args=args)

    def process_input_stream(self, stream, filename=None):

        def sub_xpath(mo):
            result_elem = text_elem.xpath(mo.group(1))[0]
            if isinstance(result_elem, bytes):
                return result_elem
            else:
                return etree.tostring(result_elem)

        with vrtxml.VrtXmlSplitReader(
                stream, pos_attr_names=self._opts.pos_attrs, number_tokens=True,
                token_numbering_reset_regex=r'^<sentence\b') as vrt_reader:
            for text_elem in vrt_reader:
                result = self._transform(text_elem)
                if self._opts.output_filename_template:
                    filename = re.sub(ur'{(?:xpath:)?(.*?)}', sub_xpath,
                                      self._opts.output_filename_template)
                    # print 'filename', filename
                    with io.open(filename, 'wb') as outf:
                        outf.write(bytes(result))
                else:
                    sys.stdout.write(unicode(result))

    def getopts(self, args=None):
        self.getopts_basic(
            dict(usage="%progname [options] [input] > output"),
            args,
            ['--xslt-stylesheet'],
            ['--pos-attrs', '--pos-attribute-names'],
            ['--output-filename-template'],
        )
        if self._opts.pos_attrs:
            self._opts.pos_attrs = re.split(r'[\s,]+', self._opts.pos_attrs)
        if self._opts.xslt_stylesheet:
            xslt = etree.parse(self._opts.xslt_stylesheet)
            self._transform = etree.XSLT(xslt)
        else:
            sys.stderr.write('Please specify an XSLT transformation stylesheet'
                             ' with --xslt-stylesheet\n')
            exit(1)


if __name__ == "__main__":
    VrtTransformer().run()
