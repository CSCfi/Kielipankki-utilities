# -*- mode: Python; -*-

'''Testing libvrt protocol 1 aka pr1 through the special test tool,
vrt-test-pr1-meta, that implements the protocol using an external
program, `cut -f 3`, to extract for each sentence an identifier to be
added to the attributes.

The tokens and their annotations are left alone.

The external program sees each sentence as units as a one-line record
that consists of a couple of fields followed by the tokens.

'''

from subprocess import run, PIPE

def test_001a():
    inf = b'\n'.join((b'<!-- #vrt positional-attributes: ref word -->',
                      b'<text topic="basic" subtopic="lone sentences">',
                      b'<paragraph n="1">',
                      b'<sentence>',
                      b'1\tTietokoneilla',
                      b'2\tvoi',
                      b'3\tvaihtaa',
                      b'4\ttaustakuvaa',
                      b'5\t.',
                      b'</sentence>',
                      b'</paragraph>',
                      b'<paragraph n="2">',
                      b'<sentence>',
                      b'1\t:-)',
                      b'</sentence>',
                      b'</paragraph>',
                      b'</text>',
                      b''))
    proc = run([ './vrt-test-pr1-meta', '--word=word' ],
               input = inf,
               stdout = PIPE,
               stderr = PIPE,
               timeout = 5)
    assert not proc.returncode
    assert proc.stdout
    assert not proc.stderr
    assert (
        proc.stdout ==
        b'\n'.join((b'<!-- #vrt positional-attributes: ref word -->',
                    b'<text topic="basic" subtopic="lone sentences">',
                    b'<paragraph n="1">',
                    b'<sentence ans="unk1">',
                    b'1\tTietokoneilla',
                    b'2\tvoi',
                    b'3\tvaihtaa',
                    b'4\ttaustakuvaa',
                    b'5\t.',
                    b'</sentence>',
                    b'</paragraph>',
                    b'<paragraph n="2">',
                    b'<sentence ans="unk2">',
                    b'1\t:-)',
                    b'</sentence>',
                    b'</paragraph>',
                    b'</text>',
                    b''))
    )

def test_001b():
    inf = b'\n'.join((b'<!-- #vrt positional-attributes: ref word -->',
                      b'<text topic="basic" subtopic="adjacent sentences">',
                      b'<paragraph n="1">',
                      b'<sentence>',
                      b'1\tTietokoneilla',
                      b'2\tvoi',
                      b'3\tvaihtaa',
                      b'4\ttaustakuvaa',
                      b'5\t.',
                      b'</sentence>',
                      b'<sentence>',
                      b'1\t:-)',
                      b'</sentence>',
                      b'</paragraph>',
                      b'</text>',
                      b''))
    proc = run([ './vrt-test-pr1-meta', '--word=word' ],
               input = inf,
               stdout = PIPE,
               stderr = PIPE,
               timeout = 5)
    assert not proc.returncode
    assert proc.stdout
    assert not proc.stderr
    assert (
        proc.stdout ==
        b'\n'.join((b'<!-- #vrt positional-attributes: ref word -->',
                    b'<text topic="basic" subtopic="adjacent sentences">',
                    b'<paragraph n="1">',
                    b'<sentence ans="unk1">',
                    b'1\tTietokoneilla',
                    b'2\tvoi',
                    b'3\tvaihtaa',
                    b'4\ttaustakuvaa',
                    b'5\t.',
                    b'</sentence>',
                    b'<sentence ans="unk2">',
                    b'1\t:-)',
                    b'</sentence>',
                    b'</paragraph>',
                    b'</text>',
                    b''))
    )

def test_002():
    inf = b'\n'.join((b'<!-- #vrt positional-attributes: ref word -->',
                      b'<text topic="inner meta">',
                      b'<paragraph n="1">',
                      b'<sentence>',
                      b'1\tTietokoneilla',
                      b'2\tvoi',
                      b'<application>',
                      b'3\tvaihtaa',
                      b'4\ttaustakuvaa',
                      b'</application>',
                      b'5\t.',
                      b'</sentence>',
                      b'</paragraph>',
                      b'<paragraph n="2">',
                      b'<sentence>',
                      b'<humor>',
                      b'1\t:-)',
                      b'</humor>',
                      b'</sentence>',
                      b'</paragraph>',
                      b'</text>',
                      b''))
    proc = run([ './vrt-test-pr1-meta', '--word=word' ],
               input = inf,
               stdout = PIPE,
               stderr = PIPE,
               timeout = 5)
    assert not proc.returncode
    assert proc.stdout
    assert not proc.stderr
    assert (
        proc.stdout ==
        b'\n'.join((b'<!-- #vrt positional-attributes: ref word -->',
                    b'<text topic="inner meta">',
                    b'<paragraph n="1">',
                    b'<sentence ans="unk1">',
                    b'1\tTietokoneilla',
                    b'2\tvoi',
                    b'<application>',
                    b'3\tvaihtaa',
                    b'4\ttaustakuvaa',
                    b'</application>',
                    b'5\t.',
                    b'</sentence>',
                    b'</paragraph>',
                    b'<paragraph n="2">',
                    b'<sentence ans="unk2">',
                    b'<humor>',
                    b'1\t:-)',
                    b'</humor>',
                    b'</sentence>',
                    b'</paragraph>',
                    b'</text>',
                    b''))
    )

def test_003a():
    inf = b'\n'.join((b'<!-- #vrt positional-attributes: ref word -->',
                      b'<text topic="class one" subtopic="lone sentences">',
                      b'<paragraph n="1">',
                      b'<sentence class="one">',
                      b'1\tTietokoneilla',
                      b'2\tvoi',
                      b'3\tvaihtaa',
                      b'4\ttaustakuvaa',
                      b'5\t.',
                      b'</sentence>',
                      b'</paragraph>',
                      b'<paragraph n="2">',
                      b'<sentence class="two">',
                      b'1\t:-)',
                      b'</sentence>',
                      b'</paragraph>',
                      b'</text>',
                      b''))
    proc = run([ './vrt-test-pr1-meta', '--word=word', '--class=one' ],
               input = inf,
               stdout = PIPE,
               stderr = PIPE,
               timeout = 5)
    assert not proc.returncode
    assert proc.stdout
    assert not proc.stderr
    assert (
        proc.stdout ==
        b'\n'.join((b'<!-- #vrt positional-attributes: ref word -->',
                    b'<text topic="class one" subtopic="lone sentences">',
                    b'<paragraph n="1">',
                    b'<sentence ans="unk1" class="one">',
                    b'1\tTietokoneilla',
                    b'2\tvoi',
                    b'3\tvaihtaa',
                    b'4\ttaustakuvaa',
                    b'5\t.',
                    b'</sentence>',
                    b'</paragraph>',
                    b'<paragraph n="2">',
                    b'<sentence class="two">',
                    b'1\t:-)',
                    b'</sentence>',
                    b'</paragraph>',
                    b'</text>',
                    b''))
    )

def test_003b():
    inf = b'\n'.join((b'<!-- #vrt positional-attributes: ref word -->',
                      b'<text topic="class one" subtopic="adjacent sentences">',
                      b'<paragraph n="1">',
                      b'<sentence class="one">',
                      b'1\tTietokoneilla',
                      b'2\tvoi',
                      b'3\tvaihtaa',
                      b'4\ttaustakuvaa',
                      b'5\t.',
                      b'</sentence>',
                      b'<sentence class="two">',
                      b'1\t:-)',
                      b'</sentence>',
                      b'</paragraph>',
                      b'</text>',
                      b''))
    proc = run([ './vrt-test-pr1-meta', '--word=word', '--class=one' ],
               input = inf,
               stdout = PIPE,
               stderr = PIPE,
               timeout = 5)
    assert not proc.returncode
    assert proc.stdout
    assert not proc.stderr
    assert (
        proc.stdout ==
        b'\n'.join((b'<!-- #vrt positional-attributes: ref word -->',
                    b'<text topic="class one" subtopic="adjacent sentences">',
                    b'<paragraph n="1">',
                    b'<sentence ans="unk1" class="one">',
                    b'1\tTietokoneilla',
                    b'2\tvoi',
                    b'3\tvaihtaa',
                    b'4\ttaustakuvaa',
                    b'5\t.',
                    b'</sentence>',
                    b'<sentence class="two">',
                    b'1\t:-)',
                    b'</sentence>',
                    b'</paragraph>',
                    b'</text>',
                    b''))
    )

def test_003c():
    inf = b'\n'.join((b'<!-- #vrt positional-attributes: ref word -->',
                      b'<text topic="class two" subtopic="lone sentences">',
                      b'<paragraph n="1">',
                      b'<sentence class="one">',
                      b'1\tTietokoneilla',
                      b'2\tvoi',
                      b'3\tvaihtaa',
                      b'4\ttaustakuvaa',
                      b'5\t.',
                      b'</sentence>',
                      b'</paragraph>',
                      b'<paragraph n="2">',
                      b'<sentence class="two">',
                      b'1\t:-)',
                      b'</sentence>',
                      b'</paragraph>',
                      b'</text>',
                      b''))
    proc = run([ './vrt-test-pr1-meta', '--word=word', '--class=two' ],
               input = inf,
               stdout = PIPE,
               stderr = PIPE,
               timeout = 5)
    assert not proc.returncode
    assert proc.stdout
    assert not proc.stderr
    assert (
        proc.stdout ==
        b'\n'.join((b'<!-- #vrt positional-attributes: ref word -->',
                    b'<text topic="class two" subtopic="lone sentences">',
                    b'<paragraph n="1">',
                    b'<sentence class="one">',
                    b'1\tTietokoneilla',
                    b'2\tvoi',
                    b'3\tvaihtaa',
                    b'4\ttaustakuvaa',
                    b'5\t.',
                    b'</sentence>',
                    b'</paragraph>',
                    b'<paragraph n="2">',
                    b'<sentence ans="unk1" class="two">',
                    b'1\t:-)',
                    b'</sentence>',
                    b'</paragraph>',
                    b'</text>',
                    b''))
    )

def test_003d():
    inf = b'\n'.join((b'<!-- #vrt positional-attributes: ref word -->',
                      b'<text topic="class two" subtopic="adjacent sentences">',
                      b'<paragraph n="1">',
                      b'<sentence class="one">',
                      b'1\tTietokoneilla',
                      b'2\tvoi',
                      b'3\tvaihtaa',
                      b'4\ttaustakuvaa',
                      b'5\t.',
                      b'</sentence>',
                      b'<sentence class="two">',
                      b'1\t:-)',
                      b'</sentence>',
                      b'</paragraph>',
                      b'</text>',
                      b''))
    proc = run([ './vrt-test-pr1-meta', '--word=word', '--class=two' ],
               input = inf,
               stdout = PIPE,
               stderr = PIPE,
               timeout = 5)
    assert not proc.returncode
    assert proc.stdout
    assert not proc.stderr
    assert (
        proc.stdout ==
        b'\n'.join((b'<!-- #vrt positional-attributes: ref word -->',
                    b'<text topic="class two" subtopic="adjacent sentences">',
                    b'<paragraph n="1">',
                    b'<sentence class="one">',
                    b'1\tTietokoneilla',
                    b'2\tvoi',
                    b'3\tvaihtaa',
                    b'4\ttaustakuvaa',
                    b'5\t.',
                    b'</sentence>',
                    b'<sentence ans="unk1" class="two">',
                    b'1\t:-)',
                    b'</sentence>',
                    b'</paragraph>',
                    b'</text>',
                    b''))
    )
