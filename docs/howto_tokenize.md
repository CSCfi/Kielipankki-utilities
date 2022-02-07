# Tokenizing: Tools and process
The input format for the tokenizing scripts is **HRT** (for more information on this format see [docs: how to convert data to HRT](howto_convert_data_to_hrt.md)). The output format of the tokenizing process is **VRT**. For more information on the **VRT** format see [Kielipankki: corpus input format](https://www.kielipankki.fi/development/korp/corpus-input-format/).

The scripts can be found in GitHub [Kielipankki-utilities/vrt-tools](https://github.com/CSCfi/Kielipankki-utilities/tree/master/vrt-tools)

If you have your own copy of ‘Kielipankki-utilities’ on Puhti already, you can just update it with the help of the command `git pull`. Then you can create a symbolic link to the folder ‘vrt-tools’ from the respective corpora folder in your working directory, e.g.:

    ln -s /homeappl/home/‘username’/Kielipankki-utilities/vrt-tools/ bin

Now you have the tools available in your corpus folder in a folder named ‘bin’. 

If you have to tokenize a corpus again some time later, you should first update your copy of the folder ‘Kielipankki-utilities’. Go to Kielipankki-utilities in your HOME directory and update it with the command `git pull`.
Of course, this is only one suggestion on how to use the tokenizing scripts.

It is recommended to always convert data in an interactive batch job session on Puhti.
The command is 'sinteractive', for more information see [CSC: interactive usage](https://docs.csc.fi/computing/running/interactive-usage/).
(in Puhti, always use the 'small' partition).

You can define the resource requests directly within the command line, e.g.:

    sinteractive --account clarin --time 4:00:00 -m 8000



The scripts for tokenizing are


1. **vrt-dehype**: This script attempts to remove line-breaking hyphens (and page numbers) in plaintext within HRT markup (only needed when such hyphens are found in the data!)


1. **vrt-paragraize**: This script inserts paragraph tags into plaintext within HRT markup using lines of all whitespace as boundary indicators within blocks of plaintext (not needed if the data already has paragraph tags!)


1. **hrt-tokenize-udpipe**: This script tokenizes plaintext within HRT markup. It also adds sentence elements if not there already.

The scripts can be run like this:

    bin/hrt-tokenize-udpipe --out folder/filename_tokenized.vrt folder/filename.hrt

In case all three scripts are needed, they should be run one after the other, in the given order. They could also be combined in a shell script.



An example of running the hrt-tokenize-udpipe with 'game':

    $ bin/game --job tokenize --log log/tokenize --minutes 180 bin/hrt-tokenize-udpipe -I hrt/vrt // tokenized/lang_fin_paragraized.hrt

Note: 'game' has assimilated 'gamarr'. Technically, it always creates an "array job" now, but interprets arguments after "//" as inputs for separate tasks, when there is a "//" on the command line. Otherwise the job has only one task.

The output format of the tokenizing process is 'VRT'.
