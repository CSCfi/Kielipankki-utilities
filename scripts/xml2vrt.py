#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import codecs
import re

import xml.etree.ElementTree as et

from optparse import OptionParser


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


class Tokenizer(object):

    def __init__(self):
        pass

    def tokenize(self, text):
        text = text or ''
        text = re.sub(r'([.?!,:])(")', r'\1 \2', text)
        text = re.sub(r'(\.\.\.)([,:;?!")])', r' \1 \2', text)
        text = re.sub(r'([.,:;?!")]|\.\.\.)([ \n]|\Z)', r' \1\2', text)
        text = re.sub(r'([ \n]|\A)(["(])', r'\1\2 ', text)
        return text


class ElemRulePart(object):

    pass


class ElemRule(ElemRulePart):

    def __init__(self, elemconds, target=None):
        if not isinstance(elemconds, list):
            elemconds = [elemconds]
        self._elemconds = dict([(elemcond.get_elemname(), elemcond)
                                for elemcond in elemconds])
        self._target = target

    def get_elemnames(self):
        return self._elemconds.keys()

    def matches(self, et_elem):
        cond = None
        if isinstance(et_elem, et.Element):
            cond = self._elemconds.get(et_elem.tag) or self._elemconds.get('*')
        elif isinstance(et_elem, basestring):
            cond = self._elemconds.get('%TEXT')
        return cond.matches(et_elem) if cond else False

    def make_target(self, et_elem, converter):
        return self._target.make_target(et_elem, converter)

    def __repr__(self):
        return 'ElemRule({0}, target={1})'.format(
            repr(self._elemconds), repr(self._target))


class ElemCond(ElemRulePart):

    def __init__(self, elemname, *conds):
        self._elemname = elemname
        self._conds = conds

    def get_elemname(self):
        return self._elemname

    def matches(self, et_elem):
        if isinstance(et_elem, et.Element):
            return ((et_elem.tag == self._elemname or self._elemname == '*')
                    and self._conds_match(et_elem))
        elif isinstance(et_elem, basestring):
            return (self._elemname == '%TEXT')
        else:
            return False

    def _conds_match(self, et_elem):
        for cond in self._conds:
            if not cond.matches(et_elem):
                return False
        return True


class ElemCondCond(ElemRulePart):

    def matches(self, et_elem):
        pass


class ElemCondAttrCond(ElemCondCond):

    def __init__(self, attrname, attrval):
        self._attrname = attrname
        self._attrval = attrval


class ElemCondAttrEq(ElemCondAttrCond):

    def __init__(self, attrname, attrval):
        ElemCondAttrCond.__init__(self, attrname, attrval)

    def matches(self, et_elem):
        return et_elem.get(self._attrname) == self._attrval


class ElemCondAttrNe(ElemCondAttrCond):

    def __init__(self, attrname, attrval):
        ElemCondAttrCond.__init__(self, attrname, attrval)

    def matches(self, et_elem):
        return et_elem.get(self._attrname) != self._attrval


class ElemTarget(ElemRulePart):

    def make_target(self, et_elem, converter):
        pass


class VrtList(list):

    def __init__(self, *args):
        list.__init__(self, *args)


class VrtListFields(VrtList):

    def __init__(self, *args):
        VrtList.__init__(self, *args)

    def extend(self, lst):
        VrtList.extend(self[0], [elem for sublist in lst for elem in sublist])


class VrtListLines(VrtList):

    def __init__(self, *args):
        VrtList.__init__(self, *args)

    def extend(self, lst):
        for sublist in self:
            VrtList.extend(sublist,
                           [elem for sublist2 in lst for elem in sublist2])


class ElemTargetVrt(ElemTarget):

    def __init__(self, fields):
        self._fields = fields

    def make_target(self, et_elem, converter):
        result_lines = []
        text = et_elem if isinstance(et_elem, basestring) else et_elem.text
        text = self.strip_newlines(text)
        for line in text.split('\n'):
            # Make the first fields separately to get the right class
            result_line_fields_list = self._fields[0].make_values(line, et_elem)
            for fields in self._fields[1:]:
                result_line_fields_list.extend(
                    fields.make_values(line, et_elem))
            for result_line_fields in result_line_fields_list:
                # print result_line_fields
                result_lines.append('\t'.join(result_line_fields))
                # print result_lines
        return '\n'.join(result_lines) + '\n'

    @classmethod
    def strip_newlines(cls, s):
        start = 1 if s.startswith('\n') else 0
        end = -1 if s.endswith('\n') else len(s)
        return s[start:end]


class ElemTargetVrtField(ElemTarget):

    def make_values(self, line, et_elem):
        pass


class ElemTargetVrtAttrField(ElemTargetVrtField):

    def __init__(self, attrnames, opts=None):
        if not isinstance(attrnames, list):
            attrnames = [attrnames]
        self._attrnames = attrnames
        self._opts = opts if opts is not None else {}

    def make_values(self, line, et_elem):
        return VrtListFields([[et_elem.get(attrname, '')
                               for attrname in self._attrnames]])


class ElemTargetVrtTextField(ElemTargetVrtField):

    def __init__(self, field_nrs=[0], opts=None):
        if not isinstance(field_nrs, list):
            field_nrs = [field_nrs]
        self._field_nrs = field_nrs
        self._opts = opts if opts is not None else {}

    def make_values(self, line, et_elem):
        elem_fields = line.split('\t')
        # print self._field_nrs, elem_fields
        return VrtListFields([[self._make_value(elem_fields[fieldnr])
                               for fieldnr in self._field_nrs
                               if fieldnr < len(elem_fields)]])

    def _make_value(self, value):
        if self._opts.get('strip'):
            value = value.strip()
        if self._opts.get('tokenize'):
            value = self._tokenizer(value)
        return value


class ElemTargetVrtConstField(ElemTargetVrtField):

    def __init__(self, value):
        self._value = value

    def make_values(self, line, et_elem):
        return VrtListFields([[self._value]])
    

class ElemTargetVrtText(ElemTargetVrtField):

    def __init__(self, opts=None):
        self._opts = opts if opts is not None else {}
        self._tokenizer = self._opts.get('tokenizer') or Tokenizer()

    def make_values(self, line, et_elem):
        if self._opts.get('strip'):
            line = line.strip()
        if self._opts.get('tokenize'):
            line = self._tokenizer.tokenize(line)
        if self._opts.get('split'):
            return VrtListLines([[word] for word in line.split()])
        else:
            return VrtListFields([[line]])
            

class ElemTargetElem(ElemTarget):

    def __init__(self, elemname, attrs, content):
        self._elemname = elemname
        self._attrs = attrs
        self._content = content

    def make_target(self, et_elem, converter):
        result_e = et.Element(self._make_elemname(et_elem))
        self._add_attrs(et_elem, result_e)
        self._make_content(et_elem, result_e, converter)
        # print result_e, result_e.tag, '<', result_e.tail, '>'
        return [result_e]

    def _make_elemname(self, et_elem):
        return self._elemname if self._elemname != '*' else et_elem.tag

    def _add_attrs(self, et_elem, result_e):
        for attr in self._attrs:
            attr.set_value(et_elem, result_e)

    def _make_content(self, et_elem, result_e, converter):
        self._content.make_content(et_elem, result_e, converter)


class ElemTargetSkip(ElemTarget):

    def __init__(self, content):
        self._content = content

    def make_target(self, et_elem, converter):
        # KLUDGE: Use a dummy Element so that make_content works;
        # return only the list of children.
        result_e = et.Element('dummy')
        self._content.make_content(et_elem, result_e, converter)
        return list(result_e)


class ElemAttr(ElemRulePart):

    def __init__(self, attrname):
        self._attrname = attrname

    def get_attrname(self):
        return self._attrname

    def set_value(self, et_elem, result_e):
        result_e.set(self._attrname, self.make_value(et_elem))

    def make_value(self, et_elem):
        pass


class ElemAttrConst(ElemAttr):

    def __init__(self, attrname, value):
        ElemAttr.__init__(self, attrname)
        self._value = value

    def make_value(self, et_elem):
        return self._value


class ElemAttrAttr(ElemAttr):

    def __init__(self, attrname, src_attrname):
        ElemAttr.__init__(self, attrname)
        self._src_attrname = src_attrname

    def make_value(self, et_elem):
        return et_elem.get(self._src_attrname, '')


class ElemAttrId(ElemAttr):

    def __init__(self, attrname):
        ElemAttr.__init__(self, attrname)
        self._id_value = 0

    def make_value(self, et_elem):
        self._id_value += 1
        return str(self._id_value)


class ElemAttrContent(ElemAttr):

    def __init__(self, attrname, content_path):
        ElemAttr.__init__(self, attrname)
        self._content_path = content_path

    def make_value(self, et_elem):
        return ' | '.join([self._get_value(elem) for elem in
                           et_elem.findall(self._content_path)])

    def _get_value(self, elem):
        pass


class ElemAttrContentText(ElemAttrContent):

    def __init__(self, attrname, content_path):
        ElemAttrContent.__init__(self, attrname, content_path)

    def _get_value(self, elem):
        return elem.text.strip()
    

class ElemAttrContentAttr(ElemAttrContent):

    def __init__(self, attrname, content_path, content_attrname):
        ElemAttrContent.__init__(self, attrname, content_path)
        self._content_attrname = content_attrname

    def _get_value(self, elem):
        return elem.get(self._content_attrname, '')


class ElemAttrCopy(ElemAttr):

    def __init__(self, attrnames):
        if not isinstance(attrnames, list):
            attrnames = [attrnames]
        self._attrnames = attrnames

    def set_value(self, et_elem, result_e):
        if self._attrnames[0] == '*':
            for (key, val) in et_elem.items():
                result_e.set(key, val)
        else:
            for attrname in self._attrnames:
                result_e.set(attrname, et_elem.get(attrname, ''))
        

class ElemContent(ElemRulePart):

    def __init__(self, child_names):
        if not isinstance(child_names, list):
            child_names = [child_names]
        self._child_names = dict([(name, 1) for name in child_names])
        if '**' in self._child_names:
            self._child_names.update({'*': 1, '%TEXT': 1})
        self._process_all_elems = ('*' in self._child_names)
        self._process_text = ('%TEXT' in self._child_names)
        # print self._process_all_elems, self._process_text

    def make_content(self, et_elem, result_e, converter):
        # print 'make_content', et_elem.tag
        result_e.text = self._make_text_content(et_elem.text, converter)
        prev_subresult = None
        for subelem in et_elem:
            subresults = None
            if self._process_all_elems or subelem.tag in self._child_names:
                subresults = converter.convert_elem(subelem)
            if subresults:
                # print 'sr', et_elem.tag, subelem.tag, type(subresults), subresults
                for subresult in subresults:
                    if isinstance(subresult, et.Element):
                        subresult.tail = self._make_text_content(subelem.tail,
                                                                 converter)
                        prev_subresult = subresult
                        result_e.append(subresult)
                    else:
                        if prev_subresult is None:
                            result_e.text += subresult
                        else:
                            prev_subresult.tail += subresult
            else:
                text = self._make_text_content(subelem.tail, converter)
                if text:
                    if prev_subresult is None:
                        result_e.text += text
                    else:
                        prev_subresult.tail += text
        self.add_content_newlines(result_e)
        for subresult in result_e:
            self.add_content_newlines(subresult)

    def _make_text_content(self, text, converter):
        # print self._process_text, text
        if self._process_text and text is not None and text.strip():
            # print 'make_text_content'
            return converter.convert_elem(text)
        else:
            return ''

    @classmethod
    def add_content_newlines(cls, elem):

        def add_lead_trail_newline(s):
            s = (s.strip() or '\n') if s else '\n'
            if s[0] != '\n':
                s = '\n' + s
            if s[-1] != '\n':
                s += '\n'
            return s

        elem.text = add_lead_trail_newline(elem.text)
        elem.tail = add_lead_trail_newline(elem.tail)


class Converter(object):

    def __init__(self, opts=None, rules=None):
        self._opts = opts if opts is not None else {}
        self._rules = ListDict()
        if rules is not None:
            for rule in rules:
                self.add_rule(rule)
        # print self._rules

    def add_rule(self, rule):
        for elemname in rule.get_elemnames():
            self._rules.add_to(elemname, rule)

    def process_input(self, f):
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


def getopts():
    optparser = OptionParser()
    optparser.add_option('--rule-file', '--rules', '-r')
    (opts, args) = optparser.parse_args()
    return (opts, args)


test_rules = [
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


def get_rules(opts):
    if opts.rule_file:
        rules = eval(read_file(opts.rule_file))
    else:
        rules = test_rules
    return rules


def read_file(fname):
    contents = ''
    with codecs.open(fname, 'r', encoding='utf-8') as f:
        for line in f:
            contents += line
    return contents


def main():
    input_encoding = 'utf-8'
    output_encoding = 'utf-8'
    # ElementTree.XMLParser uses the encoding specified in the XML
    # header, so we should not modify it here.
    # sys.stdin = codecs.getreader(input_encoding)(sys.stdin)
    # sys.stdout = codecs.getwriter(output_encoding)(sys.stdout)
    (opts, args) = getopts()
    converter = Converter(opts, rules=get_rules(opts))
    converter.process_input(args[0] if args else sys.stdin)


if __name__ == "__main__":
    main()
