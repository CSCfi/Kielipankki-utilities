#!/bin/bash
#create a simple form of xml

echo "combine all xml files per year"
echo "1999"
cat ../arkistosiirto1999/*.xml > ../conv/STT_1999_combined.xml



#Add xml header and root element to the combined files
#echo "add xml header and root element"
#echo "for 1992"
#cat <(echo -e '<?xml version="1.0" encoding="UTF-8"?>\n<articles>\n') ../conv/STT_1992_combined.hrz > ../conv/STT_1992_format.xml

#echo -e '\n</articles>' >> ../conv/STT_1992_format.xml



#fix characters
#echo "fix characters for 1999"
#cat ../conv/ylioppilasaineet_1999_format.xml | perl fix_characters.pl > ../conv/ylioppilasaineet_1999_format_fixed.xml



#echo "rename and add text attributes"
#echo "for 1994"
#java com.icl.saxon.StyleSheet -o ../conv/ylioppilasaineet_1994_output.xml ../conv/ylioppilasaineet_1994_format.xml convert_ylioppilasaineet.xsl



