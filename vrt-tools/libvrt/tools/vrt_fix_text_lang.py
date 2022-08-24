'''A vrt tool implementation to improve the summary values of sentence
lang attribute in containing paragraph and text elements, assuming
sentence elements are contained in paragraph and text elements,
identified with vrt-id-sentence-lang and then summarized with
vrt-sum-sentene-lang. (Started as a copy of vrt-sum-sentence-class.)

'''

from collections import Counter
from itertools import chain, count
from re import search, findall
from unicodedata import category

from libvrt.args import transput_args, BadData
from libvrt.elements import text_elements
from libvrt.metaline import mapping
from libvrt.dataline import unescape

# hm libvrt.metaname appears to have similar so one is once again
# duplicating one's efforts?
from libvrt.nameargs import nametype, prefixtype, suffixtype

def parsearguments(argv, *, prog = None):

    description = '''

    Improves sentence language annotations from vrt-id-sentence-lang
    using hand-written rules informed by a sample of national library
    data.

    Replaces the values of the input attributes (default "lang" and
    "lang_conf") in each sentence element. To preserve the inputs,
    modify their name with --prefix or --suffix.

    '''

    parser = transput_args(description = description)

    parser.add_argument('--word', metavar = 'name',
                        default = 'word',
                        type = nametype,
                        help = '''

                        word attribute (word)

                        ''')

    parser.add_argument('--lang', metavar = 'name',
                        default = 'lang',
                        type = nametype,
                        help = '''

                        sentence attribute to rewrite (lang)

                        ''')

    parser.add_argument('--conf', metavar = 'name',
                        default = 'lang_conf',
                        type = nametype,
                        help = '''

                        sentence attribute to rewrite (lang_conf)

                        ''')

    parser.add_argument('--prefix', '-p', metavar = 'fix',
                        default = '',
                        type = prefixtype,
                        help = '''

                        prefix to preserve the input attributes
                        (default empty, do not preserve)

                        ''')

    parser.add_argument('--suffix', '-s', metavar = 'fix',
                        default = '',
                        type = suffixtype,
                        help = '''

                        suffix to preserve the input attributes
                        (default empty, do not preserve)

                        ''')

    parser.add_argument('--missing', metavar = 'value',
                        default = b'NSA', # No Such Attribute
                        type = str.encode,
                        help = '''

                        imputed value when sentence does not have the
                        attribute (default NSA, for No Such Attribute)

                        ''')

    # parser.add_argument('--sort', choices = ['value', 'count'],
    #                    default = 'value',
    #                    help = '''
    #
    #                    primary sort key (default is decreasing count,
    #                    break ties by code) [option has no effect]
    #
    #                    ''')

    args = parser.parse_args(argv)
    args.prog = prog or parser.prog
    return args

WORD = None # computed from positional-attributes line in ins

def main(args, ins, ous):
    '''Transput VRT (bytes) in ins to VRT (bytes) in ous.'''

    # make WORD the index of the args.word field
    head = []
    for line in ins:
        head.append(line)
        if not line.startswith(b'<'):
            raise BadData('data line before positional-attributes line')
        if line.startswith(b'<!-- #vrt positional-attributes: '):
            try:
                global WORD
                WORD = line.split(b':')[1].strip().split(b' ').index(args.word)
            except ValueError as exn:
                raise('field name not found: ' + args.word)
            break

    for group in text_elements(chain(head, ins), ous,
                               as_text = False):
        # lines outside any text element are shipped to ous, while
        # lines inside are collected, annotated, then shipped here
        text = list(group)
        rewrite(text, args)
        for line in text:
            ous.write(line)

def rewrite(text, args):
    '''Rewrite sentence lang attributes in text (a list of lines from
    text start tag to text end tag)

    '''

    # regex matches the sentence attribute, captures the value
    observed = args.lang + b'="(.*?)"'
    keeplang = ((args.prefix or args.suffix) and
                (args.prefix + args.lang + args.suffix))

    # get input lang and conf presumably
    # then use Tommi's rules
    # TODO!

    def prev(sentinfo, i):
        '''So prev(si, i) for i = 1, 2, 3, 4 are the four previous sentence
        infos that Tommi's rule refer to (his pre, prepre, pre2, pre3,
        respectively, so the numbering is not the same), and anything
        previous to the first sentence info, infos[0], can be the same
        sentinel object with lang xxx, conf 0.0 (and invalid number
        None that cannot be used to index info).

        '''
        k = sentinfo.number
        return (info[k - i] if k > i else PREV)

    # an Info for each sentence in the text, in order of appearance
    info = tuple(Info(k, s, text, args)
                 for k, s
                 in enumerate(s
                              for s, line
                              in enumerate(text)
                              if line.startswith(b'<sentence ')))

    # rewrite other than 7 most frequent language codes as unknown
    # (currently this is xxx, in future it is meant to be und), also
    # keeping any codes that are tied with the 8th; no that is not
    # right: there may remain fewer than 7 if they are tied with the
    # 8th, no? TODO check carefully against Tommi's code
    langc = Counter(sen.lang for sen in info)
    if len(langc) > 7:
        _, low = langc.most_common()[7]
        for sen in info:
            if langc[sen.lang] <= low:
                sen.lang = b'xxx'

    # that was Rule 1

    for sen in info:

        # first consider current sentence on its own
        if sen.lang == b'xxx':
            pass

        elif (
                sen.alphacharc < 5 # Rule 2
                or sen.alphawordc < 2 # Iteration 10.2, 11 (Training4, rule 3)
                or sen.conf < 0.25 # changed 10.0 (Training5, rule 4)
                or False ):
            sen.lang = b'xxx'

        elif (
                # Training6, rule 5
                (sen.alphawordc < 3 and sen.conf < 2.4) or
                (sen.alphawordc < 4 and sen.conf < 0.9) or
                (sen.alphawordc < 5 and sen.conf < 0.8) or
                (sen.alphawordc < 6 and sen.conf < 0.75) or
                (sen.alphawordc < 7 and sen.conf < 0.65) or
                (sen.alphawordc < 8 and sen.conf < 0.55) or
                (sen.alphawordc < 9 and sen.conf < 0.35) or
                (sen.alphawordc < 11 and sen.conf < 0.3)
                or False ):
            sen.lang = b'xxx'

        elif (
                # Iteration 12, 13, (Training7, rule 6)
                sen.lowerwordc < 1
                and ((sen.alphawordc < 6 and sen.conf < 1.7) or
                     (sen.alphawordc < 7 and sen.conf < 1.4) or
                     (sen.alphawordc < 8 and sen.conf < 1.1) or
                     (sen.alphawordc < 9 and sen.conf < 0.8)
                     or False) ):
            sen.lang = b'xxx'

        elif (
                # (Training8, rule 7)
                (sen.alphatypec < 2) or
                (sen.alphawordc / sen.alphatypec > 2.3 and sen.conf < 1.1)
                or False):
            sen.lang = b'xxx'
        else:
            pass

        # then consider the sentence two steps back in the current
        # context (if there is no such sentence, leave the sentinel
        # object alone as it already has lang xxx)

        prev2 = prev(sen, 2)
        if prev2.lang == b'xxx':
            pass
        elif (
                # Iteration 8, changed 9.3, changed 10.3,. 13, 14 (Training9, rule 8)
                sum(prev2.lang == con.lang
                    for con in (prev(sen, 4),
                                prev(sen, 3),
                                prev(sen, 1),
                                prev(sen, 0))) < 2  # prev(sen, 0) is sen
                and ((prev2.conf < 2.5 and prev2.alphawordc < 3) or
                     (prev2.conf < 1.9 and prev2.alphawordc < 4) or
                     (prev2.conf < 1.6 and prev2.alphawordc < 5) or
                     (prev2.conf < 1.3 and prev2.alphawordc < 6) or
                     (prev2.conf < 1.0 and prev2.alphawordc < 7) or
                     (prev2.conf < 0.9 and prev2.alphawordc < 10) or
                     (prev2.conf < 0.8 and prev2.alphawordc < 13) or
                     (prev2.conf < 0.7 and prev2.alphawordc < 15) or
                     (prev2.conf < 0.6 and prev2.alphawordc < 18) or
                     (prev2.conf < 0.5 and prev2.alphawordc < 21) or
                     (prev2.conf < 0.4)) ):
            prev2.lang = b'xxx'
        else:
            pass

        # then consider *again* the sentence two steps back in the
        # current context (if there is no such sentence, leave the
        # sentinel object alone as it already has lang xxx)

        if prev2.lang == b'xxx':
            pass
        elif (
                # Iteration 9.5, 13, 14, 15, 16, 17, 20 (Training10, rule 9)
                sum(prev2.lang == con.lang
                    for con in (prev(sen, 4),
                                prev(sen, 3),
                                prev(sen, 1),
                                prev(sen, 0))) == 0
                and ((prev2.conf < 3.1 and prev2.alphawordc < 4) or
                     (prev2.conf < 2.2 and prev2.alphawordc < 5) or
                     (prev2.conf < 1.7 and prev2.alphawordc < 6) or
                     (prev2.conf < 1.5 and prev2.alphawordc < 7) or
                     (prev2.conf < 1.4 and prev2.alphawordc < 10) or
                     (prev2.conf < 1.3 and prev2.alphawordc < 12) or
                     (prev2.conf < 1.2 and prev2.alphawordc < 14) or
                     (prev2.conf < 1.1 and prev2.alphawordc < 17) or
                     (prev2.conf < 1.0 and prev2.alphawordc < 22) or
                     (prev2.conf < 0.9 and prev2.alphawordc < 28) or
                     (prev2.conf < 0.8 and prev2.alphawordc < 31) or
                     (prev2.conf < 0.7 and prev2.alphawordc < 34) or
                     (prev2.conf < 0.6 and prev2.alphawordc < 37) or
                     (prev2.conf < 0.5 and prev2.alphawordc < 56)) ):
            prev2.lang = b'xxx'
        else:
            pass

        # Iteration 7.2 - if at last sentence, consider the previous
        # sentence, then the last sentence in the current context

        if sen is info[-1]:
            last0 = prev(sen, 0) # last sentence (aka sen)
            last1 = prev(sen, 1) # last sentence but one, if any (aka what)
            last2 = prev(sen, 2) # last sentence but two
            last3 = prev(sen, 3) # last sentence but three

            # consider last1 (last sentence but one) in current context
            if last1.lang == b'xxx':
                pass
            elif (
                    # second to last added at 11., 14, 15, 18 (Training11, rule 10)
                    sum(last1.lang == con.lang
                        for con in (last3,
                                    prev2,
                                    last0)) == 0
                    and ((last1.conf < 1.2 and last1.alphawordc < 4) or
                         (last1.conf < 1.1 and last1.alphawordc < 5) or
                         (last1.conf < 1.0 and last1.alphawordc < 9) or
                         (last1.conf < 0.8 and last1.alphawordc < 10) or
                         (last1.conf < 0.7 and last1.alphawordc < 11) or
                         (last1.conf < 0.6 and last1.alphawordc < 12) or
                         (last1.conf < 0.3 and last1.alphawordc < 31)) ):
                last1.lang = b'xxx'
            else:
                pass

            # consider last0 (last sentence, aka sen) in current context
            if last0.lang == b'xxx':
                pass
            elif (
                    # last sentence 14, 15, 16, 19, 21, 22 (Training12, rule 11)
                    sum(last0.lang == con.lang
                        for con in (last1,
                                    last2)) == 0
                    and ((last0.conf < 1.5 and last0.alphawordc < 4) or
                         (last0.conf < 1.2 and last0.alphawordc < 5) or
                         (last0.conf < 1.0 and last0.alphawordc < 6) or
                         (last0.conf < 0.8 and last0.alphawordc < 7) or
                         (last0.conf < 0.7 and last0.alphawordc < 8) or
                         (last0.conf < 0.6 and last0.alphawordc < 10) or
                         (last0.conf < 0.5 and last0.alphawordc < 12)) ):
                last0.lang = b'xxx'
            else:
                pass
        else:
            pass

        # back to considering whatever sen was under consideration,
        # which again may or may not be the last in info

        assert prev2 is prev(sen, 2) # just a sanity check, ok

        prev2 = prev(sen, 2)
        prev1 = prev(sen, 1)

        # consider the previous sentence (prev1) in current context
        # (if it has a previous sentence prev2)

        if prev1.lang == b'xxx':
            pass
        elif prev2.number is None:
            pass
        elif (
                # Training13, rule 12
                prev1.alphawordc < 3
                and sum(prev1.lang == con.lang
                        for con in (prev2,
                                    sen)) == 0):
            prev1.lang = b'xxx'
        elif (
                # Training14, rule 13
                sum(sen.lang == con.lang
                    for con in (prev1,
                                prev2)) == 0
                and (2 * prev1.conf < prev2.conf)
                and (2 * prev1.conf < sen.conf) ):
            prev1.lang = b'xxx'

        elif (
                # Sixth iteration rule: (Training15, rule 14)
                sum(con.lang == prev1.lang
                    for con in (prev2,
                                sen)) == 0
                and prev1.lowerwordc == 0 ):
            prev1.lang = b'xxx'

        elif (
                # Iteration 6.2: (Training16, rule 15)
                sum(con.lang == prev1.lang
                    for con in (prev2,
                                sen)) == 0
                and prev1.lang != b'deu'
                and 2 * prev1.lowerwordc <= prev1.upperwordc ):
            prev1.lang = b'xxx'

        else:
            pass
    else:
        # END LOOP (for sen in info)
        pass

    # duplicated at 9.4: (Training 17, repeating rules 8-15)
    # some sort of second pass, twice, second and third pass

    for _ in ('kerran', 'toisen'):
        for sen in info:
            prev4 = prev(sen, 4)
            prev3 = prev(sen, 3)
            prev2 = prev(sen, 2)
            prev1 = prev(sen, 1)

            # Iteration 8, changed 9.3, changed 10.3., 13, 14 (Training9, rule 8)
            if prev2.lang == b'xxx':
                pass
            elif ( sum(prev2.lang == con.lang
                       for con in (prev3, prev1, sen)) < 2
                   and ((prev2.conf < 2.5 and prev2.alphawordc < 3) or
                        (prev2.conf < 1.9 and prev2.alphawordc < 4) or
                        (prev2.conf < 1.6 and prev2.alphawordc < 5) or
                        (prev2.conf < 1.3 and prev2.alphawordc < 6) or
                        (prev2.conf < 1.0 and prev2.alphawordc < 7) or
                        (prev2.conf < 0.9 and prev2.alphawordc < 10) or
                        (prev2.conf < 0.8 and prev2.alphawordc < 13) or
                        (prev2.conf < 0.7 and prev2.alphawordc < 15) or
                        (prev2.conf < 0.6 and prev2.alphawordc < 18) or
                        (prev2.conf < 0.5 and prev2.alphawordc < 21) or
                        (prev2.conf < 0.4)) ):
                prev2.lang = b'xxx'
            else:
                pass

            # Iteration 9.5, 13, 14, 15, 16, 17, 20 (Training10, rule 9)
            if prev2.lang == b'xxx':
                # the following branch could be another branch above,
                # right? because this will be skipped anyway if the
                # above rule took effect, right?
                pass
            elif ( prev3.number is not None
                   and not any(prev2.lang == con.lang
                               for con in (prev4, prev3, prev1, sen))
                   and ((prev2.conf < 3.1 and prev2.alphawordc < 4) or
                        (prev2.conf < 2.2 and prev2.alphawordc < 5) or
                        (prev2.conf < 1.7 and prev2.alphawordc < 6) or
                        (prev2.conf < 1.5 and prev2.alphawordc < 7) or
                        (prev2.conf < 1.4 and prev2.alphawordc < 10) or
                        (prev2.conf < 1.3 and prev2.alphawordc < 12) or
                        (prev2.conf < 1.2 and prev2.alphawordc < 14) or
                        (prev2.conf < 1.1 and prev2.alphawordc < 17) or
                        (prev2.conf < 1.0 and prev2.alphawordc < 22) or
                        (prev2.conf < 0.9 and prev2.alphawordc < 28) or
                        (prev2.conf < 0.8 and prev2.alphawordc < 31) or
                        (prev2.conf < 0.7 and prev2.alphawordc < 34) or
                        (prev2.conf < 0.6 and prev2.alphawordc < 37) or
                        (prev2.conf < 0.5 and prev2.alphawordc < 56)) ):
                prev2.lang = b'xxx'
            else:
                pass

            # Iteration 7.2 (repeat rule on last sentence but one)
            if sen is info[-1]:

                # second to last added at 11., 14, 15, 18 (Training11, rule 10)
                if prev1.lang == b'xxx':
                    pass
                elif (not any(prev1.lang == con.lang
                              for con in (prev3, prev2, sen))
                      and ((prev1.conf < 1.2 and prev1.alphawordc < 4) or
                           (prev1.conf < 1.1 and prev1.alphawordc < 5) or
                           (prev1.conf < 1.0 and prev1.alphawordc < 9) or
                           (prev1.conf < 0.8 and prev1.alphawordc < 10) or
                           (prev1.conf < 0.7 and prev1.alphawordc < 11) or
                           (prev1.conf < 0.6 and prev1.alphawordc < 12) or
                           (prev1.conf < 0.3 and prev1.alphawordc < 31)) ):
                    prev1.lang = b'xxx'
                else:
                    pass

                # last sentence 14, 15, 16, 19, 21, 22 (Training12, rule 11)
                # repeat rule on last sentence
                if sen.lang == b'xxx':
                    pass
                elif (not any(sen.lang == con.lang
                              for con in (prev2, prev1))
                      and ((sen.conf < 1.5 and sen.alphawordc < 4) or
                           (sen.conf < 1.2 and sen.alphawordc < 5) or
                           (sen.conf < 1.0 and sen.alphawordc < 6) or
                           (sen.conf < 0.8 and sen.alphawordc < 7) or
                           (sen.conf < 0.7 and sen.alphawordc < 8) or
                           (sen.conf < 0.6 and sen.alphawordc < 10) or
                           (sen.conf < 0.5 and sen.alphawordc < 12)) ):
                    sen.lang = b'xxx'
                else:
                    pass

                # repeat rule on last sentence but one *again*
                # but now the last sentence may have changed
                if prev1.lang == b'xxx':
                    pass
                elif prev1.number is None:
                    pass
                elif (
                        ((
                            # (Training13, rule 12)
                            prev1.alphawordc < 3
                            and not any(prev1.lang == con.lang
                                        for con in (prev2, sen))) or
                         (
                             # (Training14, rule 13)
                             not any(sen.lang == con.lang
                                     for con in (prev2, prev1))
                             and 2 * prev1.conf < sen.conf
                             and 2 * prev1.conf < prev2.conf) or
                         (
                             # Sixth iteration rule: (Training15, rule 14)
                             not any(con.lang == prev1.lang
                                     for con in (prev2, sen))
                             and prev1.lowerwordc == 0) or
                         (
                             # Iteration 6.2: (Training16, rule 15)
                             not any(con.lang == prev1.lang
                                     for con in (prev2, sen))
                             and prev1.lang != b'deu'
                             and 2 * prev1.lowerwordc <= prev1.upperwordc)) ):
                    prev1.lang = b'xxx'
                else:
                    pass
            else:
                # sen is not last sentence
                pass
        else:
            # one pass of repeat rules done ok
            pass
    else:
        # both passes of repeat rules done ok
        pass

    for sen in info:
        [
            sen.attr[args.prefix + args.lang + args.suffix],
            sen.attr[args.prefix + args.conf + args.suffix]
        ] = [
            sen.attr[args.lang],
            sen.attr[args.conf]
        ]
        [
            sen.attr[args.lang],
            sen.attr[args.conf]
        ] = [
            sen.lang,
            str(sen.conf).encode('UTF-8')
        ]
        # not bothering to check what line termination characters the
        # input line had? mainly it could have been CR LF or could it?
        # but the dict items themselves are either already escaped in
        # the input or do not need any escaping (lang and conf values)
        # print(sen.attr)
        text[sen._start] = b''.join((b'<sentence ',
                                     b' '.join((k + b'="' + v + b'"'
                                                for k, v in sorted(sen.attr.items()))),
                                     b'>\n'))

# shouldn't this be in some library already? is this even used here?
def renderstart(name, meta):
    '''Render start tag line for the element name (paragraph or text) and
    the meta dict (values already rendered).

    '''
    return b''.join((b'<', name,
                     *(b' ' + key + b'="' + value + b'"'
                       for key, value in sorted(meta.items())),
                     b'>\n'))

class Info(object):
    '''Information on a sentence in a text, used by Tommi's rules
    to rewrite some lang attributes.

    '''

    def __init__(self, number, start, text, args):
        self._number = number
        self._start = start
        self._text = text
        self._args = args
        self._attr = None
        self._lang = None
        self._conf = None
        self._words = None
        self._mean = None
        self._acc = None # number of alphabetic characters
        self._awc = None # number of words with alphabetics
        self._atc = None # number of types with alphabetics
        self._uwc = None # number of uppercase-initiated words
        return

    @property
    def number(self):
        return self._number

    @property
    def attr(self):
        '''Modify self.attr at end before rendering the final attributes.
        Until then, access self.lang and self.conf, q.v., during this
        rewriting process.

        '''
        if self._attr is None:
            # must parse in "text" form
            # is this in some library?
            # this should be in some library!
            # but libvrt/metaline.py is for binary lines
            self._attr = dict(findall(br'(\S+)="([^""]*)"',
                                      self._text[self._start]))
            pass
        return self._attr

    @property
    def words(self):
        if self._words is None:
            self._words = tuple(self._scan())
            # print('words:', self._words)
            pass
        return self._words

    def _scan(self):
        for k in count(self._start):
            line = self._text[k]
            if line.startswith(b'</sentence>'):
                return
            if line.startswith(b'<'):
                continue
            record = line.rstrip(b'\r\n').split(b'\t')
            for word in record[WORD].split(b' '):
                # print('word:', word) # DEBUG
                # split each "word" at any spaces, following Tommi's Java code
                if not word: continue
                yield unescape(word).decode('UTF-8')

    @property
    def lang(self):
        if self._lang is None:
            # expect args to be at self._args, yes?
            self._lang = self.attr[self._args.lang]
            pass
        return self._lang

    @lang.setter
    def lang(self, value):
        '''lang and conf are the rewritten attributes'''
        self._lang = value
        return

    @property
    def conf(self):
        if self._conf is None:
            self._conf = float(self.attr[self._args.conf])
            pass
        return self._conf

    @conf.setter
    def conf(self, value):
        '''lang and conf are the rewritten attributes'''
        self._conf = value
        return

    @property
    def wordc(self):
        '''Count words'''
        return len(self.words)

    @property
    def alphacharc(self):
        '''Count alphabetic characters'''
        if self._acc is None:
            # why are modifiers counted as alphabetics?
            self._acc = sum(category(char).startswith(('L', 'M'))
                            for word in self.words
                            for char in word)
            pass
        return self._acc

    @property
    def alphawordc(self):
        '''Count words with any alphabetic characters in them'''
        if self._awc is None:
            # why are modifiers counted as alphabetics?
            self._awc = sum(any(category(char).startswith(('L', 'M'))
                                for char in word)
                            for word in self.words)
            pass
        return self._awc

    @property
    def alphatypec(self):
        '''Count word types with any alphabetic characters in them'''
        if self._atc is None:
            self._atc = len(set(word
                                for word in self.words
                                if any(category(char).startswith(('L', 'M'))
                                       for char in word)))
            pass
        return self._atc

    @property
    def upperwordc(self):
        '''Count words with letters in them and first letter in upper case'''
        if self._uwc is None:
            self._uwc = sum(next((char
                                  for char in word
                                  if category(char).startswith(('L', 'M'))),
                                 '_') == 'Lu'
                            for word in self.words)
            pass
        return self._uwc

    @property
    def lowerwordc(self):
        '''Count other words with letters in them'''
        return self.alphawordc - self.upperwordc

    @property
    def meanwordlen(self):
        '''Mean word length over all tokens'''
        return sum(map(len, self.words)) / len(self.words)

class Prev(object):
    '''A sentinel object nominally before any sentence'''
    def __init__(self):
        pass

    @property
    def number(self):
        '''Not a valid index. (In Python, -1 would be valid! But None is not a
        valid index.)

        '''
        return None

    @property
    def lang(self):
        return b'xxx'

    @property
    def conf(self):
        return 0.0

PREV = Prev()
