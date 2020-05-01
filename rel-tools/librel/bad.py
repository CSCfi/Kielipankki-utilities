# had to break an apparent circularity of import

class BadData(Exception): pass # stack trace is just noise
class BadCode(Exception): pass # this cannot happen
