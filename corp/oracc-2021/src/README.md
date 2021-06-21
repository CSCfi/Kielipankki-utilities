# Files 

- ```make_vrt.py``` calls ```oracc_json_parser.py``` to batch process zipped JSONs into VRT.
- ```xlit_fixer.py``` is used to generate fix list for the badly broken cams-gkab corpus (no need to rerun this, but if you do, first generate VRT files for all corpora)
- ```xlit_tools.py``` a tool for normalizing stuff, used by ```orac_json_parser.py```
- ```oracc_generate_defs.py``` a generator for Korp frontend stuff.
- ```oracc_downloader.py``` downloads zipped JSONs.

