# Specialties and difficulties found while converting text corpora

## Lehdet90ff
Original data: 

- Format: PDF, converted to text with ABBYY Fine READER

- Most data was harvested from the internet (scripts created by Aleksi)


Action needed:

- NOTE: Some data was not UTF-8! Always check the format and change if necessary!

- Metadata has to be collected ‘by hand’ (title, date).

- Script takes care of adding links to the original web pages (created by Aleksi)

- Tokenizing done by Aleksi’s scripts

- Parsing done by Jussi


## Classics Library
Original data: 

- Format: XML, UTF-8, has metadata

- OCR’d data of partly poor quality

- Elements marking page breaks

- Some page elements split sentences

- Original data contains duplicates of whole works as well as part of works

- Original data contains empty books

- Original data contains works written in other languages than Finnish or Swedish


Action needed:

- Split data into two parts: Finnish and Swedish

- Remove duplicates

- Remove empty works and those written in other languages

- Sort data by author and year

- Create a list of all works, sorted by author, and add to portal (linked to from Metashare)

- Add links to original PDFs in Doria to the metadata of the corpus (as attribute of ‘text’)

- Encode and decode the data (because of inline elements, here page elements)


Not needed for publication right now; could be done for a later version:

- The deletion of duplicates of parts of works

- Add to Korp the support for the links to downloadable PDFs




## Lönnrot
Original data: 

- Format: TEI XML, UTF-8, has metadata

- Original structure to be preserved (table, linegroup etc. …)

- Inline elements (as a result of preserving the original structure)

- Nested elements (corrections, like additions and deletions of text done by the author)

- Markup of parts of words (sub-token structure)

- (Empty) page break elements sometimes split sentences and paragraphs


Action needed:

- Split data in two parts: Finnish and Swedish

- Sort data by addressee and year

- Create feature-set-valued attributes (e.g. langs="|se-SE:85|et-ET:10|fi-FI:5|")

- Deal with inline elements (think of names of elements/attributes, make sure they are all within paragraph structure; run encoding and decoding scripts)

Not needed for publication right now; could be done for a later version:

-	Take care of nested elements

-	Take care of sub-token structure


## STT
Original data: 

- Format: XML, UTF-8, has metadata

- Original data in thousands of small files (batch processing on such data is slow)

- Three empty files detected

- Lots of meta information


Action needed:

- Combine files for each year

- Find and remove empty files

- Remove unwanted data from corpus (articles with headline containing ‘EI ULOS’)

- Create feature-set-valued attributes for subjects given in a certain order and on different levels 

- Deal with inline elements (run encoding and decoding scripts)


## Ylioppilasaineet
Original data: 

- Format: RTF, transformed to HRT by Jussi

- Contains several characters marked as {name}, e.g. {Alpha}

- Data contains duplicates


Action needed:

- Fix characters

- Remove duplicates

- Combine files for each year


## OpenSubtitles/Wikipedia
Original data: 

- Format: parsed VRT (from Tatu Huovilainen)

- closing tags </sentence> and </file> are missing in every file

- data contains control characters


Action needed:

- Fixes: Add closing tags, remove control characters (Jussi)

- Parse the data with the TDT parser and keep the existing annotations as secondary ones

- Find a solution on how to present the data with two sets of annotations in Korp (Jyrki)
