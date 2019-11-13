#!/bin/bash
#create a simple form of xml


#path has to be adapted for each magazine and year
#remember to change the title of magazine in convert xsl
for file in ../../ydin/su/su-1935/*.xml

do
    echo "$file"
    namewith="${file##*/}"
    name="${namewith%.xml}"
    echo "$name"

    echo "clean xml data"
    ##removes stylesheet and dtd information
    cat "$file" | perl clean_xmldata.pl > ../tmp/"$name"_clean.xml


    echo "create text element with attributes"
    ##creates text elements with attributes
    java com.icl.saxon.StyleSheet -o ../tmp/"$name"_output.xml ../tmp/"$name"_clean.xml convert_aikakaus_with_meta.xsl

    echo "optimize metadata"
    ##formats the metadata
    cat ../tmp/"$name"_output.xml | perl clean_metadata.pl > ../tmp/"$name"_metadata.xml

    echo "clean issue information"
    cat ../tmp/"$name"_metadata.xml | perl clean_issues.pl > ../tmp/"$name"_issues.xml

    echo "remove unnecessary white spaces"
    cat ../tmp/"$name"_issues.xml | sed 's/^ *//' | sed 's/ *$//' | sed 's/  */ /g' - > ../tmp/"$name"_metadata_clean.xml

    echo "remove redundant blank lines"
    cat -s ../tmp/"$name"_metadata_clean.xml > ../results/"$name"_result.XML
done

echo "combine all result files to one"
cat ../results/*.XML > ../results/all_result.xml &&
rm ../results/*.XML

cat ../results/all_result.xml | perl clean_all.pl > ../results/all_result_clean.xml

rm ../results/all_result.xml

echo "remove files from folder tmp"
rm ../tmp/*.xml



