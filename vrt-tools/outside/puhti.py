# For ../outsidelib.py if it seems to be used in puhti.
# Provides paths to underlying components of vrt tools
# in the form expected by those specific vrt tools.

import os
from .fixenv import prebins, prelibs, utf8ish

# where kielipankki software modules are installed
LINGDIR = '/appl/soft/ling'

# where tdp "alpha" components are installed on a temporary basis
VARPUNENDIR = '/projappl/clarin/varpunen'

# tdp "alpha" omorfi transducer
ALOMORFI = (
    os.path.join(VARPUNENDIR, 'models',
                 'morphology.finntreebank.hfstol')
)

# tdp "alpha" marmot command
ALMARMOTCMD = [
    'java', '-cp',
    os.path.join(VARPUNENDIR, 'marmot-2014-10-22.jar'),
    'marmot.morph.cmd.Annotator',
    '--model-file',
    os.path.join(VARPUNENDIR, 'models', 'fin_model.marmot'),
    '--test-file', 'form-index=0,token-feature-index=1,/dev/stdin',
    '--pred-file', '/dev/stdout'
]

# tdp "alpha" parser command (sans -out pipename)
ALPARSERCMD = [
    # The underlying thing is known variously as "mate tools" (though
    # mate tools consist of other things, too), "anna" (for whatever
    # motivation, nowhere to be found), apparently "is2", and "the
    # parser" and certain other locutions that describe or praise the
    # parser.
    'java', '-cp',
    os.path.join(VARPUNENDIR, 'mate-tools/anna-3-1.jar'),
    'is2.parser.Parser',
    '-model',
    os.path.join(VARPUNENDIR, 'models', 'parser.model'),
    '-test', '/dev/stdin'

    # extend with [ '-out', pipename ] at the point of Popen,
    # when a named-pipe name is at hand, because this version
    # of this thing writes its *diagnostics* in its stdout
]

UDPIPE = os.path.join(LINGDIR, 'udpipe/1.2.0/bin/udpipe')

UDPIPEMODEL = (
    os.path.join(LINGDIR,
                 'udpipe/models/udpipe-ud-2.3-181115',
                 '{}-ud-2.3-181115.udpipe')
)

# certain scripts need HFSTBIN in PATH, and they need to work on
# certain servers that do not have HFSTBIN in PATH; and then those
# binaries need HFSTLIB in LD_LIBRARY_PATH, of course; and certain
# scripts may rely on input/output streams being in a UTF-8 locale
HFSTBIN = os.path.join(LINGDIR, 'hfst/3.15.0/bin')
HFSTLIB = os.path.join(LINGDIR, 'hfst/3.15.0/lib')
HFSTENV = dict(os.environ,
               PATH = prebins(HFSTBIN),
               LD_LIBRARY_PATH = prelibs(HFSTLIB),
               LC_ALL = utf8ish(),
               PYTHONIOENCODING = 'UTF-8')

OMORFITOKENIZER = (
    # pending version number component: 1.3.2, 1.4.0, ...
    os.path.join(LINGDIR,
                 'finnish-tagtools/{}/share/finnish-tagtools',
                 'omorfi_tokenize.pmatch')
)

FINERCMD = (
    # pending version number component: 1.3.2, 1.4.0, ...
    os.path.join(LINGDIR, 'finnish-tagtools/{}/bin',
                 'finnish-nertag')
)

FINPOSCMD =  (
    # pending version number component: 1.3.2, 1.4.0, ...
    os.path.join(LINGDIR, 'finnish-tagtools/{}/bin',
                 'finnish-postag')
)

HUNPOSTAG = os.path.join(LINGDIR, 'hunpos/1.0/bin/hunpos-tag')

SPARVDIR = os.path.join(LINGDIR, 'sparv_pipeline/2.0_MIT_2017-10-23')

HUNPOSMODELS = dict(
    sparv = os.path.join(SPARVDIR, 'models',
                         'hunpos.suc3.suc-tags.default-setting.utf8.model'),
)

MALTPARSER = os.path.join(SPARVDIR, 'jars', 'maltparser-1.7.2.jar')
SWEMALTDIR = os.path.join(SPARVDIR, 'models')
SWEMALTMODEL = 'swemalt-1.7.2'

CSTLEMMA = os.path.join(SPARVDIR, 'bin', 'cstlemma')

CSTLEMMAMODELS = dict(
    # model options: variants of dictionary (*.dict) and rules (*.flex)
    saldo = [
        '-d', os.path.join(SPARVDIR, 'models', 'saldo.cstlemma.dict'),
        '-f', os.path.join(SPARVDIR, 'models', 'saldo.cstlemma.flex'),
    ],
    suc = [
        '-d', os.path.join(SPARVDIR, 'models', 'suc.cstlemma.dict'),
        '-f', os.path.join(SPARVDIR, 'models', 'suc.cstlemma.flex'),
    ],
    sucsaldo = [
        '-d', os.path.join(SPARVDIR, 'models', 'suc-saldo.cstlemma.dict'),
        '-f', os.path.join(SPARVDIR, 'models', 'suc-saldo.cstlemma.flex'),
    ]
)
