Aikakauslehtikorpus - Conversion of the data

Original data: The corpus data is in TEI XML, with metadata in RDF XML. 
The data is in IDA at /ida/sa/clarin/corpora/Aikakauslehtikorpus/

Conversion process 
Folder structure for conversion: folder 'conversion' added under 'teksti'
within the structure of the original data. 
There the following sub folders are needed: 'results', 'scripts', 'tmp', 'vrt'.
The script *aikakaus_make_simple_xml.sh* gives out the result in a simple form of xml, with all needed structural attributes in the elements <text>.
Notes: The path to each magazine and year in the shell script has to be adapted by hand.
Remember to change the title of the magazine in the xslt:
"Suomen Kuvalehti", "Historiallinen aikakauskirja", "Lakimies", "Suomi".
The result xml files are combined for each magazine and year.

*tokenize.sh* converts the xml to vrt; does the tokenizing and validating of the vrt files, using the scripts available in GitHub: kielipankki-konversio/scripts/prevrt/.
(vrt-paragraize is not used for this corpus, because the data has already paragraphs)

The result files have to be re-named by hand, e.g. kal_perus_ha_1917.vrt

The vrt data was then parsed with the TDT parser and NER-tagged with FiNER.
