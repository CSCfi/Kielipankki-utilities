# -*- mode: Python; -*-

'''Testing libvrt protocol 1 aka pr1 through the special test tool,
vrt-test-pr1-data, that implements the protocol using an external
program, `cut -c -3`, to extract a prefix of three characters from a
given field as the contents of a new field.

The external program sees one field (on its own line) for each token,
empty line between sentences.

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
    proc = run([ './vrt-test-pr1-data', '--word=word' ],
               input = inf,
               stdout = PIPE,
               stderr = PIPE,
               timeout = 5)
    assert not proc.returncode
    assert proc.stdout
    assert not proc.stderr
    assert (
        proc.stdout ==
        b'\n'.join((b'<!-- #vrt positional-attributes: ref word word_ch3 -->',
                    b'<text topic="basic" subtopic="lone sentences">',
                    b'<paragraph n="1">',
                    b'<sentence>',
                    b'1\tTietokoneilla\tTie',
                    b'2\tvoi\tvoi',
                    b'3\tvaihtaa\tvai',
                    b'4\ttaustakuvaa\ttau',
                    b'5\t.\t.',
                    b'</sentence>',
                    b'</paragraph>',
                    b'<paragraph n="2">',
                    b'<sentence>',
                    b'1\t:-)\t:-)',
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
    proc = run([ './vrt-test-pr1-data', '--word=word' ],
               input = inf,
               stdout = PIPE,
               stderr = PIPE,
               timeout = 5)
    assert not proc.returncode
    assert proc.stdout
    assert not proc.stderr
    assert (
        proc.stdout ==
        b'\n'.join((b'<!-- #vrt positional-attributes: ref word word_ch3 -->',
                    b'<text topic="basic" subtopic="adjacent sentences">',
                    b'<paragraph n="1">',
                    b'<sentence>',
                    b'1\tTietokoneilla\tTie',
                    b'2\tvoi\tvoi',
                    b'3\tvaihtaa\tvai',
                    b'4\ttaustakuvaa\ttau',
                    b'5\t.\t.',
                    b'</sentence>',
                    b'<sentence>',
                    b'1\t:-)\t:-)',
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
    proc = run([ './vrt-test-pr1-data', '--word=word' ],
               input = inf,
               stdout = PIPE,
               stderr = PIPE,
               timeout = 5)
    assert not proc.returncode
    assert proc.stdout
    assert not proc.stderr
    assert (
        proc.stdout ==
        b'\n'.join((b'<!-- #vrt positional-attributes: ref word word_ch3 -->',
                    b'<text topic="inner meta">',
                    b'<paragraph n="1">',
                    b'<sentence>',
                    b'1\tTietokoneilla\tTie',
                    b'2\tvoi\tvoi',
                    b'<application>',
                    b'3\tvaihtaa\tvai',
                    b'4\ttaustakuvaa\ttau',
                    b'</application>',
                    b'5\t.\t.',
                    b'</sentence>',
                    b'</paragraph>',
                    b'<paragraph n="2">',
                    b'<sentence>',
                    b'<humor>',
                    b'1\t:-)\t:-)',
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
    proc = run([ './vrt-test-pr1-data', '--word=word', '--class=one' ],
               input = inf,
               stdout = PIPE,
               stderr = PIPE,
               timeout = 5)
    assert not proc.returncode
    assert proc.stdout
    assert not proc.stderr
    assert (
        proc.stdout ==
        b'\n'.join((b'<!-- #vrt positional-attributes: ref word word_ch3 -->',
                    b'<text topic="class one" subtopic="lone sentences">',
                    b'<paragraph n="1">',
                    b'<sentence class="one">',
                    b'1\tTietokoneilla\tTie',
                    b'2\tvoi\tvoi',
                    b'3\tvaihtaa\tvai',
                    b'4\ttaustakuvaa\ttau',
                    b'5\t.\t.',
                    b'</sentence>',
                    b'</paragraph>',
                    b'<paragraph n="2">',
                    b'<sentence class="two">',
                    b'1\t:-)\t_',
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
    proc = run([ './vrt-test-pr1-data', '--word=word', '--class=one' ],
               input = inf,
               stdout = PIPE,
               stderr = PIPE,
               timeout = 5)
    assert not proc.returncode
    assert proc.stdout
    assert not proc.stderr
    assert (
        proc.stdout ==
        b'\n'.join((b'<!-- #vrt positional-attributes: ref word word_ch3 -->',
                    b'<text topic="class one" subtopic="adjacent sentences">',
                    b'<paragraph n="1">',
                    b'<sentence class="one">',
                    b'1\tTietokoneilla\tTie',
                    b'2\tvoi\tvoi',
                    b'3\tvaihtaa\tvai',
                    b'4\ttaustakuvaa\ttau',
                    b'5\t.\t.',
                    b'</sentence>',
                    b'<sentence class="two">',
                    b'1\t:-)\t_',
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
    proc = run([ './vrt-test-pr1-data', '--word=word', '--class=two' ],
               input = inf,
               stdout = PIPE,
               stderr = PIPE,
               timeout = 5)
    assert not proc.returncode
    assert proc.stdout
    assert not proc.stderr
    assert (
        proc.stdout ==
        b'\n'.join((b'<!-- #vrt positional-attributes: ref word word_ch3 -->',
                    b'<text topic="class two" subtopic="lone sentences">',
                    b'<paragraph n="1">',
                    b'<sentence class="one">',
                    b'1\tTietokoneilla\t_',
                    b'2\tvoi\t_',
                    b'3\tvaihtaa\t_',
                    b'4\ttaustakuvaa\t_',
                    b'5\t.\t_',
                    b'</sentence>',
                    b'</paragraph>',
                    b'<paragraph n="2">',
                    b'<sentence class="two">',
                    b'1\t:-)\t:-)',
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
    proc = run([ './vrt-test-pr1-data', '--word=word', '--class=two' ],
               input = inf,
               stdout = PIPE,
               stderr = PIPE,
               timeout = 5)
    assert not proc.returncode
    assert proc.stdout
    assert not proc.stderr
    assert (
        proc.stdout ==
        b'\n'.join((b'<!-- #vrt positional-attributes: ref word word_ch3 -->',
                    b'<text topic="class two" subtopic="adjacent sentences">',
                    b'<paragraph n="1">',
                    b'<sentence class="one">',
                    b'1\tTietokoneilla\t_',
                    b'2\tvoi\t_',
                    b'3\tvaihtaa\t_',
                    b'4\ttaustakuvaa\t_',
                    b'5\t.\t_',
                    b'</sentence>',
                    b'<sentence class="two">',
                    b'1\t:-)\t:-)',
                    b'</sentence>',
                    b'</paragraph>',
                    b'</text>',
                    b''))
    )
