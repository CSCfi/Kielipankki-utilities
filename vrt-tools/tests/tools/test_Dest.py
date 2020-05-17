import os
import pathlib2 # needs? anyway, that be where tmp_path is
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired

import fake # sibling library module to provide fake data

send = b''.join(fake.nameloop(120, b'foo bar baz'.split()))
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
