# Conversion of text data to HRT
The format of the original data can differ between corpora. It can be for example plain text, PDF, XML, RTF. The first aim is to convert this data to **HRT**, a simple form of XML, the pre-format of **VRT** (VeRticalized Text), which is the input format for Korp. For more information on the **VRT** format see [kielipankki: corpus input format](https://www.kielipankki.fi/development/korp/corpus-input-format/). The HRT data must be **UTF-8** encoded Unicode. 

To test the encoding of a file, you can use the command ‘file’:

    file -i filename.txt

You will get information like the following:

    filename.txt:          text/plain; charset=utf-8

For changing the encoding of a file, you can use the command ‘iconv’:

    iconv -f old-encoding -t new-encoding file.txt > newfile.txt

You can get a list of supported encodings:

    iconv -l (lower case ‘L’)

The **HRT** data consists of one or more `<text>` elements per file with all needed structural attributes. The text elements may contain child elements `<paragraph>` and those can be split to `<sentence>` elements.  
For converting the original data to HRT, you can use your preferred tools, may it be Python, Perl, XSLT or something else.

More information about the conversion process can be found from [kielipankki: converting a corpus and importing it to Korp](https://www.kielipankki.fi/development/korp/corpus-import/#Converting_a_corpus_and_importing_it_to_Korp)

In case the original data does not have paragraph and/or sentence tags, these will be added in the tokenizing process. The tokenizer needs indicators like empty lines within the text though, to be able to add the paragraph tags at the correct place.

In case the original data has another or additional structure (e.g. tables, line groups), they preferably should be preserved in the HRT format. A guideline on how to preserve the original structure with a standardized set of element names can be found from [docs: naming inline elements](naming_inline_elements_hrt.md). In this case you would need to encode these inline elements before tokenizing and decode them after parsing. A guideline on how to use the **tag encoding and decoding scripts** can be found from [docs: tag encoding and decoding](howto_tag_encoding_decoding.md).

Note that all `text` tags as well as all `paragraph` and `sentence` element tags must be on their own line, and they have to be at the beginning of the line (be aware of empty spaces here).

Example of **HRT** format:

    <text author="Agricola, Mikael" contributor="" title="Se meiden Herran Jesusen Christusen pina, ylesnousemus  ia taiuaisen astumus, niste neliest euangelisterist coghottu." year="1549" lang="fin" datefrom="15490101"  dateto="15491231" timefrom="000000" timeto="235959" natlibfi="Klassikkokirjasto, Kansalliskirjasto." rights="" digitized="2017-04-20" filename="KlK_with_timestamps.xml" book_number="975">
    <paragraph>
    <sentence>
    text text text
    </sentence>
    <sentence>
    text text text
    </sentence>
    (…)
    </paragraph>
	<parapraph>
	<sentence>
	text text text
	</sentence>
    <sentence>
    text text text
    </sentence>
    (…)
	</paragraph>
    (etc.)
	</text>


You can add attributes to the `paragraph` and `sentence` element tags, like for example `type='heading'`. If the original data has a similar structure with different names, you could preserve the original element names with the help of an attribute; e.g. `'type_orig='headline'`.

Save the converted file(s) with the shortname of the corpus and ending '.hrt', ideally in a folder named 'hrt'.
