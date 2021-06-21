import os
import oracc_json_parser as OJP

def make():
    p = os.listdir('../jsonzip')

    texts = 0
    skipped = 0

    for x in p:
        #if x != 'epsd2-admin-ur3.zip':
        parsed_json = OJP.Converter(OJP.parse_projects([x]))
        parsed_json.make_vrt()
        texts += parsed_json.number_of_texts
        skipped += parsed_json.skipped_texts

    print(texts, skipped)


def merge(files, outfile):
    """ Concatenate VRT files into groups of texts """
    all_ = []
    for fn in files:
        with open('../vrt/' + fn, 'r', encoding='utf-8') as f:
            all_.extend(f.read().splitlines())

    with open('../grouped_vrt/%s.vrt' % outfile, 'w', encoding='utf-8') as f:
        for line in all_:
            f.write(line + '\n')

make()

""" Group vrts in to projects: NOTE!"""
plist = [x for x in os.listdir('../vrt') if x.endswith('.vrt')]

def group(proj):
    return [p for p in sorted(plist) if p.startswith(proj)]

project_abbrs = set([x.split('-')[0].replace('.vrt', '') for x in plist])
projects = {'oracc2021_%s' % abbr: group(abbr) for abbr in project_abbrs}

for abbr, files in projects.items():
    merge(files, abbr)

OJP.save_logs()

#print(os.listdir('../vrt'))


