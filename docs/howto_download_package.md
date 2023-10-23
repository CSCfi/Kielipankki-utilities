# Publish source data/VRT data in Download
Source data of a resource as well as its VRT version can be offered in the download service of Kielipankki [http://www.kielipankki.fi/download](http://www.kielipankki.fi/download "http://www.kielipankki.fi/download").

The **source data** is offered as is, meaning that usually it is not changed by us, except for packaging the data (in zip files) in a suitable way. The original data should be available in IDA, so it can be taken from there to create a download package.

The **VRT data** can be extracted from Korp in order to create a download package. You have to ask someone with access rights to the Korp server for this.

As for all resources and all their versions, a META-SHARE record has to be created, URNs to be requested, the resource has to be added to the list of upcoming resources, if not there yet. (See [instructions](https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/))

The name of the **source version** of a resource should contain the additional information 'source', e.g. `Yle Finnish News Archive 2011-2018, source`. The short name should have the suffix '-src', e.g. `ylenews-fi-2011-2018-src`.

Accordingly, the name of the **VRT version** of a resource should contain the information 'VRT', e.g. `Yle Finnish News Archive 2011-2018, VRT`. The short name should have the suffix '-vrt', e.g. `ylenews-fi-2011-2018-vrt`. Please follow Kielipankki's [Language resource naming conventions](https://www.kielipankki.fi/development/language-resource-naming-conventions/).

License pages in the portal have to be created and linked to from META-SHARE.
Citation information also has to be added to the META-SHARE record.

## Creating the download package
Download the data from IDA to your work directory on CSC's computing environment (Puhti) in a separate folder. 

Create a README.txt containing at least the following information:
long name of the corpus, shortname, metadata PID, license information, short description of the corpus as given in META-SHARE, link to the resource group page. Add an explanation of the structure of the download package if needed.

Create a LICENSE.txt. The text of this file should be taken from the respective license page in the portal.

The README and LICENSE files should be offered twice: once included in the download package and once uncompressed included in the download folder on the same level as the download package.

Unzip the data. 

Check if there are empty files, log files or tmp directories, which can be removed.

A download package needs a subdirectory to extract to, usually named based on the shortname of the corpus. 
There should only be directories in the zip's root directory, no files. Exceptions are the README.txt and LICENSE.txt.

Create a folder named after the shortname of the corpus, e.g. 'ylenews-fi-2011-2018-src'.
Add the unzipped data to this folder (create a subfolder if needed).
Add README.txt and LICENSE.txt.

Zip the file and name it after the short name of the corpus, e.g. ylenews-fi-2011-2018-src.zip

Structure of the download package:

- short-name.zip:
- short-name/README.txt
- short-name/LICENSE.txt
- short-name/short-name/data files ... (including possible sub directories)

Copy the package together with the uncompressed LICENSE.txt and README.txt to the folder `/scratch/clarin/download_preview/CORPUS/` on Puhti. CORPUS here is a placeholder for the folder structure that should be shown in the download service.

For example 

`/scratch/clarin/download_preview/YLE/fi/2019-2020-src/`

would be shown in the download service as 

`https://kielipankki/download/YLE/fi/2019-2020-src/`



## Packing huge data (interactive batch job)
NOTE: If the zip file is huge and/or consists of hundreds of files, it is recommended to unzip and pack the data within an interactive batch job session.
The command is 'sinteractive', for more information see [CSC: interactive usage](https://docs.csc.fi/computing/running/interactive-usage/).
For more information on the 'fast local scratch area' ($LOCAL_SCRATCH) see [CSC: local scratch for data processing](https://docs.csc.fi/support/faq/local_scratch_for_data_processing/).

Example

    $ sinteractive --account clarin --time 4:00:00 -m 8000 -d 500 (max. is 750)
    
    $ cd $LOCAL_SCRATCH

Under local scratch, create a folder for unzipping the data. 
Unzip and re-pack the data. Remember to add the README.txt and LICENSE.txt to the package.
Remember to copy the re-packed data back from local scratch to either your work directory or directly to `/scratch/clarin/download_preview/`, because when you leave the interactive session, all your data on the local scratch area will be deleted.


## Publishing the resource
Have the package on `/scratch/clarin/download_preview/'CORPUS'/` on Puhti tested by someone else of the team.

Ask someone with the needed access rights to upload the package to the download service.
For a RES corpus, ask also to create an LBR record.

Check the uploaded resource, or better, have it checked by someone else of the team.
Check if:

- the download folder has the correct name (short-name)
- the description has the correct name (possibly slightly shortened) and links via URN to META-SHARE
- the subdirectory contains the zip file (short-name.zip)
- the subdirectory contains the uncompressed README.txt and sometimes separate LICENSE.txt
- for restricted corpora a license and acceptance page opens, that needs to be approved before download

Move the resource from the list of upcoming resources to the list of published resources. See instructions under [docs: how to maintain resources lists](howto_maintain_resource_lists_database.md)

Update the META-SHARE record and add the location PID.

Create or upate the resource group page, see [docs: how to create a resource group page](howto_resource_group_page.md).

Publish news about the new corpus in the portal, see [docs: howto create news in the portal](howto_portal_news.md) .



More information on how to publish a corpus in the download service:
[Kielipankki: corpus data publication for download at the language-bank](https://www.kielipankki.fi/development/corpus-data-publication-for-download-at-the-language-bank/)

