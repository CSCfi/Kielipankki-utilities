
"""
test_argtypes.py

Pytest tests for libvrt.argtypes.
"""


import pytest

from argparse import ArgumentTypeError

import libvrt.argtypes as at


class TestEncodeUtf8:

    """Tests for vrtlib.argtypes function encode_utf8."""

    @pytest.mark.parametrize(
        'input,expected', [
            ('', b''),
            ('xy', b'xy'),
            ('äé', 'äé'.encode('UTF-8')),
        ]
    )
    def test_encode_utf8(self, input, expected):
        """Test encode_utf8() with various inputs."""
        assert at.encode_utf8(input) == expected


class TestAttrlist:

    """Tests for vrtlib.argtypes function attrlist."""

    @pytest.mark.parametrize(
        'input,expected', [
            ('', []),
            ('a', [b'a']),
            ('a,b', [b'a', b'b']),
            ('a b', [b'a', b'b']),
            (' a   b  ', [b'a', b'b']),
            (' a ,  b , ', [b'a', b'b']),
            (',a,,,b,,,', [b'a', b'b']),
        ]
    )
    def test_attrlist(self, input, expected):
        """Test attrlist() with various inputs."""
        assert at.attrlist(input) == expected

    @pytest.mark.parametrize(
        'input', [
            'a,a',
            'a a',
            'a,b,a',
        ]
    )
    def test_attrlist_dupl(self, input):
        """Test attrlist() with duplicate values."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            assert at.attrlist(input)
        assert 'duplicate attribute names: a' in str(excinfo.value)

    @pytest.mark.parametrize(
        'input,invalid', [
            ('a,Z', 'Z'),
            ('a,:zz', ':zz'),
            ('a,zz.', 'zz.'),
            ('a,z/z', 'z/z'),
            ('a,1x', '1x'),
            ('a,1x,b', '1x'),
            ('1x,b', '1x'),
            ('1x,1z', '1x'),
        ]
    )
    def test_attrlist_invalid(self, input, invalid):
        """Test attrlist() with invalid values."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            assert at.attrlist(input)
        assert f'invalid attribute name: {invalid}' in str(excinfo.value)


class TestAttrRegexListCombined:

    """Tests for vrtlib.argtypes function attr_regex_list_combined."""

    @pytest.mark.parametrize(
        'input,expected', [
            ('', b''),
            ('a', b'a'),
            ('a,b', b'a|b'),
            ('a b', b'a|b'),
            (' a   b  ', b'a|b'),
            (' a ,  b , ', b'a|b'),
            (',a,,,b,,,', b'a|b'),
            ('_,a', b'_|a'),
            ('_.*,a', b'_.*|a'),
            ('_.+2,a', b'_.+2|a'),
            ('a.,b.+,c[de],f(g|hi)j', b'a.|b.+|c[de]|f(g|hi)j'),
            (r'a\Db', br'a\Db'),
            ('(?P<a>[a-z])(?P=a)', b'(?P<a>[a-z])(?P=a)'),
        ]
    )
    def test_attr_regex_list_combined(self, input, expected):
        """Test attr_regex_list_combined() with various inputs."""
        assert at.attr_regex_list_combined(input).pattern == expected

    @pytest.mark.parametrize(
        'input,dupl', [
            ('a,a', 'a'),
            ('a a', 'a'),
            ('a,b,a', 'a'),
            ('a.b,c, a.b', 'a.b'),
        ]
    )
    def test_attr_regex_list_combined_dupl(self, input, dupl):
        """Test attr_regex_list_combined() with duplicate values."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            assert at.attr_regex_list_combined(input)
        assert (f'duplicate attribute name regular expressions: {dupl}'
                in str(excinfo.value))

    @pytest.mark.parametrize(
        'input,invalid,errmsg', [
            ('a,+.', '+.', 'nothing to repeat at position 0'),
            ('a,(a', '(a', 'missing ), unterminated subpattern at position 0'),
            ('a,a)', 'a)', 'unbalanced parenthesis at position 1'),
            ('a,[a', '[a', 'unterminated character set at position 0'),
            ('a,aäb', 'aäb', 'contains non-ASCII characters'),
            ('a,a\x01b', 'a\x01b', 'contains non-printable characters'),
            ('a,aUb', 'aUb', 'contains upper-case characters'),
        ]
    )
    def test_attr_regex_list_combined_invalid(self, input, invalid, errmsg):
        """Test attr_regex_list_combined() with invalid values."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            assert at.attr_regex_list_combined(input)
        assert (
            f'invalid attribute name regular expression: "{invalid}": {errmsg}'
            in str(excinfo.value))


class TestAttrRegexListIndividual:

    """Tests for vrtlib.argtypes function attr_regex_list_individual."""

    @pytest.mark.parametrize(
        'input,expected', [
            ('', []),
            ('a', [b'a']),
            ('a,b', [b'a', b'b']),
            ('a b', [b'a', b'b']),
            (' a   b  ', [b'a', b'b']),
            (' a ,  b , ', [b'a', b'b']),
            (',a,,,b,,,', [b'a', b'b']),
            ('_,a', [b'_', b'a']),
            ('_.*,a', [b'_.*', b'a']),
            ('.+2,a', [b'.+2', b'a']),
            ('a.,b.+,c[de],f(g|hi)j', [b'a.', b'b.+', b'c[de]', b'f(g|hi)j']),
            (r'a\Db', [br'a\Db']),
            ('(?P<a>[a-z])(?P=a)', [b'(?P<a>[a-z])(?P=a)']),
        ]
    )
    def test_attr_regex_list_individual(self, input, expected):
        """Test attr_regex_list_individual() with various inputs."""
        result = at.attr_regex_list_individual(input)
        [regex.pattern for regex in result] == expected

    @pytest.mark.parametrize(
        'input,dupl', [
            ('a,a', 'a'),
            ('a a', 'a'),
            ('a,b,a', 'a'),
            ('a.b,c, a.b', 'a.b'),
        ]
    )
    def test_attr_regex_list_individual_dupl(self, input, dupl):
        """Test attr_regex_list_individual() with duplicate values."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            assert at.attr_regex_list_individual(input)
        assert (f'duplicate attribute name regular expressions: {dupl}'
                in str(excinfo.value))

    @pytest.mark.parametrize(
        'input,invalid,errmsg', [
            ('a,+.', '+.', 'nothing to repeat at position 0'),
            ('a,(a', '(a', 'missing ), unterminated subpattern at position 0'),
            ('a,a)', 'a)', 'unbalanced parenthesis at position 1'),
            ('a,[a', '[a', 'unterminated character set at position 0'),
            ('a,aäb', 'aäb', 'contains non-ASCII characters'),
            ('a,a\x01b', 'a\x01b', 'contains non-printable characters'),
            ('a,aUb', 'aUb', 'contains upper-case characters'),
        ]
    )
    def test_attr_regex_list_individual_invalid(self, input, invalid, errmsg):
        """Test attr_regex_list_individual() with invalid values."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            assert at.attr_regex_list_individual(input)
        assert (
            f'invalid attribute name regular expression: "{invalid}": {errmsg}'
            in str(excinfo.value))


class TestAttrRegexListCombinedValue:

    """Tests for vrtlib.argtypes function attr_regex_list_combined_value."""

    @pytest.mark.parametrize(
        'input,expected', [
            # Value only
            ('', (b'.+', b'')),
            ('a', (b'.+', b'a')),
            ('a,b', (b'.+', b'a,b')),
            ('a,a', (b'.+', b'a,a')),
            ('a b', (b'.+', b'a b')),
            (' a   b  ', (b'.+', b' a   b  ')),
            # Value prefixed by a colon
            (':a', (b'.+', b'a')),
            # Value containing a colon
            ('::', (b'.+', b':')),
            (':a:a', (b'.+', b'a:a')),
            # Regular expression (list) with a value
            ('a:a:a', (b'a', b'a:a')),
            ('a,b:x', (b'a|b', b'x')),
            ('a b:x', (b'a|b', b'x')),
            (' a   b  :x', (b'a|b', b'x')),
            (' a ,  b , : x ', (b'a|b', b' x ')),
            (',a,,,b,,,:x', (b'a|b', b'x')),
            ('_,a:x', (b'_|a', b'x')),
            ('_.*,a:x', (b'_.*|a', b'x')),
            ('.*2,a:x', (b'.*2|a', b'x')),
            ('a.,b.+,c[de],f(g|hi)j:x', (b'a.|b.+|c[de]|f(g|hi)j', b'x')),
        ]
    )
    def test_attr_regex_list_combined_value(self, input, expected):
        """Test attr_regex_list_combined_value() with various inputs."""
        result = at.attr_regex_list_combined_value(input)
        assert (result[0].pattern, result[1]) == expected

    @pytest.mark.parametrize(
        'input,dupl', [
            ('a,a:x', 'a'),
            ('a a:x', 'a'),
            ('a,b,a:x', 'a'),
            ('a.b,c, a.b:x', 'a.b'),
        ]
    )
    def test_attr_regex_list_combined_value_dupl(self, input, dupl):
        """Test attr_regex_list_combined_value() with duplicate values."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            assert at.attr_regex_list_combined_value(input)
        assert (f'duplicate attribute name regular expressions: {dupl}'
                in str(excinfo.value))

    @pytest.mark.parametrize(
        'input,invalid,errmsg', [
            ('a,+.:x', '+.', 'nothing to repeat at position 0'),
            ('a,(a:x', '(a',
             'missing ), unterminated subpattern at position 0'),
            ('a,a):x', 'a)', 'unbalanced parenthesis at position 1'),
            ('a,[a:x', '[a', 'unterminated character set at position 0'),
            ('a,aäb:x', 'aäb', 'contains non-ASCII characters'),
            ('a,a\x01b:x', 'a\x01b', 'contains non-printable characters'),
            ('a,aUb:x', 'aUb', 'contains upper-case characters'),
        ]
    )
    def test_attr_regex_list_combined_value_invalid(
            self, input, invalid, errmsg):
        """Test attr_regex_list_combined_value() with invalid values."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            assert at.attr_regex_list_combined_value(input)
        assert (
            f'invalid attribute name regular expression: "{invalid}": {errmsg}'
            in str(excinfo.value))


class TestAttrRegexListIndividualValue:

    """Tests for vrtlib.argtypes function attr_regex_list_individual_value."""

    # CHECK: This class is copied and modified from
    # TestAttrRegexListCombinedValue. Could the two classes be
    # combined or the repetition otherwise be reduced?

    @pytest.mark.parametrize(
        'input,expected', [
            # Value only
            ('', [(b'.+', b'')]),
            ('a', [(b'.+', b'a')]),
            ('a,b', [(b'.+', b'a,b')]),
            ('a,a', [(b'.+', b'a,a')]),
            ('a b', [(b'.+', b'a b')]),
            (' a   b  ', [(b'.+', b' a   b  ')]),
            # Value prefixed by a colon
            (':a', [(b'.+', b'a')]),
            # Value containing a colon
            ('::', [(b'.+', b':')]),
            (':a:a', [(b'.+', b'a:a')]),
            # Regular expression (list) with a value
            ('a:a:a', [(b'a', b'a:a')]),
            ('a,b:x', [(b'a', b'x'), (b'b', b'x')]),
            ('a b:x', [(b'a', b'x'), (b'b', b'x')]),
            (' a   b  :x', [(b'a', b'x'), (b'b', b'x')]),
            (' a ,  b , : x ', [(b'a', b' x '), (b'b', b' x ')]),
            (',a,,,b,,,:x', [(b'a', b'x'), (b'b', b'x')]),
            ('_,a:x', [(b'_', b'x'), (b'a', b'x')]),
            ('_.*,a:x', [(b'_.*', b'x'), (b'a', b'x')]),
            ('.*2,a:x', [(b'.*2', b'x'), (b'a', b'x')]),
            ('a.,b.+,c[de],f(g|hi)j:x', [
                (b'a.', b'x'),
                (b'b.+', b'x'),
                (b'c[de]', b'x'),
                (b'f(g|hi)j', b'x'),
            ]),
        ]
    )
    def test_attr_regex_list_individual_value(self, input, expected):
        """Test attr_regex_list_individual_value() with various inputs."""
        result = at.attr_regex_list_individual_value(input)
        assert len(result) == len(expected)
        for i, exp_item in enumerate(expected):
            assert (result[i][0].pattern, result[i][1]) == exp_item

    @pytest.mark.parametrize(
        'input,dupl', [
            ('a,a:x', 'a'),
            ('a a:x', 'a'),
            ('a,b,a:x', 'a'),
            ('a.b,c, a.b:x', 'a.b'),
        ]
    )
    def test_attr_regex_list_individual_value_dupl(self, input, dupl):
        """Test attr_regex_list_individual_value() with duplicate values."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            assert at.attr_regex_list_individual_value(input)
        assert (f'duplicate attribute name regular expressions: {dupl}'
                in str(excinfo.value))

    @pytest.mark.parametrize(
        'input,invalid,errmsg', [
            ('a,+.:x', '+.', 'nothing to repeat at position 0'),
            ('a,(a:x', '(a',
             'missing ), unterminated subpattern at position 0'),
            ('a,a):x', 'a)', 'unbalanced parenthesis at position 1'),
            ('a,[a:x', '[a', 'unterminated character set at position 0'),
            ('a,aäb:x', 'aäb', 'contains non-ASCII characters'),
            ('a,a\x01b:x', 'a\x01b', 'contains non-printable characters'),
            ('a,aUb:x', 'aUb', 'contains upper-case characters'),
        ]
    )
    def test_attr_regex_list_individual_value_invalid(
            self, input, invalid, errmsg):
        """Test attr_regex_list_individual_value() with invalid values."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            assert at.attr_regex_list_individual_value(input)
        assert (
            f'invalid attribute name regular expression: "{invalid}": {errmsg}'
            in str(excinfo.value))


class TestAttrValueOpts:

    """Tests for `vrtlib.argtypes` function `attr_value_opts`."""

    @pytest.mark.parametrize('encode', [False, True])
    @pytest.mark.parametrize('strip', [False, True])
    @pytest.mark.parametrize(
        'regex,prefix,suffix,seps,input,expected', [
            # Simple value
            (None, None, None, None, 'a=b', ('a', 'b')),
            # Simple value, colon separator
            (None, None, None, None, 'a:b', ('a', 'b')),
            # Empty value
            (None, None, None, None, 'a=', ('a', '')),
            # Value with spaces only
            (None, None, None, None, 'a= \t ', ('a', ' \t ')),
            # Spaces around name and value
            (None, None, None, None, ' a =  b c  ', ('a', '  b c  ')),
            # Value containing =, : and "
            (None, None, None, None, 'a=b:=c="d"e', ('a', 'b:=c="d"e')),
            # Attribute name containing _ and digits
            (None, None, None, None, '_a_b_9_=c', ('_a_b_9_', 'c')),
            # Attribute name regex allowing . and :
            ('[_a-z][_a-z0-9:.]*', None, None, '=', 'a.b:c=d', ('a.b:c', 'd')),
            # Allow attribute name prefix !
            (None, '!', None, None, '!a_b = c ', ('!a_b', ' c ')),
            # Allow attribute name suffix /
            (None, None, '/', None, 'a_b/ = c ', ('a_b/', ' c ')),
            # The above three combined
            ('[_a-z][_a-z0-9:.]*', '!', '/', '=', '!a.b:c/ = d ',
             ('!a.b:c/', ' d ')),
            # Space as name-value separator
            (None, None, None, ' ', ' a b c ', ('a', 'b c ')),
        ]
    )
    def test_attr_value_opts(self, encode, strip, regex, prefix, suffix, seps,
                             input, expected):
        """Test `attr_value_opts` with various options and inputs."""
        if strip:
            expected = (expected[0], expected[1].strip())
        if encode:
            expected = tuple(val.encode('utf-8') for val in expected)
        result = at.attr_value_opts(
            attrname_regex=regex, attrname_prefix=prefix,
            attrname_suffix=suffix, sepchars=seps, strip_value=strip,
            return_bytes=encode)(input)
        assert result == expected

    @pytest.mark.parametrize(
        'seps,input', [
            (None, ''),
            (None, '  '),
            (None, 'abc/def'),
            (None, 'abc def'),
            (' ', 'abc=def'),
            (':=/', 'abcdef'),
        ]
    )
    def test_attr_value_opts_no_separator(self, seps, input):
        """Test `attr_value_opts` with invalid values without a separator."""
        seplist = ', '.join(f'"{sep}"' for sep in seps or ':=')
        with pytest.raises(ArgumentTypeError, match=(
                fr'no name-value separator \({seplist}\) in attribute-value'
                f' specification: {input}$')):
            result = at.attr_value_opts(sepchars=seps)(input)

    @pytest.mark.parametrize(
        'regex,prefix,suffix,input,invalid', [
            (None, None, None, '1a=b', '1a'),
            (None, None, None, '1=2', '1'),
            (None, None, None, 'a-b=c', 'a-b'),
            (None, None, None, '&=a', '&'),
            (None, None, None, '&a=b', '&a'),
            (None, None, None, '=a', ''),
            (None, None, None, ' =a', ''),
            (None, None, None, 'a b=c', 'a b'),
            (None, None, None, ' a b =c', 'a b'),
            (None, None, None, 'a.b=c', 'a.b'),
            ('[a-z]', None, None, 'aa=b', 'aa'),
            (None, '!', None, '&a=2', '&a'),
            (None, None, '@', 'a&=c', 'a&'),
            ('[a-z]', '!', '@', '!aa@=b', '!aa@'),
        ]
    )
    def test_attr_value_opts_invalid_attrname(self, regex, prefix, suffix,
                                              input, invalid):
        """Test `attr_value_opts` with invalid attribute names."""
        with pytest.raises(ArgumentTypeError,
                           match=(f'invalid attribute name "{invalid}" in'
                                  f' attribute-value specification: {input}$')):
            result = at.attr_value_opts(
                attrname_regex=regex, attrname_prefix=prefix,
                attrname_suffix=suffix)(input)


class TestAttrValue:

    """Tests for vrtlib.argtypes functions attr_value and attr_value_str."""

    # Functions to test (for parametrization)
    _attr_value_funcs = [
        at.attr_value_str,
        at.attr_value,
    ]

    @pytest.mark.parametrize('attr_value_func', _attr_value_funcs)
    # Whether to convert = to :
    @pytest.mark.parametrize('colon', [False, True])
    @pytest.mark.parametrize(
        'input,expected', [
            # Simple value
            ('a=b', ('a', 'b')),
            # Empty value
            ('a=', ('a', '')),
            # Value with spaces
            ('a=b c', ('a', 'b c')),
            # Value with leading spaces
            ('a=  bc', ('a', '  bc')),
            # Value with trailing spaces
            ('a=bc  ', ('a', 'bc  ')),
            # Value containing =
            ('a=b=c=d', ('a', 'b=c=d')),
            # Value containing :
            ('a=b:c:d', ('a', 'b:c:d')),
            # Value containing "
            ('a=b"c"d', ('a', 'b"c"d')),
            # Spaces around attribute name
            (' a =b', ('a', 'b')),
            # Attribute name containing _
            ('_a_b_=c', ('_a_b_', 'c')),
            # Sole _ as attribute name
            ('_=c', ('_', 'c')),
            # Attribute name containing digits
            ('ab9=c', ('ab9', 'c')),
        ]
    )
    def test_attr_value(self, attr_value_func, colon, input, expected):
        """Test attr_value(_str) with various inputs."""
        if colon:
            input = input.replace('=', ':', 1)
        if attr_value_func == at.attr_value:
            expected = tuple(val.encode('utf-8') for val in expected)
        result = attr_value_func(input)
        assert result == expected

    @pytest.mark.parametrize('attr_value_func', _attr_value_funcs)
    @pytest.mark.parametrize(
        'input', [
            '',
            '  ',
            'abc/def',
            'abc def',
        ]
    )
    def test_attr_value_no_separator(self, attr_value_func, input):
        """Test attr_value(_str) with invalid values without a separator."""
        with pytest.raises(ArgumentTypeError, match=(
                r'no name-value separator \(":", "="\) in attribute-value'
                f' specification: {input}$')):
            result = attr_value_func(input)

    @pytest.mark.parametrize('attr_value_func', _attr_value_funcs)
    @pytest.mark.parametrize(
        'input,invalid', [
            ('1a=b', '1a'),
            ('1=2', '1'),
            ('a-b=c', 'a-b'),
            ('&=a', '&'),
            ('&a=b', '&a'),
            ('=a', ''),
            (' =a', ''),
            ('a b=c', 'a b'),
            (' a b =c', 'a b'),
            ('a.b=c', 'a.b'),
        ]
    )
    def test_attr_value_invalid_attrname(self, attr_value_func, input, invalid):
        """Test attr_value(_str) with invalid attribute names."""
        with pytest.raises(ArgumentTypeError,
                           match=(f'invalid attribute name "{invalid}" in'
                                  f' attribute-value specification: {input}$')):
            result = attr_value_func(input)


class TestListOpts:

    """Tests for libvrt.argtypes function list_opts."""

    # Basic splitting

    @pytest.mark.parametrize(
        'seps,input,expected', [
            # Default seps split on commas and spaces
            (None, 'a', ['a']),
            (None, 'a,b', ['a', 'b']),
            (None, 'a b', ['a', 'b']),
            (None, 'a,b,c', ['a', 'b', 'c']),
            # Multiple adjacent separators are treated as one
            (None, 'a,,b', ['a', 'b']),
            (None, 'a, b', ['a', 'b']),
            # Custom separators
            (':', 'a:b:c', ['a', 'b', 'c']),
            ('|', 'a|b', ['a', 'b']),
            ('|:', 'a|b:c', ['a', 'b', 'c']),
        ]
    )
    def test_split(self, seps, input, expected):
        """Test list_opts splitting with default and custom separators."""
        assert at.list_opts(seps=seps)(input) == expected

    def test_seps_empty_no_split(self):
        """Test list_opts with seps='' applies process_item to whole string."""
        # When seps='', the whole string is passed to process_item directly
        assert at.list_opts(seps='')('hello world') == 'hello world'

    def test_seps_empty_with_process_item(self):
        """Test list_opts with seps='' and a process_item function."""
        assert at.list_opts(seps='', process_item=str.upper)('hello') == 'HELLO'

    # process_item as callable

    def test_process_item_function(self):
        """Test list_opts with process_item as a callable."""
        assert at.list_opts(process_item=str.upper)('a,b') == ['A', 'B']

    # process_item as regex

    def test_process_item_regex_valid(self):
        """Test list_opts with process_item as a regex; valid items pass."""
        assert at.list_opts(process_item=r'[a-z]+')('a,b') == ['a', 'b']

    def test_process_item_regex_invalid_item(self):
        """Test list_opts with process_item regex; invalid item raises error."""
        with pytest.raises(ArgumentTypeError, match='invalid item: 1'):
            at.list_opts(process_item=r'[a-z]+')('a,1')

    def test_process_item_regex_custom_item_name(self):
        """Test list_opts item_name is used in error messages."""
        with pytest.raises(ArgumentTypeError, match='invalid letter: 1'):
            at.list_opts(
                process_item=r'[a-z]+', item_name='letter')('a,1')

    # process_item as list (composition)

    def test_process_item_list_of_functions(self):
        """Test list_opts with process_item as a list of callables."""
        # Functions applied in order: upper first, then strip
        assert at.list_opts(
            process_item=[str.upper, str.strip])('a,b') == ['A', 'B']

    def test_process_item_list_regex_and_function(self):
        """Test list_opts with process_item as list mixing regex and callable."""
        assert at.list_opts(
            process_item=[r'[a-z]+', str.upper])('a,b') == ['A', 'B']

    # process_result

    def test_process_result_function(self):
        """Test list_opts with process_result applied to the whole list."""
        assert at.list_opts(process_result=sorted)('c,a,b') == ['a', 'b', 'c']

    def test_process_result_list_of_functions(self):
        """Test list_opts with process_result as a list of functions."""
        assert at.list_opts(
            process_result=[sorted, list])('c,a,b') == ['a', 'b', 'c']

    # return_bytes — these tests expose the bug in list_opts

    def test_return_bytes_no_process_item(self):
        """Test list_opts return_bytes=True with no process_item."""
        # Bug: currently raises AttributeError (None.append)
        assert at.list_opts(return_bytes=True)('a,b') == [b'a', b'b']

    def test_return_bytes_with_function(self):
        """Test list_opts return_bytes=True with process_item as a function."""
        # Bug: currently raises AttributeError (method.append)
        assert at.list_opts(
            process_item=str.upper, return_bytes=True)('a,b') == [b'A', b'B']

    def test_return_bytes_with_regex(self):
        """Test list_opts return_bytes=True with process_item as a regex."""
        # Bug: currently raises AttributeError (str.append)
        assert at.list_opts(
            process_item=r'[a-z]+',
            return_bytes=True)('a,b') == [b'a', b'b']

    def test_return_bytes_with_list_no_mutation(self):
        """Test list_opts return_bytes=True with process_item as list.

        The original process_item list must not be mutated; encode_utf8
        would accumulate on repeated calls otherwise.
        """
        process_item = [str.upper]
        at.list_opts(process_item=process_item, return_bytes=True)('a,b')
        # Bug: currently mutates process_item, adding encode_utf8 each time
        assert process_item == [str.upper]

    def test_return_bytes_stable_on_repeated_calls(self):
        """Test list_opts return_bytes=True gives consistent results on repeat.

        With the mutation bug a second call would try encode_utf8(bytes)
        and crash.
        """
        fn = at.list_opts(return_bytes=True)
        assert fn('a,b') == [b'a', b'b']
        # Bug: second call fails when process_item list has been mutated
        assert fn('c,d') == [b'c', b'd']


class TestKeylistValuelistOpts:

    """Tests for libvrt.argtypes function keylist_valuelist_opts."""

    # Basic key-value splitting

    @pytest.mark.parametrize(
        'input,expected', [
            ('a=b', (['a'], ['b'])),
            ('a:b', (['a'], ['b'])),
            ('a,b=x,y', (['a', 'b'], ['x', 'y'])),
            ('a=x,y', (['a'], ['x', 'y'])),
            ('a,b=x', (['a', 'b'], ['x'])),
        ]
    )
    def test_basic(self, input, expected):
        """Test keylist_valuelist_opts with default separators."""
        assert at.keylist_valuelist_opts()(input) == expected

    # key_value_seps='' — return only a value list

    def test_empty_key_value_seps_returns_list(self):
        """Test that key_value_seps='' returns only a value list."""
        assert at.keylist_valuelist_opts(key_value_seps='')('a,b') == ['a', 'b']

    # Custom key_value_seps

    def test_custom_key_value_seps(self):
        """Test keylist_valuelist_opts with custom key_value_seps."""
        assert at.keylist_valuelist_opts(
            key_value_seps='|')('a,b|x,y') == (['a', 'b'], ['x', 'y'])

    # Custom key_seps / value_seps

    def test_custom_key_seps(self):
        """Test keylist_valuelist_opts with custom key_seps."""
        assert at.keylist_valuelist_opts(
            key_seps=':', key_value_seps='=')('a:b=x') == (['a', 'b'], ['x'])

    def test_custom_value_seps(self):
        """Test keylist_valuelist_opts with custom value_seps."""
        assert at.keylist_valuelist_opts(
            value_seps=':', key_value_seps='=')('a=x:y') == (['a'], ['x', 'y'])

    # default_key and default_value

    def test_default_key_used_when_no_separator(self):
        """Test that default_key is used when input has no key-value sep."""
        assert at.keylist_valuelist_opts(
            default_key='k')('v') == (['k'], ['v'])

    def test_default_value_used_when_no_separator(self):
        """Test that default_value is used when input has no key-value sep."""
        assert at.keylist_valuelist_opts(
            default_value='v')('k') == (['k'], ['v'])

    def test_default_key_takes_precedence_over_default_value(self):
        """Test that default_key is preferred over default_value."""
        assert at.keylist_valuelist_opts(
            default_key='k',
            default_value='v')('x') == (['k'], ['x'])

    # Error: no separator and no defaults

    def test_no_separator_no_defaults_raises(self):
        """Test error raised when no sep and neither default is given."""
        with pytest.raises(
                ArgumentTypeError,
                match=r'no key-value separator \(":", "="\)'):
            at.keylist_valuelist_opts()('ab')

    def test_no_separator_arg_type_name_in_error(self):
        """Test that arg_type_name appears in the error message."""
        with pytest.raises(ArgumentTypeError, match='in mytype'):
            at.keylist_valuelist_opts(arg_type_name='mytype')('ab')

    # strip_key and strip_value

    def test_strip_key(self):
        """Test strip_key=True strips whitespace from the key string."""
        assert at.keylist_valuelist_opts(
            strip_key=True)('  a  =b') == (['a'], ['b'])

    def test_strip_value(self):
        """Test strip_value=True strips whitespace from the value string."""
        assert at.keylist_valuelist_opts(
            strip_value=True)('a=  b  ') == (['a'], ['b'])

    # return_bytes — inherits list_opts bug

    def test_return_bytes(self):
        """Test keylist_valuelist_opts return_bytes=True encodes to bytes."""
        # Bug: currently raises AttributeError (None.append) via list_opts
        assert at.keylist_valuelist_opts(
            return_bytes=True)('a=b') == ([b'a'], [b'b'])

    def test_return_bytes_multiple(self):
        """Test keylist_valuelist_opts return_bytes=True with lists."""
        assert at.keylist_valuelist_opts(
            return_bytes=True)('a,b=x,y') == ([b'a', b'b'], [b'x', b'y'])

    def test_return_bytes_stable_on_repeated_calls(self):
        """Test return_bytes=True gives consistent results on repeat calls."""
        fn = at.keylist_valuelist_opts(return_bytes=True)
        assert fn('a=b') == ([b'a'], [b'b'])
        # Bug: second call fails due to list mutation in list_opts
        assert fn('c=d') == ([b'c'], [b'd'])

    def test_return_bytes_with_process_key_function(self):
        """Test return_bytes=True with process_key as a function."""
        assert at.keylist_valuelist_opts(
            process_key=str.upper, return_bytes=True)('a=b') == (
                [b'A'], [b'b'])

    # process_key, process_value

    def test_process_key_function(self):
        """Test process_key function is applied to each key item."""
        assert at.keylist_valuelist_opts(
            process_key=str.upper)('a,b=x') == (['A', 'B'], ['x'])

    def test_process_value_function(self):
        """Test process_value function is applied to each value item."""
        assert at.keylist_valuelist_opts(
            process_value=str.upper)('a=x,y') == (['a'], ['X', 'Y'])

    def test_process_key_regex(self):
        """Test process_key as a regex validates each key item."""
        assert at.keylist_valuelist_opts(
            process_key=r'[a-z]+')('a,b=x') == (['a', 'b'], ['x'])

    def test_process_key_regex_invalid(self):
        """Test process_key regex raises on invalid key."""
        with pytest.raises(ArgumentTypeError, match='invalid key: 1'):
            at.keylist_valuelist_opts(
                process_key=r'[a-z]+', key_name='key')('1=x')

    def test_process_value_regex_invalid(self):
        """Test process_value regex raises on invalid value."""
        with pytest.raises(ArgumentTypeError, match='invalid value: 1'):
            at.keylist_valuelist_opts(
                process_value=r'[a-z]+', value_name='value')('a=1')

    # process_keylist, process_valuelist

    def test_process_keylist_function(self):
        """Test process_keylist is applied to the full key list."""
        assert at.keylist_valuelist_opts(
            process_keylist=sorted)('b,a=x') == (['a', 'b'], ['x'])

    def test_process_valuelist_function(self):
        """Test process_valuelist is applied to the full value list."""
        assert at.keylist_valuelist_opts(
            process_valuelist=sorted)('a=y,x') == (['a'], ['x', 'y'])


class TestStructAttrRegex:

    """Tests for libvrt.argtypes function struct_attr_regex."""

    @pytest.mark.parametrize(
        'input,expected_struct,expected_attr,expected_regex_pattern', [
            ('text:a=foo', b'text', b'a', b'foo'),
            ('paragraph:type=intro', b'paragraph', b'type', b'intro'),
            # Regex with alternation
            ('paragraph:type=intro|body', b'paragraph', b'type', b'intro|body'),
            # Regex with quantifier
            ('sentence:id=.+', b'sentence', b'id', b'.+'),
            # Regex containing '='
            ('text:a=x=y', b'text', b'a', b'x=y'),
            # Empty regex
            ('text:a=', b'text', b'a', b''),
            # Attribute name with underscores and digits
            ('text:my_attr2=val', b'text', b'my_attr2', b'val'),
        ]
    )
    def test_struct_attr_regex_valid(
            self, input, expected_struct, expected_attr,
            expected_regex_pattern):
        """Test struct_attr_regex() with valid inputs."""
        struct, attr, regex = at.struct_attr_regex(input)
        assert struct == expected_struct
        assert attr == expected_attr
        assert regex.pattern == expected_regex_pattern

    @pytest.mark.parametrize(
        'input', [
            'text',       # no ':' separator
            'textfoo',    # no ':' separator
            ':a=foo',     # missing struct name
            '1text:a=foo',  # struct name starting with digit
            'Text:a=foo',   # struct name with uppercase
        ]
    )
    def test_struct_attr_regex_invalid_struct(self, input):
        """Test struct_attr_regex() with invalid structure name."""
        with pytest.raises(ArgumentTypeError,
                           match='struct:attr=regex'):
            at.struct_attr_regex(input)

    @pytest.mark.parametrize(
        'input', [
            'text:afoo',    # no '=' separator in attr part
            'text:A=foo',   # attr name with uppercase
            'text:1a=foo',  # attr name starting with digit
            'text::a=foo',  # double colon, attr part starts with ':'
        ]
    )
    def test_struct_attr_regex_invalid_attr(self, input):
        """Test struct_attr_regex() with invalid attribute name."""
        with pytest.raises(ArgumentTypeError,
                           match='struct:attr=regex'):
            at.struct_attr_regex(input)

    @pytest.mark.parametrize(
        'input', [
            r'text:a=[invalid',   # unclosed bracket
            r'text:a=(*)',        # invalid quantifier
        ]
    )
    def test_struct_attr_regex_invalid_regex(self, input):
        """Test struct_attr_regex() with invalid regular expression."""
        with pytest.raises(ArgumentTypeError,
                           match='struct:attr=regex'):
            at.struct_attr_regex(input)


class TestAttrTemplateRegexList:

    """Tests for libvrt.argtypes function attr_template_regex_list."""

    # Helper to extract comparable data from a result
    @staticmethod
    def _result(s, placeholder):
        # Replace "{}" in s with placeholder
        s = s.replace('{}', placeholder)
        template, regexes = at.attr_template_regex_list(s)
        return (template, [r.pattern for r in regexes])

    @pytest.mark.parametrize('placeholder', ['{}', '{attr}'])
    @pytest.mark.parametrize(
        'input,expected_template,expected_patterns', [
            # Minimal template and single regex
            ('new_{}=a', b'new_{}', [b'a']),
            # Colon as separator
            ('new_{}:a', b'new_{}', [b'a']),
            # {} at the start
            ('{}=a', b'{}', [b'a']),
            # {} in the middle
            ('pre_{}suf=a', b'pre_{}suf', [b'a']),
            # {} after underscore prefix
            ('_{}=a', b'_{}', [b'a']),
            # Template with digits after {}
            ('{}_2=a', b'{}_2', [b'a']),
            # Multiple regexes, comma-separated
            ('new_{}=a,b', b'new_{}', [b'a', b'b']),
            # Multiple regexes, space-separated
            ('new_{}=a b', b'new_{}', [b'a', b'b']),
            # Mixed comma/space separators in regex list
            ('new_{}=a, b', b'new_{}', [b'a', b'b']),
            # Whitespace around template is stripped
            (' new_{} =a', b'new_{}', [b'a']),
            # Regex with quantifier
            ('new_{}=a.*', b'new_{}', [b'a.*']),
            # Regex with alternation group
            ('new_{}=f(g|hi)j', b'new_{}', [b'f(g|hi)j']),
        ]
    )
    def test_valid(self, input, expected_template, expected_patterns,
                   placeholder):
        """Test attr_template_regex_list() with valid inputs."""
        assert (self._result(input, placeholder)
                == (expected_template, expected_patterns))

    @pytest.mark.parametrize(
        'input', [
            'new_x_a',      # no separator at all
            'new_{}',       # no separator (no = or :)
        ]
    )
    def test_no_separator(self, input):
        """Test attr_template_regex_list() raises when separator is missing."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            at.attr_template_regex_list(input)
        assert ('no name-value separator (":", "=") in'
                ' attribute-template-regex-list specification'
                in str(excinfo.value))

    @pytest.mark.parametrize(
        'input,template', [
            ('new_x=a', 'new_x'),
            ('prefix=a', 'prefix'),
            ('{a}=a', '{a}'),
            ('{a=a', '{a'),
            (' no_brace =a', 'no_brace'),
        ]
    )
    def test_no_placeholder(self, input, template):
        """Test error when template contains no '{}'."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            at.attr_template_regex_list(input)
        assert (('attribute name template must contain "{}" or "{attr}": '
                 + template) in str(excinfo.value))

    @pytest.mark.parametrize(
        'input,template', [
            ('{}_{}=a', '{}_{}'),
            ('{}{}=a', '{}{}'),
            ('{attr}{attr}=a', '{attr}{attr}'),
            ('{attr}_{}=a', '{attr}_{}'),
        ]
    )
    def test_multiple_placeholders(self, input, template):
        """Test error when template contains more than one '{}'."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            at.attr_template_regex_list(input)
        assert (('attribute name template must contain exactly one "{}" or'
                 ' "{attr}": ' + template) in str(excinfo.value))

    @pytest.mark.parametrize(
        'input,template', [
            # Starts with a digit
            ('1{}=a', '1{}'),
            # Contains uppercase
            ('NEW_{}=a', 'NEW_{}'),
            # Contains a dot
            ('a.{}=a', 'a.{}'),
            # Starts with {}; {} replaced by x gives 'x', but suffix invalid
            ('{}!=a', '{}!'),
            ('{attr}!=a', '{attr}!'),
        ]
    )
    def test_invalid_template(self, input, template):
        """Test error when template is not a valid attribute name."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            at.attr_template_regex_list(input)
        assert (f'invalid attribute name template: {template}'
                in str(excinfo.value))

    @pytest.mark.parametrize(
        'input,dupl', [
            ('new_{}=a,a', 'a'),
            ('new_{}=a a', 'a'),
            ('new_{}=a,b,a', 'a'),
            ('new_{attr}=a,b,a', 'a'),
        ]
    )
    def test_duplicate_regex(self, input, dupl):
        """Test error when regex list contains duplicates."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            at.attr_template_regex_list(input)
        assert (f'duplicate attribute name regular expressions: {dupl}'
                in str(excinfo.value))

    def test_empty_regex_list(self):
        """Test error when regex list is empty."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            at.attr_template_regex_list('new_{}=')
        assert 'attribute regex list must not be empty' in str(excinfo.value)

    @pytest.mark.parametrize(
        'input,invalid,errmsg', [
            ('new_{}=+.', '+.', 'nothing to repeat at position 0'),
            ('new_{}=(a', '(a',
             'missing ), unterminated subpattern at position 0'),
            ('new_{}=aUb', 'aUb', 'contains upper-case characters'),
            ('new_{}=aäb', 'aäb', 'contains non-ASCII characters'),
            ('new_{attr}=aäb', 'aäb', 'contains non-ASCII characters'),
        ]
    )
    def test_invalid_regex(self, input, invalid, errmsg):
        """Test error when regex list contains an invalid regex."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            at.attr_template_regex_list(input)
        assert (
            f'invalid attribute name regular expression: "{invalid}": {errmsg}'
            in str(excinfo.value))
