Date: Mon, 12 Sep 2016 14:24:16 +0300
From: Aleksi Sahala
To: Ute Dieckmann
Cc: Jyrki Niemi
Subject: Scripts and files

[...]

> raw_to_vrt.py
Converts ABBYY plain text into VRT. You'll have to modify this script
for every magazine individually (change the regexp to match the way
issue/year has been represented in the filename). See the script for
more information.

usage: python3 raw_to_vrt.py [input_file] > [output]

Some magazines may also have a separate meta-data file with urls to
the original PDFs. These are named logfile.txt or read.me. Each
magazine has also a file called Hot Folder Log.txt which must be
removed.

Note that some files may not have issue/year information at all. If
there are just few of these, I've tried to find this information
manually from the file and rename them accordingly (you'll have to
modify also the metadata file if such exists, as the metadata is
aligned with the txt files by filename). If there are dozens of
undated files, I'd probably leave them undated instead of going
through all of them manually.

> vrt_tools.py
A (rather ugly) script for tokenizing and splitting the text into
sentences. This was originally written for internet discussion data
which didn't follow the normal ortography/grammar, but it works ok
with the OCR'd data too. This script is called automatically by
raw_to_vrt.py

I will rewrite this script at some point, there are few gimmicks that
should be re-designed (e.g. preserving different quotes, now it
converts them all into "; and handling html-entities consistently).

> vrt_fix_sents.py
Does some post -processing for the vrt by removing empty sentences and
paragraphs and giving them each an id number. This should be run after
all the individual vrt files have been combined.

usage: python3 vrt_fix_sents.py < [input] > [output]

> loop2.sh
This bash file:

1) removes the Hot Folder Log.txt
2) removes BOM from file headers
3) runs raw_to_vrt.py for every .txt file
4) combines the results into one file
5) runs vrt_fix_sents.py for this combined file and produces ´all.VRT´
6) runs Jyrki's vrt-fix-attrs.py for the result (this will be needed
when you'll import the file into Korp) and saves it as ´all.fix´

You should store the ´all.VRT´ and rename it
"lehdet_magazinesname.vrt" (please use lowercase and [a-z_] only),
this file will be later sent to Jussi Piitulainen for morphological
analysis. ´all.fix´ is the file that will be imported into Korp with
cwb-encode (when you'll get the CSC account and your own test Korp).

It's often wise to take a look how the vrt file looks, especially
those dateform and dateto attributes in the text element that your
regexp has produced. I have used grep for this.

[...]
