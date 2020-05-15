from subprocess import Popen, PIPE, TimeoutExpired

import fake # sibling library module to provide fake data

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
    send = ( b'<!-- #vrt positional-attributes: v0 v1 v2 -->\n'
             b'(one)\t(1)\t(yksi)\n' )
    want = send.replace(b'v2', b'wev')
    proc = Popen([ './vrt-rename', '--map', 'v2=wev' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out == want
    assert not err
    assert proc.returncode == 0

# TODO make ./vrt-rename
# accept comma-or-space-separated pairs in each --map option
# drop further name comments
# librarified in libvrt/.
