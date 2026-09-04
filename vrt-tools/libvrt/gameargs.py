# -*- mode: Python; -*-

from argparse import ArgumentParser, ArgumentTypeError, REMAINDER
import os, grp, sys

from libvrt.args import version_args

def parsearguments(argv):
    host = guesshost()

    description = '''

    Send a command to the batch system in Roihu, with all manner of
    defaults, as an array job to be run in the current working
    directory on each argument, without waiting. Array arguments, if
    any, start at '//' on the command line, and one array argument is
    passed to the command in each task.

    By default, module "kieli" is not loaded (does not exist in roihu).

    '''

    parser = version_args(description = description)

    defaults = dict()

    parser.add_argument('command',
                        help = '''

                        the name of an executable command

                        ''')
    parser.add_argument('argument', metavar = '...', nargs = REMAINDER,
                        help = '''

                        the options and initial arguments to the
                        command, optionally followed by '//' followed
                        by a sequence of arguments, each of which is
                        passed to the command as a last argument in an
                        array job (and partitions have limits - but
                        does a "task" mean a task, or does a "task"
                        mean a core, and what is the difference?)

                        ''')
    parser.add_argument('--log', default = 'gamelog', metavar = 'dir',
                        help = '''

                        directory where the standard input and
                        standard output of the batch job are written
                        in files named %%A-%%a-<job>.{out,err} where
                        %%A is the job number and %%a the task number
                        in an array job (log directory is created as
                        needed) (default: ./gamelog)

                        ''')

    parser.add_argument('--job', default = 'game', metavar = 'name',
                        help = '''a short name [game] for the job''')

    parser.add_argument('--out', '-o', metavar = 'file',
                        help = '''

                       standard output from the command on zero exit
                       status; replace any "{}" in the pathname with
                       the actual stem of the input file; on non-zero
                       status, without --accept leave standard output
                       in a sibling file with suffix ".<random>.tmp"

                       ''')
    parser.add_argument('--accept', '-a', action = 'store_true',
                        help = '''

                        (with --out) accept standard output from
                        command regardless of exit status

                        ''')

    # time group - either specify hours or specify minutes (default one
    # hour is probably good for the purpose)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--minutes', '-M', metavar = 'num',
                       dest = 'time', type = minutestype,
                       default = '60',
                       help = 'minutes [60] to reserve')
    group.add_argument('--hours', '-H', metavar = 'num',
                       dest = 'time', type = hourstype,
                       help = 'hours [1] to reserve')

    # memory group - man pages refer to megabytes and gigabytes but
    # example at CSC says 4GB = 4096MB so they must mean 2^20 and 2^30
    # rather than 10^6 and 10^9 https://en.wikipedia.org/wiki/Gibibyte
    # https://research.csc.fi/taito-constructing-a-batch-job-file#3.1.2
    # (defaults are tentative - less might do for the purpose? reduced
    # to 4G now)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--GiB', metavar = 'num',
                       dest = 'memory', type = gibitype,
                       default = '4',
                       help = 'gibibytes [4] to reserve')
    group.add_argument('--MiB', metavar = 'num',
                       dest = 'memory', type = mebitype,
                       help = 'mebibytes [4096] to reserve')

    parser.add_argument('--scratch', '-S', metavar = 'size',
                        type = int,
                        help = '''

                        amount of fast local storage per node, in GB,
                        max 3600, accessed in jobs through the
                        environment variable LOCAL_SCRATCH (may be
                        only allowed/meaningful in Puhti)

                        ''')

    parser.add_argument('--cat', action = 'store_true',
                        help = '''
                        write the job description to standard output
                        instead of sending it to the batch queue
                        (for information only when using temp file)
                        ''')

    if host == 'roihu':
        parser.add_argument('--cores', '-C',
                            choices = [
                                # need to find values that apply
                                # to Roihu - in "test" and "small"
                                # partitions memory and cpus can
                                # be requested separately but is
                                # there any restriction to these
                                # numbers like there was before?
                                # (max is 384 ... absurd for us)
                                '1', '2', '4', '8', '16', '24'
                            ],
                            default = '4', # not sure!
                            help = '''
                            how many Roihu cores to use,
                            all in one node [tentative default is 4]
                            (looks like this *could* be any number
                            up to 384 now, for "small" and "test")
                            ''')
    else: raise HostNotRecognizedError() # not even defined

    # default partition is set just before parsing the arguments;
    # Roihu will default to "small" (1 node, up to 384 cores).
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--test', dest = 'partition',
                       action = 'store_const', const = 'test',
                       help = '''
                       run in "test" partition
                       ''')
    if host == 'roihu':
        defaults['partition'] = 'small'
        group.add_argument('--small', dest = 'partition',
                           action = 'store_const', const = 'small',
                           help = '''
                           run in "small" partition (default)
                           ''')

    else: raise HostNotRecognizedError()

    parser.add_argument('--bill', '-B', metavar = 'group',
                        type = billinggrouptype,
                        default = guessgroup(getgroupnames()),
                        help = '''

                        bill the project associated with the group
                        [defaults to clarin if user is in clarin]

                        ''')

    parser.add_argument('--kieli',
                        choices = [
                            'yes',
                            'out',
                            'err',
                            'null',
                            'no'
                        ],
                        default = 'no',
                        help = '''
                        how to load module kieli
                        (default is no, do not load;
                        yes leaves its stdout and stderr as they are,
                        out redirects stderr to stdout,
                        err stdout to stderr,
                        null both to /dev/null, and
                        no means do not load)
                        ''')

    # add options

    parser.set_defaults(**defaults)
    args = parser.parse_args(argv)
    args.prog = parser.prog
    return args

def billinggrouptype(name):
    groupnames = getgroupnames()
    if name in groupnames:
        return name
    raise ArgumentTypeException('user not in billing group: {}: {}'
                                .format(name, *' '.join(groupnames)))

def minutestype(arg):
    try:
        minutes = int(arg)
        if minutes < 5: raise ValueError('invalid minutes')
        hours, minutes = divmod(minutes, 60)
        time = '{:d}:{:02d}:00'.format(hours, minutes)
        return time
    except ValueError:
        raise ArgumentTypeError('invalid minutes: {}'.format(arg))

def hourstype(arg):
    try:
        hours = int(arg)
        if hours < 1: raise ValueError('invalid hours')
        time = '{:d}:00:00'.format(hours)
        return time
    except ValueError:
        raise ArgumentTypeError('invalid hours: {}'.format(arg))

def mebitype(arg):
    try:
        mebies = int(arg)
        if mebies < 1: raise ValueError('invalid mebibytes')
        return '{}M'.format(arg)
    except ValueError:
        raise ArgumentTypeError('invalid mebibytes: {}'.format(arg))

def gibitype(arg):
    try:
        gibies = int(arg)
        if gibies < 1: raise ValueError('invalid gibibytes')
        return '{}G'.format(arg)
    except ValueError:
        raise ArgumentTypeError('invalid gibibytes: {}'.format(arg))

def checkbill(args):
    if args.bill:
        print('{}: info: billing "{}" project'.format(args.prog, args.bill),
              file = sys.stderr)
    else:
        raise BadData('{}: error: no billing group'.format(args.prog))

def guesshost():
    if os.path.exists('/appl/soft/manual/kielipankki'):
        return 'roihu'

    raise HostNotRecognizedError() # nah

def getgroupnames():
    return [ grp.getgrgid(k).gr_name for k in os.getgroups() ]

def guessgroup(groupnames):
    return ('clarin' if 'clarin' in groupnames else None)
