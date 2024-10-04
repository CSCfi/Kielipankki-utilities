#! /usr/bin/env python3
# -*- mode: Python; -*-

'''A preprocessor to prevent vrt-finnish-nertag from attempting
certain types of sentence that the underlying finnish-nertag
empirically cannot handle. If such a pattern is detected in the token
sequence, the string "finnish-nertag" is inserted in the set-valued
sentence attribute _skip.

Developed in connection with name-tagging Suomi24 to protect against
patterns that were actually found (finnish-nertag version was 1.6) to
cause problems in the form of excessive time or sometimes excessive
memory consumption, and _#_ as a token turned out be skipped?

'''

from argparse import ArgumentTypeError
from itertools import chain, islice # , groupby
import re, sys

from libvrt.args import transput_args
from libvrt.elements import sentence_elements
from libvrt.nameargs import nametype
from libvrt.nameline import isnameline, parsenameline
from libvrt.bad import BadData, BadCode
from libvrt.dataline import record, unescape
from libvrt.metaline import element, mapping, starttag

def parsearguments(argv):

    description = '''

    Mark with sentence attribute _skip="|finnish-nertag|" such
    sentences whose token patterns are empirically too hard for
    finnish-nertag (at version 1.6) to handle gracefully. To be used
    before vrt-finnish-nertag.

    '''
    parser = transput_args(description = description)

    parser.add_argument('--word', '-w', metavar = 'name',
                        default = 'word',
                        type = nametype,
                        help = '''

                        input field name [word]

                        ''')

    args = parser.parse_args(argv)
    args.prog = parser.prog
    return args

def main(args, ins, ous):

    # set WORD to word field index (or raise BadData)
    # expecting positional-attributes line near top
    # (do we not have this in some library already?)
    head = list(islice(ins, 100))
    for line in head:
        if not isnameline(line): continue
        WORD = (
            parsenameline(line, required = { args.word })
            .index(args.word)
        )
        break
    else:
        raise BadData('positional attribute names not found')

    for k, sentence in enumerate(sentence_elements(chain(head, ins), ous)):
        ship_sentence(list(sentence), WORD, ous)

def ship_sentence(lines, WORD, ous):
    '''Ship sentence start tag with _skip="|finnish-nertag|" if any
    relevant issue is detected in text (add or extend the attribute as
    needed), else ship tag as is. Ship remaining sentence lines as
    they are.

    '''

    start = lines[0]

    # extract sentence contents as space-delimited tokens in UTF-8 for
    # convenient pattern matching; ignore any meta lines, if any (and
    # there are always at least two such)
    text = (
        b' '.join(chain([b''],
                        (
                            unescape(record(line)[WORD])
                            for line in lines
                            if not line.startswith(b'<')
                        ),
                        [b'']))
        .decode('UTF-8')
    )

    skip_this_sentence = bool(
        # Long (or even somewhat long) sequences of tokens in all
        # caps, or even just capitalized words, in a sentence take
        # unreasonable time; these are typically trollish messages,
        # often but not always repeating the same word, typically
        # excessively many times and the message is usually also
        # repeated.
        #
        # Was looking for 10 in a row too harsh? Is looking for 20 in
        # a row too lenient?. Not allowing any punctuation at all is
        # too lenient. It does happen that the capitalized token is
        # just one capital letter, like T H I S, or also D D D D ...
        #
        # Blocking 12-long sequences of all-caps words, possibly with
        # trailing punctuation, but for the moment only all-caps, not
        # just initial capital. Hard to be sure whether this is rather
        # reckless or, contrarywise, excessively careful. (There were
        # longer sequences of all caps but broken by commas.)
        #
        # The forward slash is included in the relevant tokens mainly
        # because it occurs i our own redaction of excessively long
        # tokens.
        #
        # One did not expect exclamation marks _inside_ a "word" but
        # that actually happens, at least when a short "sentence" is
        # repeated without a space at the end of that sentence.
        #
        # TODO consider other punctuation.
        #
        # TODO consider detecting first capital letter further in.
        #
        # This blocks lists of actual names, which is unfortunate, but
        # then a list of names is not a name, so what can one do. And
        # trollish repetition of a name has been observed.
        re.search('( [A-ZÅÄÖ][A-ZÅÄÖa-zåäö\-/]*){20,20} ', text) or
        re.search('( [A-ZÅÄÖ][A-ZÅÄÖ\-!?]*){12,12} ', text) or

        # Sequences of tokens that start with a letter and end in
        # digits have been observed (in failing sentences) as
        # statistics (of a game character levels, of newsgroup
        # activities), as configuration files, and apparently as
        # assignment statements (possibly the same thing as config),
        # with various punctuation (game character levels also without
        # any separation). Also, a sequence of "species,count"
        # resulted from the inexplicable omission of the space after
        # comma in a list that actually goes "count species".
        #
        # Added hyphen to the pattern upon encounter with an installed
        # package list where sufficiently many had version numbers in
        # a row that the sentence would have been caught here. (Yes,
        # excessive time consumption.)
        #
        # Added TX and RX as possible word forms: no digits in them
        # but they cut more than one such net traffic report in pieces
        # so short that the pattern did not match any part. Presumably
        # because they are in caps. (Trying to be careful here.)
        #
        # Pattern is somewhat rare but may occur repeatedly when it
        # occurs. Pattern could also start with a digit, as in an
        # instance that was a list of Bible verses but included at
        # least ten in a row that started with a letter.
        #
        # Also, such sequence of length 8 was observed to cause
        # trouble, hence the shortening of the pattern from 10 to 8)
        #
        # (Added # and / to the pattern because of a few sequences of
        # alternating URI-with-digits-at-end and #comment-digits. Not
        # a nice solution, these are already increasing particular.)
        #
        # Added initial & and internal [] upon encountering, in 2015,
        # a sequence of &gameselect[]=DIGITS which also would have
        # been caught with just the initial & except some of those
        # were separated as their own tokens. Will this ever repeat?
        re.search('( [A-ZÅÄÖa-zåäö#&/][A-ZÅÄÖa-zåäö0-9/,.:!=\-\[\]]*[0-9]| TX| RX){8,8} ', text) or

        # Sequences of URIs have led to excessive consumption. This is
        # blocking rather short such. (Was this the case where memory
        # consumption went through the roof? Or was this just time?)
        re.search('( (http|https|ftp)://\S+){5,5} ', text) or

        # A long sequences of /REDACTED/ tokens was observed to cause
        # problems where the originally repeated over-long token
        # probably would not have contained capital letters at all.
        # (The token actually ends in digits, which may the issue.)
        # (But should be no harm in blocking /REDACTED/ sequences.)
        re.search('( \S*/REDACTED/\S*){10,10} ', text) or

        # finnish-nertag (version 1.6, --no-tokenize) eats _#_
        # altogether, which must be considered a bug in the tool
        ' _#_ ' in text
    )

    if skip_this_sentence:
        name = element(start)
        attributes = mapping(start)
        if b'_skip' in attributes:
            if b'|finnish-nertag|' in attributes[b'_skip']:
                pass
            else:
                attributes[b'_skip'] += b'finnish-nertag|'
        else:
            attributes[b'_skip'] = b'|finnish-nertag|'
        start = starttag(name, attributes)

    ous.write(start)
    for k, line in enumerate(lines):
        if k == 0: continue
        ous.write(line)
