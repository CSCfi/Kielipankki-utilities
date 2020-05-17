'''Test that some of the tools handle keyboard interrupt nicely, some
of the time.

Minimally nice handling means termination with a non-zero return code
(often called status). It is also intended that the individual tools
let INT be handled in the relevant branch of a common try block in the
generic args processor, so the output "vrt-keep: keyboard interrupt"
is expected. (A Python traceback is not expected.)

'''

from subprocess import Popen, PIPE, TimeoutExpired
from time import sleep

import fake # sibling library module to provide fake data

def test_001(tmpdir):
    old = b'word line loop'.split()
    send = b''.join(fake.nameloop(120, old))
    proc = Popen([ './vrt-keep', '--rest' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    proc.stdin.write(send)
    sleep(0.1)
    proc.send_signal(2)
    out, err = proc.communicate(timeout = 5)
    assert proc.returncode
    assert b'vrt-keep: keyboard interrupt' in err
