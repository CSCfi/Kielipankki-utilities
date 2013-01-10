#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import re

import ply.lex as lex
from ply.lex import TOKEN


class ElemRuleLexer(object):

    states = (
        ('attrval', 'inclusive'),
        )

    _keywords = ['ID', 'TEXT', 'VRT', 'STRIP', 'TOKENIZE', 'SPLIT']

    tokens = [
        'ARROW',
        'COLON',
        'SEMICOLON',
        'COMMA',
        'EQ',
        'NE',
        'LSQB',
        'RSQB',
        'VBAR',
        'RANGE',
        'ANYELEM',
        'ANYCONTENT',
        'NUM',
        'STRING',
        'ELEMNAME',
        'ATTRNAME',
        'PATH',
        'KEYWORD'
        ] + _keywords

    t_COLON = r':'
    t_SEMICOLON = r';'
    t_COMMA = r','
    t_NE = r'!='
    t_LSQB = r'\['
    t_RSQB = r'\]'
    t_VBAR = r'\|'
    t_RANGE = r'\.\.'
    t_ANYELEM = r'\*'
    t_ANYCONTENT = r'\*\*'

    t_ignore = ' \t'

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, reflags=re.UNICODE, **kwargs)

    def t_comment(self, t):
        r'\#.*'
        pass

    def t_STRING(self, t):
        r'"([^\"\\]|\\[\"\\])*"'
        t.value = t.value[1:-1]
        t.lexer.begin('INITIAL')
        return t

    def t_NUM(self, t):
        r'\d+'
        t.value = int(t.value)
        t.lexer.begin('INITIAL')
        return t

    def t_ATTRNAME(self, t):
        r'@([a-zA-Z_][a-zA-Z0-9:_]*|\*)'
        t.value = t.value[1:]
        t.lexer.begin('INITIAL')
        return t

    def t_KEYWORD(self, t):
        r'%[a-zA-Z]+'
        origval = t.value
        t.value = t.value[1:].upper()
        t.lexer.begin('INITIAL')
        if t.value not in self._keywords:
            sys.stderr.write("Invalid keyword '{}'\n".format(origval))
            return None
        t.type = t.value
        return t

    def t_attrval_PATH(self, t):
        r'[^@"%\s]\S*'
        t.lexer.begin('INITIAL')
        return t

    def t_ELEMNAME(self, t):
        r'[a-zA-Z_][a-zA-Z0-9:_]*'
        return t

    def t_ARROW(self, t):
        r'=>'
        return t

    def t_EQ(self, t):
        r'='
        t.lexer.begin('attrval')
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        sys.stderr.write("Illegal character '{}'\n".format(t.value[0]))
        t.lexer.skip(1)

    def test(self, data):
        self.lexer.input(data)
        while True:
             tok = lex.token()
             if not tok:
                 break
             print tok


if __name__ == '__main__':
    lexer = ElemRuleLexer()
    while True:
        s = ''
        while True:
            try:
                s += raw_input() + '\n'
            except EOFError:
                break
        if s:
            lexer.test(s)
        else:
            break
