# Creating a Korp package
Encoding VRT data into the CWB database format and creating a Korp package for the corpus can be done with a single command: **korp-make**. On Puhti it is generally available as /projappl/clarin/Kielipankki-utilities/scripts/korp-make, so with the above PATH, you can access it simply as “korp-make”. The script can also be found in GitHub [Kielipankki-utilities/scripts](https://github.com/CSCfi/Kielipankki-utilities/tree/master/scripts).

The command should be run from your HOME directory on Puhti in the respective corpus folder. In this corpus folder it is recommended to have a folder ‘scripts’ containing your (HRT) conversion scripts and a readme about the conversion process (give the date of conversion as well as version numbers of vrt-tools, parser and FiNER). Furthermore, in the corpus folder you should have a readme about the corpus (you can find the according information from METASHARE) and a configuration file named **korp-make-CORPUS.conf”**, where CORPUS is an abbreviation of the corpus name (short name).

The basic content of the **korp-make-CORPUS.conf”** is just the path to your conversion scripts' folder:

    script-dir = $HOME/'corpusname'/scripts/
   
For licensed data the content of the corpus.conf could be:

    script-dir = $HOME/'corpusname'/scripts/
    licence-type = ACA
    lbr-id = 201407301 

The licence-type can be either ACA or RES. The libr-id is usually the URN of the META-SHARE article for the corpus.


NOTE: Please keep in mind that the script that korp-make calls for adding ne structures and their attributes doesn’t yet recognize the new format of NER tags! Thus, if you wish to run korp-make now and add the ne structures only later, you should give korp-make the option `--no-name-attributes` or specify `no-name-attributes = 1` 
in the korp-make configuration file. The Korp corpus configuration will also have to be adjusted for the new NER attributes.

For nertagged data the content of the corpus.conf could be:

    script-dir = $HOME/'corpusname'/scripts/
	no-name-attributes = 1


The input to korp-make is a zip file containing the parsed (sometimes also NER-tagged) and validated VRT data with correctly named and ordered positional attributes.

An example command for running korp-make:

	$ ../Kielipankki-utilities/vrt-tools/game --job korpmake --log log/korpmake -C 2 --GiB 16 --hours 2 --scratch=10 --small korp-make --config-file=korp-make-nlfcl.conf --readme-file=readme_about_classics_library.txt nlfcl_fi /scratch/clarin/dieckman/nlfcl/vrt-ne/nlfcl_fi.zip


Here the command is running with 'game'; 2 cores, 16 GiB memory and two hours of time, on the 'small' partition of Puhti. 

The korp-id for the corpus (here: nlfcl_fi) should be derived from the short name of the corpus, which is given in the Metashare article. It can consist of lower-case letters and underscores.

If korp-make has to be re-run on the same corpus, add option `--force` to the above mentioned command, after 'korp-make' (this will overwrite all existing data created by korp-make earlier).

The script korp-make creates a corpus package under `/scratch/clarin/korp/corpora/pkgs/'corpus_id'/` and it writes a log file to `/scratch/clarin/korp/corpora/log/`on Puhti.

The corpus package has to be installed on the Korp server. If you do not have access rights to the Korp server, ask someone with the rights to do that.

The corpus will not be visible in Korp yet. The next step is to add a corpus configuration to Korp. For instructions on how to add a corpus configuration to Korp, see [docs: how to add a corpus configuration to Korp](howto_korp_configuration.md). 

