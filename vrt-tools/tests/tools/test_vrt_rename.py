from subprocess import Popen, PIPE, TimeoutExpired

from libvrt.nameline import makenameline

from tests.tools import fake # sibling library module to provide fake data

def test_000(tmpdir):
    proc = Popen([ './vrt-rename', '--help' ],
                 stdin = None,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 5)
    assert out
    assert not err
    assert proc.returncode == 0

def test_001(tmpdir):
    old = makenameline(b'v0 v1 v2'.split())
    new = old.replace(b'v2', b'wev')
    send = old + b'(one)\t(1)\t(yksi)\n'
    want = new + b'(one)\t(1)\t(yksi)\n'
    proc = Popen([ './vrt-rename', '--map', 'v2=wev' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out == want
    assert not err
    assert proc.returncode == 0

def test_002(tmpdir):
    old = b'word line loop'.split()
    new = b'word line loop'.split()
    send = b''.join(fake.nameloop(120, old))
    want = b''.join(fake.nameloop(120, new, once = True))
    proc = Popen([ './vrt-rename',
                   '-m' 'line=line',
                   '-m', 'word=word, loop=loop' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out == want
    assert not err
    assert proc.returncode == 0
