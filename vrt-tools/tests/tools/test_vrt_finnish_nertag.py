# -*- mode: Python; -*-

'''Testing vrt-finnish-nertag that uses libvrt protocol 1 aka pr1 to
run the finnish-nertag tool of finnish-tagtools on VRT. This is the
first VRT tool to use pr1 in anger.

'''

# tests can detect tokens of SENT1 and SENT2 by the start of the line

DATA1 = "Francis Bacon oli komitea IBM:n lakimiehiä .".split()
DATA2 = "Francis Bacon kirjoitti Shakespearen näytelmiä .".split()

SENT1 = [ 'SENT1\t{}\t{}'.format(ref, word)
          for ref, word in enumerate(DATA1, start = 1)
]
SENT2 = [ 'SENT2\t{}\t{}'.format(ref,word)
          for ref, word in enumerate(DATA2, start = 1)
]

def marked(sent, *phrases):
    '''Yield sent lines with the phrases wrapped in <ne> before their
    first "word", </ne> after last.

    '''
    for word in sent:
        if any(word.endswith('\t' + phrase[0])
               for phrase in phrases):
            yield '<ne>'
        yield word
        if any(word.endswith('\t' + phrase[-1])
               for phrase in phrases):
            yield '</ne>'

# insert internal markup to variants of the sentences
# (really testing "protocol 1" rather than the tool)
# (but nertag is the first tool to use pr1 in anger)

SENT1_ne = list(marked(SENT1, ['Francis', 'Bacon'], ['IBM:n']))
SENT2_ne = list(marked(SENT2, ['Francis', 'Bacon'], ['Shakespearen']))

def sentence(content, skip = False):
    '''Wrap content lines in sentence tags and encode the whole element as
    one bytes object in UTF-8.

    '''
    start = ( '<sentence _skip="|finnish-nertag|">'
              if skip else
              '<sentence>' )
    end = '</sentence>'
    return '\n'.join((start, *content, end)).encode('UTF-8')

import pytest, re
from subprocess import run, PIPE

def test_help():
    proc = run([ './vrt-new-finnish-nertag', '--help' ],
               stdin = None,
               stdout = PIPE,
               stderr = PIPE,
               timeout = 5)
    assert not proc.returncode
    assert proc.stdout
    assert not proc.stderr

def test_defaults():
    '''Tag first sentence with default format (set-valued field). Skip
    second sentence.

    '''
    inf = b'\n'.join((b'<!-- #vrt positional-attributes: sen ref word -->',
                      b'<text topic="basic" subtopic="lone sentences">',
                      b'<paragraph n="1">',
                      sentence(SENT1),
                      b'</paragraph>',
                      b'<paragraph n="2">',
                      sentence(SENT2, skip = True),
                      b'</paragraph>',
                      b'</text>\n'))
    proc = run([ './vrt-new-finnish-nertag' ],
               input = inf,
               stdout = PIPE,
               stderr = PIPE,
               timeout = 5)

    assert not proc.returncode
    assert not proc.stderr
    assert proc.stdout

    ouf = proc.stdout.decode('UTF-8').split('\n')
    assert len(ouf) == len(inf.split(b'\n'))

    # default input field, output field names: word nertags/
    assert ouf[0] == '<!-- #vrt positional-attributes: sen ref word nertags/ -->'

    # SENT1 should be tagged with sets of tags by default
    sent1 = [ line for line in ouf if line.startswith('SENT1') ]
    assert len(sent1) == len(SENT1)
    for line in sent1:
        assert line.count('\t') == 3
        sen, ref, word, tag = line.split('\t')
        assert re.fullmatch('\|([^\|]+\|)*', tag)

    # SENT2 should be all | because _skip="|finnish-nertag|"
    sent2 = [ line for line in ouf if line.startswith('SENT2') ]
    assert len(sent2) == len(SENT2)
    for line in sent2:
        assert line.count('\t') == 3
        sen, ref, word, tag = line.split('\t')
        assert tag == '|'

def test_ne_markup():
    '''Ignore internal structure in both sentences. Skip first
    sentence. Tag second sentence with set-valued field by explicit
    option, with non-default output field name.

    '''
    inf = b'\n'.join((b'<!-- #vrt positional-attributes: sen ref word -->',
                      b'<text topic="basic" subtopic="lone sentences">',
                      b'<paragraph n="1">',
                      sentence(SENT1_ne, skip = True),
                      b'</paragraph>',
                      b'<paragraph n="2">',
                      sentence(SENT2_ne),
                      b'</paragraph>',
                      b'</text>\n'))
    proc = run([ './vrt-new-finnish-nertag', '--all', '--tag=xnertag/' ],
               input = inf,
               stdout = PIPE,
               stderr = PIPE,
               timeout = 5)

    assert not proc.returncode
    assert not proc.stderr
    assert proc.stdout

    ouf = proc.stdout.decode('UTF-8').split('\n')
    assert len(ouf) == len(inf.split(b'\n'))

    # default input field, non-default output field names: word xnertag/
    assert ouf[0] == '<!-- #vrt positional-attributes: sen ref word xnertag/ -->'

    # SENT1 should be all | because _skip="|finnish-nertag|"
    sent1 = [ line for line in ouf if line.startswith('SENT1') ]
    assert len(sent1) == len(SENT1)
    for line in sent1:
        assert line.count('\t') == 3
        sen, ref, word, tag = line.split('\t')
        assert tag == '|'

    # SENT2 should be tagged with sets of tags because --all
    sent2 = [ line for line in ouf if line.startswith('SENT2') ]
    assert len(sent2) == len(SENT2)
    for line in sent2:
        assert line.count('\t') == 3
        sen, ref, word, tag = line.split('\t')
        assert re.fullmatch('\|([^\|]+\|)*', tag)

def test_middle_skip():
    '''Skip middle sentence. Tag maximal names. Use non-default input
    field name.

    (Skip logic had several embarrassing bugs in the initial
    implementation of vrt-finnish-nertag, so make the extra test.)

    '''
    inf = b'\n'.join((b'<!-- #vrt positional-attributes: sen ref data -->',
                      b'<text>',
                      sentence(SENT1_ne),
                      sentence(SENT2_ne, skip = True),
                      sentence(SENT1),
                      b'</text>\n'))
    proc = run([ './vrt-new-finnish-nertag', '--max', '--word=data' ],
               input = inf,
               stdout = PIPE,
               stderr = PIPE,
               timeout = 5)

    assert not proc.returncode
    assert not proc.stderr
    assert proc.stdout

    ouf = proc.stdout.decode('UTF-8').split('\n')
    assert len(ouf) == len(inf.split(b'\n'))

    # non-default input field, default output field names: data nertag
    assert ouf[0] == '<!-- #vrt positional-attributes: sen ref data nertag -->'

    # SENT1 should be tagged with maximal tags because --max
    sent1 = [ line for line in ouf if line.startswith('SENT1') ]
    assert len(sent1) == 2 * len(SENT1)
    for line in sent1:
        assert line.count('\t') == 3
        sen, ref, word, tag = line.split('\t')
        assert re.fullmatch('[^|]+', tag)

    # SENT2 should be all _ because _skip="|finnish-nertag|" and --max
    sent2 = [ line for line in ouf if line.startswith('SENT2') ]
    assert len(sent2) == len(SENT2)
    for line in sent2:
        assert line.count('\t') == 3
        sen, ref, word, tag = line.split('\t')
        assert tag == '_'

def test_biotags():
    '''Skip middle sentence. BIO-tag maximal names.

    '''
    inf = b'\n'.join((b'<!-- #vrt positional-attributes: sen ref word -->',
                      b'<text>',
                      sentence(SENT1),
                      sentence(SENT2, skip = True),
                      b'</text>\n'))
    proc = run([ './vrt-new-finnish-nertag', '--bio' ],
               input = inf,
               stdout = PIPE,
               stderr = PIPE,
               timeout = 5)

    assert not proc.returncode
    assert not proc.stderr
    assert proc.stdout

    ouf = proc.stdout.decode('UTF-8').split('\n')
    assert len(ouf) == len(inf.split(b'\n'))

    # non-default input field, default output field names: data nertag
    assert ouf[0] == '<!-- #vrt positional-attributes: sen ref word nerbio -->'

    # SENT1 should be tagged with maximal BIO tags because --bio,
    # even tokens outside names are tagged O rather than _
    sent1 = [ line for line in ouf if line.startswith('SENT1') ]
    assert len(sent1) == len(SENT1)
    for line in sent1:
        assert line.count('\t') == 3
        sen, ref, word, tag = line.split('\t')
        assert re.fullmatch('[^|_]+', tag)

    # SENT2 should be all _ because _skip="|finnish-nertag|" and --bio
    sent2 = [ line for line in ouf if line.startswith('SENT2') ]
    assert len(sent2) == len(SENT2)
    for line in sent2:
        assert line.count('\t') == 3
        sen, ref, word, tag = line.split('\t')
        assert tag == '_'
