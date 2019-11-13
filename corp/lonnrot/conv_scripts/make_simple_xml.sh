#!/bin/bash
#create a simple form of xml

#echo "combine all xml files to one"
#for i in ../orig_20191002/*.xml; do echo -e "\nFilename: $i"; cat "$i"; done > ../conv_20191002/tmpfile; mv ../conv_20191002/tmpfile ../conv_20191002/loennrot_combined.xml;

echo "clean xml"
cat ../conv_20191002/loennrot_combined.xml | perl clean_xmldata.pl > ../conv_20191002/loennrot_clean.xml

echo "add filename to letter"
cat ../conv_20191002/loennrot_clean.xml | perl add_filename.pl > ../conv_20191002/loennrot_clean_withfilename.xml

echo "add xml header and root element"
cat <(echo -e '<?xml version="1.0" encoding="UTF-8"?>\n<letters>\n') ../conv_20191002/loennrot_clean_withfilename.xml > ../conv_20191002/loennrot_clean_fixed.xml

echo -e '\n</letters>' >> ../conv_20191002/loennrot_clean_fixed.xml


echo "create text element with attributes"
java com.icl.saxon.StyleSheet -o ../conv_20191002/loennrot_output.xml ../conv_20191002/loennrot_clean_fixed.xml convert_loennrot.xsl


echo "optimize metadata"
##formats the metadata and cleans data
cat ../conv_20191002/loennrot_output.xml | perl clean_metadata.pl > ../conv_20191002/loennrot_output_metadata.xml

echo "some fixes after cleaning"
cat ../conv_20191002/loennrot_output_metadata.xml | perl clean_metadata_fixes.pl > ../conv_20191002/loennrot_output_metadata_fixed.xml

echo "add level to nested elements"
java com.icl.saxon.StyleSheet -o ../conv_20191002/loennrot_output_nested_elements.xml ../conv_20191002/loennrot_output_metadata_fixed.xml nested_elements.xsl

echo "create file Swedish"
##collect all Swedish works in one file
java com.icl.saxon.StyleSheet -o ../conv_20191002/loennrot_lang_swe.xml ../conv_20191002/loennrot_output_nested_elements.xml only_swe.xsl


echo "clean Swedish"
##last fixes, remove root element
cat ../conv_20191002/loennrot_lang_swe.xml | perl clean.pl > ../conv_20191002/loennrot_lang_swe_fixed.xml


echo "create file Finnish"
##collect all Finnish works in one file
java com.icl.saxon.StyleSheet -o ../conv_20191002/loennrot_lang_fin.xml ../conv_20191002/loennrot_output_nested_elements.xml only_fin.xsl


echo "clean Finnish"
cat ../conv_20191002/loennrot_lang_fin.xml | perl clean.pl > ../conv_20191002/loennrot_lang_fin_fixed.xml



