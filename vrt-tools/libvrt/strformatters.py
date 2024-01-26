
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
    A string formatter handling missing objects.

    A string formatter that outputs an empty (or other specified)
    string or keeps the replacement field intact when the object
    specified in the replacement field is missing and would cause a
    `KeyError`, `IndexError` or `AttributeError`, .

    Adapted and extended from
    http://stackoverflow.com/questions/20248355/how-to-get-python-to-gracefully-format-none-and-non-existing-fields
    https://gist.github.com/navarroj/7689682
    """

    class _Missing:
        """Empty class for a unique value to represent missing value."""
        pass

    # Unique value to represent a missing value
    _MISSING = _Missing()

    # Temporary replacements of double and single curly brackets for
    # protection from replacement; the mapping needs to be ordered, as
    # double curly brackets need to be replaced before single ones
    _CURLY_REPL = OrderedDict((s, chr(i + 1))
                              for i, s in enumerate(['{{', '}}', '{', '}']))

    def __init__(self, missing=''):
        """Initialize formatter; replace missing objects with `missing`.

        If `missing` is `None`, keep intact replacement fields
        referring to a non-existent object (positional or keyword
        argument). Note that this only works for whole arguments, not
        if an index or attribute is missing; in the latter case, the
        replacement field is replaced with an empty string.
        """
        super().__init__()
        self._missing = missing

    def vformat(self, format_string, args, kwargs):
        """Actual formatting; handle keeping replacement fields for missing args

        Call `Formatter.vformat`; if `self._missing` is `None`,
        protect replacement fields without corresponding arguments
        before calling it and remove protection from the result.
        """
        if self._missing is None:
            format_string = self._protect_missing_replfields(
                format_string, len(args), kwargs.keys())
            return self._unprotect_replfields(
                super().vformat(format_string, args, kwargs))
        else:
            return super().vformat(format_string, args, kwargs)

    def _protect_replfields(self, format_string):
        """Protect all single and double curly brackets in `format_string`."""
        for curly, repl in self._CURLY_REPL.items():
            format_string = format_string.replace(curly, repl)
        return format_string

    def _unprotect_replfields(self, format_string):
        """Replace curly bracket replacements in `format_string` with brackets.

        As the method is called after `Formatter.vformat` has replaced
        "{{" and "}}" with "{" and "}", this also replaces the
        replacements of "{{" and "}}" with "{" and "}", respectively.
        """
        for curly, repl in self._CURLY_REPL.items():
            format_string = format_string.replace(repl, curly[0])
        return format_string

    def _protect_missing_replfields(self, format_string, args_len, kwargs_keys):
        """Protect replacement fields in `format_string` with missing arg.

        Protect the replacement fields in `format_string` with an
        index greater than or equal to `args_len` or a key not in
        `kwargs_keys`. Note that this does *not* consider possible
        missing indices, keys or attributes of existing arguments.
        """
        # Unprotect those with index <= args_len or key in kwargs
        return self._unprotect_present_replfields(
            self._protect_replfields(format_string), args_len, kwargs_keys)

    def _unprotect_present_replfields(self, format_string, args_len,
                                      kwargs_keys):
        """Unprotect replacement fields in `format_string` with present arg.

        Unprotect the replacement fields in `format_string` with an
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

        Call `Formatter.get_field`; on error, return (`self._MISSING`,
        `field_name`).
        """
        try:
            return super().get_field(field_name, args, kwargs)
        except (KeyError, IndexError, AttributeError):
            return self._MISSING, field_name

    def format_field(self, value, spec):
        """Override `Formatter.format_field`.

        Call `Formatter.format_field` on `value` or `self._missing` if
        `value` is `self._MISSING`.
        """
        if value is self._MISSING:
            value = self._missing if self._missing is not None else ''
        return super().format_field(value, spec)

    def convert_field(self, value, conversion):
        """Override `Formatter.convert_field`.

        If `value` is `self._MISSING`, return it as such; otherwise,
        call `Formatter.convert_field` on `value`.
        """
        if value is self._MISSING:
            if self._missing is None:
                return value
            else:
                value = self._missing
        return super().convert_field(value, conversion)


def _bytes_to_string(bs):
    """If `bs` is `bytes` (UTF-8), decode it to `str`, else return as is."""
    return bs.decode('UTF-8') if isinstance(bs, bytes) else bs


class BytesFormatter(Formatter):

    """
    A string formatter converting bytes to strings

    This string formatter converts bytes to strings in replacement
    values. Moreover, if accessing a dict value with a string key
    fails, it tries the key encoded to UTF-8 bytes.
    """

    def __init__(self):
        """Initialize formatter."""
        super().__init__()

    def get_field(self, field_name, args, kwargs):
        """Override `Formatter.get_field`.

        If calling superclass `get_field` raises a `KeyError` and
        `field_name` contains key indexing and no attribute access,
        try indexing with a key to UTF-8 bytes.
        """
        try:
            value, used_key = super().get_field(field_name, args, kwargs)
        except KeyError:
            if field_name[-1] == ']' and '.' not in field_name:
                field_name, _, idx = field_name[:-1].partition('[')
                if field_name.isdigit():
                    field_name = int(field_name)
                obj = self.get_value(field_name, args, kwargs)
                if idx.isdigit():
                    # This probably is not needed, as it would not
                    # have raised a KeyError
                    value = obj[int(idx)]
                else:
                    value = obj[idx.encode('UTF-8')]
                value = _bytes_to_string(value)
                used_key = field_name
            else:
                raise
        return _bytes_to_string(value), used_key

    def get_value(self, key, args, kwargs):
        """Override `Formatter.get_value`.

        Call superclass `get_value` and convert the result to `str` if
        it is `bytes`.
        """
        return _bytes_to_string(super().get_value(key, args, kwargs))
