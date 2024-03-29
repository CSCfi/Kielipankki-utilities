# How to preserve the original structure of corpus data
## Naming elemens and attributes

For some text corpora the original data may be structured in some way already (e.g. if it is in a form of XML), which should be preserved. There might be tables, lists, highlighting, comments etc.

Because the tokenizer wants the text, paragraph and sentence tags to be on their own line, we call these additional tags 'inline element tags' here. These additional elements can be within sentences or as siblings to sentences, but they always have to be within paragraphs.

Because the tokenizer cannot handle such inline element tags, they have to be encoded in the HRT before tokenizing, and decoded again after parsing.
For this purpose we have the scripts `hrt-encode-tags` and `vrt-decode-tags` available in our vrt-tools, for instructions on how to use them see [docs: tags encoding and decoding](howto_tag_encoding_decoding.md)


This is an attempt to collect names for such elements, which might be used for those corpora universally.

As a basis to start a list, here are the elements used in the text corpus `Lönnrot`:

- alternative        (two different versions of a text structure (word, sentence ...); the old/not used version is carried in the attribute value)
- cell               (part of table)
- correction         (types: additions and deletions; done by the original author. The text content of deletions is carried in the attribute value, whereas the text content of an addition is the content of the element)
- hi                 (highlighting; the kind is given as the attribute value)
- line               (part of linegroup)
- linegroup
- row                (part of table)
- span               (type: e.g. editor_note )
- table


Example of HRT with inline elements:

    <paragraph type="">
    Schildt  <hi rend="underline">sanat</hi>, joista usiammat ovat tavallisia, vähempi osa uusia, lähetän tämän muassa takaisin. Ne uudet sanat, jotka mielestäni ovat huonoja, olen pois pyyhkäisnyt.
    </paragraph>



Example for a nested element 'correction':
	
	<paragraph type="">
	(...)
    Italialainen, Hispanialainen, Hunkarialainen, Greekalainen, Wenäläinen, kukin kirjoittavat niitä kielensä luonnon mukaan, <span type="editor_note" text="lisäys seuraavalla rivillä"> </span><correction type="addition" orig="" level="1"><correction type="addition" orig="" level="2">jos</correction> ehkä kohta helpommasti kun Suomalainen saisivat kielensä muukalaiseenki tapaan kääntymään</correction> <correction type="deletion" orig="vaikka niin" level="1"> </correction> peräti toisin kun moni niitä tahtoisi suomeksi kirjoitettavan  –  Elkää siis ennen kun saatte Ingmannin johdon ruvetko maan osottajanne uudistamiseen.
	(...)
	</paragraph>
