# -*- mode: Python; -*-

# It is to be noted that "./game" is sensitive to the host. It may
# guess a default a host for which it can create job scripts but not
# succesfully submit them (unless it guessed correctly, that is).
# Tests with --cat should be ok.

# Each test should either have --cat (to not submit the job at all) or
# have --test (to submit to the test partition). Having both is, of
# course, all right.

# Tests with --test wait for ./game, ./game waits for sbatch. In
# tests, SBATCH_WAIT=1 *or any non-zero number* seems to be effective,
# and 0 or *any non-number* not. The document where one learned about
# SBATCH_WAIT does not say anything about what *value* works.

# Finally, so that the actual jobs see the tmp_path directory at all:
#
# $ pytest --basetemp=./whatever
#
# Because the job runs in a different computer, as it were. It dies
# without a trace when it does not have the directory for its log
# files, let alone the result file.

# Post-finally, run (some) tests *in* the tmp_path directory! Refer to
# ./game as tmp_path.cwd() / 'game' with the subprocess cwd set to
# tmp_path. (Actually Path.cwd() but tmp_path serves as a handle.)

import os
from subprocess import run, Popen, PIPE, TimeoutExpired

# Decorate with @have_sbatch to be able to run sbatch.
from tests.tools.skippers import have_sbatch

def test_001(tmp_path):
    proc = Popen([ str(tmp_path.cwd() / 'game'),
                   '--help' ],
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
    logpath = tmp_path / 'log'
    result0 = tmp_path / 'result0.out'
    proc = run([ str(tmp_path.cwd() / 'game'),
                 '--test', '-M5',
                 '--log', 'log',
                 'touch', 'result0.out' ],
               cwd = str(tmp_path),
               env = dict(os.environ,
                          SBATCH_WAIT = '1'),
               capture_output = True,
               timeout = 30)
    assert proc.returncode == 0
    assert b'Submitted batch job' in proc.stdout
    assert b'billing' in proc.stderr
    assert len(tuple(logpath.glob('*-*-game.err'))) == 1
    assert len(tuple(logpath.glob('*-*-game.out'))) == 1
    assert result0.exists()

@have_sbatch
def test_004b(tmp_path):
    logpath = tmp_path / 'log'
    result1 = tmp_path / 'result1.out'
    proc = run([ str(tmp_path.cwd() / 'game'),
                 '--test', '-M5',
                 '--log', 'log',
                 'touch', '//',
                 'result1.out' ],
               cwd = str(tmp_path),
               env = dict(os.environ,
                          SBATCH_WAIT = '1'),
               capture_output = True,
               timeout = 30)
    assert proc.returncode == 0
    assert b'Submitted batch job' in proc.stdout
    assert b'billing' in proc.stderr
    assert len(tuple(logpath.glob('*-*-game.err'))) == 1
    assert len(tuple(logpath.glob('*-*-game.out'))) == 1
    assert result1.exists()

@have_sbatch
def test_004c(tmp_path):
    logpath = tmp_path / 'log'
    # test partition has a 2-node limit
    result1 = tmp_path / 'result1.out'
    result2 = tmp_path / 'result2.out'
    proc = run([ str(tmp_path.cwd() / 'game'),
                 '--test', '-M5',
                 '--log', 'log',
                 'touch', '//',
                 'result1.out',
                 'result2.out' ],
               cwd = str(tmp_path),
               env = dict(os.environ,
                          SBATCH_WAIT = '1'),
               capture_output = True,
               timeout = 60)
    assert proc.returncode == 0
    assert b'Submitted batch job' in proc.stdout
    assert b'billing' in proc.stderr
    assert len(tuple(logpath.glob('*-*-game.err'))) == 2
    assert len(tuple(logpath.glob('*-*-game.out'))) == 2
    assert result1.exists()
    assert result2.exists()
