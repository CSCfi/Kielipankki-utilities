
# Tests in Python for some scripttestlib features that are difficult to test in
# test_scripttestlib.py


_defs = {
    'empty_output': {
        'stdout': '',
        'stderr': '',
        'returncode': 0,
    },
}

testcases = [
    {
        'name': 'scripttestlib: Reference a reusable definition in Python',
        'input': {
            'cmdline': 'cat /dev/null',
        },
        'output': _defs['empty_output'],
    },
]
