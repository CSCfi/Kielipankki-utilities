# Tag encoding and decoding
The original structure of data should be preserved as far as possible. Data in TEI-XML format, for example, can have a rich structure of elements like lists, tables, quotes etc. Here it should be decided, which structure is important to be preserved, and how these elements should be named. A standardized set of element names is planned to be created. 

You should make sure, that all additional structural elements are within paragraph elements. These additional structural elements do not have to be on their own line. You would need to encode these tags before tokenizing and decode them after parsing. The scripts **hrt-encode-tags** and **vrt-decode-tags** are created for this purpose. The scripts were created by Jyrki Niemi and are available in GitHub [https://github.com/CSCfi/Kielipankki-utilities/vrt-tools](https://github.com/CSCfi/Kielipankki-utilities/vrt-tools).

The following commands are given based on the assumption, that you created a folder 'bin' in your work directory referring to the folder 'vrt-tools' in GitHub, as recommended in the step [Tokenizing](howto_tokenize.md). 

Before tokenizing, run the script **hrt-encode-tags** on your HRT data:

    bin/hrt-encode-tags input.hrt > input-encoded.hrt

Now use this encoded hrt as the new input data for the tokenizer. Run the tokenizing and parsing tools as described in the guidelines.

After the last parsing step (‘Renaming and final ordering of pos attributes after parsing’) use the script **vrt-decode-tags** for decoding the data.

	bin/vrt-decode-tags parsed.vrt > output_decoded.vrt


The result, here ‘output_decoded.vrt’, is the final VRT file, which is then used to create a package for Korp.


#### Here is an example to illustrate, what the encoding and decoding scripts do:

Example ‘input.hrt’: 

    <text> 
    This text contains <hi rend="italics">words in italics</hi> 
    and <hi rend="bold">others in bold</hi>face. 
    </text> 

Command for encoding:

    hrt-encode-tags input.hrt > input-encoded.hrt 

input-encoded.hrt: 

    <text> 
    <!-- #vrt structure-tag: hi rend="italics"|16 xtcontains wordsinita --> 
    <!-- #vrt structure-tag: /hi|30 sinitalics andothersi --> 
    <!-- #vrt structure-tag: hi rend="bold"|33 italicsand othersinbo --> 
    <!-- #vrt structure-tag: /hi|45 hersinbold face. --> 
    This text contains words in italics 
    and others in boldface. 
    </text> 

Command for tokenizing:

    hrt-tokenize-udpipe input-encoded.hrt > output-encoded.vrt 

output-encoded.vrt:

    <!-- #vrt positional-attributes: wid word spaces --> 
    <text> 
    <!-- #vrt structure-tag: hi rend="italics"|16 xtcontains wordsinita --> 
    <!-- #vrt structure-tag: /hi|30 sinitalics andothersi --> 
    <!-- #vrt structure-tag: hi rend="bold"|33 italicsand othersinbo --> 
    <!-- #vrt structure-tag: /hi|45 hersinbold face. --> 
    <sentence> 
    1   This_ 
    2   text_ 
    3   contains_ 
    4   words   _ 
    5   in  _ 
    6   italics SpacesAfter=\n 
    7   and _ 
    8   others  _ 
    9   in  _ 
    10  boldfaceSpaceAfter=No 
    11  .   SpacesAfter=\n\n 
    </sentence> 
    </text> 

Command for decoding tags: 
(the parsing steps were left out in this example)

    vrt-decode-tags output-encoded.vrt > output.vrt 

output.vrt :

    <!-- #vrt positional-attributes: wid word spaces --> 
    <text> 
    <sentence> 
    1   This_ 
    2   text_ 
    3   contains_ 
    <hi rend="italics" struct_num="|1|"> 
    4   words   _ 
    5   in  _ 
    6   italics SpacesAfter=\n 
    </hi> 
    7   and _ 
    <hi rend="bold" struct_num="|2|" struct_charspan="|" struct_tokens="|others in|" struct_tokens_all="|others in bold|" struct_partnum="|1/2|" struct_continues="|r|"> 
    8   others  _ 
    9   in  _ 
    </hi> 
    <hi rend="bold" struct_num="|2|" struct_charspan="|1-4|" struct_tokens="|bold|" struct_tokens_all="||" struct_partnum="|2/2|" struct_continues="|l|"> 
    10  boldfaceSpaceAfter=No 
    </hi> 
    11  .   SpacesAfter=\n\n 
    </sentence> 
    </text>

