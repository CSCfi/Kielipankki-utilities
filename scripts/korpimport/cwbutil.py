# -*- coding: utf-8 -*-


"""
Module korpimport.cwbutil

Common utilities wrapping calls to CWB utility programs.
"""


import re

from subprocess import Popen, PIPE


class CWBError(Exception):
    """An error from a CWB utility program."""


class CWBCorpusAccessError(CWBError):
    """Error in accessing a CWB corpus."""
    # TODO: The corpus whose access caused the error as a parameter


class CWBCorpusInfo(object):

    """
    Wrap corpus information obtained from cwb-describe-corpus.

    The public attributes `attributes` and `attrdict` contain
    attribute information from ``cwb-describe-corpus``.
    """

    def __init__(self, corpus_id):
        self._corpus_id = corpus_id
        self.attributes = {
            'pos': [],
            'struct': [],
            'align': [],
        }
        self._attrtype_map = {'p': 'pos', 's': 'struct', 'a': 'align'}
        for key, val in self._attrtype_map.iteritems():
            self.attributes[key] = self.attributes[val]
        self.attrdict = {}
        self._describe_corpus()

    def _describe_corpus(self):
        proc = Popen(['cwb-describe-corpus', '-s', self._corpus_id],
                     stdout=PIPE, stderr=PIPE, bufsize=-1)
        stdout, stderr = proc.communicate()
        if stderr:
            # TODO: Raise CWBCorpusAccessError if the error is in
            # accessing the corpus
            raise CWBError('Error in cwb-describe-corpus:\n'
                           + stderr.rstrip('\n'))
        for line in stdout.split('\n'):
            if line[1:5] == '-ATT':
                mo = re.match(
                    r'''(?P<type> [psa]) -ATT \s+
                        (?P<name> \S+) \s+
                        (?:
                            (?P<numtokens> \d+) \s+ tokens, \s+
                            (?P<numtypes> \d+) \s+ types
                          | (?P<numregions> \d+) \s+ regions
                          | (?P<numblocks> \d+) \s+ alignment \s blocks
                        )''',
                    line, re.VERBOSE)
                attrprops = mo.groupdict()
                self.attrdict[attrprops['name']] = attrprops
                self.attributes[attrprops['type']].append(attrprops)
