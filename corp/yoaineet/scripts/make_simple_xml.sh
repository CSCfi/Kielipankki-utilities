#!/bin/bash
#create a simple form of xml

echo "combine all xml files per year"
echo "1994"
cat ../hrz/1994/*.hrz > ../conv/ylioppilasaineet_1994_combined.hrz

echo "1999"
cat ../hrz/1999/*.hrz > ../conv/ylioppilasaineet_1999_combined.hrz

echo "2004"
cat ../hrz/2004/*.hrz > ../conv/ylioppilasaineet_2004_combined.hrz


#Add xml header and root element to the combined files
echo "add xml header and root element"
echo "for 1994"
cat <(echo -e '<?xml version="1.0" encoding="UTF-8"?>\n<essays>\n') ../conv/ylioppilasaineet_1994_combined.hrz > ../conv/ylioppilasaineet_1994_format.xml

echo -e '\n</essays>' >> ../conv/ylioppilasaineet_1994_format.xml


echo "for 1999"
cat <(echo -e '<?xml version="1.0" encoding="UTF-8"?>\n<essays>\n') ../conv/ylioppilasaineet_1999_combined.hrz > ../conv/ylioppilasaineet_1999_format.xml

echo -e '\n</essays>' >> ../conv/ylioppilasaineet_1999_format.xml


echo "for 2004"
cat <(echo -e '<?xml version="1.0" encoding="UTF-8"?>\n<essays>\n') ../conv/ylioppilasaineet_2004_combined.hrz > ../conv/ylioppilasaineet_2004_format.xml

echo -e '\n</essays>' >> ../conv/ylioppilasaineet_2004_format.xml


#fix characters
echo "fix characters for 1999"
cat ../conv/ylioppilasaineet_1999_format.xml | perl fix_characters.pl > ../conv/ylioppilasaineet_1999_format_fixed.xml



echo "rename and add text attributes"
echo "for 1994"
java com.icl.saxon.StyleSheet -o ../conv/ylioppilasaineet_1994_output.xml ../conv/ylioppilasaineet_1994_format.xml convert_ylioppilasaineet.xsl

echo "for 1999"
java com.icl.saxon.StyleSheet -o ../conv/ylioppilasaineet_1999_output.xml ../conv/ylioppilasaineet_1999_format_fixed.xml convert_ylioppilasaineet.xsl

echo "for 2004"
java com.icl.saxon.StyleSheet -o ../conv/ylioppilasaineet_2004_output.xml ../conv/ylioppilasaineet_2004_format.xml convert_ylioppilasaineet.xsl

#remove duplicates from 1994
echo "remove duplicates from 1994"
java com.icl.saxon.StyleSheet -o ../conv/ylioppilasaineet_1994_output_without_dupl.xml ../conv/ylioppilasaineet_1994_output.xml remove_duplicates.xsl

#last fixes
echo "last fixes"
echo "for 1994"
cat ../conv/ylioppilasaineet_1994_output_without_dupl.xml | perl last_fixes.pl > ../conv/ylioppilasaineet_1994_output_fixed.xml

echo "for 1999"
cat ../conv/ylioppilasaineet_1999_output.xml | perl last_fixes.pl > ../conv/ylioppilasaineet_1999_output_fixed.xml

echo "for 2004"
cat ../conv/ylioppilasaineet_2004_output.xml | perl last_fixes.pl > ../conv/ylioppilasaineet_2004_output_fixed.xml


