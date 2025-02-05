
"""
test_funcdefutils.py

Pytest tests for libvrt.funcdefutils.
"""


import pytest

import libvrt.funcdefutils as fdu


class TestDefineTransformFunc:

    """Tests for function define_transform_func."""

    def test_define_transform_func_single_expr(self):
        """Test define_transform_func with a single expression."""
        func, funcdef = fdu.define_transform_func('val + "x"')
        assert func('y') == 'yx'
        assert funcdef == 'def transfunc(val):\n  return val + "x"'

    @pytest.mark.parametrize(
        'code,result,regexp,repl,count,flags',
        [
            # Base case
            ('s/a+/z/', 'z abc bbc AAb', 'a+', 'z', '1', '0'),
            # /g
            ('s/[ab]+/z/g', 'z zc zc AAz', '[ab]+', 'z', '0', '0'),
            # /i
            ('s/[ab]+/z/gi', 'z zc zc z', '[ab]+', 'z', '0', 're.I'),
            # /x
            ('s/ [ab] + \t/z/x', 'z abc bbc AAb', ' [ab] + \t', 'z', '1',
             're.X'),
            # /xig (multiple flags)
            ('s/ [ab] + \t/z/xig', 'z zc zc z', ' [ab] + \t', 'z', '0',
             're.X|re.I'),
            # Group reference
            ('s/(a+)(b+)/$2-$1/ig', 'aaa b-ac bbc b-AA', '(a+)(b+)', r'\2-\1',
             '0', 're.I'),
            # TODO: Test /l (run-time locale rules)
        ]
    )
    def test_define_transform_func_perl_subst(self, code, result, regexp, repl,
                                              count, flags):
        """Test define_transform_func with a Perl-style regexp substitution."""
        func, funcdef = fdu.define_transform_func(code)
        assert func('aaa abc bbc AAb') == result
        assert funcdef == (f'def transfunc(val):\n  return re.sub('
                           f'r"""{regexp}""", r"""{repl}""", val, {count},'
                           f' {flags})')

    @pytest.mark.parametrize('with_return', [False, True])
    def test_define_transform_func_multi_line(self, with_return):
        """Test define_transform_func with a multi-line function body."""
        code = ('result = ""\n'
                'for c in val[:-1]:\n'
                '  result += c + c')
        if with_return:
            code += '\nreturn result'
        else:
            code += '\nval = result'
        func, funcdef = fdu.define_transform_func(code)
        assert func('abcde') == 'aabbccdd'
        assert funcdef == ('def transfunc(val):\n  '
                           + code.replace('\n', '\n  ')
                           + ('\n  return val' if not with_return else ''))

    @pytest.mark.parametrize(
        'code',
        [
            # Only one slash
            's/a',
            # Only two slashes
            's/a/s',
            # Invalid flag
            's/a/s/z',
        ]
    )
    def test_define_transform_func_perl_subst_error(self, code):
        """Test define_transform_func with invalid Perl-style substitution."""
        with pytest.raises(
                fdu.FuncDefError,
                match=('Perl-style substitution not of the form'
                       r' s/regexp/repl/\[agilx]\*:')):
            func, funcdef = fdu.define_transform_func(code)

    @pytest.mark.parametrize(
        'code',
        [
            'if else',
            'for i in range(10):\n  if else',
        ]
    )
    def test_define_transform_func_syntax_error(self, code):
        """Test define_transform_func with code raising Python syntax error."""
        with pytest.raises(
                fdu.FuncDefError,
                match='Syntax error in transformation:'):
            func, funcdef = fdu.define_transform_func(code)

    @pytest.mark.parametrize(
        'code,error',
        [
            ('x', 'NameError'),
            ('import _xyz\nreturn val', 'ModuleNotFoundError'),
        ]
    )
    def test_define_transform_func_invalid_code(self, code, error):
        """Test define_transform_func, code raising NameError or ImportError."""
        with pytest.raises(
                fdu.FuncDefError,
                match=f'Invalid transformation:(.|\n)*{error}'):
            func, funcdef = fdu.define_transform_func(code)
