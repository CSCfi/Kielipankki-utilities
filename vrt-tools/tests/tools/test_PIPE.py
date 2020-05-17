'''Test that some of the tools handle broken pipe nicely, some of the
time.

Minimally nice handling means termination with a non-zero return code
(often called status). It is also intended that the individual tools
let PIPE be handled in the relevant branch of a common try block in
the generic args processor, so the output "vrt-keep: broken pipe" is
expected. (A Python traceback is not expected.)

Trick to trigger PIPE seems to be to actually pipe the output to an
external command that closes its stdin early, i.e., head -n 0. That
is, other attempts failed, while this attempt worked at least once.

'''

from subprocess import Popen, PIPE, STDOUT, TimeoutExpired

import fake # sibling library module to provide fake data

def test_001(tmpdir):
    old = b'word line loop'.split()
    send = b''.join(fake.nameloop(1200, old))
    head = Popen([ 'head', '--lines', '0' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = STDOUT)
    proc = Popen([ './vrt-keep', '--rest' ],
                 stdin = PIPE,
                 stdout = head.stdin,
                 stderr = PIPE)
    out, _ = head.communicate(timeout = 3)
    _, err = proc.communicate(input = send, timeout = 3)
    assert proc.returncode
    assert not head.returncode
    assert not out
    assert b'vrt-keep: broken pipe' in err
