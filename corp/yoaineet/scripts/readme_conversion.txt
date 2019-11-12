16.09.2019

Ylioppilasaineet - Conversion of the data

Original data: RTF
The data was transformed from RTF to HRT (pre-format for conversion to VRT) by Jussi Piitulainen.
In IDA: corpora/Ylioppilasaineet/ylioppilasaineet-alpha.zip

Output: The script 'make_simple_xml.sh' runs all necessary scripts and gives out the result in a simple form of xml,
(HRT) with all needed structural attributes in the elements <text>. 
The output consists of three XML files, one for each of the years 1994, 1999 and 2004.

The HRT data was then tokenized with the script 'hrt-tokenize-udpipe' 
and validated with 'vrt-validate'.

The script 'vrt-fix-sentbreaks' was used to fix incorrect sentence breaks.

The validated VRT data was parsed with the Turku Dependency Treebank (TDT) parser, alpha version. For this step the tool 'TDPipe' was used.

After parsing the data was NER-tagged with FiNER, a part of Finnish Tagtools version 1.4.0: http://urn.fi/urn:nbn:fi:lb-201908161

FIN-CLARIN VRT tools (version 0.8.4): All relevant tools for tokenizing and parsing are available in GitHub https://github.com/CSCfi/Kielipankki-konversio/tree/master/vrt-tools






