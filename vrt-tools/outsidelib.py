import os, sys

# all this to find out a workable locale
from subprocess import Popen, PIPE, TimeoutExpired

MARMOTJAR = '/proj/kieli/varpunen/marmot-2014-10-22.jar'

MARMOTMODEL = '/proj/kieli/varpunen/models/fin_model.marmot'

UDPIPE = '/appl/ling/udpipe/1.2.0/bin/udpipe'

UDPIPEMODEL = (
    '/appl/ling/udpipe/models/udpipe-ud-2.3-181115/{}-ud-2.3-181115.udpipe'
)

# certain scripts need HFSTBIN in PATH, and they need to work on
# certain servers that do not have HFSTBIN in PATH; and then those
# binaries need HFSTLIB in LD_LIBRARY_PATH, of course
HFSTBIN = '/appl/ling/hfst/3.15.0/bin'
HFSTLIB = '/appl/ling/hfst/3.15.0/lib'

# no longer using HFSTTOKENIZE? but find it in HFSTBIN?
HFSTTOKENIZE = '/appl/ling/hfst/3.15.0/bin/hfst-tokenize'
OMORFITOKENIZE = (
    '/appl/ling/finnish-tagtools/1.3.2/share/finnish-tagtools'
    '/omorfi_tokenize.pmatch'
)

FINER = (
    '/appl/ling/finnish-tagtools/1.3.2/bin/finnish-nertag'
)

FINPOS =  (
    '/appl/ling/finnish-tagtools/1.3.2/bin/finnish-postag'
)

def prebins(*paths):
    '''Return the string where paths are prepended to PATH.'''
    return ':'.join(paths +
                    tuple(path
                          for path
                          in os.environ['PATH'].split(':')
                          if path))

def prelibs(*paths):
    '''Return the string were paths are prepended to LD_LIBRARY_PATH.'''
    return ':'.join(paths +
                    tuple(path
                          for path
                          in os.environ.get('LD_LIBRARY_PATH', '').split(':')
                          if path))

def utf8ish():
    '''Guess and return a locale string, like en_US.UTF-8, fi_FI.UTF-8,
    C.UTF-8, that at least seems to be available on the platform and
    may be able to deal with UTF-8 to the extent that even Python is
    willing to assume UTF-8 rather than ASCII as a default file
    encoding.

    '''

    LANG = os.environ.get('LANG', '')
    if 'UTF-8' in LANG: return LANG

    ask = Popen(['locale', '-a'],
                stdout = PIPE,
                universal_newlines = True)
    try:
        response, _ = ask.communicate(timeout = 20)
    except TimeoutExpired:
        print('cannot find available locales (LANG={})'
              .format(LANG),
              file = sys.stderr)
        raise

    try:
        ask.terminate()
    except ProcessLookupError:
        pass

    for lang in ('en_US.UTF-8', 'en_GB.UTF-8',
                 'fi_FI.UTF-8',
                 'C.UTF-8'):
        if lang in response:
            return lang

    print('no preferred UTF-8 locale detected (LANG={})'
          .format(LANG),
          file = sys.stderr)
    
    for lang in response.split('\n'):
        if 'UTF-8' in lang:
            print('selecting {} from:'.format(lang),
                  response,
                  sep = '\n',
                  file = sys.stderr)
            return lang

    print('no UTF-8 locale detected:',
          response,
          sep = '\n',
          file = sys.stderr)

    raise Exception('cannot proceed without UTF-8')
