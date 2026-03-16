# Publish a new version of an existing resource

If changes have been made to an already published resource, the extent of these changes must first be determined.
Is it necessary to publish a new version of this resource, or would a CHANGE LOG suffice?
When a decision is made to release a new version, what is the status of this version? Is it a major or minor change or even non-significant? 
Would it be possible to restore the original version of the data and how much effort would it take? 
The answers to these questions will help to decide how to deal with the changes in the resource data.

More about non-significant changes and how they can be recorded in a CHANGE-LOG is documented here:
https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_change-log.md


## To add or to replace
It needs to be decided, if the updated version of the data will replace the former one, or if the versions will be available next to each other.
We would need to have a policy or guidelines for when (or for how long) to preserve old versions!


## Versioning, Naming conventions
If a new version of the corpus is created by adding to or modifying the original texts, the version information is added after the name of the corpus. Example:

    Classics of English and American Literature as translated by Kersti Juva, English-Finnish parallel corpus version 2, VRT
    shortname: ceal-par-v2-vrt

If we modify the attribute information in the vrt-file, for example re-parsing with new parser and not including the old one, we add the version information after the VRT (or Korp, etc.). Examples:

    Classics of English and American Literature as translated by Kersti Juva, English-Finnish parallel corpus, VRT version 2
    shortname: ceal-par-vrt-v2
	
    Classics of English and American Literature as translated by Kersti Juva, English-Finnish parallel corpus version 2, VRT version 2
    shortname: ceal-par-v2-vrt-v2


## Version numbers
The first version of a resource does not get a version number. 
The following versions of a resource get version numbers of the format Major.Minor (e.g. 1.1, 1.2, 2, 2.1, 2.2.)
The Major number is incremented for significant, often backwards-incompatible changes. The Minor number is increased in case of smaller updates, 
such as new features or bug fixes, while maintaining backwards compatibility.
More about major or minor changes see below.


## Naming conventions of download packages

e.g. The Suomi24 Corpus 2001-2017, VRT version 1.3

 package name: suomi24-2001-2017-vrt-v1-3.zip

 The README.txt should have the same version number in its name as the corresponding data package: README-v1-3.txt
 
 If the changes affect the license, this file should also have the same version number in its name: LICENSE-v1-3.txt
 Usually the license of a resource is not affected by a version update. In those cases the LICENSE.txt does not have to be versioned.



## Minor and major changes
Minor changes mean smaller updates, such as new features or bug fixes, while maintaining backwards compatibility.  
Examples:
the data has been updated with annotations of names recognized with FiNER
the data has been updated with annotations of languages of sentences identified with HeLI-OTS
the format of the audio files has been automatically converted


Major changes are significant, often backwards-incompatible changes.
Examples:
the data has been re-parsed with a new parser without including the old one
the content has been changed by adding, modifying or removing (parts of) the original texts


## Example use cases
Suomi24
lehdet90ff



## Task list for publishing a new version of the source data in Download
Use the usual stories and task lists for publishing the source data in Download, with the following changes:

You will not need the story

**_shortname_: Prepare for publishing the source data in Download**



Instead of the story

**_shortname_: Package and upload the source data**


create a Jira Story with the following title:

***

### _shortname_: Package and upload the new version of the source data

```
# [ ] _*?IDA*_ Get/create the new version of the original data 
# [ ] _*?HYSTORE*_ In case intermediate versions need to be maintained, upload the data as a zip file (named as shortname-src_yyyymmdd.zip) and the separate shortname-src_yyyymmdd_README.txt file to the HFST server, under data/corpora/wip/ (= “work in progress”).
# [ ] _*+PUHTI*_ Create a download package [how to create a download package | https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_download_package.md]
# [ ] _*+DATA*_ Create/Update the README-v1-1.txt (use the correct version number) for the source data, to be shown to the end-users. Add information about the changes for this new version.
# [ ] _*+DATA*_ Create a file CHANGE-LOG.txt, if needed
## [ ] _*+PUHTI*_ Zip the data and the readme and license files (and CHANGE-LOG.txt) into a package named as shortname-src-v1-1.zip (use the correct version number for all files!).
## [ ] _*+PUHTI*_ Compute an MD5 checksum for the zip package
# [ ] _*?DATA*_ In case the resource contains personal data (+PRIV) or other confidential information, [include the original zip file(s) in a new, password-protected zip package| https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_protected_packages.md ] for internal storage and transfer. Use the [appropriate password| https://github.com/CSCfi/Kielipankki-passwords/blob/master/howto_manage_corpus_passwords.md ].
# [ ] _*+PUHTI*_ Add the download package, MD5 checksum file and readme and license files to the directory {{/scratch/clarin/download_preview}} on Puhti
# [ ] _*+TEST*_ Have the package tested
# [ ] _*?MANAGE*_ If this is a RES-licensed corpus and an LBR application does not yet exist, fill in an instance of the [Jira issue "_shortname_: Create an LBR record for a RES-licensed corpus" | https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/corpus_publishing_tasklist.md#csc_lbr ] and assign it forward to CSC (add label: lb-csc-task and prioritize if needed).
# [ ] _*+MANAGE*_ Have the package uploaded to the download service: fill in an instance of [the Jira issue "_shortname_: Upload to the download service" | https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/corpus_publishing_tasklist.md#csc_upload ] and assign it forward to CSC (add label "lb-csc-task" and prioritize if needed).
# [ ] _*+TEST*_ When uploaded, have the package tested again and check access rights.
\\
```
***


Instead of the story

**_shortname_: Announce the publication of the source data in Download**


create a Jira Story with the following title:

***

### _shortname_: Announce the publication of the new version of the source data in Download


```
NOTE: Metadata and Access PIDs are not going to change! Only the version number will be added to the resource name
# [ ] _*+DB*_ In the resource database, add the version number to the resource names (en, fi, shortname)
# [ ] _*+META*_ Update the [COMEDI | https://clarino.uib.no/comedi/records] record: add the version number to the resource names (en, fi, shortname) and change the Availability start date (under Distribution)
# [ ] _*?META*_ Update the metadata record: add information about what has changed for the new version to the description
# [ ] _*+META*_ Update the license pages: add the version number to the resource names (en, fi)
# [ ] _*?META*_ If required, create a portal page "shortname: Notes for the user", to inform about found issues in the data. Make sure the [COMEDI | https://clarino.uib.no/comedi/records] record also contains a link to the notes' page (in case the information is only one sentence, add it directly to the metadata description).
# [ ] _*+PORTAL*_ Publish news about the new version of the corpus on the Portal
# [ ] _*+DB*_ Change the Language Bank Publication Date to the [resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_1]
# [ ] _*?SUPPORT*_ Inform the depositor/rightholder about the publication
\\
```




## Task list for publishing a new version of a resource in Korp
Use the usual stories and task lists for publishing a resource in Korp, with the following changes:

You will not need the story

**_shortname_: Prepare for publishing the resource in Korp**



Instead of the story

**_shortname_: Announce the publication of the new Korp corpus as release candidate**


create a Jira Story with the following title:

***
### _shortname_: Announce the publication of the *new version* of the Korp corpus as release candidate

```
NOTE: Metadata and Access PIDs are not going to change! Only the version number will be added to the resource name
# [ ] _*+GITHUB*_ Update the access location URN (path in Korp)
# [ ] _*+TEST*_ Test (or have tested) the resource in production Korp and check access rights.
# [ ] _*+DB*_ In the resource database, add the version number to the resource names (en, fi, shortname) (add status "release candidate" to the name!)
# [ ] _*+META*_ Update [COMEDI | https://clarino.uib.no/comedi/records]  record; add the version number to the resource names (en, fi, shortname) and change the Availability start date (under Distribution)
# [ ] _*?META*_ Update the metadata record: add information about what has changed for the new version to the description
# [ ] _*?META*_ Update the metadata record: add annotation information and tools used during the corpus processing pipeline
# [ ] _*+META*_ Add "release candidate" status information to metadata record
# [ ] _*+META*_ Update the license pages: add the version number to the resource names (en, fi)
# [ ] _*?META*_ If required, create a portal page "shortname: Notes for the user", to inform about found issues in the data. Make sure the [COMEDI | https://clarino.uib.no/comedi/records] record also contains a link to the notes' page (in case the information is only one sentence, add it directly to the metadata description).
# [ ] _*+PORTAL*_ Publish news about this new version of the corpus in the portal
# [ ] _*+DB*_ Change the Language Bank Publication Date in the [resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_1]
## [ ] _*+META*_ Add the date when the release candidate status can be removed (two weeks from now) to the following two stories (about removing the release candidate status)
# [ ] _*?SUPPORT*_ Inform corpus owner and possibly interested researchers on the corpus in Korp and ask them to test it
\\
```


## Task list for publishing a new version of the VRT data in Download 
Use the usual stories and task lists for publishing the VRT data in download, with the following changes:

You will not need the story

**_shortname_: Prepare for publishing the VRT data in Download**



Instead of the story

**_shortname_: Prepare for publishing the VRT data in Download**


create a Jira Story with the following title:

***

### _shortname_: Announce the publication of the *new version* of the VRT data in Download

```
NOTE: Metadata and Access PIDs are not going to change! Only the version number will be added to the resource name
# [ ] _*+DB*_ In the resource database, add the version number to the resource names (en, fi, shortname)
# [ ] _*+META*_ Update the [COMEDI | https://clarino.uib.no/comedi/records] record; add the version number to the resource names (en, fi, shortname) and change the Availability start date (under Distribution)
# [ ] _*?META*_ Update the metadata record: add information about what has changed for the new version to the description
# [ ] _*+META*_ Update the license pages: add the version number to the resource names (en, fi)
# [ ] _*?META*_ If the package is published as release candidate (during the release candidate stage of the corresponding Korp corpus), add release candidate status to the metadata record and database
# [ ] _*?META*_ If required, create a portal page "shortname: Notes for the user", to inform about found issues in the data. Make sure the metadata record also contains a link to the notes' page (in case the information is only one sentence, add it directly to the metadata description).
# [ ] _*+PORTAL*_ Publish news about the new version of the corpus on the Portal
# [ ] _*+DB*_ Change the Language Bank Publication Date to the [resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_1]
## [ ] _*+META*_ If the package is published as release candidate, add the date when this status can be removed (two weeks from now) to the following story (about removing the release candidate status)
# [ ] _*?SUPPORT*_ Inform the depositor/rightholder and interested researchers about the VRT publication
\\
```
