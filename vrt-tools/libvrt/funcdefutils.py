
"""
libvrt.funcdefutils

This library module contains a utility function for dynamically
defining functions for transforming a value, for example, based on
command-line arguments.
"""


import re


class FuncDefError(Exception):

    """Error in a function definition."""

    pass


def define_transform_func(code):
    """Define a function for transforming an input value.

    Define function based on `code` and return a pair with the
    function and its definition.

    `code` can be a function body, a single expression or a Perl-style
    substitution expression (s/regexp/subst/flags). The function body
    and single expression take parameter `val` as the argument and
    return it as transformed by the expression or body. If the
    function body contains no explicit `return` statement, `return
    val` is appended to it.
    """

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
        body = convert_perl_subst(code)
        if body is None:
            raise FuncDefError(f'Perl-style substitution not of the form'
                               f' s/regexp/repl/[agilx]*: {code}')
        body = 'return ' + body
    elif is_single_expr(code):
        body = 'return ' + code
    else:
        if not re.search(r'(^|;)\s*return', code, re.MULTILINE):
            body = code + '\nreturn val'
        else:
            body = code
    funcdef = 'def transfunc(val):\n' + indent(body)
    # sys.stderr.write(funcdef + '\n')
    try:
        exec(funcdef, globals())
    except SyntaxError as e:
        raise FuncDefError(f'Syntax error in transformation: {code}\n{e}:\n'
                           + indent(funcdef))
    try:
        _ = transfunc('')
    except (ImportError, NameError) as e:
        raise FuncDefError(f'Invalid transformation: {code}\n'
                           f'{e.__class__.__name__}: {e}:\n'
                           + indent(funcdef))
    except Exception:
        # Should we also check some other exceptions here? At least
        # IndexError, KeyError and ValueError may depend on the
        # argument value, so they are checked when actually
        # transforming values.
        pass
    return (transfunc, funcdef)


def convert_perl_subst(expr):
    """Convert Perl-style substitution `expr` to a Python `re.sub` call.

    Convert Perl-style regular-expression substitution `expr` of the
    form `s/regepx/subst/flags` to a Python `re.sub` expression and
    return it. Return `None` if `expr` is not valid.

    The flags a, g, i, l and x are converted, and Perl-style group
    references $N in the are converted to \\N, but otherwise the
    regular expression and the substitution expression must follow
    Python syntax. Only slashes are recognized as separators.
    """
    mo = re.fullmatch(r's/((?:[^/]|\\/)+)/((?:[^/]|\\/)*)/([agilx]*)', expr)
    if not mo:
        return None
    regexp = mo.group(1)
    repl = re.sub(r'\$(\d)', r'\\\1', mo.group(2))
    flags = mo.group(3)
    count = 0 if 'g' in flags else 1
    flags = '|'.join('re.' + flag.upper()
                     for flag in flags if flag != 'g')
    if not flags:
        flags = '0'
    return f're.sub(r"""{regexp}""", r"""{repl}""", val, {count}, {flags})'
