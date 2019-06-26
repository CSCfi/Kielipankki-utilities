# For YLE SV material, meant to be adaptable to other materials.
# sane(s, *, asis) = low-level sanification
# delink(s, *, info)
# splitby(s) = separation of a multiparagraph (or paragraph) and a byline
# ??normalspaced(s) = normalization of whitespace

import html, re, sys

# such rare incidences as were actually observed in the text
broken_markup_remains = re.compile(R'''
<em>
| </em>
| <strong>
| </strong>
| </a>        # some source attribute - also <a href=...> but leave that
| /nobr>
| b>
| p>
| >P>
''', re.VERBOSE)

# such rare but actually observed control characters as should not be
# there at all - not at all sure what they were meant to be or how
# they came to be there, either - and the couple of "angle brackets"
# that seem to occur as remnants of some markup about as often as in
# some creative ASCII-art construction: sigh - too expensive oh
# nupdate these control codes are Microsoft character codes encoded in
# UTF-8 instead of translated to the intended Unicode points first.

character_encoding = str.maketrans({
    
    # U+0091, U+0092 probably meant to be U+2018, U+2019 but make both U+0027
    # according to the advice that both should look the same in ... Finnish?
    # but this is Swedish ... and also that the latter (either way) can also
    # occur as an apostrophe

    '\u0002' : '', # STX
    '\u0008' : '', # BS (sic)
    '\u007f' : "'", # DEL -> '
    '\u0080' : '\u20ac', # -> EURO SIGN
    '\u008f' : '', # SS3 (Single Shift Three)
    '\u0090' : '', # DCS (Device Control String)
    '\u0091' : "'", # PRIVATE USE ONE -> left single quotation mark (U+2018)
    '\u0092' : "'", # PRIVATE USE TWO -> right single quotation mark (U+2019)
    '\u0093' : '"', # -> left double quotation mark (U+201C)
    '\u0094' : '"', # CANCEL CHARACTER -> right double quotation mark (U+201D)
    '\u0095' : '\u2022', # MESSAGE WAITING -> bullet
    '\u0096' : '-', # -> en dash (U+2013)
    '\u0097' : '-', # -> em dash (U+2014)
    '\u009a' : '\u0161', # SINGLE CHARACTER INTRODUCER to s caron (Windows 1252)
    '\u009e' : '\u017e', # PRIVACY MESSAGE to z caron (Windows 1252)

    # private use characters
    '\uf02d' : '',
    '\uf04a' : '',
    '\uf0bd' : '',
})

last_angles = str.maketrans({
    '<' : ' ',      # still in <3
    '>' : ' ',      # still in => -> >> and > (some clearly wrong?)
})

def sane(text, *, asis = False):
    '''Undo XML character entities (there are a few), remove other
    remnants of XML markup (a few half-tags and such), eliminate
    garbage characters (random control characters? not many).

    There are _both_ raw ampersands and ampersands as entities. When
    an irrestible force meets an immovable object, something's gotta
    give.

    '''

    # early return option in case there is need to observe insane text
    # for debugging, probably in combination with args.parainfo to
    # observe just the phenomena that are being sanitized right here
    
    if asis: return text

    text = text.translate(character_encoding)

    # Note: &mdash; becomes U+2014 EM DASH; it is used to introduce
    # some bylines(?) at end of a paragraph

    text = html.unescape(text)

    text = broken_markup_remains.sub(' ', text)
    text = text.translate(last_angles)

    return text

# se [denna exempelsida](http://example.com); => se denna sida;
# pattern captures full match and the replacement text

delink_pattern = re.compile(R'''
( \[ ( [^\[\]]+ ) \] \( [^\(\)]+ \) )
''', re.VERBOSE)

def delink(text, *, info = False):
    '''Replace every [text](link) in text with just text. Used before
    actual tokenization to remove highly non-linguistic material that
    does not even appear to an ordinary reader.

    '''

    if info:
        first = True
        for full, keep in delink_pattern.findall(text):
            if first:
                print('----', file = sys.stderr)
                first = False
            print(keep, '<=', full, file = sys.stderr)

    retext = delink_pattern.sub(r'\2', text)

    # to see the full effect on the whole text - much output
    # if text != retext:
    #    print('----', file = sys.stderr)
    #    print(repr(text), file = sys.stderr)
    #    print('->', file = sys.stderr)
    #    print(repr(retext), file = sys.stderr)

    return retext

# splitby(text) to split away a paragraph-final "byline" (if that be
# what it is called), rather heuristically tailored to what is
# observed, because such an element is not properly an element of the
# last sentence but at best of the paragraph as a whole - probably
# ship them as a kind of sentence? or leave them out? decide later.
# Decided to ship them as another paragraph. May be more proper
# anyway, and is not worth the hassle not to anyway.

byparentheses = re.compile(R'''

# Like one of these at the very end of a multiparagraph:
#
# (Av Maria von Kraemer)
# (Av Susanne Nylund-Torp)
# (Av Rabbe Nilsson)
# (Av Åboland)
# (Av intfree01)
#
# But there are also such as use a hyphen or an em-dash :(
# There may or may not be whitespace just before the byline.
# Or anything!

[(]
Av
(?: [ ] \w+ (?: -\w+)? ) {1,3}
[)]
$

''', re.VERBOSE)

def splitby(text):
    '''Return actual text (a possibly empty multi-paragraph) together with
    a byline paragraph (as a string) split off at the end.

    '''

    mo = byparentheses.search(text)
    if mo:
        text = mo.string[:mo.start()].rstrip()
        by = mo.group()
        return text, by # [ (dict(type = 'by'), by.split()) ]
    
    return text, ''
