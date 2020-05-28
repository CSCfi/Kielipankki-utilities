# -*- mode: Python; -*-

# It is to be noted that "game" is sensitive to the host.
# It may guess a default a host for which it can create
# job scripts but not succesfully submit them (unless it
# guessed correctly, that is). Tests with --cat should
# be ok.

# Each test should either have --cat (to not submit the
# job at all) or have --test (to submit to the test
# partition). It is all right to have both, of course.

import os
from subprocess import Popen, PIPE, TimeoutExpired

# Decorate with @have_sbatch to be able to run sbatch.
from tests.tools.skippers import have_sbatch

def test_001(tmp_path):
    proc = Popen([ './game', '--help' ],
                 stdin = None,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 3)
    assert out
    assert not err
    assert proc.returncode == 0

def test_002a(tmp_path):
    proc = Popen([ './game', '--cat',
                   'echo' ],
                 stdin = None,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 3)
    assert out
    assert not err
    assert proc.returncode == 0
    assert b'#SBATCH --job-name=game' in out
    assert b'#SBATCH --out=gamelog/%A-%a-game.out' in out
    assert b'#SBATCH --error=gamelog/%A-%a-game.err' in out
    assert b'#SBATCH --nodes=1' in out
    assert b'#SBATCH --array=1-1' in out
    assert b'echo nth arg: NA' in out

def test_002b(tmp_path):
    proc = Popen([ './game', '--cat',
                   '--job=regret',
                   '--log=log/test',
                   '--test',
                   'echo' ],
                 stdin = None,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 3)
    assert out
    assert not err
    assert proc.returncode == 0
    assert b'#SBATCH --job-name=regret' in out
    assert b'#SBATCH --partition=test' in out
    assert b'#SBATCH --out=log/test/%A-%a-regret.out' in out
    assert b'#SBATCH --error=log/test/%A-%a-regret.err' in out
    assert b'#SBATCH --nodes=1' in out
    assert b'#SBATCH --array=1-1' in out
    assert b'echo nth arg: NA' in out

def test_003a(tmp_path):
    proc = Popen([ './game', '--cat',
                   'echo', 'this', 'is', 'a test'],
                 stdin = None,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 3)
    assert out
    assert not err
    assert proc.returncode == 0
    assert b'#SBATCH --array=1-1' in out
    assert b'echo nth arg: NA' in out

def test_003b(tmp_path):
    proc = Popen([ './game', '--cat',
                   'echo', '//', 'this', 'is', 'a test'],
                 stdin = None,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 3)
    assert out
    assert not err
    assert proc.returncode == 0
    assert b'#SBATCH --array=1-3' in out
    assert b'echo nth arg:' in out
    assert b'echo nth arg: NA' not in out

def test_003c(tmp_path):
    proc = Popen([ './game', '--cat',
                   'echo', 'this', 'is', '//', 'a test', 'not a test'],
                 stdin = None,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 3)
    assert out
    assert not err
    assert proc.returncode == 0
    assert b'#SBATCH --array=1-2' in out
    assert b'echo nth arg:' in out
    assert b'echo nth arg: NA' not in out

def test_003d(tmp_path):
    proc = Popen([ './game', '--cat',
                   'echo', 'this', 'is', 'fail', '//'],
                 stdin = None,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 3)
    assert not out
    assert err
    assert proc.returncode

@have_sbatch
def test_004a(tmp_path):
    proc = Popen([ './game', '--test', '-M10',
                   'touch', str(tmp_path / 'result.out') ],
                 env = dict(os.environ,
                            SBATCH_WAIT = 'please'),
                 stdin = None,
                 stdout = PIPE,
                 stderr = PIPE)
    out, err = proc.communicate(timeout = 30)
    assert proc.returncode == 0
    assert not out
    assert b'billing' in err
