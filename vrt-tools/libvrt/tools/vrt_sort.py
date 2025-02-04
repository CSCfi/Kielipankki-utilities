
"""
vrt_sort.py

The actual implementation of vrt-sort.

Sort text structures within VRT input by creating a sort key from text
attribute values and using the Unix sort command to sort according to the key.

The script uses the GNU/Unix "sort" command to do the actual sorting
and "cut" to remove the sort key. The script reads the input and
writes a temporary file with the keys and text start and end offsets,
sorts the offset file and then reads the original input (or its
temporary copy if the input is not seekable) using random access in
the order of the sorted offset file and writes to output.

Please run "vrt-sort -h" for more information.
"""


# TODO (if deemed useful):
# - Transformations with access to all key attributes as a dict
#   (transformation attribute label "*"), either modifying one or more
#   of the key attribute values or producing a separate key value
# - Recognize some way to keep comments with the first text, so that
#   they are not grouped with the comments at the beginning of the
#   input, such as a separating empty comment or something like that
# - Allow sorting e.g. paragraphs or sentences within texts
# - Take the sort order from the attributes of a corpus (as
#   vrt-sort-texts.sh --order-from-corpus does)
# - Allow specifying character start and end positions in sort keys
# - Add option --show-transforms to only show the transformations and
#   their function definitions for each attribute, without actually
#   processing the input.


import os
import re
import sys

from collections import defaultdict
from subprocess import Popen, PIPE, TimeoutExpired
from tempfile import NamedTemporaryFile
from time import sleep

from vrtargsoolib import InputProcessor


class VrtSorter(InputProcessor):

    """Sort text structures within VRT input."""

    DESCRIPTION = """
    Sort text structures within the input VRT according to the values
    of given attributes.

    Comments and tags before the first <text> tag in the input are
    preserved at the top of the output and those after the last
    </text> tag at the end, so the input may have a structure spanning
    the whole input containing the text structures, but it should not
    have structures spanning multiple texts but not all of them.
    """
    ARGSPECS = [
        ('--key|attribute = attrlist',
         '''Use attributes listed in attrlist (separated by spaces or
            commas) as the sort keys: sort primarily by the first
            attribute, secondarily by the second and so on. Multiple
            keys can also be specified by repeating the option. Each
            attribute name may be followed by a colon and sort
            ordering option characters recognized by the "sort"
            command: often one or more of the following: b (ignore
            leading blanks), d (dictionary order), f (ignore case), g
            (general numeric sort), i (ignore nonprinting), M (month
            sort), h (human numeric sort), R (random sort), r
            (reverse), V (version sort).''',
         {'required': True,
          'action': 'append'}),
        ('--transform = attrname',
         '''Transform the value of the attribute attrname using code
            before using it as a sort key. attrname is one of the
            attributes listed in the argument of --key. (attrname and
            the colon may be omitted if only one key attribute is
            specified.) code may be
            one of the following: (1) a Perl-style substitution
            "s/regexp/subst/[flags]", where regexp and subst follow
            Python regular expression syntax and flags is zero or more
            of the following letters: a (make \\w, \\W, \\b, \\B, \\d,
            \\D match ASCII characters only instead of whole Unicode),
            g (replace all matches and not only the first one), i
            (match case-insensitively), l (make \\w, \\W, \\b, \\B
            dependent on the current locale), x (ignore whitespace and
            comments); (2) a single Python expression; or (3) the body
            of a Python function. In (2) and (3), the variable "val"
            refers to the value of the attribute (str), and they
            return the result of the transformation (converted to
            str). If (3) has no
            return statement, the value of "val" is returned. On an
            error depending on the value of "val", an empty string is
            returned. The option may be repeated to specify
            transformations for different attributes and/or multiple
            transformations for a single attribute. Multiple
            transformations for an attribute are processed in the
            order they are specified.''',
         {'metavar': '[attrname:]code',   # colon cannot be used in spec above
          'action': 'append'}),
    ]

    def __init__(self):
        super().__init__()
        self._key_attrs = []
        self._key_attrs_set = set()
        self._key_attr_count = 0
        self._key_re = None
        self._make_key = None
        self._sorter_key_opts = None
        self._concat_key0 = False
        self._concat_all_keys = False
        self._transform_funcs = defaultdict(list)
        self._transform_attrs = set()
        self._transform_sources = {}

    def check_args(self, args):
        super().check_args(args)
        args.key = ' '.join(args.key).replace(',', ' ')
        keys = [key.partition(':') for key in args.key.split()]
        self._key_attrs = [key[0].encode() for key in keys]
        self._key_attrs_set = set(self._key_attrs)
        key_opts = [key[2] for key in keys]
        self._key_attr_count = len(keys)
        if len(keys) == 1:
            self._make_key = self._make_key_single
            self._key_re = re.compile(b' ' + self._key_attrs[0] + rb'="(.*?)"')
        else:
            self._make_key = self._make_key_multi
            self._key_re = re.compile(rb' ([\w-]+)="(.*?)"')
        if all(key_opts[i] == '' for i in range(len(key_opts))):
            self._concat_all_keys = True
            self._sorter_key_opts = ['-k1,1']
        else:
            self._sorter_key_opts = ['-k{0},{0}{1}'.format(i + 1, key_opts[i])
                                     for i in range(len(key_opts))]
        # sys.stderr.write(repr(self._key_attrs) + '\n'
        #                  + repr(self._sorter_key_opts) + '\n')
        self._make_transforms(args.transform or [])
        self._transform_attrs = set(self._transform_funcs.keys())

    def _make_transforms(self, transforms):
        attrname_re = re.compile('\s*([\w-]+)\s*:\s*')
        for transform in transforms:
            mo = attrname_re.match(transform)
            if mo:
                key = mo.group(1)
                code = attrname_re.sub('', transform, 1)
            elif self._key_attr_count == 1:
                key = self._key_attrs[0].decode()
                code = transform
            else:
                self.error_exit(
                    'Multiple key attributes but transform does not '
                    'specify to which one it applies: '
                    + transform)
            key_b = key.encode()
            code = code.lstrip()
            if key_b not in self._key_attrs:
                self.error_exit('Transform attribute ' + key
                                + ' not listed in the argument of --key')
            self._transform_funcs[key_b].append(self._make_transform_func(code))
        # sys.stderr.write(repr(self._transform_funcs) + '\n')

    def _make_transform_func(self, code):

        def is_single_expr(code):
            # Use eval to check if the code is a single expression
            try:
                compile(code, '', mode='eval')
            except SyntaxError:
                return False
            return True

        def indent(lines):
            return '  ' + lines.replace('\n', '\n  ')

        body = ''
        if code.startswith('s/'):
            mo = re.fullmatch(r's/((?:[^/]|\\/)+)/((?:[^/]|\\/)*)/([agilx]*)',
                              code)
            if not mo:
                self.error_exit(f'Perl-style substitution not of the form'
                                f' s/regexp/repl/[agilx]*: {code}')
            regexp = mo.group(1)
            repl = mo.group(2)
            repl = re.sub(r'\$(\d)', r'\\\1', repl)
            flags = mo.group(3)
            count = 0 if 'g' in flags else 1
            flags = '|'.join('re.' + flag.upper()
                             for flag in flags if flag != 'g')
            if not flags:
                flags = '0'
            # f-strings require at least Python 3.5
            body = (f'return re.sub(r"""{regexp}""",'
                    f' r"""{repl}""", val, {count}, {flags})')
        elif is_single_expr(code):
            body = 'return ' + code
        else:
            if not re.search(r'(^|;)\s*return', code):
                body = code + '\nreturn val'
            else:
                body = code
        funcdef = 'def transfunc(val):\n' + indent(body)
        # sys.stderr.write(funcdef + '\n')
        try:
            exec(funcdef, globals())
        except SyntaxError as e:
            self.error_exit(
                f'Syntax error in transformation: {code}\n{e}:\n'
                + indent(funcdef))
        try:
            _ = transfunc('')
        except (ImportError, NameError) as e:
            self.error_exit(f'Invalid transformation: {code}\n'
                            f'{e.__class__.__name__}: {e}:\n'
                            + indent(funcdef))
        except Exception:
            # Should we also check some other exceptions here? At least
            # IndexError, KeyError and ValueError may depend on the
            # argument value, so they are checked when actually
            # transforming values.
            pass
        self._transform_sources[transfunc] = {
            'source': code,
            'funcdef': funcdef,
        }
        return transfunc

    def main(self, args, inf, ouf):

        def make_sort_line(key, start, end):
            return (b'\t'.join([key,
                                str(start).encode(),
                                str(end).encode()])
                    + b'\n')

        LESS_THAN = '<'.encode('utf-8')[0]
        # If the original input is not seekable, the input is copied
        # to a seekable temporary file. Python 3.6.8 on Puhti seems to
        # return seekable() == True for stdin, so also test for name
        # "<stdin>".
        write_tmp = not inf.seekable() or inf.name == '<stdin>'
        seekable_inf = NamedTemporaryFile(delete=False) if write_tmp else inf
        seekable_inf_name = seekable_inf.name
        # print(inf.seekable(), write_tmp, inf, seekable_inf_name,
        #       file=sys.stderr)
        # Use Popen as context manager to close standard file
        # descriptors and wait for the process on exit
        with Popen(['sort', '-s', '-t\t'] + self._sorter_key_opts,
                   stdin=PIPE, stdout=PIPE, stderr=PIPE,
                   bufsize=-1) as sorter:
            # print(self._sorter_key_opts, file=sys.stderr)
            # Give sort time to start to see if it produces an error message
            sleep(0.1)
            sorter.poll()
            # TODO: Interpret the sort error message
            if sorter.returncode is not None:
                sorter_errmsg = [line.decode()[:-1] for line in sorter.stderr]
                self.error_exit('Invalid sort option; sort error message:\n'
                                + ''.join(sorter_errmsg))
            # tee = Popen(['tee', 'vrt-sort-keys.out'],
            #             stdin=sorter.stdout, stdout=PIPE, bufsize=-1)
            key_count = 1 if self._concat_all_keys else self._key_attr_count
            orderf = NamedTemporaryFile(delete=False)
            orderf_name = orderf.name
            with Popen(['cut', '-d\t', '-f{0}-'.format(key_count + 1)],
                       stdin=sorter.stdout, stdout=orderf,
                       bufsize=-1) as cutter:
                # Close sorter stdout to make it detect SIGPIPE
                sorter.stdout.close()
                keysep = b'\x01' if self._concat_all_keys else b'\t'
                text_seen = False
                text_open = False
                comment_offsets = {'initial': [0, 0], 'final': [0, 0]}
                key = ''
                linenr = 0
                text_start_offset = 0
                start_offset = end_offset = 0
                # Write keys and text start and end offsets to the
                # sorter pipe to be sorted
                for line in inf:
                    if write_tmp:
                        seekable_inf.write(line)
                    linenr += 1
                    end_offset += len(line)
                    if text_open:
                        if line[0] == LESS_THAN and line.startswith(b'</text>'):
                            text_open = False
                            sorter.stdin.write(
                                make_sort_line(key, text_start_offset,
                                               end_offset))
                            # Next text starts immediately after
                            text_start_offset = end_offset
                    else:
                        if line[0] == LESS_THAN and line.startswith(b'<text '):
                            key = self._make_key(line, keysep, linenr)
                            # Initial comments
                            if not text_seen and linenr > 1:
                                comment_offsets['initial'] = [0, start_offset]
                                text_start_offset = start_offset
                            text_open = text_seen = True
                    start_offset = end_offset
                # Final comments
                if text_start_offset != end_offset:
                    comment_offsets['final'] = [text_start_offset, end_offset]
                    if text_open:
                        self.warn(
                            'the last <text> structure in input not closed;'
                            ' keeping it at the end')
                sorter.stdin.close()
                if write_tmp:
                    seekable_inf.close()
        # Read text start and end offsets from the sorted file, read
        # the texts from the input (or its copy) in that order and
        # write to output
        with open(seekable_inf_name, 'rb') as seekable_inf:
            with open(orderf_name, 'rb') as orderf:
                self._write_output(seekable_inf, ouf, orderf, comment_offsets)
        os.remove(orderf_name)
        if write_tmp:
            os.remove(seekable_inf_name)

    def _write_output(self, inf, ouf, orderf, comment_offsets):

        def write_text(start, end):
            if end > start:
                inf.seek(start)
                ouf.write(inf.read(end - start))

        write_text(*comment_offsets['initial'])
        for line in orderf:
            start, _, end = line[:-1].partition(b'\t')
            write_text(int(start), int(end))
        write_text(*comment_offsets['final'])

    def _make_key_single(self, tagline, keysep, linenr):
        mo = self._key_re.search(tagline)
        if mo and mo.group(1) is not None:
            if self._transform_funcs:
                return self._apply_transforms(
                    self._key_attrs[0], mo.group(1), linenr)
            else:
                return mo.group(1)
        else:
            return b''

    def _make_key_multi(self, tagline, keysep, linenr):
        attrvals = dict((key, val)
                        for key, val in self._key_re.findall(tagline)
                        if key in self._key_attrs_set)
        for attrname in self._transform_attrs:
            attrvals[attrname] = self._apply_transforms(
                attrname, attrvals[attrname], linenr)
        return keysep.join(attrvals.get(attrname, b'')
                           for attrname in self._key_attrs)

    def _apply_transforms(self, attrname, value, linenr):
        # sys.stderr.write('_apply_transforms(' + repr(attrname) + ', '
        #                  + repr(value) + ') -> ')
        value = value.decode('utf-8')
        for transform in self._transform_funcs[attrname]:
            try:
                value = transform(value)
            except (ArithmeticError, AttributeError, LookupError, RuntimeError,
                    TypeError, ValueError) as e:
                # Should we also catch other errors?
                self.warn(f'input line {linenr}: returning "" for attribute'
                          f' {attrname.decode()} with value "{value}":'
                          f' transformation caused {e.__class__.__name__}:'
                          f' {e}: '
                          + self._transform_sources[transform]['source'])
                value = ''
        # sys.stderr.write(repr(value) + '\n')
        return str(value).encode('utf-8')
