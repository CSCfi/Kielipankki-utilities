#Guidelines for data storage
Resource data has to be stored in a safe and accessible place, where the data is backed up.

##Naming conventions
Standardized naming conventions for data versions: original, source, Korp, VRT ('orig', 'src', 'korp' or 'vrt)
name for a zip package: shortname-orig_yyyymmdd.zip
name for the accompanying readme: shortname-orig_yyyymmdd_README.txt

##Storing original data
The original data is stored in IDA as well as on the HFST server (under data/corpora/originals/'shortname'/). 
More information on how to archive the original data of a resource can be found from [docs: archive original data](https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_archive_original_data)

##Storing corpus packages
Source data packages available on the Download server as well as published Korp and VRT packages are not stored in IDA any more, as they are backed up on the Korp server.

In case **intermediate versions** need to be maintained, they can be stored on the HFST server, under data/corpora/wip/ (= "work in progress").
The data should be stored as a zip package under data/corpora/wip/'shortname'/. Add a README file containing corpus information and an explanation of the current status.
The naming conventions for intermediate source data is:  shortname-src_yyyymmdd.zip + shortname-src_yyyymmdd_README.txt
The naming conventions for intermediate Korp data is:  shortname-korp_yyyymmdd.zip + shortname-korp_yyyymmdd_README.txt

In case a resource is only published as a scrambled version, the unscrambled **base data** should be stored on the HFST server, 
under data/corpora/korp-base/'shortname'/.
The naming conventions for a base data package is: shortname-korp_yyyymmdd.zip + shortname-korp_yyyymmdd_README.txt


##Archiving agreements
Agreements should be stored in IDA as well as on the HFST server, under data/corpora/agreements/'shortname'/. 
Additionally, it was agreed on starting using the contracts register of the University of Helsinki, 
to make the contracts accessible for the university administration and also because the system allows 
for some metadata to be added to the contracts (details will be added later).