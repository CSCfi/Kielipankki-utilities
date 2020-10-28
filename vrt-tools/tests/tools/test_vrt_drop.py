from subprocess import Popen, PIPE, TimeoutExpired

from libvrt.nameline import makenameline

from tests.tools import fake # sibling library module to provide fake test data

def test_000(tmpdir):
    proc = Popen([ './vrt-drop', '--help' ],
                 stdin = None,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 5)
    assert out
    assert not err
    assert proc.returncode == 0

def test_001(tmpdir):
    old = b'word line loop'.split()
    new = b'line'.split()
    send = b''.join(fake.nameloop(120, old))
    want = b''.join(fake.nameloop(120, new, keep = (1,), once = True))
    proc = Popen([ './vrt-drop', '-f', 'loop,word' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out == want
    assert not err
    assert proc.returncode == 0

def test_deprecated_001(tmpdir):
    '''Deprecated -n is alias to newly favoured -f, so testing the same
    thing as test_001.

    '''
    old = b'word line loop'.split()
    new = b'line'.split()
    send = b''.join(fake.nameloop(20, old))
    want = b''.join(fake.nameloop(20, new, keep = (1,), once = True))
    proc = Popen([ './vrt-drop', '-n', 'loop,word' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out == want
    assert not err
    assert proc.returncode == 0

def test_002(tmpdir):
    old = b'word line.x loop.x'.split()
    new = b'word'.split()
    send = b''.join(fake.nameloop(20, old))
    want = b''.join(fake.nameloop(20, new, keep = (0,), once = True))
    proc = Popen([ './vrt-drop', '--dots' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out.decode('UTF-8') == want.decode('UTF-8')
    assert not err
    assert proc.returncode == 0

def test_003(tmpdir):
    old = b'word line loop'.split()
    send = b''.join(fake.nameloop(120, old))
    want = b''.join(fake.nameloop(120, old, once = True))
    proc = Popen([ './vrt-drop' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out == want
    assert not err
    assert proc.returncode == 0
