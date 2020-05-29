#! /usr/bin/env python3

# The original inspiration for the name "game" was a dialogue in a
# Tenavat [Peanuts] cartoon where Kaustiset [Woodstocks] followed
# Ressu [Snoopy] on some sort of hiking mission.
#
# - Mitä on erä? [What is batch?]
# - Riistaa kuten te. [Game like you.]
#
# That particular cartoon seems to have vanished.
#
# This is a new game now and subsumes array jobs.

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
                   timeout = 60)
    except BadData as exn:
        print('{}:'.format(args.prog), exn,
              file = sys.stderr)
        exit(1)
