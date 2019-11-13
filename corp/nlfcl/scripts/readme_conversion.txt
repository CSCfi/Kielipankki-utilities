Classics Library of the National Library of Finland - Kielipankki version
 - Conversion of the data -

Original data: The OCR’d data is in an XML format with some metadata information added.
To find in IDA at /ida/sa/clarin/corpora/KK_KlK (note the lowercase L in “KK_KlK”, to distinguish it from “KLK”)

Output: The script *make_simple_xml.sh* gives out the result in a simple form of xml, with all needed structural attributes in the elements <text>. 
The output consists of two xml files, one for the Finnish part and 
one for the Swedish part of ClassicsLibrary.

*tokenize_fin.sh* does the tokenizing for the Finnish part 
(using the scripts available in GitHub: kielipankki-konversio/scripts/prevrt/.)

*tokenize_swe.sh* does the tokenizing for the Swedish part.

The tokenized result vrt files were validated with *vrt-validate* 
(available in GitHub: kielipankki-konversio/scripts/prevrt/.).

The vrt data was then parsed with the TDT parser and NER-tagged with FiNER.

After the conversion process it was decided to use the name 'nlfcl' instead of 'KlK'.
The result vrt files were renamed to: nlfcl_fi.vrt and nlfcl_sv.vrt





