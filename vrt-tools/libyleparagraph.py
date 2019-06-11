# For YLE SV, could probably be a little smarter - no idea how much
# could be gained easily - adapt for other material.

# paragraphs(text) = split at empty line and normalize to one line each

from itertools import groupby

def paragraphs(text):
    yield from (' '.join(lines)
                for kind, lines
                in groupby(text.splitlines(), hastext)
                if kind)

def hastext(line):
    '''True if line has some non-whitespace in it, for grouping non-empty
    lines when tokenizing multiparagraph text. (The empty lines
    separate paragraphs.)

    '''
    
    return bool(line.strip())
