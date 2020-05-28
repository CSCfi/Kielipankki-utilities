import os
import pathlib2 # needs? anyway, that be where tmp_path is
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired

from tests.tools import fake # sibling library module to provide fake data

# ./vrt-drop maps "send" to "want" but fails on "fail"
# (omitting redundant names but requiring initial names)
send = b''.join(fake.nameloop(120, b'foo bar baz'.split()))
fail = b''.join(fake.nameloop(120, b'foo bar baz'.split(), sans = True))
want = b''.join(fake.nameloop(120, b'foo bar baz'.split(), once = True))

def test_000(tmp_path):
    '''Can direct stdout to file.'''
    ouf = tmp_path / 'roska.vrt'
    with ouf.open('bw') as ous:
        proc = Popen([ './vrt-drop' ],
                     stdin = PIPE,
                     stdout = ous,
                     stderr = PIPE)
        out, err = proc.communicate(input = send, timeout = 5)
    assert proc.returncode == 0
    assert ouf.exists()
    assert not out
    assert not err
    assert ouf.read_bytes() == want
    # also there should not be any other files there
    # (nor any stray effects anywhere else)

def test_001(tmp_path):
    '''Can pipe stdout to another process.'''
    ouf = tmp_path / 'roska.vrt'
    with ouf.open('bw') as ous:
        copy = Popen([ 'cat' ],
                    stdin = PIPE,
                    stdout = ous,
                    stderr = None)
        proc = Popen([ './vrt-drop' ],
                     stdin = PIPE,
                     stdout = copy.stdin,
                     stderr = STDOUT)
        _, _ = proc.communicate(input = send, timeout = 3)
        out, err = copy.communicate(timeout = 3)
    assert proc.returncode == 0
    assert ouf.exists()
    assert not out
    assert not err
    assert ouf.read_bytes() == want
    # also there should not be any other files there
    # (nor any stray effects anywhere else)

def test_002(tmp_path):
    '''Can write to a named file.'''
    ouf = tmp_path / 'roska.vrt'
    proc = Popen([ './vrt-drop', '-o', str(ouf) ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 3)
    assert proc.returncode == 0
    assert ouf.exists()
    assert not out
    assert not err
    assert ouf.read_bytes() == want
    # also there should not be any other files there
    # (nor any stray effects anywhere else)

def test_003(tmp_path):
    '''Can write to a sibling file.'''
    inf = tmp_path / 'roska.vrt'
    ouf = tmp_path / 'roska.vrt.out'
    inf.write_bytes(send)
    assert inf.exists()
    assert not ouf.exists()
    proc = Popen([ './vrt-drop', '-I', 'out', str(inf) ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 3)
    assert proc.returncode == 0
    assert ouf.exists()
    assert not out
    assert not err
    assert inf.read_bytes() == send
    assert ouf.read_bytes() == want
    # also there should not be any other files there
    # (nor any stray effects anywhere else)

def test_004(tmp_path):
    '''Can write to a sibling file.'''
    inf = tmp_path / 'roska.vrt'
    ouf = tmp_path / 'roska.out'
    inf.write_bytes(send)
    assert inf.exists()
    assert not ouf.exists()
    proc = Popen([ './vrt-drop', '-I', 'vrt/out', str(inf) ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 3)
    assert proc.returncode == 0
    assert ouf.exists()
    assert not out
    assert not err
    assert inf.read_bytes() == send
    assert ouf.read_bytes() == want
    # also there should not be any other files there
    # (nor any stray effects anywhere else)

def test_005(tmp_path):
    '''Can replace input file with output!'''
    inf = tmp_path / 'roska.vrt'
    inf.write_bytes(send)
    assert inf.exists()
    proc = Popen([ './vrt-drop', '-i', str(inf) ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 3)
    assert proc.returncode == 0
    assert inf.exists()
    assert not out
    assert not err
    assert inf.read_bytes() == want
    # also there should not be any other files there
    # (nor any stray effects anywhere else)

def test_006(tmp_path):
    '''Can replace input file with output, with backup!'''
    inf = tmp_path / 'roska.vrt'
    bak = tmp_path / 'roska.vrt-'
    inf.write_bytes(send)
    assert inf.exists()
    assert not bak.exists()
    proc = Popen([ './vrt-drop', '-b', '-', str(inf) ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 3)
    assert proc.returncode == 0
    assert inf.exists()
    assert bak.exists()
    assert not out
    assert not err
    assert inf.read_bytes() == want
    assert bak.read_bytes() == send
    # also there should not be any other files there
    # (nor any stray effects anywhere else)

# TODO test that all manner of invalid filename option combinations
# FAIL as intended (with input intact and often partial tmp file,
# error status, error message, what not)

def test_007(tmp_path):
    '''Cannot name existing file as output file'''
    old = tmp_path / 'roska.vrt'
    old.write_bytes(send)
    assert old.exists()
    proc = Popen([ './vrt-drop', '-o', str(old) ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 3)
    assert proc.returncode
    assert old.exists()
    assert not out
    assert err
    assert old.read_bytes() == send
    # also there should not be any other files there
    # (nor any stray effects anywhere else)

def test_008(tmp_path):
    '''Cannot name sibling without named input'''
    proc = Popen([ './vrt-drop', '-I', 'out' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 3)
    assert proc.returncode
    assert not out
    assert err
    # also there should not be any other files there
    # (nor any stray effects anywhere else)

def test_009(tmp_path):
    '''Cannot name sibling without named input'''
    proc = Popen([ './vrt-drop', '-I', 'vrt/out' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 3)
    assert proc.returncode
    assert not out
    assert err
    # also there should not be any other files there
    # (nor any stray effects anywhere else)

def test_010(tmp_path):
    '''Cannot name existing sibling as output file'''
    inf = tmp_path / 'roska.vrt'
    old = tmp_path / 'roska.vrt.out'
    inf.write_bytes(send)
    old.write_bytes(send)
    assert inf.exists()
    assert old.exists()
    proc = Popen([ './vrt-drop', '-I', 'out', str(inf) ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 3)
    assert proc.returncode
    assert inf.exists()
    assert old.exists()
    assert not out
    assert err
    assert inf.read_bytes() == send
    assert old.read_bytes() == send
    # also there should not be any other files there
    # (nor any stray effects anywhere else)

def test_011(tmp_path):
    '''Cannot name existing sibling as output file'''
    inf = tmp_path / 'roska.vrt'
    old = tmp_path / 'roska.out'
    inf.write_bytes(send)
    old.write_bytes(send)
    assert inf.exists()
    assert old.exists()
    proc = Popen([ './vrt-drop', '-I', 'vrt/out', str(inf) ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 3)
    assert proc.returncode
    assert inf.exists()
    assert old.exists()
    assert not out
    assert err
    assert inf.read_bytes() == send
    assert old.read_bytes() == send
    # also there should not be any other files there
    # (nor any stray effects anywhere else)

def test_012(tmp_path):
    '''Leave named output in temp file upon failure'''
    ouf = tmp_path / 'roska.vrt'
    proc = Popen([ './vrt-drop', '-o', str(ouf) ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = fail, timeout = 3)
    assert proc.returncode
    assert not ouf.exists()
    assert tmp_path.glob('*.tmp')
    assert not out
    assert err
    # also there should not be any other files there
    # (nor any stray effects anywhere else)

def test_013(tmp_path):
    '''Leave sibling output in temp file upon failure'''
    inf = tmp_path / 'roska.vrt'
    ouf = tmp_path / 'roska.vrt.out'
    inf.write_bytes(fail)
    proc = Popen([ './vrt-drop', '-I', 'out', str(inf) ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 3)
    assert proc.returncode
    assert inf.exists()
    assert not ouf.exists()
    assert tmp_path.glob('roska.vrt.out.*.tmp')
    assert not out
    assert err
    # also there should not be any other files there
    # (nor any stray effects anywhere else)

def test_014(tmp_path):
    '''Leave sibling output in temp file upon failure'''
    inf = tmp_path / 'roska.vrt'
    ouf = tmp_path / 'roska.out'
    inf.write_bytes(fail)
    proc = Popen([ './vrt-drop', '-I', 'vrt/out', str(inf) ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 3)
    assert proc.returncode
    assert inf.exists()
    assert not ouf.exists()
    assert tmp_path.glob('roska.out.*.tmp')
    assert not out
    assert err
    # also there should not be any other files there
    # (nor any stray effects anywhere else)

def test_015(tmp_path):
    '''Leave in-place output in temp file upon failure'''
    inf = tmp_path / 'roska.vrt'
    inf.write_bytes(fail)
    proc = Popen([ './vrt-drop', '-i', str(inf) ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 3)
    assert proc.returncode
    assert inf.exists()
    assert inf.read_bytes() == fail
    assert tmp_path.glob('roska.vrt.*.tmp')
    assert not out
    assert err
    # also there should not be any other files there
    # (nor any stray effects anywhere else)

def test_016(tmp_path):
    '''Leave in-place output in temp file upon failure'''
    inf = tmp_path / 'roska.vrt'
    bak = tmp_path / 'roska.vrt-'
    inf.write_bytes(fail)
    proc = Popen([ './vrt-drop', '-b-', str(inf) ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 3)
    assert proc.returncode
    assert inf.exists()
    assert not bak.exists()
    assert inf.read_bytes() == fail
    assert tmp_path.glob('roska.vrt.*.tmp')
    assert not out
    assert err
    # also there should not be any other files there
    # (nor any stray effects anywhere else)

