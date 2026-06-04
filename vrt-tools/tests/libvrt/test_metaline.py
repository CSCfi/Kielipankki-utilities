
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


@pytest.mark.parametrize(
    'input,attrs', [
        # No attributes
        (b'<elem>\n', []),
        (b'<elem a="b">\n', [(b'a', b'b')]),
        (b'<elem a="b" b="&lt;">\n', [(b'a', b'b'), (b'b', b'&lt;')]),
        # Attribute values with spaces
        (b'<elem a=" b " b="  ">\n', [(b'a', b' b '), (b'b', b'  ')]),
        # Attribute names with digits, underscores
        (b'<elem a1="b" b_="c">\n', [(b'a1', b'b'), (b'b_', b'c')]),
        (b'<elem _a="b" b_c="c">\n', [(b'_a', b'b'), (b'b_c', b'c')]),
        (b'<elem _1="b" b_1_="c">\n', [(b'_1', b'b'), (b'b_1_', b'c')]),
        (b'<elem __1="b" b_1__="c">\n', [(b'__1', b'b'), (b'b_1__', b'c')]),
        (b'<elem _="b" __="c">\n', [(b'_', b'b'), (b'__', b'c')]),
        # Attribute values ending in "="
        (b'<elem a="=" b="=">\n', [(b'a', b'='), (b'b', b'=')]),
        (b'<elem a="b=" b="x=">\n', [(b'a', b'b='), (b'b', b'x=')]),
        (b'<elem a="=b=" b="=x=">\n', [(b'a', b'=b='), (b'b', b'=x=')]),
    ])
class TestAttributeFuncs:

    """Tests for vrtlib.metaline functions pairs, mapping, attributes."""

    def test_pairs(self, input, attrs):
        """Test that pairs(input) == attrs."""
        assert ml.pairs(input) == attrs

    def test_mapping(self, input, attrs):
        """Test that mapping(input) == OrderedDict(attrs)."""
        assert ml.mapping(input) == OrderedDict(attrs)

    def test_attributes(self, input, attrs):
        """Test that attributes(input) contains names in attrs."""
        assert ml.attributes(input) == tuple(name for name, _ in attrs)


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


# The following fixtures and tests for libvrt.metaline.valuegetter()
# were generated by GitHub Copilot (with Claude Haiku 4.5) on
# 2026-03-18, inspected and somewhat modified by Jyrki Niemi.


@pytest.fixture
def valuegetter_factory_no_warn():
    """Factory fixture for creating getters without warnings."""

    def _factory(head, missing, **kwargs):
        kwargs.setdefault('warn', False)
        return ml.valuegetter(head, missing=missing, **kwargs)

    return _factory


@pytest.fixture
def valuegetter_factory_warn():
    """Factory fixture for creating getters with warnings."""

    def _factory(head, missing, prog='test', many=None, superset=False):
        return ml.valuegetter(head, missing=missing, warn=True, prog=prog,
                              many=many, superset=superset)

    return _factory


class TestValuegetterBasic:
    """Test basic valuegetter functionality without warnings."""

    @pytest.mark.parametrize("head,line,expected", [
        ((b'name', b'value'), b'name="Alice" value="123"', (b'Alice', b'123')),
        ((b'z', b'x', b'y'), b'x="1" y="2" z="3"', (b'3', b'1', b'2')),
        ((b'single',), b'single="value"', (b'value',)),
    ])
    def test_simple_retrieval(self, valuegetter_factory_no_warn,
                              head, line, expected):
        """Test basic value retrieval with various inputs."""
        getter = valuegetter_factory_no_warn(head, b'MISSING')
        result = getter(line)
        assert result == expected

    @pytest.mark.parametrize("head,line,missing,expected", [
        ((b'name', b'value', b'age'), b'name="Alice" value="123"', b'N/A',
         (b'Alice', b'123', b'N/A')),
        ((b'a', b'b', b'c'), b'x="1" y="2"', b'NONE',
         (b'NONE', b'NONE', b'NONE')),
        ((b'a', b'b', b'c'), b'a="" b="value" c=""', b'NULL',
         (b'', b'value', b'')),
    ])
    def test_missing_and_empty_values(self, valuegetter_factory_no_warn,
                                      head, line, missing, expected):
        """Test retrieval with missing or empty attribute values."""
        getter = valuegetter_factory_no_warn(head, missing)
        result = getter(line)
        assert result == expected

    def test_empty_head(self, valuegetter_factory_no_warn):
        """Test with empty head tuple."""
        getter = valuegetter_factory_no_warn((), b'-')
        result = getter(b'a="1" b="2"')
        assert result == ()

    def test_empty_line(self, valuegetter_factory_no_warn):
        """Test with empty line."""
        getter = valuegetter_factory_no_warn((b'a', b'b'), b'EMPTY')
        result = getter(b'')
        assert result == (b'EMPTY', b'EMPTY')


class TestValuegetterUnescaping:
    """Test HTML entity unescaping functionality."""

    @pytest.mark.parametrize("head,entity_input,expected_output", [
        ((b'text',), b'text="&lt;tag&gt;"', (b'<tag>',)),
        ((b'html',), b'html="&lt;&amp;&gt;&quot;&apos;"', (b'<&>"\'',)),
        ((b'code',), b'code="a&amp;b"', (b'a&b',)),
        ((b'mixed',), b'mixed="&lt;tag attr=&quot;val&quot;&gt;"',
         (b'<tag attr="val">',)),
    ])
    def test_entity_unescaping(self, valuegetter_factory_no_warn,
                               head, entity_input, expected_output):
        """Test unescaping of various HTML entities."""
        getter = valuegetter_factory_no_warn(head, b'-')
        result = getter(entity_input)
        assert result == expected_output

    def test_tab_character_unescaping(self, valuegetter_factory_no_warn):
        """Test tab character unescaping to {TAB}."""
        getter = valuegetter_factory_no_warn((b'text',), b'-')
        result = getter(b'text="hello\tworld"')
        assert result == (b'hello{TAB}world',)


class TestValuegetterWithWarnings:
    """Test valuegetter with warnings enabled."""

    @pytest.mark.parametrize("extra_attrs,should_warn", [
        (b'extra="value"', True),
        (b'', False),
    ])
    def test_extra_attributes_warning(self, valuegetter_factory_warn, capsys,
                                      extra_attrs, should_warn):
        """Test warning when line has attributes not in head."""
        head = (b'name',)
        getter = valuegetter_factory_warn(head, b'-')
        line = b'name="Alice"' + (b' ' + extra_attrs if extra_attrs else b'')
        result = getter(line)
        assert result == (b'Alice',)
        captured = capsys.readouterr()
        if should_warn:
            assert 'not in head: \'extra\'' in captured.err
        else:
            assert captured.err == ''

    @pytest.mark.parametrize("head,line,prog,should_contain", [
        ((b'name', b'age'), b'name="Alice"', 'test', ['missing: age']),
        ((b'name',), b'name="Alice" extra="value"', 'myapp',
         ['not in head: \'extra\'']),
        ((b'a', b'b'), b'a="1" c="extra"', 'test',
         ['not in head: \'c\'', 'missing: b']),
    ])
    def test_warning_messages(self, valuegetter_factory_warn, capsys,
                              head, line, prog, should_contain):
        """Test warning message format and content."""
        getter = ml.valuegetter(head, missing=b'-', warn=True, prog=prog)
        getter(line)
        captured = capsys.readouterr()
        for content in should_contain:
            assert content in captured.err
        assert prog in captured.err

    def test_no_warning_when_all_match(self, valuegetter_factory_warn, capsys):
        """Test no warning when all attributes match."""
        getter = valuegetter_factory_warn((b'name', b'age'), b'-')
        result = getter(b'name="Alice" age="30"')
        assert result == (b'Alice', b'30')
        captured = capsys.readouterr()
        assert captured.err == ''

    def test_superset_true_no_extra_warning(self, capsys):
        """Test no 'not in head' warning when superset=True."""
        getter = ml.valuegetter((b'name',), missing=b'-', warn=True,
                                superset=True)
        getter(b'name="Alice" extra="value"')
        captured = capsys.readouterr()
        assert 'not in head' not in captured.err

    @pytest.mark.parametrize("many,expected_warnings,should_have_ellipsis", [
        (1, 1, True),
        (2, 2, True),
        (0, 0, False),
        (None, 3, False),
    ])
    def test_many_limit_warnings(self, capsys, many, expected_warnings,
                                 should_have_ellipsis):
        """Test that warnings are limited by 'many' parameter."""
        getter = ml.valuegetter((b'name',), missing=b'-', warn=True, many=many)
        # Generate 3 warning-triggering calls
        getter(b'name="Alice" extra1="value"')
        getter(b'name="Bob" extra2="value"')
        getter(b'name="Charlie" extra3="value"')
        captured = capsys.readouterr()
        not_in_head_count = captured.err.count('not in head')
        assert not_in_head_count == expected_warnings
        if should_have_ellipsis:
            assert '...' in captured.err
        elif many is not None:
            assert '...' not in captured.err

    def test_multiple_calls_accumulate_seen(self, capsys):
        """Test that seen counter accumulates across multiple calls."""
        getter = ml.valuegetter((b'name',), missing=b'-', warn=True, many=1)
        # First call - warning issued (seen=1), triggers ellipsis
        getter(b'name="Alice" extra1="value"')
        captured1 = capsys.readouterr()
        # Second call - no new warning (seen >= many)
        getter(b'name="Bob" extra2="value"')
        captured2 = capsys.readouterr()
        assert 'not in head' in captured1.err
        assert '...' in captured1.err
        assert captured2.err == ''


class TestValuegetterEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.mark.parametrize("head,missing,line,expected", [
        ((b'x',), b'__MISSING__', b'y="1"', (b'__MISSING__',)),
        ((b'a', b'b', b'c'), b'NULL', b'', (b'NULL', b'NULL', b'NULL')),
        ((b'single',), b'X', b'single="value"', (b'value',)),
    ])
    def test_missing_marker_variants(self, valuegetter_factory_no_warn,
                                     head, missing, line, expected):
        """Test with various missing marker values."""
        getter = valuegetter_factory_no_warn(head, missing)
        result = getter(line)
        assert result == expected

    def test_large_head_tuple(self, valuegetter_factory_no_warn):
        """Test with a large head tuple."""
        head = tuple(('field{}'.format(i)).encode() for i in range(100))
        getter = valuegetter_factory_no_warn(head, b'X')
        line = b'field0="0" field50="50"'
        result = getter(line)
        assert len(result) == 100
        assert result[0] == b'0'
        assert result[50] == b'50'
        for i in range(1, 100):
            if i != 50:
                assert result[i] == b'X'

    @pytest.mark.parametrize("head,line,expected", [
        ((b'data-value', b'my_field'),
         b'data-value="test" my_field="123"',
         (b'test', b'123')),
        ((b'id', b'type', b'name'),
         b'id="12345" name="example" type="document"',
         (b'12345', b'document', b'example')),
    ])
    def test_special_attribute_names(self, valuegetter_factory_no_warn,
                                     head, line, expected):
        """Test with hyphens, underscores, and realistic XML-like names."""
        getter = valuegetter_factory_no_warn(head, b'NONE')
        result = getter(line)
        assert result == expected


class TestValuegetterWarningMessageDetails:
    """Test the specific format and content of warning messages."""

    def test_not_in_head_message_format(self, capsys):
        """Test the format of 'not in head' warnings."""
        getter = ml.valuegetter((b'expected',), missing=b'-', warn=True,
                                prog='myapp')
        getter(b'expected="1" unexpected="2"')
        captured = capsys.readouterr()
        assert 'myapp: warning: not in head:' in captured.err
        assert "'unexpected'" in captured.err

    def test_missing_message_format(self, capsys):
        """Test the format of 'missing' warnings."""
        getter = ml.valuegetter((b'required', b'optional'), missing=b'-',
                                warn=True, prog='myapp')
        getter(b'optional="value"')
        captured = capsys.readouterr()
        assert 'myapp: warning: missing:' in captured.err
        assert 'required' in captured.err

    def test_sorted_extra_attributes_in_warning(self, capsys):
        """Test that extra attributes are sorted in warning message."""
        getter = ml.valuegetter((b'expected',), missing=b'-', warn=True)
        getter(b'expected="1" zebra="z" apple="a" banana="b"')
        captured = capsys.readouterr()
        lines = captured.err.split('\n')
        warning_line = [line for line in lines if 'not in head' in line][0]
        apple_pos = warning_line.find("'apple'")
        banana_pos = warning_line.find("'banana'")
        zebra_pos = warning_line.find("'zebra'")
        assert apple_pos < banana_pos < zebra_pos


class TestValuegetterIntegration:
    """Integration tests combining multiple features."""

    def test_full_workflow(self, capsys):
        """Test a complete workflow with multiple calls."""
        head = (b'id', b'name', b'value')
        getter = ml.valuegetter(head, missing=b'N/A', warn=True, many=2)
        # First line - complete
        result1 = getter(b'id="1" name="Alice" value="100"')
        assert result1 == (b'1', b'Alice', b'100')
        captured = capsys.readouterr()
        assert captured.err == ''
        # Second line - missing 'value'
        result2 = getter(b'id="2" name="Bob"')
        assert result2 == (b'2', b'Bob', b'N/A')
        captured = capsys.readouterr()
        assert 'missing: value' in captured.err
        # Third line - extra attribute
        result3 = getter(b'id="3" name="Charlie" value="300" extra="ignore"')
        assert result3 == (b'3', b'Charlie', b'300')
        captured = capsys.readouterr()
        assert 'not in head: \'extra\'' in captured.err

    def test_realistic_vrt_processing(self, capsys):
        """Test realistic VRT structure start tag processing."""
        head = (b'id', b'type', b'name', b'description')
        getter = ml.valuegetter(head, missing=b'EMPTY', warn=True)
        # Well-formed tag line
        result1 = getter(b'<text id="1" type="book" name="Python &amp; XML"'
                         b' description="Learn both">\n')
        assert result1 == (b'1', b'book', b'Python & XML', b'Learn both')
        # Missing description
        result2 = getter(b'<text id="2" type="article" name="Web Dev">\n')
        assert result2 == (b'2', b'article', b'Web Dev', b'EMPTY')
        captured = capsys.readouterr()
        assert 'missing: description' in captured.err
        # Extra attribute (class)
        result3 = getter(b'<text id="3" type="blog" name="Tech News"'
                         b' description="Daily updates" class="featured">\n')
        assert result3 == (b'3', b'blog', b'Tech News', b'Daily updates')
        captured = capsys.readouterr()
        assert 'not in head: \'class\'' in captured.err


class TestValuegetterWarningDisabling:
    """Test behavior with warn=False parameter."""

    @pytest.mark.parametrize("line,should_have_warning", [
        (b'name="Alice" extra="value"', True),
        (b'name="Alice"', True),
    ])
    def test_warn_false_suppresses_all_warnings(self, capsys,
                                                line, should_have_warning):
        """Test that warn=False suppresses all warnings."""
        getter = ml.valuegetter((b'name',), missing=b'-', warn=False)
        getter(line)
        captured = capsys.readouterr()
        assert captured.err == ''

    def test_warn_false_returns_same_results(self, capsys):
        """Test that warn parameter doesn't affect results."""
        head = (b'a', b'b', b'c')
        line = b'a="1" b="2" extra="ignore"'
        getter_no_warn = ml.valuegetter(head, missing=b'X', warn=False)
        getter_with_warn = ml.valuegetter(head, missing=b'X', warn=True)
        result_no_warn = getter_no_warn(line)
        captured = capsys.readouterr()
        assert captured.err == ''
        result_with_warn = getter_with_warn(line)
        assert result_no_warn == result_with_warn
        captured = capsys.readouterr()
        assert 'not in head: \'extra\'' in captured.err
        assert 'missing: c' in captured.err
