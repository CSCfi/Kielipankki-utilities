#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs
import re

import xml.sax as sax
import xml.sax.handler as saxhandler

from optparse import OptionParser

from xml2vrt.util import WrappedXMLFileReader


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
        # print '<name>'
        if self._opts.wrapper_elem and name == self._opts.wrapper_elem:
            return
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
        # print '</name>'
        if self._opts.wrapper_elem and name == self._opts.wrapper_elem:
            return
        self._elem_max_nesting.max(name, self._open_elems[name])
        self._open_elems.decr(name)
        self._elemstack.pop()
        self._prev_event = 'end'

    def characters(self, content):
        if self._prev_event != 'text' and content.strip():
            self._elem_elem_counts.apply(self._elemstack[-1], '', IncrDict.incr)
            self._prev_event = 'text'

    def format_stats(self):
        elemname_maxlen = max([len(name) for name in self._elemnames])
        attrname_maxlen = max(
            [len(attrname) for elemname in self._elemnames
             for attrname in self._elem_attr_counts.get(elemname, [])])
        # FIXME: This does not take into account the possible limit on
        # the number of attribute values to be printed.
        attrval_maxlen = (
            max([len(value) for elemname in self._elemnames
                 for attrname in self._elem_attr_counts.get(elemname, [])
                 for value in (self._elem_attr_value_counts.get(elemname, {})
                               .get(attrname, []))])
            if self._opts.attr_values else 0)
        namewidth = min(70, max(elemname_maxlen, attrname_maxlen + 1,
                                attrval_maxlen + 4))
        result = ''
        for elemname in self._elemnames:
            result += '{name:{namewidth}} {nesting:2d} {count:6d}\n'.format(
                name=elemname, namewidth=namewidth,
                nesting=self._elem_max_nesting[elemname],
                count=self._elemcounts[elemname])
            result += self._make_subcounts(
                elemname, self._elem_attr_counts,
                format=u'  @{name:{namewidth}} {count:6d}\n',
                namewidth=namewidth,
                subelem_dict=self._elem_attr_value_counts,
                subelem_args=dict(format=u'    {name:{namewidth}} {count:6d}\n',
                                  namewidth=namewidth - 1,
                                  name_format=u'"{name}"',
                                  limit=self._opts.max_attr_values))
            result += self._make_subcounts(
                elemname, self._elem_elem_counts,
                format=u'  {name:{namewidth}} {count:6d}\n',
                namewidth=namewidth + 1, name_map={'': '#DATA'})
        return result

    def format_cwb_struct_attrs(self):
        eleminfo = []
        for elemname in self._elemnames:
            eleminfo.append(
                '+'.join([elemname + ':'
                          + str(self._elem_max_nesting[elemname] - 1)]
                         + self._elem_attr_counts.get(elemname, {}).keys()))
        return ' '.join(eleminfo) + '\n'

    def _make_subcounts(self, elemname, elem_dict, format=u'{name} {count}\n',
                        name_format=u'{name}', name_map={}, limit=None,
                        subelem_dict=None, subelem_args={},
                        **extra_format_args):
        result = ''
        names = elem_dict.get(elemname, {}).keys()
        names.sort()
        if limit is None or limit < 0:
            limit = len(names)
        for name in names[:limit]:
            formatted_name = name_format.format(name=name_map.get(name, name))
            result += format.format(name=formatted_name,
                                    count=elem_dict[elemname][name],
                                    **extra_format_args)
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
            with self._open(files) as f:
                self.calc_file_stats(f, files)
        else:
            self.calc_file_stats(files)

    def _open(self, fname):
        if self._opts.input_encoding is not None:
            return codings.open(fname, 'r', encoding=self._opts.input_encoding)
        else:
            return open(fname, 'r')

    def calc_file_stats(self, f, fname=None):
        if fname != None:
            sys.stdout.write(fname + ':\n')
        stat_counter = XMLStatCounter(self._opts)
        if self._opts.wrapper_elem:
            f = WrappedXMLFileReader(f, wrapper_elem=self._opts.wrapper_elem)
        stat_counter.add_stats(f)
        if self._opts.cwb_struct_attrs:
            stats = stat_counter.format_cwb_struct_attrs()
        else:
            stats = stat_counter.format_stats()
        sys.stdout.write(stats)


def getopts():
    optparser = OptionParser()
    optparser.add_option('--attr-values', '--attribute-values',
                         action='store_true', default=False)
    optparser.add_option('--max-attr-values', '--maximum-attribute-values',
                         type='int', default=20)
    optparser.add_option('--cwb-struct-attrs', '--cwb-s-attrs',
                         '--cwb-structural-attributes',
                         action='store_true', default=False)
    optparser.add_option('--input-encoding', default=None)
    optparser.add_option('--wrapper-elem', '--wrapper-element-name',
                         default=None)
    (opts, args) = optparser.parse_args()
    if opts.wrapper_elem == '':
        opts.wrapper_elem = '__DUMMY__'
    return (opts, args)


def main():
    output_encoding = 'utf-8'
    (opts, args) = getopts()
    if opts.input_encoding is not None:
        sys.stdin = codecs.getreader(opts.input_encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    file_stats = XMLFileStats(opts)
    file_stats.process_files(args if args else sys.stdin)


if __name__ == "__main__":
    main()
