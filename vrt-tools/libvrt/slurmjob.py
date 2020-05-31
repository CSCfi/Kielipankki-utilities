# -*- mode: Python; -*-

from itertools import chain

import os, sys
from shlex import quote

from libvrt.bad import BadData
from libvrt.gameargs import guesshost
from libvrt.slurmout import setup

def moduleloader(args):
    '''Return a command to load module "kieli" and on puhti also "biojava"
    with any diagnostics directed depending on the args.kieli option,
    which may also cause the "command" to be a comment so the modules
    are not actually loaded.

    '''
    kieli = ({ 'yes' : 'module load kieli',
               'out' : '2>&1 module load kieli',
               'err' : '1>&2 module load kieli',
               'null' : '1> /dev/null 2>&1 module load kieli',
               'no' : '# module load kieli' }
             [args.kieli])

    if guesshost() == 'puhti': kieli += ' biojava'

    return kieli

# Depending on the output options, command is one of:
# cmd arg ... args[TASK_ID]
# cmd arg ... args[TASK_ID] > outfile
# cmd arg ... args[TASK_ID] > tempfile
# with appropriate quotation for the shell,
# where arg ... are the arguments before //
# and args[TASK_ID] omitted if there no //.

def separate(args):
    haumeniseparators = args.argument.count('//')
    if haumeniseparators > 1:
        raise BadData('only one // is allowed')

    if haumeniseparators == 0:
        headargs = args.argument
        tailargs = []
        return headargs, tailargs

    # haumeniseparators == 1

    argpos = args.argument.index('//')
    headargs = args.argument[:argpos]
    tailargs = args.argument[1 + argpos:]

    if len(tailargs) == 0:
        raise BadData('at least one array argument must follow //')

    if len(tailargs) > 4000:
        # https://research.csc.fi/taito-array-jobs
        # https://docs.csc.fi/computing/running/batch-job-partitions/
        # TODO a task is a core, a task is not a core
        # TODO understand what that means and what is the actual limit
        raise BadData(('way too many array arguments: {}: '
                       'even puhti "large" partition limit is 4000 cores'
                      .format(len(tailargs))))

    return headargs, tailargs

def arraylines(tailargs):
    '''Lay out and yield the separate arguments in lines that are then
    joined to be the array contents in an an array job script. For
    each task, the command takes one. Or produce dummy token to run
    the command once, and the command takes none.

    '''
    if not tailargs:
        yield "    '(none)'"
        return

    n = 0
    for arg in map(quote, tailargs):
        if n == 0:
            yield '    '
            yield arg
            n = 4 + len(arg)
        elif n + len(arg) > 75:
            yield '\n    '
            yield arg
            n = 4 + len(arg)
        else:
            yield ' '
            yield arg
            n += 1 + len(arg)

def jobscript(args):

    # If not really an array job:
    # - "args" contains an unused placeholder '(none)'
    #
    # If on taito:
    # '#SBATCH --account=*' line is removed after filling.
    
    template = '''\
#! /bin/bash
#SBATCH --job-name={job}
#SBATCH --account={bill}
#SBATCH --partition={partition}
#SBATCH --nodes={nodes}
#SBATCH --ntasks={cores}
#SBATCH --time={time}
#SBATCH --mem={memory}
#SBATCH --gres=nvme:{scratch}
#SBATCH --out={out}
#SBATCH --error={err}
#SBATCH --chdir={workdir}
#SBATCH --array=1-{last}

args=(:
{args}
)

infile="${{args[$SLURM_ARRAY_TASK_ID]}}"
outfile={outfile}
outstem="${{infile##*/}}"
outstem="${{outstem%%.*}}"
outfile="${{outfile//<>/$outstem}}"

echo command: {logcommand}
echo nth arg: "$infile"
echo outfile: {outinfo}
echo workdir: {workdir}
echo partition: {partition}
echo nodes: {nodes}
echo cores: {cores}
echo time: {time}
echo memory: {memory}
echo load kieli: {whetherkieli}
echo billing group: {bill}
echo
date "+%F %T START"

{kieli}
{mktemp}
{command}

status=$?
{finish}

T=$SECONDS
printf -v time %d:%02d:%02d $((T/3600)) $((T%3600/60)) $((T%60))
date "+%F %T FINISH IN $time WITH STATUS $status"
'''

    logdir, outfile = setup(args)

    mktemp = (
        ''
        if outfile is None else
        ( 'mkdir --parents "${outfile%/*}"\n'
          'tmpfile=$(mktemp "$outfile.XXXXXX.tmp")' )
    )

    finish = (
        ''
        if outfile is None else
        'mv "$tmpfile" "$outfile"'
        if args.accept else
        'test $status -eq 0 && mv "$tmpfile" "$outfile"'
    )

    headargs, tailargs = separate(args)

    # TODO rewrite those chains without chain now at Python 3.5

    command = ' '.join(chain([quote(args.command)],
                             map(quote, headargs),
                             ( [ '"$infile"' ]
                               if tailargs else
                               [] ),
                             ( []
                               if outfile is None else
                               ['> "$tmpfile"' ] )))

    logcommand = ' '.join(chain([quote(args.command)],
                                map(quote, headargs),
                                ( ['<nth arg>']
                                  if tailargs else
                                  [] )))

    partition = (
        ['small', 'large'][len(tailargs) > 30]
        if args.partition == 'puhti-default'
        else args.partition
    )

    script = (template
              .format(job = args.job,
                      bill = args.bill,
                      partition = partition,
                      nodes = '1',
                      cores = args.cores,
                      time = args.time,
                      memory = args.memory,
                      scratch = args.scratch,
                      out = quote(os.path.join(args.log, '%A-%a-{}.out'
                                               .format(args.job))),
                      err = quote(os.path.join(args.log, '%A-%a-{}.err'
                                               .format(args.job))),
                      last = len(tailargs) or 1,
                      workdir = quote(os.getcwd()),
                      logcommand = quote(logcommand),
                      kieli = moduleloader(args),
                      whetherkieli = args.kieli,
                      outfile = quote(outfile or '(stdout)'),
                      outinfo = quote(args.out or '(stdout)'),
                      mktemp = mktemp,
                      command = command,
                      args = ''.join(arraylines(tailargs)),
                      finish = finish)
    )

    if guesshost() == 'taito':
        # Taito does not seem to accept any value for --account,
        # but works as usual when --account is not specified.
        script = '\n'.join((line for line in script.split('\n')
                            if not line.startswith('#SBATCH --account=')))

    script = '\n'.join((line for line in script.split('\n')
                        if not line == '#SBATCH --gres=nvme:None'))

    return script
