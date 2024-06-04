
"""
libvrt.groupargs

Implements “grouped command-line arguments”: one option argument is
defined as a *grouping argument* and some other arguments as *grouped
arguments*. The values of grouped arguments are attached to the
preceding value of the grouping argument, and the values of grouped
arguments preceding any grouping argument are set as default values in
cases where a grouped argument is not given a value after a grouping
argument.

This is done by defining special `argparse.Action` subclasses for the
grouping argument and the grouped arguments.

Usage example:

>>> from argparse import ArgumentParser
>>> ap = ArgumentParser()
>>> ap.add_argument('--grp', action=grouping_arg())
>>> ap.add_argument('--aa', action=grouped_arg(), default='a')
>>> ap.add_argument('--bb', action=grouped_arg())
>>> args = '--bb=b0 --grp=a --aa=a1 --bb=b1 --grp=b --aa=a2 --grp=c'
>>> ap.parse_args(args.split())
Namespace(grp={'a': Namespace(aa='a1', bb='b1', _explicit={'aa', 'bb'}), 'b': Namespace(aa='a2', bb='b0', _explicit={'aa'}), 'c': Namespace(aa='a', bb='b0', _explicit=set())}, aa='a', bb='b0', _explicit={'bb'})

The value of the attribute `_explicit` is a set of the names of
attributes corresponding to grouped arguments whose values have been
explicitly set for an grouping argument value (or before any grouping
argument at the top level), as opposed to using a default.

Non-grouped arguments can be added as usual.

Note that although this module is currently in the `libvrt` package,
it is *not* specific to VRT Tools.
"""


# TODO:
# - Test interaction with various add_argument parameters, e.g.
#   default, type, nargs
# - Add error checking and handling: e.g., (optionally?) do not allow
#   (or warn on) duplicate values for grouping arguments, or
#   alternatively, use list of pairs instead of dict as grouping
#   argument value


from argparse import Action, Namespace, ArgumentError


def _get_namespace_attr(namespace, name, default=None):
    """Return value of attribute `name` in `namespace`, or `default`

    If `namespace` does not contain attribute `name`, set the value of
    `namespace.name` to `default` and return it.
    """
    val = getattr(namespace, name, None)
    if val is None:
        val = default
        setattr(namespace, name, val)
    return val


class ArgumentGrouping:

    """
    Class for defining argument groupings

    The public methods `grouping_arg` and `grouped_arg` return classes
    that are subclasses of `argparse.Action` and can be used as the
    values for the `action` argument of
    `argparse.ArgumentParser.add_argument` (the instances of the
    classes are callable).

    In principle, you can use multiple instances of this class to have
    multiple argument groupings for the same program, even though it
    may be a rare use case.
    """

    def __init__(self):
        """Create instance"""
        # Grouping argument (argparse.Action subclass object)
        self._grouping_arg = None
        # Current value for the grouping argument; None if none
        # encountered yet
        self._grouping_val = None
        # Grouped arguments (argparse.Action subclass objects)
        self._grouped_args = []

    def _get_grouping(self, namespace):
        """Get the grouping argument attribute from `namespace`.

        If the attribute for the grouping argument does not yet exist,
        set it to an empty `dict`.
        """
        return _get_namespace_attr(namespace, self._grouping_arg.dest, {})

    def _get_grouping_namespace(self, namespace):
        """Get the namespace for the current grouping value in `namespace`.

        If no grouping argument has yet been encountered, return
        `namespace` for setting defaults.
        Also add attribute `_explicit` to `namespace` for adding
        explicitly specified arguments if it does not exist yet.
        """
        # Check _explicit here, so that it is added even when no
        # default, non-grouping arguments are specified
        if not hasattr(namespace, '_explicit'):
            setattr(namespace, '_explicit', set())
        if self._grouping_val:
            return (
                getattr(namespace, self._grouping_arg.dest, {})
                .get(self._grouping_val))
        else:
            return namespace

    def _add_grouped_arg(self, arg):
        """Add `arg` as a grouped argument (`argparse.Action` object)."""
        self._grouped_args.append(arg)

    def _make_defaults(self, namespace):
        """Return a namespace with defaults for grouped arguments.

        The defaults are taken from the values of the attributes
        corresponding to grouped arguments in `namespace`.
        Also set `_explicit` in the namespace to an empty set, for
        listing the arguments explicitly specified for a grouped
        value.
        """
        defaults = Namespace()
        for arg in self._grouped_args:
            setattr(defaults, arg.dest, getattr(namespace, arg.dest, None))
        setattr(defaults, '_explicit', set())
        return defaults

    def _set_grouped_value(self, namespace, dest, value):
        """Set `dest` to `value` in `namespace`.

        Set the value of attribute `dest` in the namespace for the
        current value of the grouping argument, or the default
        namespace if no grouping argument has been encountered yet.
        """
        self._modify_grouped_value(namespace, dest, lambda x: value)

    def _modify_grouped_value(self, namespace, dest, func):
        """Set `dest` to `func(dest)` in `namespace`.

        Modify the value of attribute `dest` to the value returned by
        `func` for `dest` in the namespace for the current value of
        the grouping argument, or the default namespace if no grouping
        argument has been encountered yet.
        Also add `dest` to `namespace._explicit`.
        """
        namespace = self._get_grouping_namespace(namespace)
        value = func(getattr(namespace, dest, None))
        setattr(namespace, dest, value)
        # If setting value in a grouped namespace, mark the value as
        # explicitly set
        namespace._explicit.add(dest)

    def grouping_arg(outer_self):
        """Return a class to be used as an action for a grouping argument.

        Calling this method more than once (for one `ArgumentGrouping`)
        raises `ArgumentError`.
        """
        # Note that the usual `self` argument is replaced by
        # `outer_self`, as the class definition needs to refer to it
        # as well as use `self` in its own methods.
        #
        # A method returning an inner class is used so that the inner
        # class can refer to *instance* methods and variables of the
        # outer class. (Or would it be possible in some other way?)

        class GroupingArgAction(Action):

            """
            `argparse.Action` subclass implementing a grouping argument
            """

            def __init__(self, *args, **kwargs):
                """Initialize the action (in `ArgumentParser.add_argument`).

                Set the grouping argument to `self`.

                Raise `ArgumentError` if the same a grouping argument
                has already been defined for this `ArgumentGrouping`.
                """
                super().__init__(*args, **kwargs)
                if outer_self._grouping_arg is not None:
                    raise ArgumentError(
                        self,
                        'Action "grouping_arg" already used for argument '
                        + outer_self._grouping_arg.option_strings[0])
                outer_self._grouping_arg = self

            def __call__(self, parser, namespace, values, option_string=None):
                """Call the action (in `ArgumentParser.parse_args`)

                Called when parsing the arguments and a grouping
                argument is encountered: set the value for the
                grouping argument and initialize its namespace with
                defaults.
                """
                grouping = outer_self._get_grouping(namespace)
                grouping[values] = outer_self._make_defaults(namespace)
                outer_self._grouping_val = values

        return GroupingArgAction

    def grouped_arg(outer_self, action='store'):
        """Return a class to be used as an action for a grouped argument.

        `action` can be one of `'store'` (default), `'store_const'`,
        `'store_true'`, `'store_false'`, `'append'`, `'append_const'`,
        `'count'` or `'extend'`; it makes the argument behave
        (roughly) as with the similarly-named
        `ArgumentParser.add_argument()` action.

        """
        # The same notes about the inner class and `outer_self` apply
        # as for `grouping_arg`.

        class GroupedArgAction(Action):

            """
            `argparse.Action` subclass: base class for a grouped argument

            This class cannot be used as an action itself, as it does
            not implement `__call__`; that should be done in
            subclasses.
            """

            def __init__(self, *args, **kwargs):
                """Initialize the action (in `ArgumentParser.add_argument`).

                Add this object as a grouping argument.
                """
                super().__init__(*args, **kwargs)
                outer_self._add_grouped_arg(self)

            def _set_value(self, namespace, value):
                """Set `self.dest` to `value` in `namespace`.

                Set the value of attribute `self.dest` in the
                namespace for the current value of the grouping
                argument, or the default namespace if no grouping
                argument has been encountered yet.
                """
                outer_self._set_grouped_value(namespace, self.dest, value)

            def _modify_value(self, namespace, func):
                """Set `self.dest` to `func(self.dest)` in `namespace`.

                Modify the value of attribute `self.dest` to the value
                returned by `func` for `self.dest` in the namespace
                for the current value of the grouping argument, or the
                default namespace if no grouping argument has been
                encountered yet.
                """
                outer_self._modify_grouped_value(namespace, self.dest, func)

            def _append_value(self, namespace, value):
                """Append `value` to `self.dest` in `namespace`.

                Append `value` to `self.dest` (assumed to be a list)
                in the namespace for the current value of the grouping
                argument, or the default namespace if no grouping
                argument has been encountered yet.
                """

                def append(lst):
                    """Return a copy of `lst` with `value` appended."""
                    lst = (lst or []).copy()
                    lst.append(value)
                    return lst

                self._modify_value(namespace, append)

        class GroupedStoreAction(GroupedArgAction):

            """
            `GroupedArgAction` subclass for action `'store'`.
            """

            def __call__(self, parser, namespace, values, option_string=None):
                """Call the action (in `ArgumentParser.parse_args`)

                Called when parsing the arguments and a grouped
                argument is encountered: set the value of `self.dest`
                to `values` in the namespace for the current value of
                the grouping argument, or the default namespace if no
                grouping argument encountered yet.
                """
                self._set_value(namespace, values)

        class GroupedNoValueAction(GroupedArgAction):

            """
            `GroupedArgAction` subclass for option arguments without values.

            Subclasses should implement `__call__`.
            """

            def __init__(self, *args, nargs=0, **kwargs):
                """Initialize action with `nargs=0` (no value)."""
                # See https://stackoverflow.com/a/37614126
                super().__init__(*args, nargs=nargs, **kwargs)

        class GroupedStoreConstAction(GroupedNoValueAction):

            """
            `GroupedArgAction` subclass for action `'store_const'`.
            """

            def __call__(self, parser, namespace, values, option_string=None):
                """Call the action (in `ArgumentParser.parse_args`)

                Set the value of `self.dest` to `self.const` in the
                namespace for the current value of the grouping
                argument, or the default namespace if no grouping
                argument encountered yet.
                """
                self._set_value(namespace, self.const)

        class GroupedStoreTrueAction(GroupedNoValueAction):

            """
            `GroupedArgAction` subclass for action `'store_true'`.
            """

            def __init__(self, *args, default=False, **kwargs):
                """Initialize action with `default=False`."""
                super().__init__(*args, default=default, **kwargs)

            def __call__(self, parser, namespace, values, option_string=None):
                """Call the action (in `ArgumentParser.parse_args`)

                Set the value of `self.dest` to `True` in the
                namespace for the current value of the grouping
                argument, or the default namespace if no grouping
                argument encountered yet.
                """
                self._set_value(namespace, True)

        class GroupedStoreFalseAction(GroupedNoValueAction):

            """
            `GroupedArgAction` subclass for action `'store_false'`.
            """

            def __init__(self, *args, default=True, **kwargs):
                """Initialize action with `default=True`."""
                super().__init__(*args, default=default, **kwargs)

            def __call__(self, parser, namespace, values, option_string=None):
                """Call the action (in `ArgumentParser.parse_args`)

                Set the value of `self.dest` to `False` in the
                namespace for the current value of the grouping
                argument, or the default namespace if no grouping
                argument encountered yet.
                """
                self._set_value(namespace, False)

        class GroupedAppendAction(GroupedArgAction):

            """
            `GroupedArgAction` subclass for action `'append'`.
            """

            def __call__(self, parser, namespace, values, option_string=None):
                """Call the action (in `ArgumentParser.parse_args`)

                Append `values` to the value of `self.dest` in the
                namespace for the current value of the grouping
                argument, or the default namespace if no grouping
                argument encountered yet.
                """
                self._append_value(namespace, values)

        class GroupedAppendConstAction(GroupedNoValueAction):

            """
            `GroupedArgAction` subclass for action `'append_const'`.
            """

            def __call__(self, parser, namespace, values, option_string=None):
                """Call the action (in `ArgumentParser.parse_args`)

                Append `self.const` to the value of `self.dest` in the
                namespace for the current value of the grouping
                argument, or the default namespace if no grouping
                argument encountered yet.
                """
                self._append_value(namespace, self.const)

        class GroupedCountAction(GroupedNoValueAction):

            def __call__(self, parser, namespace, values, option_string=None):
                """Call the action (in `ArgumentParser.parse_args`)

                Increment the value of `self.dest` by 1 in the
                namespace for the current value of the grouping
                argument, or the default namespace if no grouping
                argument encountered yet.
                """
                self._modify_value(namespace, lambda x: (x or 0) + 1)

        class GroupedExtendAction(GroupedArgAction):

            def __call__(self, parser, namespace, values, option_string=None):
                """Call the action (in `ArgumentParser.parse_args`)

                Extend the value of `self.dest` with `values` in the
                namespace for the current value of the grouping
                argument, or the default namespace if no grouping
                argument encountered yet.
                """

                def extend(lst):
                    """Extend copy of `lst` (assumed a list) with `values`."""
                    lst = (lst or []).copy()
                    lst.extend(values)
                    return lst

                self._modify_value(namespace, extend)

        # Map action names to classes
        action_class = {
            'store': GroupedStoreAction,
            'store_const': GroupedStoreConstAction,
            'store_true': GroupedStoreTrueAction,
            'store_false': GroupedStoreFalseAction,
            'append': GroupedAppendAction,
            'append_const': GroupedAppendConstAction,
            'count': GroupedCountAction,
            'extend': GroupedExtendAction,
        }
        try:
            return action_class[action or 'store']
        except KeyError:
            raise ValueError(f'unknown action "{action}"')


# Default argument `ArgumentGrouping`, to be used in the convenience
# functions `grouping_arg` and `grouped_arg`
_argument_grouping = ArgumentGrouping()


def grouping_arg():
    """Return an `argparse.Action` subclass for a grouping argument.

    This is a convenience function using a module-level instance of
    `ArgumentGrouping`. If you need multiple grouping arguments in a
    single program, use a different explicit `ArgumentGrouping`
    instance for each.
    """
    return _argument_grouping.grouping_arg()


def grouped_arg(action='store'):
    """Return an `argparse.Action` subclass for a grouped argument.

    `action` can be one of `'store'` (default), `'store_const'`,
    `'store_true'`, `'store_false'`, `'append'`, `'append_const'`,
    `'count'` or `'extend'`; it makes the argument behave (roughly) as
    with the similarly-named `ArgumentParser.add_argument()` action.

    This is a convenience function using a module-level instance of
    `ArgumentGrouping`.
    """
    return _argument_grouping.grouped_arg(action)
