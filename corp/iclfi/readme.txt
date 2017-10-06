::asahala/finclarin

How to convert ICLFI?

Please note, that the original ICLFI files contain several structural errors and conversion may be laborous. In the ideal situation it should  work as follows:

1) Force the files into utf-8 by using iconv or iso2utf.sh. Recommended extension is .txt.utf.
2) Plase note that some files may use different characted encodings!
3) Run icl_vrt.py [filename] [vrt_directory] for all files. This will also rename the files according to their CEFR-level.

(these steps should be included in the icl_vrt.py but they arent's)

4) use enumerate.py to add ids to vrt paragraphs and sentences
5) use vrt_fix_chars.py to replace some symbols which will show incorrectly in Korp (this should be done in a more systematic way)

If there are problems, make yourself familiar with the original file structure and run

1) icl_validate.py for every .txd.utf file, it should find you the most broken files which you'll need to fix manually
2) run iclfi_fix.sh and see the loki.txt
3) if the cwb_encode gives you warnings about nested elements (which are caused by broken files), run vrt_validate.py and vrt_find_odds.py to track the errors.


