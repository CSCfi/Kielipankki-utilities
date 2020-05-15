from subprocess import Popen, PIPE, TimeoutExpired

import fake # sibling library module to provide fake data

def test_000(tmpdir):
    proc = Popen([ './vrt-keep', '--help' ],
                 stdin = None,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 5)
    assert out
    assert not err
    assert proc.returncode == 0

# TODO
# deprecate -name/-n in favour of --field/-f
# see that -n/-f takes comma-separated groups
# librarify in libvrt/.
