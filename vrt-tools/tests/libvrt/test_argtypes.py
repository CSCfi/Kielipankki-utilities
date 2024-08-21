
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


class TestAttrRegexList:

    """Tests for vrtlib.argtypes function attr_regex_list."""

    @pytest.mark.parametrize(
        'input,expected', [
            ('', b''),
            ('a', b'a'),
            ('a,b', b'a|b'),
            ('a b', b'a|b'),
            (' a   b  ', b'a|b'),
            (' a ,  b , ', b'a|b'),
            (',a,,,b,,,', b'a|b'),
            ('a.,b.+,c[de],f(g|hi)j', b'a.|b.+|c[de]|f(g|hi)j'),
        ]
    )
    def test_attr_regex_list(self, input, expected):
        """Test attr_regex_list() with various inputs."""
        assert at.attr_regex_list(input).pattern == expected

    @pytest.mark.parametrize(
        'input,dupl', [
            ('a,a', 'a'),
            ('a a', 'a'),
            ('a,b,a', 'a'),
            ('a.b,c, a.b', 'a.b'),
        ]
    )
    def test_attr_regex_list_dupl(self, input, dupl):
        """Test attr_regex_list() with duplicate values."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            assert at.attr_regex_list(input)
        assert (f'duplicate attribute name regular expressions: {dupl}'
                in str(excinfo.value))

    @pytest.mark.parametrize(
        'input,invalid,errmsg', [
            ('a,+.', '+.', 'nothing to repeat at position 0'),
            ('a,(a', '(a', 'missing ), unterminated subpattern at position 0'),
            ('a,a)', 'a)', 'unbalanced parenthesis at position 1'),
            ('a,[a', '[a', 'unterminated character set at position 0'),
        ]
    )
    def test_attr_regex_list_invalid(self, input, invalid, errmsg):
        """Test attr_regex_list() with invalid values."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            assert at.attr_regex_list(input)
        assert (
            f'invalid attribute name regular expression: "{invalid}": {errmsg}'
            in str(excinfo.value))


class TestAttrRegexListValue:

    """Tests for vrtlib.argtypes function attr_regex_list_value."""

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
            ('a.,b.+,c[de],f(g|hi)j:x', (b'a.|b.+|c[de]|f(g|hi)j', b'x')),
        ]
    )
    def test_attr_regex_list_value(self, input, expected):
        """Test attr_regex_list_value() with various inputs."""
        result = at.attr_regex_list_value(input)
        assert (result[0].pattern, result[1]) == expected

    @pytest.mark.parametrize(
        'input,dupl', [
            ('a,a:x', 'a'),
            ('a a:x', 'a'),
            ('a,b,a:x', 'a'),
            ('a.b,c, a.b:x', 'a.b'),
        ]
    )
    def test_attr_regex_list_value_dupl(self, input, dupl):
        """Test attr_regex_list_value() with duplicate values."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            assert at.attr_regex_list_value(input)
        assert (f'duplicate attribute name regular expressions: {dupl}'
                in str(excinfo.value))

    @pytest.mark.parametrize(
        'input,invalid,errmsg', [
            ('a,+.:x', '+.', 'nothing to repeat at position 0'),
            ('a,(a:x', '(a',
             'missing ), unterminated subpattern at position 0'),
            ('a,a):x', 'a)', 'unbalanced parenthesis at position 1'),
            ('a,[a:x', '[a', 'unterminated character set at position 0'),
        ]
    )
    def test_attr_regex_list_value_invalid(self, input, invalid, errmsg):
        """Test attr_regex_list_value() with invalid values."""
        with pytest.raises(ArgumentTypeError) as excinfo:
            assert at.attr_regex_list_value(input)
        assert (
            f'invalid attribute name regular expression: "{invalid}": {errmsg}'
            in str(excinfo.value))
