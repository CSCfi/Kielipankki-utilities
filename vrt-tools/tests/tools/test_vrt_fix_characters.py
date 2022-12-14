from subprocess import Popen, PIPE, TimeoutExpired

from libvrt.nameline import makenameline

def test_000(tmpdir):
    proc = Popen([ './vrt-fix-characters', '--help' ],
                 stdin = None,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 5)
    assert out
    assert not err
    assert proc.returncode == 0

def test_NEL(tmpdir):
    names = makenameline(b'word'.split())
    send = b''.join((names,
                     'fud\N{NEXT LINE}ge\n'.encode('UTF-8')))
    want = b''.join((names,
                     b'fud{Cc:C1:85-NEL}ge\n'))
    proc = Popen([ './vrt-fix-characters',
                   '--field', 'word',
                   '--control',
                   '--replace=identify' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out == want
    assert not err
    assert proc.returncode == 0

def test_NEL_hex(tmpdir):
    '''Someone trying to smuggle in a NEL as a character entity
    reference. The mechanism is so that --entities recognizes the
    actual character as not allowed.

    '''
    names = makenameline(b'word'.split())
    send = b''.join((names,
                     'fud&#x85;ge\n'.encode('UTF-8')))
    want = b''.join((names,
                     b'fud{ref=Cc:C1:85-NEL}ge\n'))
    proc = Popen([ './vrt-fix-characters',
                   '--field', 'word',
                   '--entities',
                   '--replace=identify' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out == want
    assert not err
    assert proc.returncode == 0

def test_LS_hex(tmpdir):
    '''Someone trying to smuggle in a LINE SEPARATOR as a character entity
    reference. The mechanism is so that --entities recognizes the
    actual character as not allowed.

    '''
    names = makenameline(b'word'.split())
    send = b''.join((names,
                     'fud&#x2028;ge\n'.encode('UTF-8')))
    want = b''.join((names,
                     b'fud{ref=Zl:2028-LS}ge\n'))
    proc = Popen([ './vrt-fix-characters',
                   '--field', 'word',
                   '--entities',
                   '--replace=identify' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out == want
    assert not err
    assert proc.returncode == 0

def test_LS(tmpdir):
    '''Actual LINE SEPARATOR, identified.'''
    names = makenameline(b'word'.split())
    send = b''.join((names,
                     'fud\N{LINE SEPARATOR}ge\n'.encode('UTF-8')))
    want = b''.join((names,
                     b'fud{Zl:2028-LS}ge\n'))
    proc = Popen([ './vrt-fix-characters',
                   '--field', 'word',
                   '--control',
                   '--replace=identify' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out == want
    assert not err
    assert proc.returncode == 0

def test_PS_hex(tmpdir):
    '''Someone trying to smuggle in a PARAGRAPH SEPARATOR as a character
    entity reference. The mechanism is so that --entities recognizes
    the actual character as not allowed.

    '''
    names = makenameline(b'word'.split())
    send = b''.join((names,
                     'fud&#x2029;ge\n'.encode('UTF-8')))
    want = b''.join((names,
                     b'fud{ref=Zp:2029-PS}ge\n'))
    proc = Popen([ './vrt-fix-characters',
                   '--field', 'word',
                   '--entities',
                   '--replace=identify' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out == want
    assert not err
    assert proc.returncode == 0

def test_PS(tmpdir):
    '''Actual PARAGRAPH SEPARATOR, identified.'''
    names = makenameline(b'word'.split())
    send = b''.join((names,
                     'fud\N{PARAGRAPH SEPARATOR}ge\n'.encode('UTF-8')))
    want = b''.join((names,
                     b'fud{Zp:2029-PS}ge\n'))
    proc = Popen([ './vrt-fix-characters',
                   '--field', 'word',
                   '--control',
                   '--replace=identify' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out == want
    assert not err
    assert proc.returncode == 0

def test_bare_data(tmpdir):
    '''Bare & < > " ' in data. Entify & < >, leave quotes alone.

    '''
    names = makenameline(b'word'.split())
    send = b''.join((names,
                     'fud&ge\n'.encode('UTF-8'),
                     'fud<>ge\n'.encode('UTF-8'),
                     'fud"ge\n'.encode('UTF-8'),
                     "fud'ge\n".encode('UTF-8')))
    want = b''.join((names,
                     b'fud&amp;ge\n',
                     b'fud&lt;&gt;ge\n',
                     b'fud"ge\n',
                     b"fud'ge\n"))
    proc = Popen([ './vrt-fix-characters',
                   '--field', 'word',
                   '--entities' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out == want
    assert not err
    assert proc.returncode == 0

def test_C0_hex_data(tmpdir):
    '''Someone is trying to smuggle in disallowed C0 codes through
    character entity references.

    '''
    names = makenameline(b'word'.split())
    send = b''.join((names,
                     'fud&#x0;ge\n'.encode('UTF-8'),
                     'fud&#x8;ge\n'.encode('UTF-8'),
                     'fud&#x9;ge\n'.encode('UTF-8'),
                     'fud&#xa;ge\n'.encode('UTF-8'),
                     'fud&#xb;ge\n'.encode('UTF-8'),
                     "fud&#xc;ge\n".encode('UTF-8'),
                     "fud&#xd;ge\n".encode('UTF-8'),
                     "fud&#x1b;ge\n".encode('UTF-8'),
                     "fud&#x1c;ge\n".encode('UTF-8'),
                     "fud&#x1d;ge\n".encode('UTF-8'),
                     "fud&#x1e;ge\n".encode('UTF-8'),
                     "fud&#x1f;ge\n".encode('UTF-8'),
    ))
    want = b''.join((names,
                     b'fud{ref=Cc:C0:00-NUL}ge\n',
                     b'fud{ref=Cc:C0:08-BS}ge\n',
                     b'fud{ref=Cc:C0:09-HT}ge\n',
                     b'fud{ref=Cc:C0:0a-LF}ge\n',
                     b'fud{ref=Cc:C0:0b-VT}ge\n',
                     b"fud{ref=Cc:C0:0c-FF}ge\n",
                     b"fud{ref=Cc:C0:0d-CR}ge\n",
                     b"fud{ref=Cc:C0:1b-ESC}ge\n",
                     b"fud{ref=Cc:C0:1c-FS}ge\n",
                     b"fud{ref=Cc:C0:1d-GS}ge\n",
                     b"fud{ref=Cc:C0:1e-RS}ge\n",
                     b"fud{ref=Cc:C0:1f-US}ge\n",
    ))
    proc = Popen([ './vrt-fix-characters',
                   '--field', 'word',
                   '--entities' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out == want
    assert not err
    assert proc.returncode == 0

def test_entity_name_digits(tmpdir):
    '''Entity name with digits, such as &frac12;.

    '''
    names = makenameline(b'word'.split())
    send = b''.join((names,
                     b'&frac12; kg\n'
    ))
    want = b''.join((names,
                     '½ kg\n'.encode('UTF-8'),
    ))
    proc = Popen([ './vrt-fix-characters',
                   '--field', 'word',
                   '--entities' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out == want
    assert not err
    assert proc.returncode == 0

def test_amp_entities(tmpdir):
    '''Decode mis-encoded entity references such as &amp;quot;.

    '''
    names = makenameline(b'word'.split())
    send = b''.join(
        (names,
         b'<text a="&amp;quot; &amp; lt; &amp;lt; &amp;dollar; &amp;#42;">\n',
         b'&amp;quot; &amp; lt; &amp;lt; &amp;dollar; &amp;#42;\n'))
    want = b''.join(
        (names,
         b'<text a="&quot; &amp; lt; &lt; $ *">\n',
         b'" &amp; lt; &lt; $ *\n'))
    proc = Popen([ './vrt-fix-characters',
                   '--field', 'word',
                   '--attr', 'a',
                   '--entities',
                   '--amp-entities' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out == want
    assert not err
    assert proc.returncode == 0

def test_eq_end_attr(tmpdir):
    '''Attribute parsing, "=" at end of value: head="VAL=" gen="WEV".
    Nothing to fix, other than normalize the order of attributes, but
    should not break them either.

    '''
    names = makenameline(b'word'.split())
    send = b''.join((names,
                     b'<text head="VAL=" gen="WEV">\n'))
    want = b''.join((names,
                     b'<text gen="WEV" head="VAL=">\n'))
    proc = Popen([ './vrt-fix-characters',
                   '--entities',
                   '--attr', 'head',
                   '--replace=identify' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert not err
    assert out == want
    assert proc.returncode == 0
