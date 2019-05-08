# For YLE SV. Adapt for other material.

# tokens(s) = segmentation of a sentence into tokens

import re

def tokens(sentence):
    '''Yield each token in a sentence (a string).'''
    
    for k, part in enumerate(special_token.split(' {} '.format(sentence))):
        if k % 2:
            yield part
        else:
            yield from separate(part)

# Splitting a sentence (a string) into tokens goes by splitting out
# special types of tokens as units first, then separating initial and
# final punctuation from the remaining segments.

special_token = re.compile(R'''

# expect space before and after and leave them out of the match so
# that the resulting segments outside the match still have them

(?<=[ ])

# capture the special token as a group so that it will be included in
# the split

( \d+ (?: [ ]\d+)*  # like: 12 000 and 5 089 000
| [A-ZÅÄÖ]\.        # like: W.
| t\.o\.m\.
| t\.ex\.
| f\.d\.
| s\.k\.
| bl\.a\.
| Bl\.a\.
| p\.g\.a\.
| fr\.o\.m\.
| t\.f\.
| d\.v\.s\.
| dvs\.
| St\.
| st\.
| [Kk]l\.
)

(?=[ ])

''', re.VERBOSE)

general_punctuation = re.compile(R'''

# maximal punctuation sequences with at least one space in them, to
# split out more substantial tokens with their internal punctuation,
# assuming there is an initial and a final space for this to match

# typically just a space, or comma+space, or space+period, rarely
# anything more than that; note the omission of the hyphen! some other
# omissions are unintentional; note underscore _ and asterisk * are
# used for two types of emphases (of names, always?) and occur in
# twos.

(
[,;.!?:"”()_*]*   # up to the first space
[ ]
[,;.!?:"”()_* ]*  # over the subsequent spaces
)

''', re.VERBOSE)

def separate(segment):
    '''Yield each token in a sentence segment (a spaced string) by
    separating initial and final punctuation from each word token.
    This is after special tokens are taken out, like, already.

    '''

    for k, part in enumerate(general_punctuation.split(segment)):
        if k % 2:
            # consume the spaces and yield what remains; should really
            # (but rather rarely) analyze the punctuation further
            # yield from filter(None, part.split())
            for pre in part.split(): yield from stuff(pre)
        else:
            # it may be empty or it may split further (kl.18-17.30)
            for pre in part.split(): yield from pieces(pre)

def stuff(prestuff):
    '''Wee-eep. And mainly separate the two emphasis markers __ and **
    from punctuation marks and from each other.

    How does one even control that all these clauses do what they are
    meant to do? Because diminishing returns.

    '''

    if not prestuff: return # is this possible? who cares?

    # two emphasisers
    if prestuff in ('__**', '**__'):
        yield prestuff[:2]
        yield prestuff[2:]
        return

    # one punctuation character (or ellipsis) after emphasiser
    mo = re.fullmatch(R'(__|\*\*)([.,;:()"”!?]|\.\.\.)', prestuff)
    if mo: yield from mo.groups(); return

    # one punctuation character (or ellipsis) before emphasiser
    mo = re.fullmatch(R'([.,;:()"”!?]|\.\.\.)(__|\*\*)', prestuff)
    if mo: yield from mo.groups(); return

    # two punctuation characters after emphasiser
    mo = re.fullmatch(R'(__|\*\*)([.,;:()"”!?]{2})', prestuff)
    if mo:
        yield mo.group(1)
        yield from mo.group(2)
        return

    # two punctuation characters before emphasiser
    mo = re.fullmatch(R'([.,;:()"”!?]{2})(__|\*\*)', prestuff)
    if mo:
        yield mo.group(1)
        yield from mo.group(2)
        return

    # an emphasiser between two punctuation characters
    mo = re.fullmatch(R'([.,;:()"”!?])(__|\*\*)([.,;:()"”!?])', prestuff)
    if mo: yield from mo.groups(); return

    # made emph-form2.log at this point

    # one punctuation character before two emphasisers (~30 in total)
    mo = re.fullmatch(R'([.,;:()"”!?])(__\*\*|\*\*__)', prestuff)
    if mo:
        yield mo.group(1)
        yield mo.group(2)[:2]
        yield mo.group(2)[2:]
        return

    # made emph-form3.log at this point

    # a handful of relatively unique cases remain (remains, whatever)
    # and then some complex compounds (another handful) and then some
    # junk (another handful) - leave them be (this went too far)

    yield prestuff

def pieces(pretoken):
    '''Yield each "piece" of a pretoken. There may not be any,
    there may be one, there may be more than one.

    A case where there are two is kl.13-14 and its ilk.

    '''

    mo = re.match(R'([Kk]l\.)(\d.*)', pretoken)
    if mo:
        yield mo.group(1)
        yield mo.group(2)
    elif pretoken:
        yield pretoken
    else:
        pass
