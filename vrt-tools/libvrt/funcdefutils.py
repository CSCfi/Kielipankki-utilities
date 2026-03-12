
"""
libvrt.funcdefutils

This library module contains a utility function for dynamically
defining functions, typically for transforming a value, for example,
based on command-line arguments.
"""


import re


class FuncDefError(Exception):

    """Error in a function definition."""

    pass


def define_func(code, name='func', args='val', returns='val',
                functype='function', context=None, test_call=True):
    """Dynamically define a functions based on `code`.

    Return the function (function object) and its definition (`str`).

    `code` can be either a single expression to be returned or a
    complete function body. In the latter case, if `code` does not
    contain a `return` statement, one returning `returns` is appended.

    The name of the function is `name` (default ``func``), its
    arguments `args` (`str` or a list of `str` for multiple arguments,
    default ``val``) and the value to be returned `returns` if `code`
    has no explicit `return` statement (default ``val``). The value of
    `functype` is used in the messages of raised `FuncDefError`
    exceptions (default ``function``). `context` is a `dict`
    containing the execution context in which the function is to be
    defined; if `None` (the default), the context will contain only
    built-in functions.

    If `test_call` is `True`, the defined function is called with
    empty string arguments to catch possible `NameError` and
    `ImportError` exceptions early. `test_call` should perhaps be set
    to `False` if the function call has side effects, e.g. if it
    modifies global variables in `context` or calls a random-number
    generator.

    Raises `FuncDefError` if `code` raises `SyntaxError` when defining
    the function or `ImportError` or `NameError` when calling it
    (unless `test_call` is `False`).
    """

    def make_args(args):
        """If `args` is a sequence, return its items joined by comma."""
        return (args if isinstance(args, str) else ', '.join(args))

    def is_single_expr(code):
        # Use eval to check if the code is a single expression
        try:
            compile(code, '', mode='eval')
        except SyntaxError:
            return False
        return True

    def indent(lines):
        return '  ' + lines.replace('\n', '\n  ')

    args = make_args(args)
    body = ''
    context = context or {}
    if is_single_expr(code):
        body = f'return {code}'
    elif re.search(r'(^|;)\s*return', code, re.MULTILINE):
        body = code
    else:
        returns = make_args(returns)
        body = f'{code}\nreturn {returns}'
    funcdef = f'def {name}({args}):\n{indent(body)}'
    # sys.stderr.write(funcdef + '\n')
    try:
        exec(funcdef, context)
    except SyntaxError as e:
        raise FuncDefError(f'Syntax error in {functype}: {code}\n{e}:\n'
                           + indent(funcdef))
    # Test function with as many empty strings as arguments as given
    # in args
    test_args = (('',) * (args.count(',') + 1)) if args else ()
    if test_call:
        try:
            _ = context[name](*test_args)
        except (ImportError, NameError) as e:
            raise FuncDefError(f'Invalid {functype}: {code}\n'
                               f'{e.__class__.__name__}: {e}:\n'
                               + indent(funcdef))
        except Exception:
            # Should we also check some other exceptions here? At least
            # IndexError, KeyError and ValueError may depend on the
            # argument value, so they are checked when actually
            # transforming values.
            pass
    return (context[name], funcdef)


def define_transform_func(code, extra_args=None, context=None, test_call=True):
    """Define a function for transforming an input value.

    Define function based on `code` and return a pair with the
    function and its definition.

    `code` can be a function body, a single expression or a Perl-style
    substitution expression (s/regexp/subst/flags). The function body
    and single expression take parameter `val` as the argument and
    return it as transformed by the expression or body. If
    `extra_args` is not `None`, it should be a tuple or
    comma-separated string containing the names of additional
    arguments to the function. `context` is a `dict` containing the
    execution context in which the function is to be defined; if
    `None`, the context will contain only built-in functions and
    module `re`. If the function body contains no explicit `return`
    statement, `return val` is appended to it.

    If `test_call` is `True`, the defined function is called with
    empty string arguments to catch possible `NameError` and
    `ImportError` exceptions early. `test_call` should perhaps be set
    to `False` if the function call has side effects, e.g. if it
    modifies global variables in `context` or calls a random-number
    generator.
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

    context = context or {}
    # If exec context contains no "re", add it
    context.setdefault('re', re)
    if code.startswith('s/'):
        sub_code = convert_perl_subst(code)
        if sub_code is None:
            raise FuncDefError(f'Perl-style substitution not of the form'
                               f' s/regexp/repl/[agilx]*: {code}')
        code = sub_code
    if extra_args is None:
        args = 'val'
    else:
        args = 'val, ' + (extra_args if isinstance(extra_args, str)
                          else ', '.join(extra_args))
    return define_func(code, name='transfunc', args=args,
                       functype='transformation', context=context,
                       test_call=test_call)


def convert_perl_subst(expr):
    """Convert Perl-style substitution `expr` to a Python `re.sub` call.

    Convert Perl-style regular-expression substitution `expr` of the
    form `s/regepx/subst/flags` to a Python `re.sub` expression and
    return it. Return `None` if `expr` is not valid.

    The flags a, g, i, l and x are converted, and Perl-style group
    references $N in the are converted to \\N, but otherwise the
    regular expression and the substitution expression must follow
    Python syntax.

    Only slashes are recognized as separators. To include a literal
    slash in `regexp` or `subst`, precede it with a backslash.
    """

    def unprotect_slashes(str):
        """Return `str` with backslash protection removed from slashes."""
        # Protect \\ from removal, replace \/ with /, restore \\
        return (str.replace(r'\\', '\x01')
                .replace(r'\/', '/')
                .replace('\x01', r'\\'))

    mo = re.fullmatch(r's/((?:[^/]|\\/)+)/((?:[^/]|\\/)*)/([agilx]*)', expr)
    if not mo:
        return None
    regexp = unprotect_slashes(mo.group(1))
    repl = re.sub(r'\$(\d)', r'\\\1', unprotect_slashes(mo.group(2)))
    flags = mo.group(3)
    count = 0 if 'g' in flags else 1
    flags = '|'.join('re.' + flag.upper()
                     for flag in flags if flag != 'g')
    if not flags:
        flags = '0'
    return f're.sub(r"""{regexp}""", r"""{repl}""", val, {count}, {flags})'
