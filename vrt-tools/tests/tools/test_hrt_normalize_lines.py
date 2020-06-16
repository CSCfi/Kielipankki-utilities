from subprocess import Popen, PIPE

def test_000():
    proc = Popen([ './hrt-normalize-lines', '--help' ],
                 stdin = None,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 5)
    assert out
    assert not err
    assert proc.returncode == 0

def test_001():
    inf = '\n'.join((
        '',
        '',
        '<text>',
        '<paragraph>',
        '',
        'content1',
        'content2',
        '',
        '',
        'content',
        '',
        '</paragraph>',
        '</text>',
        '',
        '',
        '' # newline at end
    ))
    ouf = '\n'.join((
        '<text>',
        '<paragraph>',
        'content1',
        'content2',
        '',
        'content',
        '</paragraph>',
        '</text>',
        '' # newline at end
    ))
    proc = Popen([ './hrt-normalize-lines' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = inf.encode('UTF-8'), timeout = 5)
    assert out
    assert not err
    assert proc.returncode == 0
    assert out.decode('UTF-8') == ouf

def test_002():
    inf = '\n'.join((
        '   ',
        '\t',
        '<text>',
        '<paragraph>',
        '\xa0\xa0 \xa0',
        'content1',
        'content2',
        '',
        '\N{THIN SPACE}',
        'content',
        '',
        '</paragraph>',
        '</text>',
        '',
        '',
        '' # newline at end
    ))
    ouf = '\n'.join((
        '<text>',
        '<paragraph>',
        'content1',
        'content2',
        '',
        'content',
        '</paragraph>',
        '</text>',
        '' # newline at end
    ))
    proc = Popen([ './hrt-normalize-lines' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = inf.encode('UTF-8'), timeout = 5)
    assert out
    assert not err
    assert proc.returncode == 0
    assert out.decode('UTF-8') == ouf

def test_003():
    inf = '\n'.join((
        '   ',
        '\t',
        '<text>',
        '<paragraph>',
        '\xa0\xa0 \xa0',
        '</paragraph>',
        '<paragraph>',
        'content1',
        'content2',
        '',
        '\N{THIN SPACE}',
        '</paragraph>',
        '<paragraph>',
        'content',
        '',
        '</paragraph>',
        '</text>',
        '',
        '',
        '' # newline at end
    ))
    ouf = '\n'.join((
        '<text>',
        '<paragraph>',
        '</paragraph>',
        '<paragraph>',
        'content1',
        'content2',
        '</paragraph>',
        '<paragraph>',
        'content',
        '</paragraph>',
        '</text>',
        '' # newline at end
    ))
    proc = Popen([ './hrt-normalize-lines' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = inf.encode('UTF-8'), timeout = 5)
    assert out
    assert not err
    assert proc.returncode == 0
    assert out.decode('UTF-8') == ouf
