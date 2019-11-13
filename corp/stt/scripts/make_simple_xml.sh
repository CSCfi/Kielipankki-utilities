#!/bin/bash
#create a simple form of xml

for file in ../conv/STT_201*_combined.xml

do
    echo "$file"
    namewith="${file##*/}"
    name="${namewith%_combined.xml}"
    echo "$name"

    echo "remove xml headers"
    cat "$file" | perl pre_fix.pl > ../tmp/"$name"_pre.xml


    echo "add xml header and root element"
    cat <(echo -e '<?xml version="1.0" encoding="UTF-8"?>\n<articles>\n') ../tmp/"$name"_pre.xml > ../tmp/"$name"_format.xml

    echo -e '\n</articles>' >> ../tmp/"$name"_format.xml


    echo "rename and add text attributes"
    java com.icl.saxon.StyleSheet -o ../tmp/"$name"_out.xml ../tmp/"$name"_format.xml convert_STT.xsl


    echo "fix metadata"
    cat ../tmp/"$name"_out.xml | perl fix_metadata.pl > ../tmp/"$name"_meta_fixed.xml

    echo "remove unwanted articles"
    java com.icl.saxon.StyleSheet -o ../tmp/"$name"_cleaned.xml ../tmp/"$name"_meta_fixed.xml remove_articles.xsl

    echo "fix subjects and codes"
    #cat ../tmp/"$name"_meta_fixed.xml | perl fix_subjects.pl > ../tmp/"$name"_subj_fixed.xml
    cat ../tmp/"$name"_cleaned.xml | perl fix_subjects.pl > ../hrt/"$name"_result.hrt

done

echo "remove files from tmp folder"
rm ../tmp/*.xml


