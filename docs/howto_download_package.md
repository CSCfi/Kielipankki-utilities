# Publish source data/VRT data in Download
Source data of a resource as well as its VRT version can be offered in the download service of Kielipankki [http://www.kielipankki.fi/download](http://www.kielipankki.fi/download "http://www.kielipankki.fi/download").

The **source data** is offered as is, meaning that usually it is not changed by us, except for packaging the data (in zip files) in a suitable way. The original data should be available in IDA, so it can be taken from there to create a download package.

The **VRT data** can be extracted from Korp in order to create a download package. You have to ask someone with access rights to the Korp server for this.

As for all resources and all their versions, a metadata record has to be created, URNs to be requested, the resource has to be added to the list of upcoming resources, if not there yet. (See the respective [instructions](https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/))

The name of the **source version** of a resource should contain the additional information 'source', e.g. `Yle Finnish News Archive 2011-2018, source`. The short name should have the suffix '-src', e.g. `ylenews-fi-2011-2018-src`.

Accordingly, the name of the **VRT version** of a resource should contain the information 'VRT', e.g. `Yle Finnish News Archive 2011-2018, VRT`. The short name should have the suffix '-vrt', e.g. `ylenews-fi-2011-2018-vrt`. Please follow Kielipankki's [Language resource naming conventions](https://www.kielipankki.fi/development/language-resource-naming-conventions/).

License pages in the portal have to be created and linked to from the metadata record.
Citation information also has to be added to the metadata record.

## Creating the download package

For dealing with **confidential data**, see the instructions on [what to consider when confidential data should be made available for download](howto_protected_packages.md).

Download the data from IDA or the HFST server to your work directory on CSC's computing environment (Puhti) in a separate folder. 

Create a **README.txt** containing at least the following information:
long name of the corpus, shortname, metadata PID, license information, short description of the corpus as given in the metadata, link to the resource group page. Add an explanation of the structure of the download package if needed.
For a model of the README.txt, please see [docs: model of the download package README.txt](model_download-package-README.md)

Create a **LICENSE.txt**. The content of this file should be copied from the respective license page in the portal.

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

In case the VRT data is going to be published as **release candidate** (during the release candidate stage of the corresponding Korp corpus), add a file RELEASE_CANDIDATE.txt to `/scratch/clarin/download_preview/'CORPUS'/` on Puhti. However, in case the users are not expecting the VRT version to appear immediately, it may make more sense to wait until the Korp corpus is approved as an official release and only then to publish the VRT version. (This needs to be discussed and decided on a case-to-case basis.)

Ask someone with the needed access rights to upload the package to the download service.
For a RES corpus, ask also to create an LBR record.

Check the uploaded resource, or better, have it checked by someone else of the team.
Check if:

- the download folder has the correct name (short-name)
- the description has the correct name (possibly slightly shortened) and links via URN to the metadata record
- the subdirectory contains the zip file(s) (short-name.zip)
- the description of the zip file(s) offers the name and type of license and links via URN to the license page in the portal
- the subdirectory contains the uncompressed README.txt and LICENSE.txt
- for a release candidate the file RELEASE_CANDIDATE.txt is added
- for restricted corpora a license and acceptance page opens, that needs to be approved before download
- for RES corpora, check the functionality of the LBR record

Mark the resource as published in the database. See instructions under [docs: how to maintain resources lists](howto_maintain_resource_lists_database.md)

Update the metadata record and add the location PID.

For a release candidate, add the label to the database and the metadata record.

Create or upate the resource group page, see [docs: how to create a resource group page](howto_resource_group_page.md).

Publish news about the new corpus in the portal, see [docs: how to create news in the portal](howto_portal_news.md) .

This should be the general localized text to the description of a release candidate corpus:

    In Finnish: Huomaa, että korpus on julkaisuehdokas, joten siihen voi vielä tulla muutoksia.
    in Swedish: Observera att korpusen är en releasekandidat, så den kan fortfarande ändras.
    In English: Please note that the corpus is a release candidate, so it may still change.


## Removing the release candidate status
For a resource published as release candidate, this status will be removed and the version declared as the final version if no requests for corrections or changes are received within a period of around two weeks.
The file RELEASE_CANDIDATE.txt has to be removed from the folder in download (ask someone with the needed access rights to to that).
Remove the release candidate status from the metadata record and the database.



More information on how to publish a corpus in the download service:
[Kielipankki: corpus data publication for download at the language-bank](https://www.kielipankki.fi/development/corpus-data-publication-for-download-at-the-language-bank/)


