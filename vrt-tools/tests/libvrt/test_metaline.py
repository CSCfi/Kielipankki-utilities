
"""
test_metaline.py

Pytest tests for libvrt.metaline.
"""


import pytest

import libvrt.metaline as ml


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
