import html, sys

# Department names do contain spaces and ampersands:
# 'Frågor & svar'
# 'Sex & sånt'
# 'Jord- & skogsbruk'
#
# At least one contains vertical bar (not a main department):
# 'X3M | De bästa intervjuerna'
# Eventually decided to replace that with /.
# Have reconsidered and now replace with ¦ instead.
# Incidentally, any replacement breaks an URL or such.
#
# No " ' < > seen so far.

def finish_av(value):
    if "'" in value: print('attr', repr(value), file = sys.stderr)
    if '"' in value: print('attr', repr(value), file = sys.stderr)
    if '|' in value:
        print('attr in ', repr(value), file = sys.stderr)
        value = value.replace('|', '\N{BROKEN VERTICAL BAR}')
        print('attr out', repr(value), file = sys.stderr)
    return html.escape(value, quote = True)

def finish_avs(values):
    '''The "set-valued" thing. Too specific, *need* refactoring!'''
    return '|' + ''.join('{}|'.format(finish_av(dep['name']))
                         for dep
                         in values)

def finish_t(token):
    # if '<' in token: print(repr(token), file = sys.stderr)
    # if '>' in token: print(repr(token), file = sys.stderr)
    # if '&' in token: print(repr(token), file = sys.stderr)
    if '|' in token: print('token', repr(token), file = sys.stderr)
    return html.escape(token.replace(' ', '\xa0'), quote = False)
