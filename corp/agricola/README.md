Preparation: Have the original files in a folder 'xml' and organize them in subdirectories:
abckiria, kasikiria, messu, piina, profeetat, psaltari, rucouskiria, sewsitestamenti, veisut  

prepare_2019_12_16.sh: This script fixes minor errors found in the original data and creates the folder structure mentioned above.

To convert all files to VRT, run `./convert-all.sh` 

To convert the contents of a single subdirectory, use `./convert-subcorpus.sh [PATH]`

Resulting VRT files can be found below `vrt/`.

To convert a single file to VRT, use
   
    bin/conv.py [FILENAME] [CORPUS_NAME] | 
    perl bin/la_murre-add-clause-elems.pl --remove-cl
    
The script `bin/la_murre-add-clause-elems.pl` splits nested `<cl>...</cl>` elements into consecutive `<clause>...</clause>` elements. The result is written to standard output.

korp-import.sh runs korp-make for all sub directories.

korp-import_2019_12_16.sh creates a test version for the fixed data. Here also the lemgrams' mapping is corrected with --lemgram-posmap
