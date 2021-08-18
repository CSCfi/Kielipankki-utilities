from bisect import bisect_left
from itertools import accumulate
from re import findall

def quant(counter, m):
    '''Return m + 1 values that are keys of counter, in their natural
    order, corresponding to the m + 1 quantile points (or what are
    they, exactly) of the counts, ceiling(k T / m) for 0 <= k <= m,
    with T the sum of the counts.

    '''

    vals = sorted(counter.keys())
    seen = tuple(accumulate(counter[val] for val in vals))
    T = seen[-1]

    return tuple(vals[bisect_left(seen, -(-k * T // m))]
                 for k in range(m + 1))

def sum_of_lengths(regex):
    def stat(text):
        return sum(map(len, findall(regex, text)))
    return stat

def number_of_runs(regex):
    def stat(text):
        return len(findall(regex, text))
    return stat

def max_length(regex):
    def stat(text):
        return max((len(hit) for hit in findall(regex, text)),
                   default = 0)
    return stat
