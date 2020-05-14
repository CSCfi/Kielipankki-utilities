from subprocess import Popen, PIPE, TimeoutExpired

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
    assert out == b'<!-- #vrt positional-attributes: v2 v1 lemon -->\n'
    assert not err
    assert proc.returncode == 0

def test_002(tmpdir):
    proc = Popen([ './vrt-name', '--map', 'v4=v4' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 5)
    assert out == b'<!-- #vrt positional-attributes: v1 v2 v3 v4 -->\n'
    assert not err
    assert proc.returncode == 0

def test_deprecated_003(tmpdir):
    proc = Popen([ './vrt-name', '-k', '2=lemon', '-k', '1=word' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 5)
    assert out == b'<!-- #vrt positional-attributes: word lemon -->\n'
    assert not err
    assert proc.returncode == 0

def test_deprecated_004(tmpdir):
    proc = Popen([ './vrt-name', '-n', '3' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 5)
    assert out == b'<!-- #vrt positional-attributes: v1 v2 v3 -->\n'
    assert not err
    assert proc.returncode == 0
