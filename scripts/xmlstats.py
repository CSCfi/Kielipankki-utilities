#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs
import re

import xml.sax as sax
import xml.sax.handler as saxhandler

from optparse import OptionParser


class IncrDict(dict):

    def __init__(self, init_val=0, init_func=None):
        dict.__init__(self)
        self._init_func = init_func or (lambda: init_val)

    def incr(self, key, step=1):
        if key not in self:
            self[key] = self._init_func()
        self[key] += step

    def decr(self, key, step=1):
        if key not in self:
            self[key] = self._init_func()
        self[key] -= step


class MaxDict(dict):

    def __init__(self):
        dict.__init__(self)

    def max(self, key, val):
        if key not in self:
            self[key] = val
        else:
            self[key] = max(self[key], val)


class DictDict(dict):

    def __init__(self, inner_type=dict, init_func=None):
        dict.__init__(self)
        self._init_func = init_func or (lambda: inner_type())

    def apply(self, key1, key2, func=dict.__setitem__, *args, **kwargs):
        if key1 not in self:
            self[key1] = self._init_func()
        func(self[key1], key2, *args, **kwargs)


class DictDictDict(dict):

    def __init__(self, inner_type=dict, init_func=None):
        dict.__init__(self)
        self._init_func = init_func or (lambda: inner_type())

    def apply(self, key1, key2, key3, func=dict.__setitem__, *args, **kwargs):
        if key1 not in self:
            self[key1] = {}
        if key2 not in self[key1]:
            self[key1][key2] = self._init_func()
        func(self[key1][key2], key3, *args, **kwargs)


class XMLStatCounter(saxhandler.ContentHandler):

    def __init__(self, opts):
        self._opts = opts
        self._parser = sax.make_parser()
        self._parser.setContentHandler(self)
        self._elemnames = []
        self._elemcounts = IncrDict()
        self._elem_attr_counts = DictDict(inner_type=IncrDict)
        self._elem_attr_value_counts = DictDictDict(inner_type=IncrDict)
        self._elem_max_nesting = MaxDict()
        self._elem_elem_counts = DictDict(inner_type=IncrDict)
        self._open_elems = IncrDict()
        self._elemstack = []
        self._prev_event = None

    def add_stats(self, f):
        self._parser.parse(f)

    def startElement(self, name, attrs):
        if name not in self._elemcounts:
            self._elemnames += [name]
        self._elemcounts.incr(name)
        self._open_elems.incr(name)
        for attrname in attrs.getNames():
            self._elem_attr_counts.apply(name, attrname, IncrDict.incr)
            if self._opts.attr_values:
                self._elem_attr_value_counts.apply(
                    name, attrname, attrs.get(attrname), IncrDict.incr)
        if self._elemstack:
            self._elem_elem_counts.apply(self._elemstack[-1], name,
                                         IncrDict.incr)
        self._elemstack.append(name)
        self._prev_event = 'start'

    def endElement(self, name):
        self._elem_max_nesting.max(name, self._open_elems[name])
        self._open_elems.decr(name)
        self._elemstack.pop()
        self._prev_event = 'end'

    def characters(self, content):
        if self._prev_event != 'text' and content.strip():
            self._elem_elem_counts.apply(self._elemstack[-1], '', IncrDict.incr)
            self._prev_event = 'text'

    def format_stats(self):
        result = ''
        for elemname in self._elemnames:
            result += '{name:10} {nesting:2d} {count:6d}\n'.format(
                name=elemname, nesting=self._elem_max_nesting[elemname],
                count=self._elemcounts[elemname])
            result += self._make_subcounts(
                elemname, self._elem_attr_counts,
                format=u'  @{name:10} {count:6d}\n',
                subelem_dict=self._elem_attr_value_counts,
                subelem_args=dict(format=u'    {name:9} {count:6d}\n',
                                  name_format=u'"{name}"',
                                  limit=self._opts.max_attr_values))
            result += self._make_subcounts(
                elemname, self._elem_elem_counts,
                format=u'  {name:11} {count:6d}\n', name_map={'': '#DATA'})
        return result

    def _make_subcounts(self, elemname, elem_dict, format=u'{name} {count}\n',
                        name_format=u'{name}', name_map={}, limit=None,
                        subelem_dict=None, subelem_args={}):
        result = ''
        names = elem_dict.get(elemname, {}).keys()
        names.sort()
        if limit is None or limit < 0:
            limit = len(names)
        for name in names[:limit]:
            formatted_name = name_format.format(name=name_map.get(name, name))
            result += format.format(name=formatted_name,
                                    count=elem_dict[elemname][name])
            if subelem_dict:
                result += self._make_subcounts(name, subelem_dict[elemname],
                                               **subelem_args)
        if limit < len(names):
            format_prefix = re.match(r'([^\{]*)', format).group(1)
            result += format_prefix + '...\n'
        return result


class XMLFileStats(object):

    def __init__(self, opts):
        self._opts = opts

    def process_files(self, files):
        if isinstance(files, list):
            for file_ in files:
                self.process_files(file_)
        elif isinstance(files, basestring):
            # codings.open() is not used so that the XML parser can
            # use the encoding from the input
            with open(files, 'r') as f:
                self.calc_file_stats(f, files)
        else:
            self.calc_file_stats(files)

    def calc_file_stats(self, f, fname=None):
        if fname != None:
            sys.stdout.write(fname + ':\n')
        stat_counter = XMLStatCounter(self._opts)
        stat_counter.add_stats(f)
        sys.stdout.write(stat_counter.format_stats())


def getopts():
    optparser = OptionParser()
    optparser.add_option('--attr-values', '--attribute-values',
                         action='store_true', default=False)
    optparser.add_option('--max-attr-values', '--maximum-attribute-values',
                         type='int', default=20)
    (opts, args) = optparser.parse_args()
    return (opts, args)


def main():
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    file_stats = XMLFileStats(opts)
    file_stats.process_files(args if args else sys.stdin)


if __name__ == "__main__":
    main()
