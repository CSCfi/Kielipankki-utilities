
"""
test_groupargs.py

Pytest tests for libvrt.groupargs.
"""


import pytest

from argparse import ArgumentParser, ArgumentError

from libvrt.groupargs import ArgumentGrouping, grouping_arg, grouped_arg


class TestArgumentGrouping:

    """Tests for ArgumentGrouping"""

    def test_argument_grouping_basic(self):
        """Test ArgumentGrouping basic functionality."""
        ap = ArgumentParser()
        ag = ArgumentGrouping()
        ap.add_argument('--grp', action=ag.grouping_arg())
        ap.add_argument('--aa', action=ag.grouped_arg())
        ap.add_argument('--bb', action=ag.grouped_arg())
        argstr = '--grp=a --aa=a1 --bb=b1 --grp=b --aa=a2'
        args = ap.parse_args(argstr.split())
        assert args._explicit == set()
        assert args.grp
        assert args.grp['a'].aa == 'a1'
        assert args.grp['a'].bb == 'b1'
        assert args.grp['a']._explicit == {'aa', 'bb'}
        assert args.grp['b'].aa == 'a2'
        assert args.grp['b'].bb == None
        assert args.grp['b']._explicit == {'aa'}

    def test_argument_grouping_defaults(self):
        """Test ArgumentGrouping default values."""
        ap = ArgumentParser()
        ag = ArgumentGrouping()
        ap.add_argument('--grp', action=ag.grouping_arg())
        ap.add_argument('--aa', action=ag.grouped_arg(), default='a')
        ap.add_argument('--bb', action=ag.grouped_arg())
        ap.add_argument('--cc', action=ag.grouped_arg())
        argstr = '--bb=b0 --grp=a --aa=a1 --bb=b1 --grp=b --aa=a2 --grp=c'
        args = ap.parse_args(argstr.split())
        assert args._explicit == {'bb'}
        assert args.grp
        assert args.grp['a'].aa == 'a1'
        assert args.grp['a'].bb == 'b1'
        assert args.grp['a'].cc == None
        assert args.grp['a']._explicit == {'aa', 'bb'}
        assert args.grp['b'].aa == 'a2'
        assert args.grp['b'].bb == 'b0'
        assert args.grp['b'].cc == None
        assert args.grp['b']._explicit == {'aa'}
        assert args.grp['c'].aa == 'a'
        assert args.grp['c'].bb == 'b0'
        assert args.grp['c'].cc == None
        assert args.grp['c']._explicit == set()

    def test_non_grouped_args(self):
        """Test non-grouped arguments."""
        ap = ArgumentParser()
        ag = ArgumentGrouping()
        ap.add_argument('--grp', action=ag.grouping_arg())
        ap.add_argument('--aa', action=ag.grouped_arg())
        ap.add_argument('--xx')
        argstr = '--grp=a --aa=a1 --grp=b --aa=a2 --xx=x'
        args = ap.parse_args(argstr.split())
        assert args._explicit == set()
        assert args.grp
        assert args.grp['a'].aa == 'a1'
        assert args.grp['a']._explicit == {'aa'}
        assert args.grp['b'].aa == 'a2'
        assert args.grp['b']._explicit == {'aa'}
        assert args.xx == 'x'
        for key in ['a', 'b']:
            with pytest.raises(AttributeError):
                assert args.grp[key].xx

    def test_two_argument_groupings(self):
        """Test two ArgumentGroupings."""
        ap = ArgumentParser()
        ag1 = ArgumentGrouping()
        ag2 = ArgumentGrouping()
        ap.add_argument('--g1', action=ag1.grouping_arg())
        ap.add_argument('--aa', action=ag1.grouped_arg())
        ap.add_argument('--bb', action=ag1.grouped_arg())
        ap.add_argument('--g2', action=ag2.grouping_arg())
        ap.add_argument('--cc', action=ag2.grouped_arg())
        ap.add_argument('--dd', action=ag2.grouped_arg())
        argstr = '--g1=a --aa=a1 --g2=c --bb=b1 --cc=c1 --g1=b --g2=d --cc=c2 --dd=d2 --aa=a2'
        args = ap.parse_args(argstr.split())
        assert args._explicit == set()
        assert args.g1
        assert args.g1['a'].aa == 'a1'
        assert args.g1['a'].bb == 'b1'
        assert args.g1['a']._explicit == {'aa', 'bb'}
        assert args.g1['b'].aa == 'a2'
        assert args.g1['b'].bb == None
        assert args.g1['b']._explicit == {'aa'}
        assert args.g2
        assert args.g2['c'].cc == 'c1'
        assert args.g2['c'].dd == None
        assert args.g2['c']._explicit == {'cc'}
        assert args.g2['d'].cc == 'c2'
        assert args.g2['d'].dd == 'd2'
        assert args.g2['d']._explicit == {'cc', 'dd'}

    def test_two_grouping_arg_error(self):
        """Test that two grouping_arg calls raise ArgumentError."""
        ap = ArgumentParser()
        ag = ArgumentGrouping()
        ap.add_argument('--grp', action=ag.grouping_arg())
        with pytest.raises(
                ArgumentError,
                match='Action "grouping_arg" already used for argument --grp'):
            ap.add_argument('--grp2', action=ag.grouping_arg())

    def test_convenience_funcs_simple(self):
        """Test ArgumentGrouping convenience functions."""
        ap = ArgumentParser()
        ap.add_argument('--grp', action=grouping_arg())
        ap.add_argument('--aa', action=grouped_arg(), default='a')
        ap.add_argument('--bb', action=grouped_arg())
        argstr = '--bb=b0 --grp=a --aa=a1 --bb=b1 --grp=b --aa=a2 --grp=c'
        args = ap.parse_args(argstr.split())
        assert args._explicit == {'bb'}
        assert args.grp
        assert args.grp['a'].aa == 'a1'
        assert args.grp['a'].bb == 'b1'
        assert args.grp['a']._explicit == {'aa', 'bb'}
        assert args.grp['b'].aa == 'a2'
        assert args.grp['b'].bb == 'b0'
        assert args.grp['b']._explicit == {'aa'}
        assert args.grp['c'].aa == 'a'
        assert args.grp['c'].bb == 'b0'
        assert args.grp['c']._explicit == set()

    def test_convenience_funcs_grouping_arg_already_used(self):
        """Test that convenience functions support only one grouping."""
        ap = ArgumentParser()
        with pytest.raises(
                ArgumentError,
                match='Action "grouping_arg" already used for argument --grp'):
            ap.add_argument('--grp2', action=grouping_arg())


class TestArgumentGroupingGroupedActions:

    """Tests for ArgumentGrouping, grouped_arg with an explicit action."""

    def test_explicit_store(self):
        """Test action "store" (default)."""
        ap = ArgumentParser()
        ag = ArgumentGrouping()
        ap.add_argument('--grp', action=ag.grouping_arg())
        ap.add_argument('--aa', action=ag.grouped_arg('store'), default='a')
        ap.add_argument('--bb', action=ag.grouped_arg('store'))
        ap.add_argument('--cc', action=ag.grouped_arg('store'))
        argstr = '--bb=b0 --grp=a --aa=a1 --bb=b1 --grp=b --aa=a2 --grp=c'
        args = ap.parse_args(argstr.split())
        assert args._explicit == {'bb'}
        assert args.grp
        assert args.grp['a'].aa == 'a1'
        assert args.grp['a'].bb == 'b1'
        assert args.grp['a'].cc == None
        assert args.grp['a']._explicit == {'aa', 'bb'}
        assert args.grp['b'].aa == 'a2'
        assert args.grp['b'].bb == 'b0'
        assert args.grp['b'].cc == None
        assert args.grp['b']._explicit == {'aa'}
        assert args.grp['c'].aa == 'a'
        assert args.grp['c'].bb == 'b0'
        assert args.grp['c'].cc == None
        assert args.grp['c']._explicit == set()

    def test_store_const(self):
        """Test action "store_const"."""
        ap = ArgumentParser()
        ag = ArgumentGrouping()
        ap.add_argument('--grp', action=ag.grouping_arg())
        ap.add_argument('--aa', dest='x', const='aa',
                        action=ag.grouped_arg('store_const'))
        ap.add_argument('--bb', dest='x', const='bb',
                        action=ag.grouped_arg('store_const'))
        ap.add_argument('--cc', dest='x', const='cc',
                        action=ag.grouped_arg('store_const'))
        argstr = '--bb --grp=a --aa --bb --grp=b --aa --grp=c'
        args = ap.parse_args(argstr.split())
        assert args._explicit == {'x'}
        assert args.grp
        assert args.grp['a'].x == 'bb'
        assert args.grp['a']._explicit == {'x'}
        assert args.grp['b'].x == 'aa'
        assert args.grp['b']._explicit == {'x'}
        assert args.grp['c'].x == 'bb'
        assert args.grp['c']._explicit == set()

    @pytest.mark.parametrize(
        "action,default,stored",
        [('store_true', False, True),
         ('store_false', True, False)]
    )
    def test_store_true_false(self, action, default, stored):
        """Test actions "store_true" and "store_false" (parametrized)."""
        ap = ArgumentParser()
        ag = ArgumentGrouping()
        ap.add_argument('--grp', action=ag.grouping_arg())
        ap.add_argument('--aa', action=ag.grouped_arg(action))
        ap.add_argument('--bb', action=ag.grouped_arg(action))
        ap.add_argument('--cc', action=ag.grouped_arg(action))
        argstr = '--bb --grp=a --aa --bb --grp=b --aa --grp=c'
        args = ap.parse_args(argstr.split())
        assert args.grp
        assert args._explicit == {'bb'}
        assert args.grp['a'].aa == stored
        assert args.grp['a'].bb == stored
        assert args.grp['a'].cc == default
        assert args.grp['a']._explicit == {'aa', 'bb'}
        assert args.grp['b'].aa == stored
        assert args.grp['b'].bb == stored
        assert args.grp['b'].cc == default
        assert args.grp['b']._explicit == {'aa'}
        assert args.grp['c'].aa == default
        assert args.grp['c'].bb == stored
        assert args.grp['c'].cc == default
        assert args.grp['c']._explicit == set()

    def test_append(self):
        """Test action "append"."""
        ap = ArgumentParser()
        ag = ArgumentGrouping()
        ap.add_argument('--grp', action=ag.grouping_arg())
        ap.add_argument('--aa', action=ag.grouped_arg('append'), default=['a'])
        ap.add_argument('--bb', action=ag.grouped_arg('append'))
        ap.add_argument('--cc', action=ag.grouped_arg('append'))
        argstr = '--bb=b0 --grp=a --aa=a1 --bb=b1 --grp=b --aa=a2 --aa=a3 --grp=c'
        args = ap.parse_args(argstr.split())
        assert args._explicit == {'bb'}
        assert args.grp
        assert args.grp['a'].aa == ['a', 'a1']
        assert args.grp['a'].bb == ['b0', 'b1']
        assert args.grp['a'].cc == None
        assert args.grp['a']._explicit == {'aa', 'bb'}
        assert args.grp['b'].aa == ['a', 'a2', 'a3']
        assert args.grp['b'].bb == ['b0']
        assert args.grp['b'].cc == None
        assert args.grp['b']._explicit == {'aa'}
        assert args.grp['c'].aa == ['a']
        assert args.grp['c'].bb == ['b0']
        assert args.grp['c'].cc == None
        assert args.grp['c']._explicit == set()

    def test_append_const(self):
        """Test action "append_const"."""
        ap = ArgumentParser()
        ag = ArgumentGrouping()
        ap.add_argument('--grp', action=ag.grouping_arg())
        ap.add_argument('--aa', dest='x', const='aa',
                        action=ag.grouped_arg('append_const'))
        ap.add_argument('--bb', dest='x', const='bb',
                        action=ag.grouped_arg('append_const'))
        ap.add_argument('--cc', dest='x', const='cc',
                        action=ag.grouped_arg('append_const'))
        argstr = '--bb --grp=a --aa --bb --grp=b --aa --grp=c'
        args = ap.parse_args(argstr.split())
        assert args._explicit == {'x'}
        assert args.grp
        assert args.grp['a'].x == ['bb', 'aa', 'bb']
        assert args.grp['a']._explicit == {'x'}
        assert args.grp['b'].x == ['bb', 'aa']
        assert args.grp['b']._explicit == {'x'}
        assert args.grp['c'].x == ['bb']
        assert args.grp['c']._explicit == set()

    def test_count(self):
        """Test action "count"."""
        ap = ArgumentParser()
        ag = ArgumentGrouping()
        ap.add_argument('--grp', action=ag.grouping_arg())
        ap.add_argument('--aa', action=ag.grouped_arg('count'), default=1)
        ap.add_argument('--bb', action=ag.grouped_arg('count'))
        ap.add_argument('--cc', action=ag.grouped_arg('count'))
        argstr = '--bb --grp=a --aa --bb --grp=b --aa --aa --grp=c'
        args = ap.parse_args(argstr.split())
        assert args._explicit == {'bb'}
        assert args.grp
        assert args.grp['a'].aa == 2
        assert args.grp['a'].bb == 2
        assert args.grp['a'].cc == None
        assert args.grp['a']._explicit == {'aa', 'bb'}
        assert args.grp['b'].aa == 3
        assert args.grp['b'].bb == 1
        assert args.grp['b'].cc == None
        assert args.grp['b']._explicit == {'aa'}
        assert args.grp['c'].aa == 1
        assert args.grp['c'].bb == 1
        assert args.grp['c'].cc == None
        assert args.grp['c']._explicit == set()

    def test_extend(self):
        """Test action "extend"."""
        ap = ArgumentParser()
        ag = ArgumentGrouping()
        ap.add_argument('--grp', action=ag.grouping_arg())
        ap.add_argument('--aa', action=ag.grouped_arg('extend'), default=['a'], nargs='+')
        ap.add_argument('--bb', action=ag.grouped_arg('extend'))
        ap.add_argument('--cc', action=ag.grouped_arg('extend'))
        argstr = '--bb b0 --grp=a --aa a1 --bb b1 --grp=b --aa a2 a3 --grp=c'
        args = ap.parse_args(argstr.split())
        assert args.grp
        assert args._explicit == {'bb'}
        assert args.grp['a'].aa == ['a', 'a1']
        assert args.grp['a'].bb == ['b', '0', 'b', '1']
        assert args.grp['a'].cc == None
        assert args.grp['a']._explicit == {'aa', 'bb'}
        assert args.grp['b'].aa == ['a', 'a2', 'a3']
        assert args.grp['b'].bb == ['b', '0']
        assert args.grp['b'].cc == None
        assert args.grp['b']._explicit == {'aa'}
        assert args.grp['c'].aa == ['a']
        assert args.grp['c'].bb == ['b', '0']
        assert args.grp['c'].cc == None
        assert args.grp['c']._explicit == set()

    def test_unknown_action(self):
        """Test unknown action name."""
        ap = ArgumentParser()
        ag = ArgumentGrouping()
        ap.add_argument('--grp', action=ag.grouping_arg())
        with pytest.raises(
                ValueError,
                match='unknown action "unknown"'):
            ap.add_argument('--aa', action=ag.grouped_arg('unknown'))
