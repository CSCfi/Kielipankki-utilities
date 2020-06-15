#!/usr/bin/env python3
from mets import get_mets
import subprocess
from sys import argv, stderr

mets = get_mets(argv[1])

date = '-'.join([ s.zfill(2) for s in mets['issue_date'].split('.')[::-1] ])
if date == '':
    stderr.write('Error: no date found for mets file ' + argv[1] + "\n")
    exit(1)

# Grep line containing NIDE_ID in linking file which is a csv file.
#
# NIDE_ID is extracted from the name of the mets file which follows
# the format {NIDE_ID}_*.
#
# The eighth field contains DIGI_PDF_URL. However, the first field
# (the name of the newspaper) may contain commas. The first field is
# enclosed by double quotes, but sometimes there are double quotes in
# the name of the newspaper that are escaped as double double quotes.
# The perl replace commands should take care of all these cases and
# remove the first field.
#
# After the first field is removed, extract the seventh field (DIGI_PDF_URL).
mets_file_name = argv[1].split('/')[-1]
nide_id = subprocess.getoutput('echo "%s" | perl -pe "s/^([^_]+)_.*$/\\1/;"' % (mets_file_name))
digi_pdf_url = subprocess.getoutput('grep ",%s," %s | perl -pe \'s/""([^,])/\\1/g; s/^("[^"]*"),(.*)/\\2/;\' | cut -f7 -d\',\'' % (nide_id, argv[2]))
if not digi_pdf_url.startswith('"http'):
    stderr.write('Error: no binding url could be extracted for mets file ' + argv[1] + "\n")
    exit(1)
if '/aikakausi/' in digi_pdf_url:
    publ_type = 'aikakausi'
elif '/sanomalehti/' in digi_pdf_url:
    publ_type = 'sanomalehti'
else:
    stderr.write('Error: no publication type could be extracted for mets file ' + argv[1] + "\n")
    exit(1)

# extract binding id from binding url
binding_id = subprocess.getoutput('echo %s | perl -pe "s/.*binding\///; s/#.*//; s/\/pdf//;"' % (digi_pdf_url))

mets.update({'date': date})
mets.update({'binding_id': binding_id})
mets.update({'publ_type': publ_type})
print(mets)
