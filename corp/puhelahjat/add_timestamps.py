#! /usr/bin/env python3
# -*- mode: Python; -*-

import os, re, sys, tempfile, traceback
import argparse

def getargs():
    argparser = argparse.ArgumentParser(
        description='''Add timestamps to VRT files''')
    argparser.add_argument('filename',
                           help='name of input file')

    return argparser.parse_args()

def read_timestamp_file(filename):
    timestamps = []
    with open(filename, 'r') as f:
        timestamp_file = f.readlines()
        for row in timestamp_file:
            if row.startswith('<'):
                continue
            else:
                row = row.split("\t")
                timestamps.append((row[0],row[1],row[2]))
    return timestamps
        

def main(args):

    ins = args.filename
    path = re.search('clt\d*_.*\d', ins).group(0)
    timestamps = read_timestamp_file("/scratch/clarin/tmp/puhelahjat_korp/puhelahjat/v1/puhelahjat_v1_token_alignments_vrt/"+path+".utf8.vrt")
    ous = re.sub(".vrt","_timestamps.vrt",ins)
    with open(ins,'r') as infile:
        with open(ous,'w') as outfile:
            for line in infile:
                line = line.strip("\n")
                if line.startswith('<!'):
                    line = '<!-- #vrt positional-attributes: wid word spaces begin_time end_time-->'
                    print(line,file=outfile)
                elif line.startswith('<'):
                    print(line,file=outfile)
                else:
                    cols = line.split("\t")
                    for stamp in timestamps:
                        if stamp[0] == cols[1]:
                            line += "\t" + stamp[1] + "\t" + stamp[2]
                            timestamps.remove(stamp)
                            break
                    print(line,file=outfile)
                    
                

if __name__ == '__main__':
    args = getargs()
    main(args)
