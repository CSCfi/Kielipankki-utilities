
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
        with pytest.raises(ArgumentTypeError,
                           match=('no ":" nor "=" in attribute-value'
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
