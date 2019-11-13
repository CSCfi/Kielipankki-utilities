#!/bin/bash
#create a simple form of xml

echo "unify KlK elements"
##creates klk elements and book-numbers seperately
cat KlK_with_timestamps.xml | perl uniform_klk.pl > KlK_clean.xml

echo "add metadata"
##extracts metadata from doria_metadata file
java com.icl.saxon.StyleSheet -o KlK_meta_insert.xml KlK_clean.xml insert_metadata.xsl

echo "add work_id"
cat KlK_meta_insert.xml | perl add_work_id.pl > KlK_with_work_id.xml

echo "create text element with attributes"
##creates text elements with attributes
java com.icl.saxon.StyleSheet -o KlK_output.xml KlK_with_work_id.xml convert_klk.xsl

echo "optimize metadata"
##formats the metadata
cat KlK_output.xml | perl clean_metadata.pl > KlK_output_metadata.xml


echo "create file Swedish"
##collect all Swedish books in one file
java com.icl.saxon.StyleSheet -o lang_swe.xml KlK_output_metadata.xml only_swe.xsl

echo "fix lang attributes for Swedish"
cat lang_swe.xml | perl fix_lang_attr_swe.pl > lang_swe_fixed.xml


#echo "remove unnecessary spaces for Swedish"
#cat lang_swe_fixed.xml | sed 's/^ *//' | sed 's/ *$//' | sed 's/  */ /g' - > KlK_swe_clean.xml
#cat lang_swe_fixed.xml | sed 's/^\s+|\s+$|\s+(?=\s)//g' - > KlK_swe_clean.xml


#echo "remove redundant blank lines for Swedish"
##This output xml is the input for the tokenize scripts
#cat -s KlK_swe_clean.xml > KlK_swe_result.xml


echo "create file Finnish"
##Collect all Finnish books in one file
java com.icl.saxon.StyleSheet -o lang_fin.xml KlK_output_metadata.xml only_fin.xsl

echo "fix lang attributes for Finnish"
cat lang_fin.xml | perl fix_lang_attr_fin.pl > lang_fin_fixed.xml


#echo "remove unnecessary spaces for Finnish"
#cat lang_fin_fixed.xml | sed 's/^ *//' | sed 's/ *$//' | sed 's/  */ /g' - > KlK_fin_clean.xml
#cat lang_fin_fixed.xml | sed 's/\s+$|\s+(?=\s)//g' - > KlK_fin_clean.xml
#cat lang_fin_fixed.xml | sed 's/ *$//' | sed 's/  */ /g' - > KlK_fin_clean.xml

#echo "remove redundant blank lines for Finnish"
##This output xml is the input for the tokenize scripts
#cat -s KlK_fin_clean.xml > KlK_fin_result.xml



