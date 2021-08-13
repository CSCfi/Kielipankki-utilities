# Support for various check tools,
# to provide uniform output format.

import sys

_binary = None
_output_stream = None

def setup_binary(ous):
    global _binary, _output_stream
    _binary = True
    _output_stream = ous
    ous.write(b'\t'.join((b'line', b'level', b'kind', b'what')))
    ous.write(b'\n')

def setup_text(ous):
    global _binary, _output_stream
    _binary = False
    _output_stream = ous
    print('line', 'level', 'kind', 'what',
          sep = '\t',
          file = ous)

def _message(k, level, kind, what):
    if _output_stream is None:
        raise Exception('libvrt.check: output stream not set')

    if _binary:
        _output_stream.write(b'\t'.join((str(k).encode('UTF-8'),
                                         level, kind, what)))
    else:
        print(k, level, kind, what, sep = '\t',
              file = _output_stream)

def error(k, kind, what):
    _message(k, (b'error' if _binary else 'error'), kind, what)

def warn(k, kind, what):
    _message(k, (b'warning' if _binary else 'warning'), kind, what)

def info(k, kind, what):
    _message(k, (b'info' if _binary else 'info'), kind, what)
