# -*- mode: Python; -*-

from subprocess import Popen, PIPE

from pytest import mark

def _sbatch_version():
    '''Try to run "sbatch" in order to see if "sbatch" can be run at all.
    Return None if that seems not to be the case.

    '''
    try:
        proc = Popen([ 'sbatch', '--version' ],
                     stdin = None,
                     stdout = PIPE,
                     stderr = PIPE)
        out, err = proc.communicate(timeout = 8)
        if proc.returncode or err or not out:
            return None
        return out.decode('UTF-8')
    except Exception:
        return None

# Decorate a test with @have_sbatch to skip the test if failed to run
# sbatch --version, which can sometimes happen on certain laptops and
# other environments that may not have slurm installed. It is to be
# hoped that there is not some other "sbatch" there, then, either.

have_sbatch = (
    mark.skipif(_sbatch_version() is None,
                reason = 'one must have sbatch')
)

def _finnish_nertag_version():
    '''Try to run "finnish-nertag" in order to see if "finnish-nertag" can
    be run at all. Return None if that seems not to be the case.

    '''
    try:
        proc = Popen([ 'finnish-nertag', '--version' ],
                     stdin = None,
                     stdout = PIPE,
                     stderr = PIPE)
        out, err = proc.communicate(timeout = 8)
        if proc.returncode or err or not out:
            return None
        return out.decode('UTF-8')
    except Exception:
        return None

# Decorate a test with @have_finnish_nertag to skip the test if failed
# to run finnish-nertag --version, which can sometimes happen on
# certain laptops and other environments that may not have slurm
# installed. It is to be hoped that there is not some other
# "finnish-nertag" there, then, either.

have_finnish_nertag = (
    mark.skipif(_finnish_nertag_version() is None,
                reason = 'one must have finnish-nertag')
)
