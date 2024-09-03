
"""
test_metaline.py

Pytest tests for libvrt.metaline.
"""


from collections import OrderedDict

import pytest

import libvrt.metaline as ml


def encode_utf8(obj):
    """Recursively encode strings in obj to UTF-8 bytes."""
    if isinstance(obj, str):
        return obj.encode('UTF-8')
    elif isinstance(obj, dict):
        # Use type(obj) to retain the type of OrderedDict and other
        # dict subclasses
        return type(obj)((encode_utf8(name), encode_utf8(val))
                         for name, val in obj.items())
    elif isinstance(obj, (list, tuple)):
        return type(obj)(encode_utf8(item) for item in obj)
    else:
        return obj


class TestElement:

    """Tests for vrtlib.metaline functions .element, strelement."""

    @pytest.mark.parametrize('input,expected',
                             [(b'<elem>', b'elem'),
                              (b'<elem2>', b'elem2')])
    def test_element_starttag_without_attrs(self, input, expected):
        """Test element() for a start tag without attributes."""
        assert ml.element(input) == expected

    @pytest.mark.parametrize('input,expected',
                             [(b'<elem a="a">', b'elem'),
                              (b'<elem2  b="b" c="c">', b'elem2')])
    def test_element_starttag_with_attrs(self, input, expected):
        """Test element() for a start tag with attributes."""
        assert ml.element(input) == expected

    @pytest.mark.parametrize('input,expected',
                             [(b'</elem>', b'elem'),
                              (b'</elem2>', b'elem2')])
    def test_element_endtag(self, input, expected):
        """Test element() for an end tag."""
        assert ml.element(input) == expected

    @pytest.mark.parametrize('input,expected',
                             [('<elem>', 'elem'),
                              ('<elem2>', 'elem2')])
    def test_strelement_starttag_without_attrs(self, input, expected):
        """Test strelement() for a start tag without attributes."""
        assert ml.strelement(input) == expected

    @pytest.mark.parametrize('input,expected',
                             [('<elem a="a">', 'elem'),
                              ('<elem2  b="b" c="c">', 'elem2')])
    def test_strelement_starttag_with_attrs(self, input, expected):
        """Test strelement() for a start tag with attributes."""
        assert ml.strelement(input) == expected

    @pytest.mark.parametrize('input,expected',
                             [('</elem>', 'elem'),
                              ('</elem2>', 'elem2')])
    def test_strelement_endtag(self, input, expected):
        """Test strelement() for an end tag."""
        assert ml.strelement(input) == expected


def _add_sort(paramlist):
    """Add parameter sort to items in paramlist, to parametrize TestStarttag.

    This function is used to expand the parameter list to TestStarttag
    methods to reduce redundancy in the list.

    paramlist is a list of pairs (attrs, expected), where the value of
    expected can be str or dict[bool, str]. If str, the value is
    expected to result with both False and True values for the sort
    argument. If dict, the key is the value of the sort argument and
    the value the expected result.

    The function returns triple (attrs, sort, expected), to be passed
    to TestStarttag methods, with sort extracted from the expected of
    paramlist.
    """
    result = []
    for attrs, expected in paramlist:
        if not isinstance(expected, dict):
            expected = {False: expected, True: expected}
        for sort, expected1 in expected.items():
            result.append((attrs, sort, expected1))
    return result


@pytest.mark.parametrize(
    'attrs,sort,expected',
    _add_sort([
        ([], '<elem>\n'),
        ([('a', 'b')], '<elem a="b">\n'),
        ([('a', 'b'), ('b', 'c')], '<elem a="b" b="c">\n'),
        # Attribute values are not (re-)encoded
        ([('a', '&amp;&quot;<')], '<elem a="&amp;&quot;<">\n'),
        # Attribute name beginning with an underscore
        ([('_ab1', 'cd')], '<elem _ab1="cd">\n'),
        ([('b', 'b'), ('a', 'c')], {False: '<elem b="b" a="c">\n',
                                    True: '<elem a="c" b="b">\n'}),
    ]))
class TestStartTag:

    """Tests for functions starttag, strstarttag."""

    def test_starttag_dict(self, attrs, sort, expected):
        """Test starttag() with an OrderedDict."""
        assert (ml.starttag(b'elem', encode_utf8(OrderedDict(attrs)), sort)
                == encode_utf8(expected))

    def test_starttag_pairlist(self, attrs, sort, expected):
        """Test starttag() with a list of pairs."""
        assert (ml.starttag(b'elem', encode_utf8(attrs), sort)
                == encode_utf8(expected))

    def test_strstarttag_dict(self, attrs, sort, expected):
        """Test strstarttag() with an OrderedDict."""
        assert ml.strstarttag('elem', OrderedDict(attrs), sort) == expected

    def test_strstarttag_pairlist(self, attrs, sort, expected):
        """Test strstarttag() with a list of pairs."""
        assert ml.strstarttag('elem', attrs, sort) == expected


@pytest.mark.parametrize('line,expected',
                         [('a', False),
                          ('&lt;', False),
                          (' <', False),
                          ('<starttag>', True),
                          ('<starttag attr="a">', True),
                          ('</endtag>', True),
                          ('<!-- comment -->', True)])
class TestIsmeta:

    """Tests for functions ismeta and strismeta."""

    def test_ismeta(self, line, expected):
        """Test ismeta()."""
        assert ml.ismeta(line.encode('UTF-8') + b'\n') == expected

    def test_strismeta(self, line, expected):
        """Test strismeta()."""
        assert ml.strismeta(line + '\n') == expected


@pytest.mark.parametrize('line,starttag,endtag,comment',
                         [('<starttag>', True, False, False),
                          ('<starttag attr="a">', True, False, False),
                          ('</endtag>', False, True, False),
                          ('<!-- comment -->', False, False, True)])
class TestMetalineType:

    """Tests for functions testing the type of a meta line."""

    def test_isstarttag(self, line, starttag, endtag, comment):
        """Test isstarttag()."""
        assert ml.isstarttag(line.encode('UTF-8') + b'\n') == starttag

    def test_strisstarttag(self, line, starttag, endtag, comment):
        """Test strisstarttag()."""
        assert ml.strisstarttag(line + '\n') == starttag

    def test_isendtag(self, line, starttag, endtag, comment):
        """Test isendtag()."""
        assert ml.isendtag(line.encode('UTF-8') + b'\n') == endtag

    def test_strisendtag(self, line, starttag, endtag, comment):
        """Test strisendtag()."""
        assert ml.strisendtag(line + '\n') == endtag

    def test_iscomment(self, line, starttag, endtag, comment):
        """Test iscomment()."""
        assert ml.iscomment(line.encode('UTF-8') + b'\n') == comment

    def test_striscomment(self, line, starttag, endtag, comment):
        """Test striscomment()."""
        assert ml.striscomment(line + '\n') == comment
