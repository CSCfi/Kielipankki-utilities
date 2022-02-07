# Archiving the corpus package
After the corpus is installed on the production Korp, the **corpus package** (created by korp-make) should be uploaded to the [IDA storage service](https://ida.fairdata.fi/login). Usually there is a folder for your corpus in IDA already, containing e.g. the original data. The package should be added to the same folder.

You can find the corpus package on Puhti under `/scratch/clarin/korp/corpora/pkgs/'corpus_id'`.

Accordingly, after publishing a VRT download package in the download service, the VRT download package should be stored in IDA. The data can be found on Puhti under `/scratch/clarin/download_preview/'CORPUS'/`, where 'CORPUS' is the shortname of the corpus in question.

Instructions on how to upload and download data to IDA can be found here: [IDA user guide](https://www.fairdata.fi/en/ida/user-guide/ "https://www.fairdata.fi/en/ida/user-guide/"). 

If you decide to use the IDA client in Puhti, you can find instructions on configuring and using IDA from the command line here: [CSC guide for archiving data](https://research.csc.fi/csc-guide-archiving-data-to-the-archive-servers#3.2.2 "https://research.csc.fi/csc-guide-archiving-data-to-the-archive-servers#3.2.2").

Assuming that you use the IDA client on Puhti, the command for uploading the package to IDA is:

    ida upload -v corpora/'corpus'/file.tgz file.tgz
    
-v means 'verbose' and will give you information about the process of uploading.
    
Example:

    ida upload -v corpora/ylioppilasaineet/yoaineet_korp_20190916.tgz yoaineet_korp_20190916.tgz

In case the folder for your corpus is already frozen in IDA, you should create a folder of the same name in the stage area and upload your package here. During the next 'freeze' the content of these folders will be combined.
NOTE: It is usually not recommended to unfreeze already frozen data in IDA!
