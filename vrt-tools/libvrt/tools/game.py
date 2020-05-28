#! /usr/bin/env python3

# Original inspiration for the name "game" was:
# - Mitä on erä?
# - Riistaa kuten te.
# (Seen in a Tenavat cartoon that has not been found again.)
#
# This is the new game now and subsumes array jobs.

from subprocess import run
import os, grp, sys

from libvrt.bad import BadData
from libvrt.gameargs import parsearguments, checkbill
from libvrt.slurmjob import jobscript

def submit(args):
    try:
        checkbill(args)
        script = jobscript(args)
        proc = run([ 'cat' if args.cat else 'sbatch' ],
                   input = script.encode('UTF-8'),
                   timeout = 20)
    except BadData as exn:
        print('{}:'.format(args.prog), exn,
              file = sys.stderr)
        exit(1)
