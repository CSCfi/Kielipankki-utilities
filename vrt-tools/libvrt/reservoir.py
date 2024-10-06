# Copyright 2021 Oscar Benjamin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Reservoir sampling version of Python's random.sample function.  This allows
sampling from an iterable without needing the iterable to be held entirely in
memory at one time and without knowing the length of the iterable ahead of
time. A typical case might be selecting lines from a large text file while
reading the file in a single pass.

Originally written here:
https://bugs.python.org/issue41311
"""


from math import exp, log, log1p, floor
from random import random, randrange, shuffle as _shuffle
from itertools import islice


def sample_iter(iterable, k=1, shuffle=True):
    """Choose a sample of k items from iterable

    shuffle=True (default) gives the items in random order
    shuffle=False preserves the original ordering of the items
    """
    iterator = iter(iterable)
    values = list(islice(iterator, k))

    irange = range(len(values))
    indices = dict(zip(irange, irange))

    kinv = 1 / k
    W = 1.0
    while True:
        W *= random() ** kinv
        # random() < 1.0 but random() ** kinv might not be
        # W == 1.0 implies "infinite" skips
        if W == 1.0:
            break
        # skip is geometrically distributed with parameter W
        skip = floor( log(random())/log1p(-W) )
        try:
            newval = next(islice(iterator, skip, skip+1))
        except StopIteration:
            break
        # Append new, replace old with dummy, and keep track of order
        remove_index = randrange(k)
        values[indices[remove_index]] = None
        indices[remove_index] = len(values)
        values.append(newval)

    values = [values[indices[i]] for i in irange]

    if shuffle:
        _shuffle(values)

    return values