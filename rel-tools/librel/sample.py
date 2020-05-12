'''Rel tools support library.

Performance turned out to be *prohibitively* low. Moved to shuf(1),
which apparently does reservoir sampling since many years. Giving up
on both repeatability and the tracking of input positions. Nice try.

'''

from itertools import islice, repeat
from math import exp, log, floor
from random import Random

def fill(reservoir, *, source, seed = None):
    '''Fill reservoir (a list) with numbered elements from source (an
    iterator), with uniform probability of inclusion in the sample.

    The random seed can be a string (or a bytes object), to set the
    random generator to repeat. If seed is None, the generator is
    initialized from the state of the environment.

    In the event of fewer elements being available from source, the
    reservoir is truncated. Reservoir is also sorted by the 1-based
    index of each element in source.

    '''

    if not isinstance(reservoir, list) or not reservoir:
        raise ValueError('reservoir must be a non-empty list')

    # 2020-04-30 https://en.wikipedia.org/wiki/Reservoir_sampling
    #     
    # "Algorithm L"
    # 
    # (* S has items to sample, R will contain the result *)
    # ReservoirSample(S[1..n], R[1..k])
    #   // fill the reservoir array
    #   for i = 1 to k
    #       R[i] := S[i]
    # 
    #   (* random() generates a uniform (0,1) random number *)
    #   W := exp(log(random())/k)
    # 
    #   while i <= n
    #       i := i + floor(log(random())/log(1-W)) + 1
    #       if i <= n
    #           (* replace a random item of the reservoir with item i *)
    #           R[randomInteger(1,k)] := S[i]  // random index between 1 and k, inclusive
    #           W := W * exp(log(random())/k)

    bits = Random()
    bits.seed(seed)

    # [0.0..1.0) => (0.0..1.0)
    rnd = filter(None, (bits.random() for _ in repeat(None)))

    # {1,...,k}
    ind = (bits.randint(1,k) for _ in repeat(None))

    R = reservoir
    k = len(R)
    R[:] = enumerate(islice(source, k), start = 1)
    i = k

    W = exp(log(next(rnd))/k)
    try:
        while True:
            s = floor(log(next(rnd))/log(1 - W))
            i += s + 1
            R[next(ind) - 1] = (i, next(islice(source, s, s + 1)))
            W *= exp(log(next(rnd))/k)
    except StopIteration:
        reservoir.sort()
