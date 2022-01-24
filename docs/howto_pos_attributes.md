# Renaming and final ordering of pos attributes after parsing
After parsing, the positional attributes might have to be renamed and re-ordered, so that Korp can handle them. The tools for this are **vrt-rename** and **vrt-keep**.

The scripts can be found in GitHub in the same place as the tokenizing and parsing scripts [Kielipankki-utilities/vrt-tools](https://github.com/CSCfi/Kielipankki-utilities/tree/master/vrt-tools).

## Finnish language data

The actual order of attributes is shown at the top of the parsed data. It looks like:

	<!-- #vrt positional-attributes: word ref wid lemma pos feat dephead deprel spaces -->


The following command is used to change the attribute name 'feat' into 'msd':

	$ bin/vrt-rename --map feat=msd parsed/input.vrt > parsed/output.vrt


Assuming that the order of attributes for Finnish data (without NERtagging) should be: 

	word ref lemma pos msd dephead deprel wid spaces 

the following command creates this order of attributes:

	$ bin/vrt-keep --field word,ref,lemma,pos,msd,dephead,deprel,wid,spaces parsed/lang_fin_renamed.vrt > parsed/output.vrt


Finally, the first line of the result file should show the correct order of attributes:

	<!-- #vrt positional-attributes: word ref lemma pos msd dephead deprel wid spaces -->



### Finnish NER-tagged data
For Finnish **NERtagged** data the names and order of positional attributes would be:

	<!-- #vrt positional-attributes: word ref lemma pos msd dephead deprel nerbio nertags/ nertag wid spaces -->


## Swedish language data

For Swedish data it might be necessary to change the field name 'lemma' to 'lemma/':

	$ bin/vrt-rename --map lemma=lemma/ parsed/input.vrt > parsed/output.vrt


The order of positional attributes for Swedish data is recommended to be:

	word ref lemma/ pos msd dephead deprel wid spaces


If necessary, the order of attributes can be changed with the same command **vrt-keep** as above.

Finally, the first line of the result file for Swedish data should show the correct order of attributes:

	<!-- #vrt positional-attributes: word ref lemma/ pos msd dephead deprel wid spaces -->

