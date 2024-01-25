
"""
Module libvrt.strformatters

This module contains custom string formatters (subclasses of
string.Formatter) for various purposes.
"""


import re

from collections import OrderedDict
from string import Formatter


class PartialStringFormatter(Formatter):

    """
    A string formatter handling missing keys.

    A string formatter that outputs an empty (or other specified)
    string when a format key would cause a `KeyError`, `IndexError` or
    `AttributeError`, or keeps the format specification intact.

    Adapted from
    http://stackoverflow.com/questions/20248355/how-to-get-python-to-gracefully-format-none-and-non-existing-fields
    https://gist.github.com/navarroj/7689682
    """

    # Temporary replacements of double and single curly brackets for
    # protection from replacement; the mapping needs to be ordered, as
    # double curly brackets need to be replaced before single ones
    _CURLY_REPL = OrderedDict((s, chr(i + 1))
                              for i, s in enumerate(['{{', '}}', '{', '}']))

    def __init__(self, missing=''):
        """Initialize formatter; replace missing values with `missing`.

        If `missing` is `None`, keep intact format specifications
        without a corresponding positional or keyword argument. Note
        that this only works for whole arguments, not if an index or
        attribute is missing; in the latter case, the format
        specification is replaced with an empty string.
        """
        super().__init__()
        self._missing = missing

    def vformat(self, format_string, args, kwargs):
        """Actual formatting; handle keeping format specs for missing keys

        Call `Formatter.vformat`; if `self._missing` is `None`,
        protect formatspecs for missing keys before calling it and
        remove protection from the result.
        """
        if self._missing is None:
            format_string = self._protect_missing_formatspecs(
                format_string, len(args), kwargs.keys())
            return self._unprotect_formatspecs(
                super().vformat(format_string, args, kwargs))
        else:
            return super().vformat(format_string, args, kwargs)

    def _protect_formatspecs(self, format_string):
        """Protect all single and double curly brackets in `format_string`."""
        for curly, repl in self._CURLY_REPL.items():
            format_string = format_string.replace(curly, repl)
        return format_string

    def _unprotect_formatspecs(self, format_string):
        """Replace curly bracket replacements in `format_string` with brackets.

        As the method is called after `Formatter.vformat` has replaced
        "{{" and "}}" with "{" and "}", this also replaces the
        replacements of "{{" and "}}" with "{" and "}", respectively.
        """
        for curly, repl in self._CURLY_REPL.items():
            format_string = format_string.replace(repl, curly[0])
        return format_string

    def _protect_missing_formatspecs(self, format_string, args_len,
                                     kwargs_keys):
        """Protect format specs in `format_string` without corresponding arg.

        Protect the format specifications in `format_string` with an
        index greater than or equal to `args_len` or a key not in
        `kwargs_keys`. Note that this does *not* consider possible
        missing indices, keys or attributes of existing fields.
        """
        # Unprotect those with index in args or key in kwargs
        return self._unprotect_present_formatspecs(
            self._protect_formatspecs(format_string), args_len, kwargs_keys)

    def _unprotect_present_formatspecs(self, format_string, args_len,
                                      kwargs_keys):
        """Unprotect format specs in `format_string` with corresponding arg.

        Protect the format specifications in `format_string` with an
        index less than `args_len` or a key in `kwargs_keys`.
        """
        return re.sub(
            (self._CURLY_REPL['{']
             + '(('
             + '|'.join([str(i) for i in range(args_len)] + list(kwargs_keys))
             + r')([!:.\[].*?)?)'
             + self._CURLY_REPL['}']),
            r'{\1}',
            format_string)

    def get_field(self, field_name, args, kwargs):
        """Override `Formatter.get_field`.

        Call `Formatter.get_field`; on error, return (`None`,
        `field_name`).
        """
        try:
            return super().get_field(field_name, args, kwargs)
        except (KeyError, IndexError, AttributeError):
            return None, field_name

    def format_field(self, value, spec):
        """Override `Formatter.format_field`.

        If `value` is `None`, return `self._missing`, otherwise call
        `Formatter.format_field`
        """
        if value is None:
            return self._missing or ''
        else:
            return super().format_field(value, spec)
