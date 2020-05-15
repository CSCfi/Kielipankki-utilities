from subprocess import Popen, PIPE, TimeoutExpired

import pytest

import fake # sibling library module to provide fake data

def test_000(tmpdir):
    proc = Popen([ './vrt-drop', '--help' ],
                 stdin = None,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 5)
    assert out
    assert not err
    assert proc.returncode == 0

@pytest.mark.skip(reason = 'need to rewrite both test and implementation')
def test_deprecated_001(tmpdir):
    send = b''.join(fake.nameloop(20))
    # is meant to replace first name comment
    # and drop the rest TODO
    # but fake.nameloop() does not even have name-comment *first*
    want = b''.join((b'!<-- #vrt positional-attributes: line -->\n',
                     *(( line
                         if line.startswith(b'<')
                         else line.split(b'\t')[1] + b'\n' )
                       for line in fake.nameloop(2)
                       if not line.startswith(b'<!-- #vrt positional-attributes: '))))
    proc = Popen([ './vrt-drop', '-n', 'loop,word' ],
                 stdin = PIPE,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(input = send, timeout = 5)
    assert out == want
    assert not err
    assert proc.returncode == 0

# TODO
# deprecate -names/-n in favour of --field/-f
# see that -n/-f takes comma-separated groups
# drop further name comments
# librarify in libvrt/.
