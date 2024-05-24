
"""
test_metaline.py

Pytest tests for libvrt.metaline.
"""


from collections import OrderedDict

import pytest

import libvrt.metaline as ml


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


@pytest.mark.parametrize(
    'attrs,sort,expected',
    [
        ([], False, '<elem>\n'),
        ([], True, '<elem>\n'),
        ([('a', 'b')], False, '<elem a="b">\n'),
        ([('a', 'b')], True, '<elem a="b">\n'),
        ([('a', 'b'), ('b', 'c')], False, '<elem a="b" b="c">\n'),
        ([('a', 'b'), ('b', 'c')], True, '<elem a="b" b="c">\n'),
        ([('b', 'b'), ('a', 'c')], False, '<elem b="b" a="c">\n'),
        ([('b', 'b'), ('a', 'c')], True, '<elem a="c" b="b">\n'),
    ])
class TestStartTag:

    """Tests for functions starttag, strstarttag."""

    def test_starttag(self, attrs, sort, expected):
        """Test starttag()."""
        attrdict = OrderedDict((key.encode('UTF-8'), val.encode('UTF-8'))
                               for key, val in attrs)
        assert ml.starttag(b'elem', attrdict, sort) == expected.encode('UTF-8')

    def test_strstarttag(self, attrs, sort, expected):
        """Test strstarttag()."""
        assert ml.strstarttag('elem', OrderedDict(attrs), sort) == expected


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
