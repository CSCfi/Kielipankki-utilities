from subprocess import Popen, PIPE, TimeoutExpired

from libvrt.nameline import makenameline

from tests.tools import fake # sibling library module to provide fake data

def test_000(tmpdir):
    proc = Popen([ './vrt-name', '--help' ],
                 stdin = None,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 5)
    assert out
    assert not err
    assert proc.returncode == 0

def test_001(tmpdir):
    proc = Popen([ './vrt-name',
                   '--map= v3=lemon, v1=v2',
                   '-m', 'v2=v1',
                   '--map', ',,,' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 5)
    assert out == makenameline(b'v2 v1 lemon'.split())
    assert not err
    assert proc.returncode == 0

def test_002(tmpdir):
    proc = Popen([ './vrt-name', '--map', 'v4=v4' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 5)
    assert out == makenameline(b'v1 v2 v3 v4'.split())
    assert not err
    assert proc.returncode == 0

def test_deprecated_003(tmpdir):
    proc = Popen([ './vrt-name', '-k', '2=lemon', '-k', '1=word' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 5)
    assert out == makenameline(b'word lemon'.split())
    assert not err
    assert proc.returncode == 0

def test_deprecated_004(tmpdir):
    proc = Popen([ './vrt-name', '-n', '3' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 5)
    assert out == makenameline(b'v1 v2 v3'.split())
    assert not err
    assert proc.returncode == 0

def test_005(tmpdir):
    '''New ./vrt-name looks for data (a token line) in the first 100 input
    lines. Test that nothing happens at that.

    '''
    old = b'word line loop'.split()
    data = tuple(fake.nameloop(120, old))
    send = b''.join(data)
    want = b''.join((makenameline(b'word line loop'.split()),
                     *fake.nameloop(120, old, sans = True)))
    proc = Popen([ './vrt-name', '-m', 'v1=word,v2=line,v3=loop' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out == want
    assert not err
    assert proc.returncode == 0

def test_006(tmpdir):
    '''New ./vrt-name looks for the actual number of fields in a token
    line (in the first 100 input lines). Test that it fails with an
    error message when the number does not match.

    '''
    old = b'word line loop'.split()
    send = b''.join(fake.nameloop(20, old)) # 3 fields
    proc = Popen([ './vrt-name', '-m', 'v2=v2' ], # specify 2 fields
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert err
    assert proc.returncode
