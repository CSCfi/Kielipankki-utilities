# NER-tagging of Finnish data
The NER-tagging (NER = Named Entity Recognition) is done on the parsed and validated VRT data. The script **vrt-finnish-nertag** annotates tokens with **FiNER**, the Finnish name classifier.

The scripts for NER-tagging can be found in GitHub in the same place as the tokenizing and parsing scripts [Kielipankki-utilities/vrt-tools](https://github.com/CSCfi/Kielipankki-utilities/tree/master/vrt-tools).

If you have your own copy of ‘Kielipankki-utilities’ on Puhti already, you can just update it with the help of the command `git pull`. Then you can create a symbolic link to the folder ‘vrt-tools’ from the respective corpora folder in your working directory, e.g.:

    ln -s /homeappl/home/‘username’/Kielipankki-utilities/vrt-tools/ bin

Now you have the tools available in your corpus folder in a folder named ‘bin’.

If you have to tokenize, parse or nertag a corpus again some time later, you should first update your copy of the folder ‘Kielipankki-utilities’. Go to Kielipankki-utilities in your HOME directory and update it with the command `git pull`.

It is recommended to always convert data in an interactive batch job session on Puhti.
The command is 'sinteractive', for more information see [CSC: interactive usage](https://docs.csc.fi/computing/running/interactive-usage/).
(in Puhti, always use the 'small' partition).

You can define the resource requests directly within the command line, e.g.:

    sinteractive --account clarin --time 4:00:00 -m 8000


The steps for NER-tagging VRT data are:

### Packing

The input data for packing is the tokenized, validated and possibly sentfixed VRT data. The data will be packed in files of a size which is suitable for the tool. In the areas where the data is split, markers will be added, so that the data can be put back together later at the correct cuts.

Example for packing the data with the command **vrt-pack**:

	$ bin/game --job pack --log log/pack-nertag -C 1 bin/vrt-pack --out nertag-data --tokens 100000 parsed/


The packed data in the folder 'nertag-data' is organized in folders a000 and following, each subfolder contains files numbered from 000 onwards.

After running the packing script, check the log files: err should be size ‘0’

In file ‘*.out’ the STATUS should be ‘0’.


### NER-tagging

**vrt-finnish-nertag** at the moment has three output formats, which could be produced all three, by running the script three times: One after the other in the given order, with the result of the preceeding step as input for the following step.

	$ bin/game --job names --log log/names -C 1 --GiB=16 --minutes 30 --small bin/vrt-finnish-nertag -I Dmax --tag nertag --max // nertag-data/a000/*.vrf

    $ bin/game --job names --log log/names -C 1 --GiB=16 --minutes 30 --small bin/vrt-finnish-nertag -I Dmax/Eall --tag nertags/ --all // nertag-data/a000/*.vrf.Dmax

    $ bin/game --job names --log log/names -C 1 --GiB=16 --minutes 30 --small bin/vrt-finnish-nertag -I Eall/Fbio --tag nerbio --bio // nertag-data/a000/*.vrf.Eall


For more information on the tool **vrt-finnish-nertag**, see the help:

	$ bin/vrt-finnish-nertag -h

The output field names are 'nertag' for --max, 'nertags/' for --all and 'nerbio' for --bio. 

      --max annotate maximal names
      --all annotate all ways that names overlap
      --bio annotate maximal names in Begin/In/Out format


### Unpacking
After NER-tagging, the data is being put back together at the correct cuts, which were marked during the packing process. The script for this is **vrt-unpack**:

	 $ bin/game --job unpack --log log/namesunpack -C 1 bin/vrt-unpack -o parsedNertag --vrf=vrf.Fbio nertag-data/
    

The input files’ names have the extension 'vrf.Fbio' (the result of the last round of NER-tagging). Folder 'nertag-data': all subfolders will be worked on.


The names and order of positional attributes for NERtagged data should be:

	<!-- #vrt positional-attributes: word ref lemma pos msd dephead deprel nerbio nertags/ nertag wid spaces -->

It might be necessary to rename and re-order the positional attributes after NER-tagging. For instructions on how to rename and re-order positional attributes, see [docs: how to order positional attributes](https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_pos_attributes.md).


It is recommended to validate the result VRT after NERtagging. For instructions on how to validate VRT data, see [docs: validating VRT](https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_validate.vrt.md).
