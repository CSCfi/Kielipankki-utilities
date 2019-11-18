# A guideline for converting, tokenizing and parsing text corpora
## Preparing a text corpus for importing it to Korp (as processed in Taito)

### Conversion to HRT
The format of the original data can differ between corpora. It can be for example plain text, PDF, XML, RTF. The first aim is to convert this data to **HRT**, a simple form of XML, the pre-format of **VRT** (VeRticalized Text), which is the input format for Korp. For more information on the **VRT** format see [kielipankki: corpus input format](https://www.kielipankki.fi/development/korp/corpus-input-format/). The HRT data must be **UTF-8** encoded Unicode. 

To test the encoding of a file, you can use the command ‘file’:

    file -i filename.txt

You will get information like the following:

    filename.txt:          text/plain; charset=utf-8

For changing the encoding of a file, you can use the command ‘iconv’:

    iconv -f old-encoding -t new-encoding file.txt > newfile.txt

You can get a list of supported encodings:

    iconv -l (lower case ‘L’)

The **HRT** data consists of one or more `<text>` elements per file with all needed structural attributes. The text elements may contain child elements `<paragraph>` and those can be split to `<sentences>`.  
For converting the original data to HRT, you can use your preferred tools, may it be Python, Perl, XSLT or something else.

More information about the conversion process can be found from [kielipankki: converting a corpus and importing it to Korp](https://www.kielipankki.fi/development/korp/corpus-import/#Converting_a_corpus_and_importing_it_to_Korp)

In case the original data does not have paragraph and/or sentence tags, these will be added in the tokenizing process. The tokenizer needs indicators like empty lines within the text though, to be able to add the paragraph tags at the correct place.

In case the original data has another or additional structure (e.g. tables, line groups), they preferably should be preserved in the HRT format. A guideline on how to preserve the original structure with a standardized set of element names can be found from [naming_inline_elements_hrt.md](naming_inline_elements_hrt.md). In this case you would need to encode these inline elements before tokenizing and decode them after parsing. A guideline on how to use the **tag encoding and decoding scripts** can be found from [howto: tag encoding and decoding](howto_tag_encoding_decoding.md).

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


### Tokenizing: Tools and process
The scripts for tokenizing were created by Jussi Piitulainen and can be found in GitHub [https://github.com/CSCfi/Kielipankki-konversio/vrt-tools](https://github.com/CSCfi/Kielipankki-konversio/vrt-tools)

If you have your own copy of ‘Kielipankki-konversio’ on Taito already, you can just update it with the help of the command `git pull`. Then you can create a symbolic link to the folder ‘vrt-tools’ from the respective corpora folder in your working directory, e.g.:

    ln -s /homeappl/home/‘username’/Kielipankki-konversio/vrt-tools/ bin

Now you have the tools available in your corpus folder in a folder named ‘bin’. 

If you have to tokenize a corpus again some time later, you should first update your copy of the folder ‘Kielipankki-konversio’. Go to Kielipankki-konversio in your HOME directory and do `git pull`.
 Of course, this is only one suggestion on how to use the tokenizing scripts.

The scripts for tokenizing are


1. **vrt-dehype**: This script attempts to remove line-breaking hyphens (and page numbers) in plaintext within HRT markup (only needed when such hyphens are found in the data!)


1. **vrt-paragraize**: This script inserts paragraph tags into plaintext within HRT markup using lines of all whitespace as boundary indicators within blocks of plaintext (not needed if the data already has paragraph tags!)


1. **hrt-tokenize-udpipe**: This script tokenizes plaintext within HRT markup. It also adds sentence elements if not there already.

The scripts can be run like this:

    bin/hrt-tokenize-udpipe --out folder/filename_tokenized.vrt folder/filename.hrt

In case all three scripts are needed, they should be run one after the other, in the given order. They could also be combined in a shell script.


### Validation of the result VRT
The result of the tokenizing process should then be validated.
The script for this is **vrt-validate**. The command is: 

    bin/vrt-validate filename.vrt

In case the validator gives out messages, they should be investigated further with **linedump**:
	
    bin/linedump -k 2751241 --repr filename.vrt 
(where the number is the number of the line in question)

It might be, that you have to fix something in your conversion to HRT. Preferably the validator should not give any messages in the end. 

Some messages, e.g. warnings of the following type, could be ignored. This should be decided for each corpus and case individually.

    line	kind	level   issue
    5443	data	warning double space in value: title of text

This warning means, that in line 5443 the attribute 'title' of element 'text' contains a double space in its value. If this is, how the title was given in the original data, you could decide to leave it as is.


### Checking sentence lengths
The tool for checking the sentence length is **vrt-report-element-size**. Checking the number of tokens within a sentence is the default here. It is used like this:

    bin/vrt-report-element-size --filename --summary=V5 folder/filename.vrt

The options --filename and --summary=H5 (or V5 or H11 or H13 for more quantiles etc.) can be used to get a summary report, where the most interesting number for the present purpose is the maximum length of sentences (and for other purposes maybe median and the low and high quartiles).
There is no definite limit in the number of tokens per sentence, but if the number exceeds 100 significantly, it is worth to have a closer look. 

There is a script for splitting extra-long sentences included in the parsing tool TDPipe.


### Fixing sentence breaks
The tokenized data should be checked regarding sentence breaks. Known problems are sentence breaks after abbreviations (e.g. ‘jne.’) or before words starting with a capital letter, like names.

In case you find other problems, it might be helpful to fix the sentence breaks with the script **vrt-fix-sentbreaks**:

	bin/vrt-fix-sentbreaks --out folder/filename_sentfix.vrt folder/filename.vrt



### Parsing with TDPipe
The scripts for parsing were created by Jussi Piitulainen and can be found in GitHub in the same place as the tokenizing scripts [https://github.com/CSCfi/Kielipankki-konversio/vrt-tools](https://github.com/CSCfi/Kielipankki-konversio/vrt-tools).

It is recommended to create a copy of the script TDPipe (available in folder ‘bin’, if you created one as recommended in the tokenizing step) to the corpus folder, one level higher than the data folders, and make it executable:

    cp bin/TDPipe .
    chmod +x TDPipe


#### 1. Packing

The input data for parsing is the tokenized, validated and possibly sentfixed VRT data. The data will be packed in files of a size which is suitable for the parser. In the areas where the data is split, markers will be added, so that the data can be put back together later at the correct cuts.

    bin/game --log logPack bin/vrt-pack -o data folder/

The parser expects to find the input data in a folder named ‘data’, so this is created here for the packed data!

NOTE: It does not work when there is a folder ‘data’ already! In case a corpus needs to be parsed again, the old folder ‘data’ should be either renamed or deleted.

Check the log files: err should be size ‘0’

In file ‘*.out’ the STATUS should be ‘0’.


#### 2. TDPipe

This tool runs the scripts for tagging and parsing.

    bin/gamarr --job parse001 --log logParse --GiB=16 ./TDPipe // data/a001/*.vrf

Give a job name (default job name is ‘game’), give a name for the log folder, maybe ask for more RAM space like here in the example (default is 8 GiB). 
The maximum amount of files the script can handle is 1000 files per array, so this parsing command might have to be run separately for each folder within folder ‘data’.
If the files altogether do not exceed the amount of 1000, the command can be run on all subfolders at once:  `// data/*/*.vrf`

NOTE: In the folder logParse the ‘err’ files are not supposed to be empty here!

Possibilities for checking the queue:

    squeue -l -u 'username' | grep PEN

    squeue -l -u 'username' | grep -Eo 'RUN|PEN' | sort | uniq -c

(-E means I can use the pipe for 'or', and -o means that it shows only the lines with RUN or PEN)

    squeue -l -u 'username' | tail

The parsing process may take some time. After parsing you can check, if the process went through, by looking at the ‘*.out’ files in the logParse.

	grep 'STATUS 0' *.out | wc -l

    grep 'STATUS 1' *.out | wc -l

The result for grapping ‘STATUS 0’ should be the number of all files, for ‘STATUS 1’ the result should be ‘0’.
In case you find one or more instances of ‘STATUS 1’, you could search in the subfolders of ‘data’ for files with suffix ‘*.tmp’. 

	$ find data/ -name '*.tmp'

You can sort or count them:

	$ find data/ -name '*.tmp' | sort

	$ find data/ -name '*.tmp' | wc -l


In the subfolders of ‘data’, for every file ‘\*.vrf’ there should be files with the same name but endings ‘Alookup’, ‘Bmarmot’, ‘Cfillup’ and ‘Dparse’. In case there are ‘\*.tmp’ files for one or more vrf files, you should have a look at the corresponding ‘\*.err’ files in the log folder. Problems could be, that there was not enough space for the job, or that the job was cancelled due to time limits. 

You can extend the RAM by adding the following option to the batch command: 

    --GiB=16

For extending the time for a job you can add the following command:

	--hours=2
	
If there are only a few files affected, you can try to parse them again separately with a command like the following (here with extended RAM and time):	

    $ bin/gamarr --job parse --log logParse1x --GiB=16 --hours=2 ./TDPipe // data/a000/{m012,m043,m065,m071,m107,m144}.vrf


#### 3. FiNER
The script for applying the Finnish named-entity recognition (**FiNER**) on the corpus data is **vrt-finer**. The following command takes the result files from the parsing process, with ending ‘Dparse’, as input and creates output files with the ending ‘Enamed’ in the folder ‘data’.

    bin/gamarr --job names --log logNames --GiB=16 bin/vrt-finer --prefix="" --suffix="_finer" -I Dparse/Enamed // data/a001/*.vrf.Dparse

Give a job name (here ‘names’) and create a log folder (here ‘logNames’). You can ask for more RAM space, like in the example.	
The options given to vrt-finer will create field names with suffix '-finer' for the corresponding attributes. This goes hand in hand with the renaming of fields (step 6 below).

You should check, if the process went through, in the same way as you did after running TDPipe. 

In case you get error messages or even dump cores (files named e.g. core.10850) in the folder where you ran the command, please contact Jussi Piitulainen.		


#### 4. Unpacking
After parsing and NER-tagging, the data is being put back together at the correct cuts, which were marked during the packing process. The script for this is **vrt-unpack**:

    bin/game --log logPack --job unpack bin/vrt-unpack -o folder_out --vrf=vrf.Enamed data/

The log files can go to the same log folder as for packing, as a job name I chose ‘unpack’ here. The output directory has to be a new folder (here: ‘folder_out’). 

The input files’ names have the extension ‘vrf.Enamed’. Folder ‘data’: all subfolders will be worked on.


#### 5. Cleaning up
In this step all columns with dots in their names will be removed.

    bin/gamarr --log logCleanup bin/vrt-drop -i --dots // folder_out/*

Here this is run as an array. Create a new log folder (here 'logCleanup'). An array always needs ‘//’ and then takes all files in the given folder.


#### 6. Renaming and final ordering of pos attributes after parsing
Finally, the positional attributes should be renamed and re-ordered, so that Korp can handle them. The commands are **vrt-rename** and **vrt-keep**. Of course, they can also be run separately.

The following command is used for corpora **not** NER-tagged with vrt-finer:

    bin/vrt-rename --map wid=initid --map feat=msd --map id=ref --map head=dephead --map rel=deprel folder/filename_cleaned.vrt | bin/vrt-keep --names "word,ref,lemma,pos,msd,dephead,deprel,spaces,initid" > folder_final/filename_final.vrt


And this command is used for corpora NER-tagged with vrt-finer:

    bin/vrt-rename --map wid=initid --map feat=msd --map id=ref --map head=dephead --map rel=deprel --map  nertag_finer=nertag folder/filename_cleaned.vrt | bin/vrt-keep --names "word,ref,lemma,pos,msd,dephead,deprel,nertag,propercat_finer,spaces,initid" > folder_final/filename_final.vrt

If your corpus consists of several files and you want to rename and order them all at once, this command can also be run as a bash script. 

The content of the bash script could be:

    #!/bin/bash
    bin/vrt-rename --map wid=initid --map feat=msd --map id=ref --map head=dephead --map rel=deprel "$1" |
    bin/vrt-keep --names "word,ref,lemma,pos,msd,dephead,deprel,spaces,initid" > folder_final/$(basename "$1" .vrt)_final.vrt

The script can be run with gamarr:

    bin/gamarr --job rename-keep --log logReNameKeep sh ./rename-keep.sh // folder_out/*.vrt
    
The input files for this command are in a folder 'out' (the result files from step 5, 'Cleaning up'). The final files go to another folder 'final' and are named *_final.vrt


#### 7. Creating a corpus zip file

Always, but especially if you have several files for one corpus (e.g. one per year), for the following steps it is recommended to create a zip file containing all the final files (result from step 6, 'Renaming and final ordering of pos attributes after parsing). You can do that with the command ‘zip’:

    zip data.zip file1 file2 …	 
or
 
    zip data.zip folder/*

With the second command you create an archive with a sub directory, to which all files are extracted when unzipping.


NOTE: It is recommended to upload the successfully parsed data (as zip file) to the respective corpus folder in IDA, especially if for some reason it is not processed further right away.

In case of data which contains dialect or other specialities (e.g. Iijoki), Melissa created some scripts for testing the parsed data and creating statistics. The instructions for using those scripts will be accessible here (link to be created).


### Creating a Korp package
Encoding VRT data into the CWB database format and creating a Korp package for the corpus can be done with a single command: **korp-make**.

The command should be run from your HOME directory in the respective corpus folder. In this corpus folder you need to have a folder ‘scripts’ containing your (HRT) conversion scripts and a readme about the conversion process. Furthermore, in the corpus folder you need to have a readme about the corpus (you can find the according information from METASHARE) and a configuration file named **corpus.conf**. 

The basic content of the corpus.conf is just the path to the scripts' folder:

    script-dir = $HOME/'corpusname'/scripts/
   
For licensed data the content of the corpus.conf could be:

    script-dir = $HOME/'corpusname'/scripts/
    licence-type = ACA
    lbr-id = 201407301 

(the libr-id is usually the URN of the top META-SHARE article for the corpus)

And you should add a line for the positional attributes, which were added during the parsing process:

For corpora **not** NER-tagged with vrt-finer:

    input-attrs = ref lemma pos msd dephead deprel spaces initid


In case you used vrt-finer to NER-tag the corpus, the line would be like this:

    input-attrs= ref lemma pos msd dephead deprel nertag propercat_finer spaces initid


The command for running korp-make is:

    /proj/clarin/korp/scripts/korp-make --config-file=corpus.conf --readme-file=readme_about_'corpus'.txt 'korp-id' /wrk/'username'/'corpus'/'corpus-parsed'.zip



The korp-id for the corpus should be derived from the short name of the corpus, which is given in the Metashare article. It can consist of lower-case letters and underscores.

If korp-make has to be re-run on the same corpus, add option `--force` to the above mentioned command (this will overwrite all existing data).

The script korp-make creates a corpus package under `/proj/clarin/korp/corpora/pkgs/'corpus_id'/` and it writes a log file to `/proj/clarin/korp/corpora/log/`on Taito(-shell).


### Adding the Korp configuration to the Korp frontend
This part of the pipeline consists of making changes to the Korp configuration and translation files on the **corpus-specific branch** of the Korp frontend repository and committing the changes.

For further information please see the instructions for [Korp configuration](howto_Korp_configuration.md "howto_Korp_configuration.md").


### Installing the corpus package and configuration
At this stage, the corpus configuration should be installed on a separate test instance of Korp. Jyrki Niemi takes care of this! Just let him know, when you pushed your changes of the Korp configuration and translation files in GitHub.

### Testing the corpus in Korp
Check that the corpus shows up and works as expected in the test instance of Korp. The corpus should be tested by at least one other person of our group. 

We would need detailed instructions on what has to be tested. (todo: link)


### Informing others of the corpus and request feedback
After the test version works as expected, you should inform at least *fin-clarin(at)helsinki.fi* and the original corpus owner or compiler if applicable. In practice, rise this topic up in our team meeting to get info about whom to inform and decide who is going to test your corpus. If you get feedback, you might need to re-do some of the previous steps. 


### Installing the corpus configuration to the production Korp
Once the corpus works as desired in the test version of Korp, it is ready to be installed on the production Korp. Jyrki Niemi takes care of that. We agreed, that usually the corpus will be published in a beta version for approximately two weeks. If during this time someone notices problems and changes need to be done to the data, it will not be necessary to change the version of the corpus.

The METASHARE article for your corpus should be checked and possibly updated. The access location (Korp URN) has to be added to the METASHARE article as well as to the Korp configuration, if not done earlier.


### Archiving the corpus package
After the corpus is installed on the production Korp, the **corpus package** should be uploaded to the IDA storage service. Usually there is a folder for your corpus in IDA already, containing e.g. the original data. The package should be added to the same folder.
You can find the corpus package in Taito(-shell) under `/proj/clarin/korp/corpora/pkgs/'corpus_id'/`.

Instructions on how to upload and download data to IDA can be found here: [IDA user guide](https://www.fairdata.fi/en/ida/user-guide/ "https://www.fairdata.fi/en/ida/user-guide/"). 

If you decide to use the IDA client in Taito, you can find instructions on configuring and using IDA from the command line here: [CSC guide for archiving data](https://research.csc.fi/csc-guide-archiving-data-to-the-archive-servers#3.2.2 "https://research.csc.fi/csc-guide-archiving-data-to-the-archive-servers#3.2.2").

Assuming that you use the IDA client on Taito, the command for uploading the package to IDA is:

    ida upload -v corpora/'corpus'/file.tgz file.tgz
    
-v means 'verbose' and will give you information about the process of uploading.
    
Example:

    ida upload -v corpora/ylioppilasaineet/yoaineet_korp_20190916.tgz yoaineet_korp_20190916.tgz

In case the folder for your corpus is already frozen in IDA, you should create a folder of the same name in the stage area and upload your package here. During the next 'freeze' the content of these folders will be combined.
NOTE: It is usually not recommended to unfreeze already frozen data in IDA!


### Archiving your conversion scripts
Your **conversion scripts** for creating the HRT should be preserved. It is recommended to upload them to GitHub. The place for your scripts is in 'Kielipankki-konversio'. Do 'git pull' to make sure your copy of the repository is up to date. Then change to the sub folder 'corp' and create a new folder for your corpus in here. Copy your conversion scripts to this folder.

The command for adding your scripts to the repository (from Kielipankki-konversio/corp/'your_corpus'/) is:

    git add .
    
With the following command you can check the git status:

    git status

Commit your changes:

    git commit
    
This will ask for a short description of your action (e.g. 'conversion scripts for 'corpus' added')
    
Finally you can push your changes:

    git push
    
    

### Additional information
For additional information, please see the following links: 


[process overview](https://www.kielipankki.fi/development/korp/process-overview/ "https://www.kielipankki.fi/development/korp/process-overview/")

[converting a corpus and importing it to Korp](https://www.kielipankki.fi/development/korp/corpus-import/#Converting_a_corpus_and_importing_it_to_Korp "https://www.kielipankki.fi/development/korp/corpus-import/#Converting_a_corpus_and_importing_it_to_Korp")

[collection of specialties found in text corpora](collection_specialties_of_corpora.md)
