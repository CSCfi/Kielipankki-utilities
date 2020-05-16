import operator

def keeper(*ix):
    '''Like itemgetter except the return getter always returns a tuple,
    even an empty tuple when given an empty index.

    '''
    if len(ix) == 0:
        return lambda arg: ()

    if len(ix) == 1:
        return lambda arg: (arg[ix[0]],)

    return operator.itemgetter(*ix)
