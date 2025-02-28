
"""
Module libvrt.datatypes

This module contains definitions of data types (classes) that are not
specific to any individual VRT tool.
"""


import sys


# OrderPreservingDict is a dictionary preserving insertion order:
# Python 3.7+ guarantees that dict preserves insertion order; for
# older Python versions, use OrderedDict
if sys.version_info >= (3, 7):
    OrderPreservingDict = dict
else:
    from collections import OrderedDict as OrderPreservingDict


class StrBytesDict(OrderPreservingDict):

    """
    Dictionary class with a partial conversion between `bytes` and `str`.

    When a `StrBytesDict` `d` is accessed with `d[key]` or
    `d.get(key)` where `key` is `str` and `d[key]` does not exist, if
    the dictionary contains a value for `key` encoded as `bytes`
    (`key_b`), add `d[key]` with the value of `d[key_b]` decoded to
    `str`. After this, `d[key]` may be modified independently.

    The method `convert_to_bytes` converts values of such keys back to
    the corresponding `bytes` keys, also for `str` keys directly
    assigned to, and removes the `str` keys.

    A use case for `StrBytesDict` is representing VRT structural
    attributes (annotations) read as `bytes` but some of which need
    processing as `str` (e.g. with regular expressions) and then
    converting back to `bytes` for writing output. With
    `StrBytesDict`, values are converted to `str` on demand, so not
    all attribute values need to be converted, which can improve
    performance.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dictionary mapping str keys to bytes keys
        self._decoded_keys = {}

    def __getitem__(self, key):
        """Return `self[key]`.

        If `self[key]` does not exist, if `key` is `str` and if
        `self[key_b]` exists where `key_b` is `key` encoded as bytes,
        set `self[key]` to `self[key_b]` decoded to `str` and return
        it.
        """
        try:
            return super().__getitem__(key)
        except KeyError as exc:
            if isinstance(key, str):
                try:
                    key_b = key.encode('utf-8')
                    self[key] = super().__getitem__(key_b).decode('utf-8')
                    self._decoded_keys[key] = key_b
                except KeyError:
                    # Raise the original exception with the original
                    # key, not encoded; "from None" suppresses "During
                    # handling of the above exception ..." messages
                    raise exc from None
                return super().__getitem__(key)
            else:
                raise

    def get(self, key, default=None):
        """Return `self[key]` or if it does not exist, `default`

        Use the same mechanism for converting between `str` and
        `bytes` as `__getitem__`.
        """
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __setitem__(self, key, value):
        """Set `self[key]` to `value`.

        If `key` is `str`, ensure that it is marked it as one, so that
        `convert_to_bytes` applies to it.
        """
        if isinstance(key, str) and not key in self._decoded_keys:
            self._decoded_keys[key] = key.encode('utf-8')
        return super().__setitem__(key, value)

    def convert_to_bytes(self):
        """Convert values of `str` keys to `bytes` keys and remove the former.

        The values are encoded as `bytes`.
        """
        for key, key_b in self._decoded_keys.items():
            self[key_b] = self[key].encode('utf-8')
            del(self[key])
        return self
