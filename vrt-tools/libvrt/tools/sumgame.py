import glob
import os
import re

from subprocess import Popen, PIPE

from libvrt.args import version_args
from libvrt.bad import BadData

def parsearguments(argv, *, prog = None):

    description = '''

    Display in stdout a summary of the distribution of memory or time
    usage of completed tasks in array jobs in a log directory. The
    information comes from SLURM accounting system. The summaries show
    columns of seven observed values at or near the five quartile
    points and next to the two extrema. (Observations coincide when
    observations are few.)

    '''

    parser = version_args(description = description)

    parser.add_argument('logdir',
                        help = '''log directory''')

    group = parser.add_mutually_exclusive_group(required = True)

    group.add_argument('--memory', '-m',
                       choices = 'KMG%',
                       help = '''

                       summarize memory usage in desired multiples
                       of 1024 bytes or relative to requested
                       memory (indicated per node or per cpu)

                       ''')

    group.add_argument('--time', '-t',
                       action = 'store_true',
                       help = '''
                       
                       summarize time usage

                       ''')

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog

    return args

def main(args):
    '''Identify array jobs from *file names* in args.logdir, compute and
    display a summary. This only works in the host of the SLURM, for
    log files named jobid-taskid-whatever.out, of which only distinct
    jobids are extracted.

    '''

    jobs = {
        name.split('-')[0]
        for name
        in map(os.path.basename,
               glob.iglob(os.path.join(args.logdir, '*.out')))
        if re.match(r'\d+-\d+-', name)
    }

    if args.memory: summemory(*jobs, unit = args.memory)
    elif args.time: sumtime(*jobs)
    else: raise BadCode('this cannot happen')

def summemory(*jobs, unit = 'K'):
    print('JobID', 'ord', 'stat',
          # hoping NCPUS equals AllocCPUS
          # but how does one see how many
          # cores the job actually used?
          'AveRSS', 'MaxRSS', 'ReqMem', 'NCPUS',
          'obs', sep = '\t')
    for job in jobs: summemory1(job, unit = unit)
    return

def summemory1(job, *, unit):
    with Popen(
            # [ 'head', '-n', '40', 'sacct-mem.out' ] or
            # [ 'cat', 'sacct-mem.out' ] or
            [ 
                'sacct', '--jobs', job,
                '--state=cd',
                '--parsable2', '--noheader',
                '--format', 'jobid,averss,maxrss,reqmem,ncpus',
                '--units=K'
            ],
            stdin = None,
            stdout = PIPE,
            stderr = None) as proc:
        records = [
            (
                line
                .rstrip(b'\r\n')
                .decode('UTF-8')
                .split('|')
            )
            for line in proc.stdout
            if b'.batch' in line
            # MaxRSS and AveRSS seem to be on those lines only
            # whatever those lines may be
        ]

    JOB, AVE, MAX, REQ, CPU = range(5)

    for record in records:
        # drop "_<taskid>.batch" from jobid
        record[JOB] = record[JOB].split('_')[0]

    AVES = equarts(sorted((r[AVE] for r in records), key = kilos))
    MAXS = equarts(sorted((r[MAX] for r in records), key = kilos))
    REQS = equarts(sorted((r[REQ] for r in records)))

    for record in zip(equarts(sorted((r[JOB] for r in records))),
                      range(1, 8),
                      ('Min', 'Min1', 'LoQ',
                       'Med',
                       'HiQ', 'Max1', 'Max'),
                      form(AVES, unit, req = REQS),
                      form(MAXS, unit, req = REQS),
                      form(REQS, unit, req = REQS),
                      equarts(sorted((r[CPU] for r in records))),
                      [len(records) for k in range(1, 8)]):
        # constant fields are sorted as strings
        # merely to make it visible if they are
        # not constants - which cannot happen
        print(*record, sep = '\t')

def kilos(size):
    '''Sort key for memorial sizes. Ask sacct to report kilobytes, it
    attaches unit "K" to non-zero AveRSS or MaxRSS, "Kn" or "Kc" for
    ReqMem for "per node" or "per cpu" (or "per core" but that may be
    the same thing). And "K" seems to mean 1024.

    '''

    if size.endswith('K'):
        return int(size[:-1])

    if size.endswith(('Kc', 'Kn')):
        return int(size[:-2])

    if size == '0':
        return int(size)

    raise BadData('unexpected size: {}'.format(size))

def form(obs, unit, *, req):
    '''Format memorial quantitities for a human consumer person in
    requested multiples of 1024, or relative to the corresponding
    requested amounts of memory req when unit is "%". Return a string,
    complete with the new unit.

    '''

    obsK = tuple(map(kilos, obs))
    reqK = tuple(map(kilos, req))

    if unit == 'K':
        return obs

    if unit == 'M':
        def scaled(k, _):
            if k == 0: return k # keep as exact 0
            return k / 1024
    elif unit == 'G':
        def scaled(k, _):
            if k == 0: return k # keep as exact 0
            return k / 1024 / 1024
    elif unit == '%':
        def scaled(k, r):
            if k == 0: return k # keep as exact 0
            return 100 * k / r
    else:
        raise BadData('did not expect unit {}'.format(unit))

    def rounded(p, o):
        if p == 0: return str(p) # keep as exact 0
        u = next(filter(None, (round(p, d) for d in (None, 0, 1, 2))), p)
        # ReqMem values end in "n" or "c" keep them that way
        return '{}{}{}'.format(u, unit, (o[-1] if o.endswith(('n', 'c')) else ''))

    return tuple(map(rounded, map(scaled, obsK, reqK), obs))

def sumtime(*jobs):
        print('JobID', 'ord', 'stat',
              'Elapsed', 'Timelimit', 'NCPUS',
              'obs', sep = '\t')
        for job in sorted(jobs): sumtime1(job)

def sumtime1(job):
    with Popen(
            # [ 'head', '-n', '40', 'sacct-tim.out' ] or
            # [ 'cat', 'sacct-tim.out' ] or
            [
                'sacct', '--jobs', job,
                '--state=cd',
                '--parsable2', '--noheader',
                '--format', 'jobid,elapsed,timelimit,ncpus'
            ],
            stdin = None,
            stdout = PIPE,
            stderr = None) as proc:
        records = [
            (
                line
                .rstrip(b'\r\n')
                .decode('UTF-8')
                .split('|')
            )
            for line in proc.stdout
            if b'.batch' not in line
            if b'.extern' not in line
            # Elapsed is on all lines
            # TimeLimit is only on those line
        ]

    JOB, ELA, LIM, CPU = range(4)

    for record in records:
        # drop "_<taskid>.batch" from jobid
        record[JOB] = record[JOB].split('_')[0]

    for record in zip(equarts(sorted(r[JOB] for r in records)),
                      range(1, 8),
                      ('Min', 'Min1', 'LoQ',
                       'Med',
                       'HiQ', 'Max1', 'Max'),
                      equarts(sorted(r[ELA] for r in records)),
                      equarts(sorted(r[LIM] for r in records)),
                      equarts(sorted(r[CPU] for r in records)),
                      (len(records) for k in range(1, 8))):
        # elapsed or limited times can be sorted as strings
        # hopefully (not true when they get longer than a
        # day) and sorting constants cannot do no harm
        print(*record, sep = '\t')

def equarts(data):

    '''Five observed quartiles in data, assumed sorted, extended with
    second and second-to-last value - - (: seven quartiles! :)

    '''

    n = len(data)

    return (
        data[0 * (n - 1) // 4],
        data[0 if n < 5 else 1],
        data[1 * (n - 1) // 4],
        data[2 * (n - 1) // 4],
        data[3 * (n - 1) // 4],
        data[(n - 1) if n < 5 else (n  - 2)],
        data[4 * (n - 1) // 4]
    )
