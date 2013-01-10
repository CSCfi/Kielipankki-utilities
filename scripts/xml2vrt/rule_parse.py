#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys

import ply.yacc as yacc

import rule_lex
import rule_ast as ast


class ElemRuleParser(object):

    def __init__(self, lexer=None, **kwargs):
        if lexer is None:
            self.lexer = rule_lex.ElemRuleLexer()
        else:
            self.lexer = lexer
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, debug=2, **kwargs)

    def parse(self, input, **kwargs):
        return self.parser.parse(input, **kwargs)

    def p_rule(self, p):
        'rule : elem_conds ARROW target SEMICOLON'
        p[0] = ast.ElemRule(p[1], p[3])

    def p_elem_conds_1(self, p):
        'elem_conds : elem_cond'
        p[0] = [p[1]]

    def p_elem_conds_m(self, p):
        'elem_conds : elem_conds VBAR elem_cond'
        p[1].append(p[3])
        p[0] = p[1]

    def p_elem_cond_none(self, p):
        'elem_cond : elemname'
        p[0] = ast.ElemCond(p[1], [])

    def p_elem_cond_conds(self, p):
        'elem_cond : elemname conds'
        p[0] = ast.ElemCond(p[1], p[2])

    def p_conds_1(self, p):
        'conds : cond'
        p[0] = [p[1]]

    def p_conds_m(self, p):
        'conds : conds cond'
        p[1].append(p[2])
        p[0] = p[1]

    def p_cond(self, p):
        'cond : attr_cond'
        p[0] = p[1]

    def p_attr_eq(self, p):
        'attr_cond : ATTRNAME EQ attr_value'
        p[0] = ast.ElemCondAttrEq(p[1], p[3])

    def p_attr_ne(self, p):
        'attr_cond : ATTRNAME NE attr_value'
        p[0] = ast.ElemCondAttrNe(p[1], p[3])

    def p_attr_value(self, p):
        'attr_value : STRING'
        p[0] = p[1]

    def p_target_skip(self, p):
        'target : COLON elem_content'
        p[0] = ast.ElemTargetSkip(p[2])

    def p_target_elem(self, p):
        'target : elemname target_attrs COLON elem_content'
        p[0] = ast.ElemTargetElem(p[1], p[2], p[4])

    def p_target_vrt(self, p):
        'target : VRT COLON vrt_content'
        p[0] = ast.ElemTargetVrt(p[3])

    def p_elemname(self, p):
        """elemname : ELEMNAME
                    | TEXT
                    | ANYELEM"""
        p[0] = p[1]

    def p_target_attrs_1(self, p):
        'target_attrs : target_attr'
        p[0] = [p[1]]

    def p_target_attrs_m(self, p):
        'target_attrs : target_attrs target_attr'
        p[1].append(p[2])
        p[0] = p[1]

    def p_target_attr_copy(self, p):
        'target_attr : ATTRNAME'
        p[0] = ast.ElemAttrCopy(p[1])

    def p_target_attr_const(self, p):
        'target_attr : ATTRNAME EQ STRING'
        p[0] = ast.ElemAttrConst(p[1], p[3])

    def p_target_attr_attr(self, p):
        'target_attr : ATTRNAME EQ ATTRNAME'
        p[0] = ast.ElemAttrAttr(p[1], p[3])

    def p_target_attr_id(self, p):
        'target_attr : ATTRNAME EQ ID'
        p[0] = ast.ElemAttrId(p[1])

    def p_target_attr_content_text(self, p):
        'target_attr : ATTRNAME EQ PATH'
        p[0] = ast.ElemAttrContentText(p[1], p[3])

    # def p_target_attr_content_attr(self, p):
    #     'target_attr : ATTRNAME EQ content_path ATTRNAME'
    #     p[0] = ast.ElemAttrContentAttr(p[1], p[3], p[4])

    def p_elem_content(self, p):
        'elem_content : elem_content_elems'
        p[0] = p[1]

    def p_elem_content_elems_1(self, p):
        'elem_content_elems : elem_content_elem'
        p[0] = [p[1]]

    def p_elem_content_elems_m(self, p):
        'elem_content_elems : elem_content_elems elem_content_elem'
        p[1].append(p[2])
        p[0] = p[1]

    def p_elem_content_elem(self, p):
        """elem_content_elem : ID
                             | ANYCONTENT
                             | ANYELEM
                             | TEXT"""
        p[0] = p[1]

    def p_vrt_content(self, p):
        'vrt_content : vrt_fields'
        p[0] = p[1]

    def p_vrt_fields_1(self, p):
        'vrt_fields : vrt_field'
        p[0] = [p[1]]

    def p_vrt_fields_m(self, p):
        'vrt_fields : vrt_fields vrt_field'
        p[1].append(p[2])
        p[0] = p[1]

    def p_vrt_field_attr(self, p):
        'vrt_field : ATTRNAME'
        p[0] = ast.ElemTargetVrtAttrField(p[1])

    def p_vrt_field_const(self, p):
        'vrt_field : STRING'
        p[0] = ast.ElemTargetVrtConstField(p[1])

    def p_vrt_field_text(self, p):
        'vrt_field : TEXT'
        p[0] = ast.ElemTargetVrtText()

    class VrtFieldTextOpts(object):

        def __init__(self, field_nrs=None, opts=None):
            self.field_nrs = field_nrs or []
            self.opts = opts or {}

        def add(self, other):
            self.field_nrs.extend(other.field_nrs)
            self.opts.update(other.opts)

    def p_vrt_field_text_opts(self, p):
        'vrt_field : TEXT LSQB vrt_text_opts RSQB'
        if p[3].field_nrs:
            p[0] = ast.ElemTargetVrtTextField(p[3].field_nrs, p[3].opts)
        else:
            p[0] = ast.ElemTargetVrtText(p[3].opts)

    def p_vrt_text_opts_1(self, p):
        'vrt_text_opts : vrt_text_opt'
        p[0] = self.VrtFieldTextOpts()
        p[0].add(p[1])
        
    def p_vrt_text_opts_m(self, p):
        'vrt_text_opts : vrt_text_opts vrt_text_opt'
        p[1].add(p[2])
        p[0] = p[1]

    def p_vrt_text_opt_field_range(self, p):
        'vrt_text_opt : NUM RANGE NUM'
        p[0] = self.VrtFieldTextOpts(field_nrs=range(p[1] - 1, p[3] - 1))

    def p_vrt_text_opt_field_single(self, p):
        'vrt_text_opt : NUM'
        p[0] = self.VrtFieldTextOpts(field_nrs=[p[1] - 1])

    def p_vrt_text_opt_field_opt(self, p):
        """vrt_text_opt : SPLIT
                        | STRIP
                        | TOKENIZE"""
        p[0] = self.VrtFieldTextOpts(opts={p[1].lower(): True})

    # Error rule for syntax errors
    def p_error(self, p):
        sys.stderr.write("Syntax error in input at token " + p.type
                         + " on line " + str(p.lexer.lineno) + "\n")


def main():
    parser = ElemRuleParser()
    while True:
        s = ''
        while True:
            try:
                s += raw_input() + '\n'
            except EOFError:
                break
        if s:
            print parser.parse(s, debug=2)
        else:
            break


if __name__ == '__main__':
    main()
