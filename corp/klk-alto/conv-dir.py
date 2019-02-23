#!/usr/bin/env python3

from sys import stderr
from conv import main
import os
import argparse

parser = argparse.ArgumentParser(description='Creates subdirectory vrt/ in given directory and converts Alto XML files in subdirectory alto/ into VRT.')
parser.add_argument('path', help='path to directory containing subdirectory alto/; subdirectory vrt/ is created here')
parser.add_argument('--mets', type=str, help='optional XML file containing metadata')
parser.add_argument('--date', type=str, default="", help='date in format YYYY, YYYYMM or YYYYMMDD; overrides whatever date is found in METS')
args = parser.parse_args()

path = args.path
mets_file = args.mets
date = args.date
mets = {}
if mets_file != None:
    mets = get_mets(args.mets_file)
    if date == '':
        date = get_date(mets)

try:
    os.mkdir(path+'/vrt')
    stderr.write('Created directory %s\n' % (path+'/vrt'))
except FileExistsError:
    pass

alto_files = sorted([ f for f in os.listdir(path+'/alto') if f.endswith('.xml') ])

for xml_filename in alto_files:
    vrt_filename = xml_filename.replace('.xml', '.vrt')
    vrt_string = main(path+'/alto/'+xml_filename, mets, date)
    vrt_file = open(path+'/vrt/'+vrt_filename, 'w', encoding='utf8')
    vrt_file.write(vrt_string)
    vrt_file.close()
    stderr.write("-> %s\n" % ( path+'/vrt/'+vrt_filename ))
