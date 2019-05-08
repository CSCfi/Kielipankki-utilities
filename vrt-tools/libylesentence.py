# For YLE SV material, meant to be adaptable to other materials.

# ?normalspaced(s) = normalization of whitespace
# sentences(s) = segmentation of a paragraph into sentences

import re

def sentences(para, *, info = False):
    '''Partition an assumed paragraph (a string) into heuristically
    somewhat sentence-like parts. This will fail, but hopefully not
    often, and then some of the time the failure is due to the failure
    of the assumption that the input is a paragraph, which is not a
    failure of this function at all. Garbage in, garbage out.

    Assume all internal whitespace is normalized to one space already!
    And initial and final whitespace is normalized away.

    Though *some* internal newlines may have been meaningful and are
    gone at this stage. This would need investigation. Expensive.

    '''

    # note: .finditer returns match objects
    ends = [ end
             for end in sentence_boundary.finditer(para)
             if not isbad(end) ]
    
    # each end is a match of a tail of a non-final sentence of the
    # paragraph

    if info: logsegments(para, ends)
        
    # Yield each sentence that ends at an end
    for k, end in enumerate(ends):
        yield para[ends[k - 1].end() if k else 0:end.end()]

    # Yield the sentence that does not end at an end
    # - but should check that the para is not empty!
    if ends:
        yield para[ends[-1].end():]
    else:
        yield para

def logsegments(para, ends):
    for k, end in enumerate(ends):
        b = ends[k - 1].end() if k else 0
        m = end.start()
        e = end.end()
        head = para[b:m]
        tail = para[m:e]
        print('## ', head, '|', sep = '')
        print('## ', tail, '||', sep = '')
    else:
        if ends:
            r = ends[-1].end()
            rest = para[r:]
            print('## ', rest, '||', sep = '')
        else:
            print('## ', para, '||', sep = '')
    print('##')

sentence_boundary = re.compile(R'''
# One or more of .?! optionally followed by any ")
# then space
# then optionally any "( then an alpanumeric not in lower case.
# Is that good enough?
# Not quite - preceding part must also be somewhat substantial.
# Maybe following too? And it must not be Mr. Etc that is split.
#
# Oops, forgot - (hyphen, when outside a word) - added.
# Also, might there be some way to make use of newlines within
# paragraphs in this corpus? (Ouch. No!)

# Make the pattern match a tail of a sentence, with a lookahead that
# matches a possible head of the following sentence. Further filtering
# can be implemented by testing what the tail is, and what actually
# precedes and follows it in the paragraph.

\S+ [ ")]* [.?!]+ [ ")]*

[ ]

(?= [-(" ]* [A-ZÅÄÖ0-9] )

# Should add the other quotation mark. - What about colons? No!
# Also those __ and **.

''', re.VERBOSE)

# Sentence_boundary matches "W. " in "George W. Bush" but there is
# no sentence boundary there. Approximately?

initial_letter = re.compile('[A-ZÅÄÖ][.] ')

def isbad(mo):
    '''Return true if a candidate sentence-boundary match object is a
    bad-looking boundary after all.

    '''

    data, tail, m, e,  = mo.string, mo.group(), mo.start(), mo.end()

    # those trailing spaces are a bit of a subtlety
    if tail in { 't.ex. ', 'bl.a. ', 'Bl.a. ', 's.k. ', 'f.d. ',
                 'p.g.a. ', 'fr.o.m. ',
                 'St. ',
                 'kl. ', 'Kl. ', }:
        return True

    if initial_letter.fullmatch(tail):
        # should also look at what follows?
        return True

    # could let it fall through for the lulz and default to None
    return False
