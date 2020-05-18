#! /usr/bin/env python3


import pytest


# Make pytest rewrite assertions in scripttestlib
# https://docs.pytest.org/en/latest/writing_plugins.html#assertion-rewriting

pytest.register_assert_rewrite('scripttestlib')


def pytest_addoption(parser):
    parser.addoption(
        '--scripttest-granularity',
        choices=['value', 'outputitem', 'programrun'], default='value',
        help="""
            parametrize scripttestlib tests at the given granularity,
            indicating what is made a pytest test of its own (from
            finest to coarsest): "value" (each value to be tested is
            made its own test), "outputitem" (each output item of a
            program run) or "programrun" (each program run) (default:
            "%(default)s")
        """
        )
