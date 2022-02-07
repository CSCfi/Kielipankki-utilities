# Validating VRT
The script for validating, **vrt-validate**, is meant for VRT data, so you should run it either after tokenizing the data or after the last step of the parsing process.

The script can be found in GitHub in the same place as the tokenizing and parsing scripts [Kielipankki-utilities/vrt-tools](https://github.com/CSCfi/Kielipankki-utilities/tree/master/vrt-tools).

	$ bin/game --job validate --log log/validate -C 1 bin/vrt-validate parsed/lang_fin_paragraized.vrt

In your log folder (here: log/validate) check the file with ending '.out' for the result of the validation.
In case the validator gives out messages, they should be investigated further with **linedump**:
	
    bin/linedump -k 2751241 --repr filename.vrt 
(where the number is the number of the line in question)

It might be, that you have to fix something in your conversion to HRT. Preferably the validator should not give any messages in the end. 

Some messages from the validator, e.g. warnings of the following type, could be ignored. This should be decided for each corpus and case individually.

    line	kind	level   issue
    5443	data	warning double space in value: title of text

This warning means, that in line 5443 the attribute 'title' of element 'text' contains a double space in its value. If this is, how the title was given in the original data, you could decide to leave it as is.


