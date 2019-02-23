To convert all files into VRT, run `./convert-all.sh` 

To convert the contents of a single subdirectory, use `./convert-dir.sh [PATH]`

Resulting VRT files can be found below `vrt/`.

To convert a single file into VRT, use
   
    bin/conv.py [FILENAME] [CORPUS_NAME] | 
    perl bin/la_murre-add-clause-elems.pl --remove-cl
    
The script `bin/la_murre-add-clause-elems.pl` splits nested `<cl>...</cl>` elements into consecutive `<clause>...</clause>` elements. The result is written into standard output.