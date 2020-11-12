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

def test_LS(tmpdir):
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
