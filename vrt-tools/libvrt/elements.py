'''Generators of groups of lines from an input stream that belong to a
specified type of element, with lines outside that type of element
sent to an output stream or ignored if the output stream is None.

The lines are meant to contain the terminating newline characters.

text = list(next(text_elements(ins, ous)))

'''

from libvrt.args import BadData

def _element(start, end, ins):
    '''Yield the start tag line followed by each line in input stream up
    to and including the next line that .startswith the specified end.

    The start tag line and the end indicators should be bytes objects
    for binary ins, strings for text ins.

    It is very much intended that the end tag is there to be
    encountered. If not, please crash.

    '''
    yield start
    for line in ins:
        yield line
        if line.startswith(end):
            return

    raise BadData('input stream ended before end tag: '
                  + repr(end))

def elements(name, ins, ous):
    '''Yield generators of the lines in input stream that belong to
    elements of the given name, bytes if names is a bytes object, else
    text. Caller must read each group, typically by collecting it into
    a list or a tuple or by otherwise iterating over its lines.

    The lines outside the named element type are sent to the output
    stream, or ignored if the output stream is None.

    '''
    binary = isinstance(name, bytes)
    begin, end = (
        ((b'<' + name + b' ', b'<' + name + b'>'), b'</' + name + b'>')
        if binary else
        (('<' + name + ' ', '<' + name + '>'), '</' + name + '>')
    )

    for line in ins:
        if line.startswith(begin):
            yield _element(line, end, ins)
        elif ous and binary:
            ous.write(line)
        elif ous:
            print(line, end = '', file = ous)
        else:
            pass

def text_elements(ins, ous, *, as_text = False):
    '''Yield generators of the groups of lines in the input stream that
    belong to a text element, for the caller to consume in full. Other
    lines are sent to the output stream, or ignored if the output
    stream is None.

    Both streams should be text streams if as_text is true, byte
    streams otherwise.

    '''
    return elements(('text' if as_text else b'text'),
                    ins,
                    ous)

def paragraph_elements(ins, ous, *, as_text = False):
    return elements(('paragraph' if as_text else b'paragraph'),
                    ins,
                    ous)

def sentence_elements(ins, ous, *, as_text = False):
    return elements(('sentence' if as_text else b'sentence'),
                    ins,
                    ous)
