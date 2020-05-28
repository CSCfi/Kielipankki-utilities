# -*- mode: Python; -*-

# It is to be noted that "./game" is sensitive to the host. It may
# guess a default a host for which it can create job scripts but not
# succesfully submit them (unless it guessed correctly, that is).
# Tests with --cat should be ok.

# Each test should either have --cat (to not submit the job at all) or
# have --test (to submit to the test partition). Having both is, of
# course, all right.

# Tests with --test wait for ./game, ./game waits for sbatch.

import os
from subprocess import run, Popen, PIPE, TimeoutExpired

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
    assert b'billing' in err
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
    assert b'billing' in err
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
    assert b'billing' in err
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
    assert b'billing' in err
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
    assert b'billing' in err
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
    # now there should be an actual error message in err
    assert err
    assert proc.returncode

@have_sbatch
def test_004a(tmp_path):
    # TODO work out how to make tmp_path so that it exists also to the
    # computer that actually runs the submitted job, and one more
    # thing! Log directory also needs to be in a temporary location!
    # Hm, job will die silently if it cannot access log directory.
    # WHERE DOES ONE TEMP?
    #
    # (BACKGROUND: could not touch the result file in a job submitted
    # from a sinteractive session - and that must be made so that it
    # works)
    assert tmp_path.exists()
    result = tmp_path / 'result.out'
    proc = run([ './game', '--test', '-M5',
                 '--log', str(tmp_path / 'log'),
                 'touch', str(result) ],
               env = dict(os.environ,
                          SBATCH_WAIT = 'please'),
               capture_output = True,
               timeout = 30)
    assert proc.returncode == 0
    assert b'Submitted batch job' in proc.stdout
    assert b'billing' in proc.stderr
    assert result.exists()
