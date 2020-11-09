from subprocess import Popen, PIPE, TimeoutExpired

from libvrt.nameline import makenameline

from tests.tools import fake # sibling library module to provide fake data

def test_000(tmpdir):
    proc = Popen([ './vrt-keep', '--help' ],
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
    proc = Popen([ './vrt-keep', '-f', 'line' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out.decode() == want.decode()
    assert not err
    assert proc.returncode == 0

def test_deprecated_001(tmpdir):
    old = b'word line loop'.split()
    new = b'line'.split()
    send = b''.join(fake.nameloop(120, old))
    want = b''.join(fake.nameloop(120, new, keep = (1,), once = True))
    proc = Popen([ './vrt-keep', '-n', 'line' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out.decode() == want.decode()
    assert not err
    assert proc.returncode == 0

def test_002(tmpdir):
    old = b'word line loop'.split()
    new = b'line word loop'.split()
    send = b''.join(fake.nameloop(120, old))
    want = b''.join(fake.nameloop(120, new, keep = (1, 0, 2), once = True))
    proc = Popen([ './vrt-keep', '-f', 'line', '--rest' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out.decode() == want.decode()
    assert not err
    assert proc.returncode == 0

def test_003(tmpdir):
    old = b'word line loop'.split()
    new = b'line word loop'.split()
    send = b''.join(fake.nameloop(120, old))
    want = b''.join(fake.nameloop(120, new, keep = (1, 0, 2), once = True))
    proc = Popen([ './vrt-keep', '-f', 'line,word', '--rest' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out.decode() == want.decode()
    assert not err
    assert proc.returncode == 0

def test_004(tmpdir):
    '''Test slash-ending names: keep one, dropping one.'''

    old = b'word line/ loop/'.split()
    new = b'line/'.split()
    send = b''.join(fake.nameloop(120, old))
    want = b''.join(fake.nameloop(120, new, keep = (1,), once = True))
    proc = Popen([ './vrt-keep', '-f', 'line/' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert not err
    assert proc.returncode == 0
    assert out.decode() == want.decode()
