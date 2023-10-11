# Archiving the original data
The original data, received by the data provider or harvested by Kielipankki, should be savely stored. The recommended form is a zip package.
The data should be accompanied by a simple readme file to explain the content of the zip package. The readme file and the zip package should be named similarly to make clear their affiliation. The name should contain the shortname of the resource, the string 'orig' and the time when the data was obtained.
For the time being, the original data is stored in IDA as well as on the HFST server.

## Instructions in detail:
1. Create a simple shortname-orig_yyyymmdd_README.txt for the original data. Mandatory content: 
  - resource title
  - PID for the metadata record of the first version
  - link to the associated epic in Jira.
  - information on the data provider or method of data aquisition (e.g. harvested from a certain web site, by whom and when)

2. Create a zip package of the original data (named as shortname-orig_yyyymmdd.zip) 

3. Upload the zip package and the readme file to the [IDA storage service](https://ida.fairdata.fi/login). In the staging area (marked with a '+'), under folder 'corpora', create a new folder, named with the resource group shortname, in lowercase characters. 
In case such a folder exists already (maybe because of an earlier version of the resource), a sub-folder with the name of this new version (e.g. 'v2') should be created and the original data be uploaded to it.
It is worth checking, if a folder for this resource already exists in the frozen area. If yes, a folder with the exact same name will have to be created in the staging area and the original data uploaded. In the process of freezing, the content of folders with the same name will be merged. But please make sure no files with the same name exist already in the frozen area, because this will cause conflicts.


Instructions on how to upload and download data to IDA can be found here: [IDA user guide](https://www.fairdata.fi/en/ida/user-guide/ "https://www.fairdata.fi/en/ida/user-guide/"). 

If you decide to use the IDA client in Puhti, you can find instructions on configuring and using IDA from the command line here: [CSC guide for archiving data](https://research.csc.fi/csc-guide-archiving-data-to-the-archive-servers#3.2.2 "https://research.csc.fi/csc-guide-archiving-data-to-the-archive-servers#3.2.2").

Assuming that you use the IDA client on Puhti, the command for uploading the package to IDA is:

    ida upload -v corpora/'corpus'/file.tgz file.tgz
    
-v means 'verbose' and will give you information about the process of uploading.
    
Example:

    ida upload -v corpora/ylioppilasaineet/yoaineet_korp_20190916.tgz yoaineet_korp_20190916.tgz


After the data is successfully uploaded, you should freeze it. For this, press the 'snowflake' button in the user interface of IDA (for more information on how to freeze, see the userguide [IDA user guide](https://www.fairdata.fi/en/ida/user-guide/ "https://www.fairdata.fi/en/ida/user-guide/").
NOTE: Only frozen data will be backed up!


4. Upload the original data zip package and the accompanying readme file to the **HFST server** (hfst-17.it.helsinki.fi). Under data/corpora/originals/ create a folder named with the resource group shortname, in lowercase characters.
Note that you need a VPN connection to the University to be able to access the HFST server. In order to be able to connect to Puhti from the HFST server, you can use e.g. sftp.

