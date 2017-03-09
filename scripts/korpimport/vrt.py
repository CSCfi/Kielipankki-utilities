# -*- coding: utf-8 -*-


"""
Module korpimport.vrt

Model VRT (verticalized text) files data.
"""


# TODO: Rethink the model to allow eg. sentence scrambling.


class VrtData(object):

    def __init__(self):
        self._tokens = []
        self._struct_begin = {}
        self._struct_end = {}
        self._struct_index = {}
        self._struct_attrs = {}

    def add_tokens(self, tokens):
        for token in tokens:
            self._tokens.append([token])

    def add_pos_attr(self, attrvals):
        token_cnt = len(self._tokens)
        attrval_cnt = len(attrvals)
        if token_cnt < attrval_cnt:
            for i in xrange(attrval_cnt - token_cnt):
                self._tokens.append([u''])
        for pos, attrval in enumerate(attrvals):
            self._tokens[pos].append(attrval)
        if attrval_cnt < token_cnt:
            for pos in xrange(attrval_cnt, token-cnt):
                self._tokens[pos].append(u'')

    def add_struct(self, struct, spans):
        self._struct_index[struct] = []
        for begin, end in spans:
            self._struct_begin.setdefault(begin, [])
            self._struct_begin[begin].append(struct)
            self._struct_end.setdefault(end, [])
            self._struct_end[end].append(struct)
            self._struct_index[struct].append((begin, end))

    def add_struct_attr(self, struct, attrname, values):
        self._struct_attrs.setdefault(struct, {})
        struct_attr = self._struct_attrs[struct]
        struct_pos = self._struct_index[struct]
        for valuenr, value in enumerate(values):
            # print valuenr, value
            struct_attr.setdefault(struct_pos[valuenr][0], []).append((
                attrname, value))

    def serialize(self):
        # print repr(self._tokens)
        for pos, token in enumerate(self._tokens):
            for struct in self._struct_begin.get(pos, []):
                yield self._make_start_tag(pos, struct) + '\n'
            yield '\t'.join(attr.replace(u'&', u'&amp;').replace(u'<', u'&lt;')
                            for attr in token) + '\n'
            for struct in reversed(self._struct_end.get(pos, [])):
                yield '</' + struct + '>\n'

    def _make_start_tag(self, pos, struct):
        return ('<' + struct
                + ''.join(u' {name}="{val}"'
                          .format(name=attrname,
                                  val=(attrval.replace(u'&', u'&amp;')
                                       .replace(u'<', u'&lt;')
                                       .replace(u'"', u'&quot;')))
                          for attrname, attrval
                          in self._struct_attrs.get(struct, {}).get(pos, []))
                + '>')

    @classmethod
    def test(cls):
        vrt = VrtData()
        vrt.add_tokens(['foo', 'bar', 'baz', 'goo'])
        vrt.add_pos_attr(['FOO', 'BAR&', 'BAZ<', 'GOO'])
        vrt.add_pos_attr(['Foo', 'Bar', 'Baz', 'Goo'])
        vrt.add_struct('text', [(0, 3)])
        vrt.add_struct_attr('text', 'foo', ['foo1'])
        vrt.add_struct('sentence', [(0, 1), (2, 3)])
        vrt.add_struct_attr('sentence', 'bar', ['bar1<', 'bar2&'])
        vrt.add_struct_attr('sentence', 'baz', ['baz1', 'baz2"'])
        return ''.join(line for line in vrt.serialize())


if __name__ == "__main__":
    import sys
    sys.stdout.write(VrtData.test())
