Original data: The OCR’d data is in an XML format with some metadata information added.
To find in IDA at /ida/sa/clarin/corpora/KK_KlK (note the lowercase L in “KK_KlK”, to distinguish it from “KLK”)

Output: The script *make_simple_xml.sh* gives out the result in a simple form of xml, with all needed structural attributes in the elements <text>. 
The output consists of two xml files, one for the Finnish part and one for the Swedish part of ClassicsLibrary.

The corpus is in a test version of Korp already:
https://korp.csc.fi/test-ute/#?cqp=%5B%5D&sort=left&search=lemgram%7Ckaikki..ab.1&stats_reduce=word&corpus=nlfcl_fi
(to find under 'Kirjallisuutta')

Afterwards some problems were found (see KP-791).

One problem still unsolved: <page> elements in the text, coming from the original data. The tokenizer does not mind and adds paragraphs and sentences correctly, but those page elements split sentences.

Possible solution: Encode the page breaks before tokenizing with the 'hrt-encode-tags' script Jyrki is about to write and then restore them after tokenization with 'vrt-decode-tags'. 

