# Oracc to Korp conversion

## Updating the project list
At first, update ```/info/projects.txt``` with the most recent data. Information about Oracc's contents can be found at [http://oracc.museum.upenn.edu/projects.json](http://oracc.museum.upenn.edu/projects.json). Do not add umbrella projects to the project list. For example, instead of ```saao```, enumerate all its sub-corpora ```saao-saa01, saao-saa02``` etc. and remove or comment the umbrella project out by adding ```#``` before it in the ```projects.txt```. 

## Downloading the zip files
Next run ```/src/oracc_downloader.py``` using the updated ```projects.txt```. It will download zipped Oracc's JSON files into ```jsonzip/``` directory. Some projects are not directly available and they may have to be downloaded manually. One such project is EPSD2, which can be found at [http://oracc.museum.upenn.edu/epsd2/about/corpora/index.html](http://oracc.museum.upenn.edu/epsd2/about/corpora/index.html).

## Parsing the JSON files
Run ```/src/make_vrt.py```. No parameters needed. The script will iterate all files in ```jsonzip/``` directory, extract them, convert them into VRT and save the files into ```vrt/``` directory. Then it groups the VRT files into umbrella projects and saves them into ```grouped_vrt/``` directory.

### Possible issues
Note that reading large zip files consume lots of memory! If you get lots for "corpus is missing or not complete" messages, you may have encountered a memory error. It's recommended to run the script using ```sbatch``` or ```sinteractive``` at Puhti anyway.

You should check that none of the VRT files in ```vrt/``` directory is 0kB in size. If they are, extract the respective JSON zip manually and check if its ```corpusjson/``` directory contains any texts. If it does not, uncomment the respective project from the ```/info/projects.txt``` and delete the zip and VRT file from ```jsonzip/``` and ```vrt/``` directories and rerun the ```merge()``` function in ```src/make_vrt.py``` (remember to uncomment ```make()```!)

If a non-umbrella project JSON file produces a 0kB VRT, there may be someting suspicious in the JSON file. One such file is ```saao-saa01```. I have added a working version of the file to the ```jsonzip_replacements/``` directory, downloaded from [http://oracc.museum.upenn.edu/saao/downloads/](http://oracc.museum.upenn.edu/saao/downloads/).

If you want to regroup projects, give VRT files same prefixes and rerun ```merge()```, e.g. ```contrib-amarna``` logically belongs to ```aemw-xxxx``` and should be put there. 

## Validate VRT files and add them to Korp
Use Jussi's VRT validator to check the produced VRT files just in case.

# What normalizations are done to Oracc data?
Directory ```norm/```contains all mappings between Oracc and Korp notation.

- Divine and Geographical names are standardised following Helsinki normalizations by Tero Alstola.
- Typical lemmatization errors are fixed
- Disgustingly broken transliterations in an unmaintaied cams-gkab corpus are fixed by heuristic rules and mappings generated with ```/src/xlit_fixer.py```
- Transliteration is normalized (determinatives are uppercased, accents are indexed, h-sounds are unified etc.) 
- Periods, language tags etc. are normalized
- POS-tags are simplified

# Logs
Logs can be found from ```/logs/``` directory. They contain list of all changes made to the transliteration and lemmatization of the corpus and new keys that need to be update in the ```norm/``` files.



