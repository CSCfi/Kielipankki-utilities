
"""
test_funcdefutils.py

Pytest tests for libvrt.funcdefutils.
"""


import pytest

import libvrt.funcdefutils as fdu


# Input string for testing Perl-style substitution expressions
_perl_subst_input = r'aaa abc/bbc\/ AAb'

# Parametrized test cases for Perl-style substitution expressions:
# expression, result (for _perl_subst_input), regexp, repl, count,
# flags
_perl_subst_testcases = [
    # Base case
    ('s/a+/z/', 'z abc/bbc\\/ AAb', 'a+', 'z', '1', '0'),
    # /g
    ('s/[ab]+/z/g', 'z zc/zc\\/ AAz', '[ab]+', 'z', '0', '0'),
    # /i
    ('s/[ab]+/z/gi', 'z zc/zc\\/ z', '[ab]+', 'z', '0', 're.I'),
    # /x
    ('s/ [ab] + \t/z/x', 'z abc/bbc\\/ AAb', ' [ab] + \t', 'z', '1', 're.X'),
    # /xig (multiple flags)
    ('s/ [ab] + \t/z/xig', 'z zc/zc\\/ z', ' [ab] + \t', 'z', '0', 're.X|re.I'),
    # Group reference
    ('s/(a+)(b+)/$2-$1/ig', 'aaa b-ac/bbc\\/ b-AA', '(a+)(b+)', r'\2-\1', '0',
     're.I'),
    # Backslash-protected slash at the beginning of regexp
    (r's/\/[bd]/x/', 'aaa abcxbc\\/ AAb', '/[bd]', 'x', '1', '0'),
    # Backslash-protected slash in the middle of regexp
    (r's/[ac]\/[bd]/x/', 'aaa abxbc\\/ AAb', '[ac]/[bd]', 'x', '1', '0'),
    # Backslash-protected slash at end of regexp
    (r's/[ac]\//x/', 'aaa abxbbc\\/ AAb', '[ac]/', 'x', '1', '0'),
    # Backslash followed by a backslash-protected slash
    (r's/[ac]\//x/', 'aaa abxbbc\\/ AAb', '[ac]/', 'x', '1', '0'),
    # Backslash-protected slash at the beginning of repl
    (r's/[a-c] /\/x/', 'aa/xabc/bbc\\/ AAb', '[a-c] ', '/x', '1', '0'),
    # Backslash-protected slash in the middle of repl
    (r's/[a-c] /x\/y/', 'aax/yabc/bbc\\/ AAb', '[a-c] ', 'x/y', '1', '0'),
    # Backslash-protected slash at the end of repl
    (r's/[a-c] /x\//', 'aax/abc/bbc\\/ AAb', '[a-c] ', 'x/', '1', '0'),
    # Backslashes followed by backslash-protected slash in regexp
    (r's/[ac]\\\/ /x/', 'aaa abc/bbxAAb', r'[ac]\\/ ', 'x', '1', '0'),
    # Backslashes followed by backslash-protected slash in repl
    (r's/[a-c] /x\\\/y/', r'aax\/yabc/bbc\/ AAb', '[a-c] ', r'x\\/y', '1', '0'),
    # TODO: Test /l (run-time locale rules)
]

_perl_subst_testcases_invalid = [
    # Only one slash
    's/a',
    # Only two slashes
    's/a/s',
    # Invalid flag
    's/a/s/z',
]


class _TestDefineFuncBase:

    """
    Common test functionality for define_func, define_transform_func.

    Methods in this class get the actual function to be tested as
    argument def_func, and funcname is the name of the defined
    function.
    """

    def _test_define_single_expr(self, def_func, funcname):
        """Test def_func with defaults and a single expression."""
        func, funcdef = def_func('val + "x"')
        assert func('y') == 'yx'
        assert funcdef == f'def {funcname}(val):\n  return val + "x"'

    def _test_define_multi_line(self, def_func, funcname, with_return):
        """Test def_func a multi-line function body (and defaults)."""
        code = ('result = ""\n'
                'for c in val[:-1]:\n'
                '  result += c + c')
        if with_return:
            code += '\nreturn result'
        else:
            code += '\nval = result'
        func, funcdef = def_func(code)
        assert func('abcde') == 'aabbccdd'
        assert funcdef == (f'def {funcname}(val):\n  '
                           + code.replace('\n', '\n  ')
                           + ('\n  return val' if not with_return else ''))

    # Code causing syntax error, for test parametrizing tests using
    # _test_define_syntax_error
    _syntax_error_code = [
        'if else',
        'for i in range(10):\n  if else',
    ]

    def _test_define_syntax_error(self, def_func, functype, code):
        """Test def_func with code raising Python syntax error."""
        with pytest.raises(
                fdu.FuncDefError,
                match=f'Syntax error in {functype}:'):
            func, funcdef = def_func(code)

    # Invalid code causing other errors, for test parametrizing tests
    # using _test_define_invalid_code
    _invalid_code = [
        ('x', 'NameError'),
        ('import _xyz\nreturn val', 'ModuleNotFoundError'),
    ]

    def _test_define_invalid_code(self, def_func, functype, code, error):
        """Test def_func, with code raising NameError or ImportError."""
        with pytest.raises(
                fdu.FuncDefError,
                match=f'Invalid {functype}:(.|\n)*{error}'):
            func, funcdef = def_func(code)


class TestDefineFunc(_TestDefineFuncBase):

    """Tests for function define_func."""

    def test_define_func_single_expr_defaults(self):
        """Test define_func with a single expression and defaults."""
        self._test_define_single_expr(fdu.define_func, 'func')

    @pytest.mark.parametrize(
        'name,args,code,argvals,result',
        [
            # No arguments
            ('f', '', '"x"', (), 'x'),
            # No arguments as a tuple
            ('f', (), '"x"', (), 'x'),
            # Single argument
            ('f', 'x', 'x + "y"', ('a',), 'ay'),
            # Single argument as a tuple
            ('f', ('x',), 'x + "y"', ('a',), 'ay'),
            # Multiple arguments as a tuple
            ('f1', ('x', 'y'), 'x + y', ('a', 'b'), 'ab'),
            # Multiple arguments as a single string
            ('f1', 'x, y', 'x + y', ('a', 'b'), 'ab'),
        ]
    )
    def test_define_func_single_expr_args(self, name, args, code, argvals,
                                          result):
        """Test define_func with a single expression and non-default args."""
        func, funcdef = fdu.define_func(code, name=name, args=args)
        assert func(*argvals) == result
        argstr = args if isinstance(args, str) else ', '.join(args)
        assert funcdef == f'def {name}({argstr}):\n  return {code}'

    @pytest.mark.parametrize('with_return', [False, True])
    def test_define_func_multi_line_defaults(self, with_return):
        """Test define_func with a multi-line function body and defaults."""
        self._test_define_multi_line(fdu.define_func, 'func', with_return)

    @pytest.mark.parametrize(
        'name,args,code,returns,argvals,result',
        [
            # No arguments, no return value (None)
            ('f0', '', 'pass', '', (), None),
            # No arguments, return fixed value
            ('f1', '', 'pass', '1', (), 1),
            # No arguments (tuple), return assigned value
            ('f2', (), 'x = 1', 'x', (), 1),
            # Multiple arguments (tuple), return single value
            ('f3', ('x', 'y'), 'z = x + y', 'z', (1, 2), 3),
            # Multiple arguments (string), return single value
            ('f4', 'x, y', 'z = x + y', 'z', (1, 2), 3),
            # Multiple arguments (string), multi-line code
            ('f5', 'x, y', 'for i in range(x):\n  y *= y', 'y', (4, 2), 65536),
            # Multiple arguments (string), multiple return values
            ('f6', 'x, y', 'for i in range(x):\n  y *= y\n  x += x', 'x, y',
             (4, 2), (64, 65536)),
        ]
    )
    @pytest.mark.parametrize('with_return', [False, True])
    def test_define_func_multi_line_args(self, name, args, code, returns,
                                         argvals, result, with_return):
        """Test define_func with multi-line function body, non-default args."""
        if with_return:
            code += f'\nreturn {returns}'
        func, funcdef = fdu.define_func(
            code, name=name, args=args, returns=returns)
        assert func(*argvals) == result
        argstr = args if isinstance(args, str) else ', '.join(args)
        assert funcdef == (f'def {name}({argstr}):\n  '
                           + code.replace('\n', '\n  ')
                           + (f'\n  return {returns}' if not with_return
                              else ''))

    @pytest.mark.parametrize('code', _TestDefineFuncBase._syntax_error_code)
    def test_define_func_syntax_error(self, code):
        """Test define_func with code raising Python syntax error."""
        self._test_define_syntax_error(fdu.define_func, 'function', code)

    @pytest.mark.parametrize('code,error', _TestDefineFuncBase._invalid_code)
    def test_define_func_invalid_code(self, code, error):
        """Test define_func, code raising NameError or ImportError."""
        self._test_define_invalid_code(fdu.define_func, 'function', code, error)


class TestDefineTransformFunc(_TestDefineFuncBase):

    """Tests for function define_transform_func."""

    def test_define_transform_func_single_expr(self):
        """Test define_transform_func with a single expression."""
        self._test_define_single_expr(fdu.define_transform_func, 'transfunc')

    @pytest.mark.parametrize(
        'code,result,regexp,repl,count,flags',
        _perl_subst_testcases
    )
    def test_define_transform_func_perl_subst(self, code, result, regexp, repl,
                                              count, flags):
        """Test define_transform_func with a Perl-style regexp substitution."""
        func, funcdef = fdu.define_transform_func(code)
        assert func(_perl_subst_input) == result
        assert funcdef == (f'def transfunc(val):\n  return re.sub('
                           f'r"""{regexp}""", r"""{repl}""", val, {count},'
                           f' {flags})')

    @pytest.mark.parametrize('with_return', [False, True])
    def test_define_transform_func_multi_line(self, with_return):
        """Test define_transform_func with a multi-line function body."""
        self._test_define_multi_line(
            fdu.define_transform_func, 'transfunc', with_return)

    @pytest.mark.parametrize(
        'code',
        _perl_subst_testcases_invalid
    )
    def test_define_transform_func_perl_subst_error(self, code):
        """Test define_transform_func with invalid Perl-style substitution."""
        with pytest.raises(
                fdu.FuncDefError,
                match=('Perl-style substitution not of the form'
                       r' s/regexp/repl/\[agilx]\*:')):
            func, funcdef = fdu.define_transform_func(code)

    @pytest.mark.parametrize('code', _TestDefineFuncBase._syntax_error_code)
    def test_define_transform_func_syntax_error(self, code):
        """Test define_transform_func with code raising Python syntax error."""
        self._test_define_syntax_error(
            fdu.define_transform_func, 'transformation', code)

    @pytest.mark.parametrize('code,error', _TestDefineFuncBase._invalid_code)
    def test_define_transform_func_invalid_code(self, code, error):
        """Test define_transform_func, code raising NameError or ImportError."""
        self._test_define_invalid_code(
            fdu.define_transform_func, 'transformation', code, error)


class TestConvertPerlSubst:

    """Tests for function convert_perl_subst."""

    @pytest.mark.parametrize(
        # Ignore the result parameter
        'expr,_,regexp,repl,count,flags',
        _perl_subst_testcases,
    )
    def test_convert_perl_subst(self, expr, _, regexp, repl, count, flags):
        """Test convert_perl_subst with various substitution expressions."""
        result = (
            f're.sub(r"""{regexp}""", r"""{repl}""", val, {count}, {flags})')
        assert fdu.convert_perl_subst(expr) == result

    @pytest.mark.parametrize(
        'expr',
        _perl_subst_testcases_invalid
    )
    def test_convert_perl_subst_invalid(self, expr):
        """Test convert_perl_subst with invalid substitution expressions."""
        assert fdu.convert_perl_subst(expr) == None
