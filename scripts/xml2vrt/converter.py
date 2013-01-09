#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs

import xml.etree.ElementTree as et

from util import WrappedXMLFileReader
from rule_ast import *


class ListDict(dict):

    def __init__(self):
        dict.__init__(self)

    def add_to(self, dictkey, elem):
        if dictkey not in self:
            self[dictkey] = []
        self[dictkey].append(elem)

    def del_from(self, dictkey, elem):
        if dictkey in self and del_value(self[dictkey], elem) is not None:
            if len(self[dictkey]) == 0:
                del self[dictkey]
            return True
        return False


class Converter(object):

    def __init__(self, opts=None, rules=None):
        self._opts = opts
        self._rules = ListDict()
        self._wrapper_elem = getattr(self._opts, 'wrapper_elem', None)
        if self._wrapper_elem is not None:
            self.add_rule(ElemRule(ElemCond(self._wrapper_elem),
                                   target=ElemTargetSkip(ElemContent('*'))))
        if rules is not None:
            for rule in rules:
                self.add_rule(rule)
        # print self._rules

    def add_rule(self, rule):
        for elemname in rule.get_elemnames():
            self._rules.add_to(elemname, rule)

    def process_inputs(self, files):
        if not isinstance(files, list):
            files = [files]
        for f in files:
            if isinstance(f, basestring):
                with open(f, 'r') as f:
                    self.process_input(f)
            else:
                self.process_input(f)

    def process_input(self, base_f):
        # print base_f
        if self._wrapper_elem is not None:
            f = WrappedXMLFileReader(base_f, wrapper_elem=self._wrapper_elem)
        else:
            f = base_f
        src_e = et.parse(f).getroot()
        for result_et in self.convert(src_e):
            result_et.write(sys.stdout, encoding='utf-8')

    def convert(self, src_e):
        return [et.ElementTree(elem) for elem in self.convert_elem(src_e)]

    def convert_elem(self, src_e):
        rule = self._find_rule(src_e)
        # print rule
        if rule is None:
            return []
        else:
            return rule.make_target(src_e, self)

    def _find_rule(self, elem):
        # print '_find_rule',
        # print ('%TEXT' if isinstance(elem, basestring) else elem.tag)
        if isinstance(elem, basestring):
            elemname = '%TEXT'
            # print elem
        elif elem.tag in self._rules:
            elemname = elem.tag
            # print elem.tag
        elif '*' in self._rules:
            elemname = '*'
            # print '*'
        else:
            # print None
            return None
        for rule in self._rules[elemname]:
            # print rule
            if rule.matches(elem):
                return rule
        return None


_test_rules = [
    ElemRule(ElemCond('s'),
             target=ElemTargetElem('sentence',
                                   [ElemAttrId('id'),
                                    ElemAttrConst('test', 's'),
                                    ElemAttrContentAttr('loc_id', 'loc', 'id'),
                                    ElemAttrContentText('t', 't')],
                                   ElemContent('**'))),
    ElemRule([ElemCond('u', ElemCondAttrEq('t', 'bar')), ElemCond('t')],
             target=ElemTargetElem('test',
                                   [ElemAttrAttr('ta', 't')],
                                   ElemContent('**'))),
    ElemRule(ElemCond('x'),
             target=ElemTargetVrt([ElemTargetVrtTextField(1),
                                   ElemTargetVrtAttrField(['y', 'z']),
                                   ElemTargetVrtTextField(0)])),
    ElemRule(ElemCond('w'),
             target=ElemTargetVrt([ElemTargetVrtTextField(0, {'strip': True}),
                                   ElemTargetVrtAttrField(['baseform', 'pos',
                                                           'msd'])])),
    ElemRule(ElemCond('z'),
             target=ElemTargetVrt([ElemTargetVrtText({'tokenize': True,
                                                      'split': True}),
                                   ElemTargetVrtAttrField('t')])),
    ElemRule(ElemCond('%TEXT'),
             target=ElemTargetVrt([ElemTargetVrtTextField([0, 1, 2, 3])])),
    ElemRule(ElemCond('*'),
             target=ElemTargetSkip(ElemContent('*')))]


def main():
    converter = Converter(None, rules=_test_rules)
    converter.process_inputs(sys.argv[1:] if len(sys.argv) > 1 else sys.stdin)


if __name__ == "__main__":
    main()
