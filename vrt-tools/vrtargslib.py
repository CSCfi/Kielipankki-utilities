'''Common interface to vrt tools, including a common version number.'''

from libvrt.bad import BadData, BadCode

# This is the common version number for vrt-tools
from libvrt.args import VERSION

# These initialize an argument parser with just --version, or with
# various input-stream/output-stream options
from libvrt.args import version_args
from libvrt.args import transput_args as trans_args

# transput(args, main) => main(args, ins, ous)
# where ins, ous are input/output streams as
# specified by args, by default decoding and
# encoding UTF-8 but can be requested binary
from libvrt.args import transput as trans_main
