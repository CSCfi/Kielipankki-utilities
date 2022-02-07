# Parsing: Tools and process
The input format for the parsing tools is **VRT**. For more information on the **VRT** format see [Kielipankki: corpus input format](https://www.kielipankki.fi/development/korp/corpus-input-format/).

The scripts for parsing can be found in GitHub in the same place as the tokenizing scripts [Kielipankki-utilities/vrt-tools](https://github.com/CSCfi/Kielipankki-utilities/tree/master/vrt-tools).

If you have your own copy of ‘Kielipankki-utilities’ on Puhti already, you can just update it with the help of the command `git pull`. Then you can create a symbolic link to the folder ‘vrt-tools’ from the respective corpora folder in your working directory, e.g.:

    ln -s /homeappl/home/‘username’/Kielipankki-utilities/vrt-tools/ bin

Now you have the tools available in your corpus folder in a folder named ‘bin’.

If you have to tokenize or parse a corpus again some time later, you should first update your copy of the folder ‘Kielipankki-utilities’. Go to Kielipankki-utilities in your HOME directory and update it with the command `git pull`.

It is recommended to always convert data in an interactive batch job session on Puhti.
The command is 'sinteractive', for more information see [CSC: interactive usage](https://docs.csc.fi/computing/running/interactive-usage/).
(in Puhti, always use the 'small' partition).

You can define the resource requests directly within the command line, e.g.:

    sinteractive --account clarin --time 4:00:00 -m 8000


The steps for parsing VRT data are:

### Packing

The input data for parsing is the tokenized, validated and possibly sentfixed VRT data. The data will be packed in files of a size which is suitable for the parser. In the areas where the data is split, markers will be added, so that the data can be put back together later at the correct cuts.

Example for packing the data with the command **vrt-pack**:

    $ bin/game --job pack --log log/pack -C 1 bin/vrt-pack --out data --tokens 1000000 tokenized/

The parser expects to find the input data in a folder named ‘data’, so this is created here for the packed data!

NOTE: The script does not work when there is a folder ‘data’ already! In case a corpus needs to be parsed again, the old folder ‘data’ should be either renamed or deleted.

The packed data in the folder 'data' is organized in folders a000 and following, each subfolder contains files numbered from 000 onwards.

After running the packing script, check the log files: err should be size ‘0’

In file ‘*.out’ the STATUS should be ‘0’.


### TDPipe (for parsing Finnish language data)

This tool runs the scripts for tagging and parsing **Finnish** data.

Example on how to run TDPipe:

    $ bin/game --job parse --log log/parse -C 20 --GiB 20 --small bash -e bin/TDPipe // data/a000/*.vrf

Give a job name (default job name is ‘game’), give a name for the log folder, maybe ask for more RAM space like here in the example (default is 8 GiB). 
The maximum amount of files the script can handle is 1000 files per array, so this parsing command might have to be run separately for each folder within folder ‘data’.
If the files altogether do not exceed the amount of 1000, the command can be run on all subfolders at once:  `// data/*/*.vrf`

NOTE: In the folder log/parse the ‘err’ files are not supposed to be empty!

Possibilities for checking the queue:

    squeue -l -u 'username' | grep PEN

    squeue -l -u 'username' | grep -Eo 'RUN|PEN' | sort | uniq -c

(-E means you can use the pipe for 'or', and -o means that it shows only the lines with RUN or PEN)

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


In the subfolders of 'data', for every file '\*.vrf' there should be files with the same name but endings 'Atear', 'Blookup', 'Cmarmot', 'Dfillup', 'Eparse' and 'Final'. 

In case there are '\*.tmp' files for one or more vrf files, you should have a look at the corresponding '\*.err' files in the log folder. Problems could be, that there was not enough space for the job, or that the job was cancelled due to time limits. 

You can extend the RAM by adding the following option to the batch command: 

    --GiB=16

For extending the time for a job you can add the following command:

	--hours=2
	
If there are only a few files affected, you can try to parse them again separately with a command like the following (here with extended RAM and time):	

    $ bin/gamarr --job parse --log log/Parse1x --GiB=16 --hours=2 ./TDPipe // data/a000/{m012,m043,m065,m071,m107,m144}.vrf


### SPARV (for parsing Swedish language data)

This tool runs the scripts for tagging and parsing **Swedish** data.

Example on how to run SPARV:

	$ bin/game --job parse --log log/parse -C 20 --GiB 20 --small bash -e bin/SPARV // data/a000/*.vrf



### Unpacking
After parsing (and possibly [NER-tagging](howto_nertagging.md)), the data is being put back together at the correct cuts, which were marked during the packing process. The script for this is **vrt-unpack**:

     $ bin/game --job unpack --log log/Unpack -C 1 bin/vrt-unpack -o parsed --vrf=vrf.Final data/
    
(-C 1 to not waste the other 3 cores; 4 are the default)

The log files can go to the same log folder as for packing, as a job name I chose ‘unpack’ here. The output directory has to be a new folder (here: ‘parsed’). 

The input files’ names have the extension 'vrf.Final'. Folder 'data': all subfolders will be worked on.


It is recommended to validate the result VRT after parsing. For instructions on how to validate VRT data, see [docs: validating VRT](howto_validate_vrt.md).

It might be necessary to rename and re-order the positional attributes after parsing. For instructions on how to rename and re-order positional attributes, see [docs: how to order positional attributes](howto_pos_attributes.md).


### Creating a corpus zip file

Always, but especially if you have several files for one corpus (e.g. one per year), for the following steps (like running 'korp-make') it is recommended to create a zip file containing all the final files (result from 'Renaming and final ordering of pos attributes after parsing'). You can do that with the command ‘zip’:

    zip data.zip file1 file2 …	 
or
 
    zip data.zip folder/*

With the second command you create an archive with a sub directory, to which all files are extracted when unzipping.


NOTE: It is recommended to upload the successfully parsed data (as zip file) to the respective corpus folder in IDA, especially if for some reason it is not processed further right away.

