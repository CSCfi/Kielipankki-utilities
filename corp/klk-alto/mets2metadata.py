#!/usr/bin/env python3
from mets import get_mets
import subprocess
from sys import argv, stderr

mets = get_mets(argv[1])

date = ''.join([ s.zfill(2) for s in mets['issue_date'].split('.')[::-1] ])
if date == '':
    stderr.write('Error: no date found for mets file ' + argv[1] + "\n")
    exit(1)

link_info = subprocess.getoutput('grep -m 1 "%s" %s' % (mets['issue_title'], argv[2]))
if link_info == '':
    stderr.write('Error: no link info found for mets file ' + argv[1] + "\n")
    exit(1)
else:
    binding_info = link_info.split(',')[8].replace('"','')
    if not binding_info.startswith('http'):
        stderr.write('Error: no binding url could be extracted for mets file ' + argv[1] + "\n")
        exit(1)

mets.update({'date': date})
mets.update({'binding': binding_info})
print(mets)
