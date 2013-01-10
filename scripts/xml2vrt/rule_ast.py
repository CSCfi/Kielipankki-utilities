#! /usr/bin/env python
# -*- coding: utf-8 -*-


import re

import xml.etree.ElementTree as et


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

    _repr_attrs = []

    def __repr__(self):
        attr_reprs = [attr.lstrip('_') + '=' + repr(getattr(self, attr, None))
                      for attr in self._repr_attrs]
        return '{cls}({attrs})'.format(cls=self.__class__.__name__,
                                       attrs=', '.join(attr_reprs))

class ElemRule(ElemRulePart):

    _repr_attrs = ['_elemconds', '_target']

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


class ElemCond(ElemRulePart):

    _repr_attrs = ['_elemname', '_conds']

    def __init__(self, elemname, conds):
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

    _repr_attrs = ['_attrname', '_attrval']

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

    _repr_attrs = ['_fields']

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

    _repr_attrs = ['_attrnames', '_opts']

    def __init__(self, attrnames, opts=None):
        if not isinstance(attrnames, list):
            attrnames = [attrnames]
        self._attrnames = attrnames
        self._opts = opts if opts is not None else {}

    def make_values(self, line, et_elem):
        return VrtListFields([[et_elem.get(attrname, '')
                               for attrname in self._attrnames]])


class ElemTargetVrtTextField(ElemTargetVrtField):

    _repr_attrs = ['_field_nrs', '_opts']

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

    _repr_attrs = ['_values']

    def __init__(self, values):
        if not isinstance(values, list):
            values = [values]
        self._values = values

    def make_values(self, line, et_elem):
        return VrtListFields([[value for value in self._values]])
    

class ElemTargetVrtText(ElemTargetVrtField):

    _repr_attrs = ['_opts']

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

    _repr_attrs = ['_elemname', '_attrs', '_content']

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

    _repr_attrs = ['_content']

    def __init__(self, content):
        self._content = content

    def make_target(self, et_elem, converter):
        # KLUDGE: Use a dummy Element so that make_content works;
        # return only the list of children.
        result_e = et.Element('dummy')
        self._content.make_content(et_elem, result_e, converter)
        return list(result_e)


class ElemAttr(ElemRulePart):

    _repr_attrs = ['_attrname']

    def __init__(self, attrname):
        self._attrname = attrname

    def get_attrname(self):
        return self._attrname

    def set_value(self, et_elem, result_e):
        result_e.set(self._attrname, self.make_value(et_elem))

    def make_value(self, et_elem):
        pass


class ElemAttrConst(ElemAttr):

    _repr_attrs = ['_attrname', '_value']

    def __init__(self, attrname, value):
        ElemAttr.__init__(self, attrname)
        self._value = value

    def make_value(self, et_elem):
        return self._value


class ElemAttrAttr(ElemAttr):

    _repr_attrs = ['_attrname', '_src_attrname']

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

    _repr_attrs = ['_attrname', '_content_path']

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

    _repr_attrs = ['_attrname', '_content_path', '_content_attrname']

    def __init__(self, attrname, content_path, content_attrname):
        ElemAttrContent.__init__(self, attrname, content_path)
        self._content_attrname = content_attrname
        self._repr_attrs = ['_attrname', '_content_path']

    def _get_value(self, elem):
        return elem.get(self._content_attrname, '')


class ElemAttrCopy(ElemAttr):

    _repr_attrs = ['_attrnames']

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

    _repr_attrs = ['_child_names']

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

        def append_to_prev_subresult(text):
            if text:
                if prev_subresult is None:
                    result_e.text += text
                else:
                    prev_subresult.tail += text

        for subelem in et_elem:
            subresults = None
            if self._process_all_elems or subelem.tag in self._child_names:
                subresults = converter.convert_elem(subelem)
            if subresults:
                # print 'sr', et_elem.tag, subelem.tag, type(subresults), subresults
                if isinstance(subresults, list):
                    for subresult in subresults:
                        if isinstance(subresult, et.Element):
                            subresult.tail = self._make_text_content(
                                subelem.tail, converter)
                            prev_subresult = subresult
                            result_e.append(subresult)
                        else:
                            append_to_prev_subresult(subresult)
                else:
                    append_to_prev_subresult(subresults)
            else:
                append_to_prev_subresult(
                    self._make_text_content(subelem.tail, converter))
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
            s = s or '\n'
            if s[0] != '\n':
                s = '\n' + s
            if s[-1] != '\n':
                s += '\n'
            return s

        elem.text = add_lead_trail_newline(elem.text)
        elem.tail = add_lead_trail_newline(elem.tail)


def main():
    pass


if __name__ == "__main__":
    main()
