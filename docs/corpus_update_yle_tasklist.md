
# Checklists for tasks in the resource publishing pipeline

After discovering a new resource that should be made available via Kielipankki, 
we need a list of the relevant tasks that must be completed.

In case an already published resource has to be **un-published**, please follow these instructions [docs: howto unpublish a resource](https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_unpublish_corpus.md).

### 1. For each new resource (or a new version of an existing resource), create an "Epic" issue on Jira. 
   - Name the Epic as:
   
    shortname: Publish XXX in Kielipankki (Korp/Download/…)
   
   - Replace "_shortname_" with the short name of the resource in question (use the "base" name only, excluding "-src" etc.).
   - Replace "XXX" with the common title of the resource group in question, to make the issue easier to find in Jira.
   - In brackets, you may specify the resource variant(s) that is/are to be published during this Epic, according to current plan: just the Download, and/or Korp, etc. 
   - NB: Both the _Epic Name_ and _Summary_ fields of the Jira Epic issue should contain identical text (= the title of the issue, composed as above).
   - Add to the description field **all important metadata** (for all versions, as a collection), as soon as they are created resp. PIDs are requested, in the following form:

<a name="jira-epic"></a>

```
----
*Resource group page (English):* [http://urn.fi/urn:nbn:fi:lb-xxxxxxxxxx]

*Resource description:* [This resource contains…]

----
*Source version:*

*Resource title in English:* …, source
*Resource title in Finnish:* …, lähdemateriaali
*Shortname:* shortname-src

*Metadata:* [http://urn.fi/urn:nbn:fi:lb-xxxxxxxxxx]
*Access location:* [http://urn.fi/urn:nbn:fi:lb-xxxxxxxxxx]

*License label:* e.g., CC BY, RES +PRIV, etc.
*License page (English):* [http://urn.fi/urn:nbn:fi:lb-xxxxxxxxxx]
*License (Finnish):* [http://urn.fi/urn:nbn:fi:lb-xxxxxxxxxx]
*(In case the corpus contains personal data:)*
*PRIV conditions (English):* [http://urn.fi/urn:nbn:fi:lb-xxxxxxxxxx]
*PRIV conditions (Finnish):* [http://urn.fi/urn:nbn:fi:lb-xxxxxxxxxx]

*Rightholder:* 
*Data controller, regarding personal data (if applicable):*

----
*Korp version:*

*Resource title in English:* …, Korp
*Resource title in Finnish:* …, Korp
*Shortname:* shortname-korp

*Metadata:* [http://urn.fi/urn:nbn:fi:lb-xxxxxxxxxx]
*Access location:* [http://urn.fi/urn:nbn:fi:lb-xxxxxxxxxx]

(Include the license information if different from the source version)

----
*VRT version:*

*Resource title in English:* …, VRT
*Resource title in Finnish:* …, VRT
*Shortname:* shortname-vrt

*Metadata:* [http://urn.fi/urn:nbn:fi:lb-xxxxxxxxxx]
*Access location:* [http://urn.fi/urn:nbn:fi:lb-xxxxxxxxxx]

(Include the license information if different from the source/Korp version)
```

   - Add to the description field **all tools used to process the data** (applies usually to the Korp and VRT versions), in the following form:
     
<a name="jira-epic-tools"></a>

```
*Tools used to process the data:*

# [ ] *VRT tools* (_please specify_), http://urn.fi/urn:nbn:fi:lb-2024021502. Annotation type: (_please specify_). Segmentation level: (_please specify_).
# [ ] *UDPipe-LBF* as a tokenizer, http://urn.fi/urn:nbn:fi:lb-201902131. Annotation type: segmentation. Segmentation level: paragraph. 
# [ ] *UDPipe-LBF* as a morpho-syntactic parser, http://urn.fi/urn:nbn:fi:lb-201902131. Annotation type: morphosyntacticAnnotation-posTagging. Segmentation level: sentence. 
# [ ] *TDPP-LBF* as a morpho-syntactic parser, http://urn.fi/urn:nbn:fi:lb-2024021501. Annotation type: morphosyntacticAnnotation-posTagging. Segmentation level: sentence. 
# [ ] *Finnish Tagtools* version 1.6, http://urn.fi/urn:nbn:fi:lb-2024021401. Annotation type: (_please specify_). Segmentation level: (_please specify_)
# [ ] *FiNER*, http://urn.fi/urn:nbn:fi:lb-2024021401. Annotation type: semanticAnnotation-namedEntities. Segmentation level: word
# [ ] *HeLI-OTS* version 2.0, http://urn.fi/urn:nbn:fi:lb-2024040301. Annotation type: language identification. Segmentation level: sentence.

(Please add or remove information according to need!)

```

     

### 2. Copy the following list of section titles to the top of the description of the Epic. Remove the sections that are not applicable to or planned for the current resource.

```
Enter a new resource to the pipeline
# [ ] _shortname_: Start negotiations with the depositor
# [ ] _shortname_: Enter the new resource to the pipeline
# [ ] _shortname_: Plan the publication process with the depositor
# [ ] _shortname_: Clear the license for the resource
# [ ] _shortname_: Publish the end-user license
# [ ] _shortname_: Acquire the original data

Publish the source data in Download
# [ ] _shortname_: Prepare for publishing the source data in Download
# [ ] _shortname_: Package and upload the source data
# [ ] _shortname_: Announce the publication of the source data in Download
# [ ] _shortname_: Clean up after publishing the source data in Download

Publish the resource in Korp
# [ ] _shortname_: Prepare for publishing the resource in Korp
# [ ] _shortname_: Convert the data for publishing the resource in Korp
# [ ] _shortname_: Parse the data for publishing the resource in Korp
# [ ] _shortname_: Create a Korp corpus package (korp-make)
# [ ] _shortname_: Create the Korp corpus configuration
# [ ] _shortname_: Create a Korp test version
# [ ] _shortname_: Publish the corpus in Korp as release candidate
# [ ] _shortname_: Announce the publication of the new Korp corpus as release candidate
# [ ] _shortname_: Fix the data and publish a new release candidate (if needed)
# [ ] _shortname_: Announce the publication of the new Korp corpus as another release candidate (if needed)
# [ ] _shortname_: Remove release candidate status
# [ ] _shortname_: Clean up and document after publishing in Korp
# [ ] _shortname_: Announce the removal of release candidate status after publishing in Korp

Publish the VRT data in Download
# [ ] _shortname_: Prepare for publishing the VRT data in Download
# [ ] _shortname_: Package and upload the VRT data
# [ ] _shortname_: Announce the publication of the VRT data in Download (as release candidate if needed)
# [ ] _shortname_: Clean up after publishing the VRT in Download (remove release candidate status if needed) 
```

   - Again, replace "_shortname_" with the short name of the resource in question.
   - NB: To make sure that the lists are rendered correctly, the text should be pasted when the Jira description input field is in “Text” mode, not “Visual”.


### 3. In the Epic, create a "Story" for each of the applicable task list sections which were previously copied to the Epic description. 
  - In case the resource is a completely new one and it has not been decided what should be done with it, just create the first story ("_shortname:_ Start negotiations with the depositor", see the first section of tasks below).
  - Use the corresponding section title in the task list as the name of the Story.
  - Replace "_shortname_" with the short name of the resource in question (use the "base" name only, excluding "-src" etc.). This makes it easier to see which resource is addressed in each individual Jira ticket.
  - Copy & paste the appropriate task list from below to the description field of the Story.
  - In each Story, you may adjust the list items and their order as appropriate for the resource in question. 
  For example, LBR records are only needed for RES licensed corpora. Thus, if you already know the corpus license will not be RES, you may remove or overstrike the LBR-related tasks.

### 4. Each task description is preceded by “[ ]”, representing a checkbox, and a tag representing the task type. 

  - When you start working on an individual task item, write your name between the square brackets (“[Name]”). 
  - When a task is completed, replace "[YourName]" with an “[X]”.
  - When all tasks in a Story are complete, you may edit the description in the main Epic and mark the corresponding section with an [X].

The task category marker is an italicized (slanted) and bolded character string. The first character is _+_ for obligatory tasks and _?_ for optional ones, and the task category markers are:

- _*MANAGE*_: general management and coordination of the corpus publication process and the related tasks (requires Jira permissions)
- _*SUPPORT*_: advising and communicating with the data depositor (requires knowledge of data management practices and the applicable instructions)
- _*META*_: metadata editing & curation (requires login + membership of the group FIN-CLARIN on COMEDI)
- _*DISCUSS*_: Decisions about priorities, schedule and distribution of work (often requires a team meeting and/or consultation with leadership)
- _*AGREEMENT*_: negotiations and administration regarding deposition agreements, license conditions, data protection practices etc. (requires legal knowledge, may require the opinion of a legal expert at UHEL, requires write access to the contract register at UHEL)
- _*LEGAL*_: Legal decisions and formal contracts involving the University of Helsinki (requires a meeting with a legal expert)
- _*PORTAL*_: editing web pages in the Portal (requires Portal permissions)
- _*DB*_: modifying content in the resource database (requires Portal permissions)
- _*GITHUB*_: creating and assigning PIDs via the GitHub repository; modifying version-controlled files on GitHub (requires permissions for CSC GitHub)
- _*IDA*_: storing, organizing, copying, naming and transferring files, checking file integrity, creating file packages and standard documentation files included in the archived data (requires permissions for IDA)
- _*HYSTORE*_: storing, organizing, copying, naming and transferring files, checking file integrity, creating file packages and standard documentation files included in the archived data (requires permissions to access the HFST server of the University of Helsinki)
- _*PUHTI*_: storing, organizing, copying, naming and transferring files, checking file integrity, creating standard documents for the archived data (requires permissions for CSC computing environment)
- _*ALLAS*_: storing, organizing, copying, naming and transferring files, checking file integrity, creating standard documents for the archived data (requires permissions for CSC computing environment)
- _*DATA*_: receiving original data, data (pre-)processing and cleanup (tasks that may be completed in different environments)
- _*KORP*_: Korp configuration (requires Korp server permissions)
- _*LBR*_: the task requires LBR administrator privileges (at this point, an issue needs to be created and handed over to the CSC team)
- _*CSC*_: the task requires administrator privileges of other specific services (at this point, an issue needs to be created and handed over to the CSC team with label 'lb-csc-task' and rank to top!)
- _*TEST*_: testing
- Other platforms can be added in a similar way if required.

NB: In previous versions of the task lists (a lot of which still exist on Jira), the second character indicates the rough type of the task by one of the following letters:

- _*A*_: administrative
- _*D*_: data processing
- _*K*_: Korp configuration
- _*T*_: testing
	

## The task lists for the Stories in Epic

The following lists should contain the tasks required for publishing a corpus. The tasks are in the rough order in which they should typically be completed.

*Recap: For each of the section titles below, create a Story and assign it as "In Epic", providing the name/number of the Epic of the resource in question. Copy & paste the appropriate task lists from below to the description field of the corresponding Jira stories.*


***

***Enter a new resource to the pipeline***

### _shortname_: Start negotiations with the depositor

```
# [ ] _*+MANAGE*_ Create a Jira Epic issue called "shortname: Publish XXX in Kielipankki (Korp/Download/…)"
# [ ] _*?SUPPORT*_ Contact the potential depositor (by email; arrange a meeting if required) 
# [ ] _*?SUPPORT*_ Ask the depositor to submit the basic details of the new corpus or resource (e-form: [http://urn.fi/urn:nbn:fi:lb-2021121421](http://urn.fi/urn:nbn:fi:lb-2021121421))
# [ ] _*+MANAGE*_ Insert the first pipeline Story under the Jira Epic and assign it forward
# [ ] _*+MANAGE*_ Copy-paste the content of the e-form as a comment under the Story (tag the person to whom it is assigned)
\\
```

### _shortname_: Enter the new resource to the pipeline

```
# [ ] _*+MANAGE*_ Insert relevant parts of this task list in the resource publication Epic (sections under linked Jira Stories)
# [ ] _*+MANAGE*_ Add to the Epic description field all important metadata (take a copy from the model description on the top of this page)
# [ ] _*+MANAGE*_ Add to the Epic description field the information about all tools used to process the data (take a copy from the model description on the top of this page)
# [ ] _*+GITHUB*_ [Request a URN | https://github.com/CSCfi/Kielipankki/tree/master/FIN-CLARIN-Administration] for the metadata record [how to request PIDs | https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_request_pid.md]
# [ ] _*+GITHUB*_ [Request the URNs | https://github.com/CSCfi/Kielipankki/tree/master/FIN-CLARIN-Administration] for the license pages [how to request PIDs | https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_request_pid.md]
# [ ] _*+META*_ In [COMEDI | https://clarino.uib.no/comedi/records], create and publish a preliminary metadata record (skeletal information only) for the source version, which is usually the first version to be published [instructions for creating metadata records | https://www.kielipankki.fi/development/creating-metadata-records/ ]
# [ ] _*+META*_ In [COMEDI | https://clarino.uib.no/comedi/records], update the metadata record with the metadata URN
# [ ] _*+DB*_ Add the [corpus to the resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_1] and make sure the resource is displayed on the list of [upcoming corpora | https://www.kielipankki.fi/aineistot/tulevat/ ]
# [ ] _*+META*_ Add citation information to the metadata record
\\
```

### _shortname_: Plan the publication process with the depositor

```
# [ ] _*+META*_ Review the [COMEDI | https://clarino.uib.no/comedi/records] record and fix the preliminary translations, at least for the time being
# [ ] _*+SUPPORT*_ Ask the rightholder to review the details in the COMEDI record (finalize shortname and title, confirm the list of authors/creators if required)
# [ ] _*?SUPPORT*_ Inform the depositor about citation practices, if relevant
# [ ] _*?SUPPORT*_ Provide the depositor with references/advice regarding the technical format and structure of the original data
# [ ] _*?SUPPORT*_ Ask the depositor/rightholder about their schedule for submitting the data
# [ ] _*?DISCUSS*_ If the size and technical specifications of the corpus seem "non-standard" in some respect, discuss the corpus details in an internal meeting to see if it is technically feasible to publish it in the Language Bank
\\
```

<a name="license"></a>

### _shortname_: Clear the license for the resource

```
# [ ] _*+DB*_ In the [resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_2], create a new (preliminary) license instance for the resource, or link an existing license instance to the resource, if available
# [ ] _*?AGREEMENT*_ Clear the license terms and conditions regarding copyrighted material
## [ ] _*?AGREEMENT*_ In case the corpus contains third-party copyrighted material, find out if the depositor has the rights to distribute it via the Language Bank (e.g., explicit license or permission from copyright holders)
## [ ] _*?LEGAL*_ When in doubt, bring the case up in a legal meeting
# [ ] _*?AGREEMENT*_ Clear the data protection terms and conditions (PRIV)
## [ ] _*?AGREEMENT*_ Find out who the data controller is
## [ ] _*?SUPPORT*_ Find out how the depositor informed the data subjects about the purpose of processing and to what the participants gave their permission/consent (is Kielipankki or similar mentioned?)
## [ ] _*?AGREEMENT*_ Ask the depositor to show their data protection information sheet (or the documents that passed ethical review, if applicable)
## [ ] _*?AGREEMENT*_ Obtain (or create) a description of the personal data categories that are included in the corpus
## [ ] _*?AGREEMENT*_ Help the depositor to find out if [a DPIA or some further risk assessment is required | https://www.kielipankki.fi/support/pre-dpia/ ], especially regarding the potential distribution via Kielipankki, and discuss further actions with the depositor if necessary
## [ ] _*?SUPPORT*_ Provide the depositor with further references regarding personal data [minimization and safeguards | https://www.kielipankki.fi/support/protective-measures/ ] that may be applied prior to submitting the corpus for distribution
# [ ] _*+AGREEMENT*_ Make a copy of the [deposition agreement template | https://helsinkifi-my.sharepoint.com/:f:/r/personal/lennes_ad_helsinki_fi/Documents/Kielipankin%20sopimusasiat/DELA%20-%20Sopimuspohjat?csf=1&web=1&e=zRNnQQ] into a new folder (labeled as _shortname_) and prepare a preliminary version of the documents for discussion
## [ ] _*?AGREEMENT*_ Make arrangements to meet the depositor about the details of the deposition agreement
## [ ] _*?SUPPORT*_ Meet with the depositor/rightholder and take note of the action points
## [ ] _*+LEGAL*_ Make the final decision as to whether the resource can be distributed via the Language Bank of Finland (bring the case up in legal meeting, if necessary)
## [ ] _*+AGREEMENT*_ Prepare the final draft of the deposition license agreement and send it to corpus owner who should fill in the remaining gaps (ask for legal advice if needed)
## [ ] _*+AGREEMENT*_ Check the final deposition agreement, combine all parts into a single pdf file and upload the document to the [UniSign | https://unisign.helsinki.fi/] system for electronic signing by the rightholder (+ the data controller) and finally by the head of department at the University of Helsinki ([How to use UniSign](https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_have_agreement_signed.md))
## [ ] _*+AGREEMENT*_ In this Jira issue, add a comment stating the final license conditions, the rightholder(s), and the final list of the persons to be cited, according to the signed agreement.
## [ ] _*+IDA*_ Upload and freeze the signed deposition agreement (or similar proof of the distribution license) as a pdf file (named as _KP_yyyy_AINEISTO_shortname_yyyymmdd.pdf_, according to the date of the last signature in the document) in IDA, under Administration/agreements/shortname. [How to archive signed agreements | https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_archive_signed_agreements.md]
## [ ] _*+HYSTORE*_ Upload the signed deposition agreement (or similar proof of the cleared distribution license) as a pdf file (named as _KP_yyyy_AINEISTO_shortname_yyyymmdd.pdf_, according to the date of the last signature in the document) to the HFST server, under _data/corpora/agreements/shortname_. [How to archive signed agreements | https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_archive_signed_agreements.md]
 ## [ ] _*+AGREEMENT*_ Upload the signed deposition agreement (or similar proof of the cleared distribution license) as a pdf file named as _KP_yyyy_AINEISTO_shortname_yyyymmdd.pdf_, according to the date of the last signature in the document; document title _Kielipankki yyyy Aineistosopimus: shortname(s)_, to the [contract register | https://sopimus.helsinki.fi/ ] of the University of Helsinki, under H402 Digitaalisten ihmistieteiden osasto. By default, agreements are not 'confidential'. [How to archive signed agreements |https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_archive_signed_agreements.md]
## [ ] _*+DB*_ In the [resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_2 ], update the license status and the agreement locations.
\\
```

### _shortname_: Publish the end-user license

```
# [ ] _*+PORTAL*_ [Create the license pages | https://www.kielipankki.fi/wp-admin/edit.php?post_type=page&page=cms-tpv-page-page) if required [how to create license pages)|https://www.kielipankki.fi/intra/creating-license-pages/ ]  
# [ ] _*?PORTAL*_ For a PRIV license, create and translate the pages for data protection terms and conditions and inform the depositor
# [ ] _*?A*_ If required, [request the URNs] (https://github.com/CSCfi/Kielipankki/tree/master/FIN-CLARIN-Administration) for the PRIV condition pages 
# [ ] _*+PORTAL*_ Update the license PIDs in the [resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_2] and make sure the resource in question is linked with the correct license instance in the resource database
# [ ] _*+META*_ Create/update the [COMEDI | https://clarino.uib.no/comedi/records] record, including the license information and the people to be cited, according to the agreement [instructions for creating metadata records | https://www.kielipankki.fi/development/creating-metadata-records/ ]
# [ ] _*+PORTAL*_ In case the resource has a RES license, add the relevant details to the table [LBR-katselmointiprosessi | https://www.kielipankki.fi/wp-admin/admin.php?page=tablepress&action=edit&table_id=37], shown on the intranet page [Katselmointiprosessi |https://www.kielipankki.fi/intra/katselmointiprosessi/ ]
# [ ] _*?DISCUSS*_ If the license requires further processing steps and resources from Kielipankki, bring them up for discussion in an internal meeting
\\
```

### _shortname_: Acquire the original data

```
# [ ] _*+DATA*_ Receive, download or harvest the data
# [ ] _*+DATA*_ Check the data: format and validity
## [ ] _*?DATA*_ Clean up the data
# [ ] _*+DATA*_ Create a simple shortname-orig_yyyymmdd_README.txt for the original data, see [instructions| https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_archive_original_data.md ].
# [ ] _*+IDA*_ Upload the original data as a zip file (named as shortname-orig_yyyymmdd.zip) and the separate shortname-orig_yyyymmdd_README.txt file to IDA, under the folder with the resource group shortname, in lowercase characters.
# [ ] _*+IDA*_ Freeze the new files in the original data folder in IDA
# [ ] _*+HYSTORE*_ Upload the original data as a zip file (named as shortname-orig_yyyymmdd.zip) and the separate shortname-orig_yyyymmdd_README.txt file to the HFST server, under data/corpora/originals/.
\\
```

***

***Publish the source data in Download***

### _shortname_: Prepare for publishing the source data in Download

```
# [ ] _*+META*_ Create or update the [COMEDI | https://clarino.uib.no/comedi/records]  record [instructions for creating metadata records | https://www.kielipankki.fi/development/creating-metadata-records/ ]
# [ ] _*+GITHUB*_ Request access location URN for download version (and check that the URNs for COMEDI and license pages are available and working)
# [ ] _*+DB*_ Make sure that the corpus is on the list of upcoming resources and citable, and update the [resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_1] if required
\\
```

### _shortname_: Package and upload the source data

```
# [ ] _*?IDA*_ Get the original data from IDA
# [ ] _*?HYSTORE*_ In case intermediate versions need to be maintained, upload the data as a zip file (named as shortname-src_yyyymmdd.zip) and the separate shortname-src_yyyymmdd_README.txt file to the HFST server, under data/corpora/wip/ (= “work in progress”).
# [ ] _*+PUHTI*_ Create a download package [how to create a download package | https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_download_package.md]
# [ ] _*+DATA*_ Create a publishable README.txt for the source data, to be shown to the end-users. Include: 1) resource title; 2) PID; 3) either the license PID, a plain link to the license, or a statement of the rightholder and the known restrictions of use for the source data, 4) any other relevant information regarding the technical structure of the source data, if applicable.
## [ ] _*+PUHTI*_ Create and add the readme and license files [how to create/update license pages | https://www.kielipankki.fi/intra/creating-license-pages/ ]
## [ ] _*+PUHTI*_ Zip the data and the readme and license files into a package named as shortname-src.zip.
## [ ] _*+PUHTI*_ Compute an MD5 checksum for the zip package
# [ ] _*+PUHTI*_ Add the download package, MD5 checksum file and readme and license files to the directory {{/scratch/clarin/download_preview}} on Puhti
# [ ] _*+TEST*_ Have the package tested
# [ ] _*?LBR*_ Create an LBR record (for a RES corpus)
# [ ] _*+CSC*_ Upload the package to the download service (or ask someone with the rights to do that)
# [ ] _*+TEST*_ Have it tested again (access rights!)
\\
```

### _shortname_: Announce the publication of the source data in Download

```
# [ ] _*+DB*_ In the resource database, change the resource status from upcoming to published
# [ ] _*+META*_ Update the [COMEDI | https://clarino.uib.no/comedi/records] record: (update and) add the location PID (under Resources) and add the Availability start date (under Distribution)
# [ ] _*?PORTAL*_ If applicable, add the new resource version to the license page of the previous versions [how to create/update license pages | https://www.kielipankki.fi/intra/creating-license-pages/ ]
# [ ] _*?META*_ Update the [COMEDI | https://clarino.uib.no/comedi/records] record: add relations to previous or parallel versions/variants of the corpus
# [ ] _*+PORTAL*_ Create or update the resource group page, and make sure the metadata record also contains a link to the resource group page
# [ ] _*?META*_ If required, create a portal page "shortname: Notes for the user", to inform about found issues in the data. Make sure the [COMEDI | https://clarino.uib.no/comedi/records] record also contains a link to the notes' page (in case the information is only one sentence, add it directly to the metadata description).
# [ ] _*+PORTAL*_ Publish news about the new corpus on the Portal
# [ ] _*+DB*_ Add the Language Bank Publication Date to the [resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_1]
# [ ] _*?SUPPORT*_ Inform the depositor/rightholder about the publication
\\
```

### _shortname_: Clean up after publishing the source data
```
# [ ] _*?CSC*_ Ask Martin (CSC) to add the data to Kielipankki directory {{/appl/data/kielipankki}} on Puhti if the source data is to be published there
# [ ] _*+PUHTI*_ Remove the download package, MD5 checksum file and readme and license files from the directory {{/scratch/clarin/download_preview}} on Puhti
\\
```

<a name="korp"></a>

***

***Publish the resource in Korp***

### _shortname_: Prepare for publishing the resource in Korp

```
# [ ] _*+META*_ Create a [COMEDI | https://clarino.uib.no/comedi/records] record [instructions for creating metadata records | https://www.kielipankki.fi/development/creating-metadata-records/ ]
# [ ] _*+GITHUB*_ Request URNs (for COMEDI, Korp, license pages)
# [ ] _*+DB*_ Add the corpus to the resource database and make sure it is on the list of upcoming resources and citable
# [ ] _*+PORTAL*_ Create/update license pages [how to create/update license pages | https://www.kielipankki.fi/intra/creating-license-pages/ ]
# [ ] _*?LBR*_ Ask CSC to create an LBR record (for a RES corpus! This needs the official corpus name, a persistant identifier for the metadata and a rudimental license page with PID)
# [ ] _*+META*_ Add citation information to the [COMEDI | https://clarino.uib.no/comedi/records] record
# [ ] _*+PORTAL*_ Create or update the resource group page, and make sure the metadata record also contains a link to the resource group page
\\
```

### _shortname_: Convert the data for publishing the resource in Korp

```
# [ ] _*?DATA*_ Get the source (or original) data from IDA, from the download service, or from the HFST server.
# [ ] _*?HYSTORE*_ In case intermediate versions need to be maintained at any point, upload the data as a zip file (named as shortname-korp_yyyymmdd.zip) and the separate shortname-korp_yyyymmdd_README.txt file to the HFST server, under data/corpora/wip/ (= “work in progress”).
# [ ] _*?DATA*_ Convert the data to HRT
# [ ] _*?DATA*_ Convert HRT to VRT (tokenizing)
# [ ] _*?DATA*_ Convert the data directly to VRT (alternative to HRT->VRT)
# [ ] _*+META*_ Store the scripts you used in GitHub
# [ ] _*+META*_ Add information about annotation and tools used during the corpus processing pipeline to the Epic description field, in order to be added to the metadata record
# [ ] _*+META*_ If additional documentation is needed, create a separate Jira-ticket
\\
```

### _shortname_: Parse the data for publishing the resource in Korp

```
# [ ] _*?DATA*_ Parse the data (for corpora in languages with a parser)
# [ ] _*?DATA*_ Re-order or group the data (e.g. chapters, articles)
# [ ] _*?DATA*_ Add additional annotations
## [ ] _*?DATA*_ Add name annotations
## [ ] _*?DATA*_ Add sentiment annotations
## [ ] _*?DATA*_ Add identified languages
# [ ] _*+DATA*_ Validate the VRT data
# [ ] _*+DATA*_ Check the positional attributes
## [ ] _*?DATA*_ Re-order to the commonly used order if necessary
# [ ] _*+META*_ Store the scripts you used in GitHub
# [ ] _*+META*_ Add information about annotation and tools used during the corpus processing pipeline to the Epic description field, in order to be added to the metadata record
# [ ] _*+META*_ If additional documentation is needed, create a separate Jira-ticket
\\
```

### _shortname_: Create a Korp corpus package (korp-make)

```
# [ ] _*?HYSTORE*_ In case the data is only published as a scrambled version, upload the unscrambled base data as a zip file (named as shortname-korp-base_yyyymmdd.zip) and the separate shortname-korp-base_yyyymmdd_README.txt file to the HFST server, under data/corpora/korp-base/.
# [ ] _*+DATA*_ Create a Korp corpus package ({{{}korp-make{}}})
## [ ] _*?DATA*_ Create a configuration file named korp-make-CORPUS.conf, where CORPUS is an abbreviation of the corpus name (short name).
## [ ] _*?DATA*_ Execute the script korp-make and make sure it has run through without error messages (check the log files)
# [ ] _*+KORP*_ Install the corpus package on the Korp server (or ask someone with the rights to do that)
\\
```

### _shortname_: Create the Korp corpus configuration

```
# [ ] _*+GITHUB*_ Add corpus configuration to Korp (currently, a new branch in [Kielipankki-korp-frontend|https://https//github.com/CSCfi/Kielipankki-korp-frontend])
## [ ] _*+DATA*_ Add the configuration proper to a Korp mode file
## [ ] _*+DATA*_ Add translations of new attribute names (and values)
## [ ] _*+GITHUB*_ Push the branch to GitHub
\\
```

### _shortname_: Create a Korp test version

```
# [ ] _*?LBR*_ Create an LBR record (for a RES corpus, if the corpus does not yet have one)
# [ ] _*+KORP*_ Create a Korp test instance and install the new configuration branch to it (or ask someone with the rights to do that)
# [ ] _*?KORP*_ For a non-PUB corpus, add temporary access rights for the people who should test it (with the {{authing/auth}} script on the Korp server)
# [ ] _*+TEST*_ Test the corpus in Korp (Korp test version) and ask someone else to test it, too
## [ ] _*?SUPPORT*_ Ask feedback from the corpus owner (depending on how involved they wish to be)
# [ ] _*?DATA*_ Fix corpus data and re-publish (if needed)
# [ ] _*?GITHUB*_ Fix Korp configuration and re-publish (if needed)
\\
```

### _shortname_: Publish the corpus in Korp as release candidate

```
# [ ] _*+KORP*_ Publish the corpus in Korp as a release candidate version
## [ ] _*+GITHUB*_ Merge the corpus configuration branch to branch {{master}}
## [ ] _*+KORP*_ Install the updated {{master}} branch to production Korp (or ask someone with the rights to do that)
# [ ] _*+GITHUB*_ Add news about this new corpus to the Korp newsdesk ([https://github.com/CSCfi/Kielipankki-korp-frontend/tree/news/master])

\\
```

### _shortname_: Announce the publication of the new Korp corpus as release candidate

```
# [ ] _*+DB*_ In the resource database, change the resource status from upcoming to published (add status "release candidate" to the name!)
# [ ] _*+META*_ Update [COMEDI | https://clarino.uib.no/comedi/records]  record; add location PID (under Resources) and Availability start date (under Distribution)
# [ ] _*?META*_ Update the metadata record: add relations to previous or parallel versions/variants of the corpus
# [ ] _*?META*_ Update the metadata record: add annotation information and tools used during the corpus processing pipeline
# [ ] _*+META*_ Add "release candidate" status information to metadata record
# [ ] _*?META*_ If required, create a portal page "shortname: Notes for the user", to inform about found issues in the data. Make sure the [COMEDI | https://clarino.uib.no/comedi/records] record also contains a link to the notes' page (in case the information is only one sentence, add it directly to the metadata description).
# [ ] _*+PORTAL*_ Publish news about this new corpus in the portal
# [ ] _*+DB*_ Add the Language Bank Publication Date to the [resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_1]
## [ ] _*+META*_ Add the date when the release candidate status can be removed (two weeks from now) to the following two stories (about removing the release candidate status)
# [ ] _*?SUPPORT*_ Inform corpus owner and possibly interested researchers on the corpus in Korp and ask them to test it
\\
```

### _shortname_: Fix the data and publish a new release candidate (if needed)
```
# [ ] _*?DATA*_ Fix corpus data based on feedback
# [ ] _*?KORP*_ Fix corpus configuration in Korp
# [ ] _*+KORP*_ Publish the corpus in Korp as a new release candidate version
## [ ] _*+GITHUB*_ Merge the corpus configuration branch to branch {{master}}
## [ ] _*+KORP*_ Install the updated {{master}} branch to production Korp (or ask someone with the rights to do that)
# [ ] _*+META*_ Document the changes done to fix the data, in order to be added to metadata record and the resource group page
\\
```

### _shortname_: Announce the publication of the new Korp corpus as another release candidate (if needed)
```
# [ ] _*+META*_ Add "release candidate" version status information to metadata record record
# [ ] _*+META*_ Add the documentation of changes done to the data to the CHANGE-LOG in the metadata record (if needed)
# [ ] _*+META*_ Add the documentation of changes done to the data to the resource group page (if needed)
# [ ] _*+META*_  Add or update information about tools used in the data processing to the metadata record (if needed)
# [ ] _*+META*_ Add the date when the new release candidate status can be removed (two weeks from now) to the following two stories (about removing the release candidate status)
# [ ] _*?SUPPORT*_ Inform corpus owner and possibly interested researchers on the corpus in Korp and ask them to test it
\\
```

### _shortname_: Remove release candidate status 
```
# [ ] _*+KORP*_ Remove release candidate status after two weeks, if no requests for corrections or changes appear during this period
## [ ] _*+KORP*_ Remove release candidate status from Korp configuration ({{{}master{}}}), push and install the updated {{master}}
## [ ] _*+KORP*_ Install the updated {{master}} branch to production Korp (or ask someone with the rights to do that)
\\
```

### _shortname_: Clean up and document after publishing in Korp 
```
# [ ] _*+TEST*_ Remove the corpus from the testing environment of Korp (Korp test version)
# [ ] _*+PUHTI*_ Remove any corpus data, used or created during the conversion process, from scratch on Puhti (usually the person who ran korp-make should take care of this)
# [ ] _*+META*_ Store the scripts you used in GitHub
# [ ] _*+META*_ Create or update a list of annotation information and tools used during the corpus processing pipeline, in order to be added to the metadata record
# [ ] _*+META*_ If additional documentation is needed, create a separate Jira-ticket
\\
```


### _shortname_: Announce the removal of release candidate status after publishing in Korp

```
## [ ] _*+META*_ Remove release candidate status from the metadata record
## [ ] _*+PORTAL*_ Remove release candidate status from the [resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_1]
\\
```


***

***Publish the VRT data in Download***

### _shortname_: Prepare for publishing the VRT data in Download

```
# [ ] _*+META*_ Create a [COMEDI | https://clarino.uib.no/comedi/records] record [instructions for creating metadata records | https://www.kielipankki.fi/development/creating-metadata-records/ ]
# [ ] _*+GITHUB*_ Request URNs (for COMEDI, download, license pages)
# [ ] _*+DB*_ Add the details of the corpus variant to the [resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_1], status "upcoming"
# [ ] _*+PORTAL*_ Create/update the license pages [how to create/update license pages | https://www.kielipankki.fi/intra/creating-license-pages/ ]
# [ ] _*+DB*_ Link the corpus variant with the correct license row in the [resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_1]
# [ ] _*+META*_ Add citation information to the [COMEDI | https://clarino.uib.no/comedi/records] record
# [ ] _*+PORTAL*_ Create or update the resource group page, and make sure the metadata record also contains a link to the resource group page
\\
```

### _shortname_: Package and upload the VRT data

```
# [ ] _*+KORP*_ Extract the data from Korp (unless more recent content can be acquired in VRT format from outside Korp)
# [ ] _*?HYSTORE*_ In case intermediate versions need to be maintained at any point, upload the data as a zip file (named as shortname-vrt_yyyymmdd.zip) and the separate shortname-vrt_yyyymmdd_README.txt file to the HFST server, under data/corpora/wip/ (= “work in progress”).
# [ ] _*+PUHTI*_ Create a download package
## [ ] _*+PUHTI*_ Create and add the downloadable readme and license files [how to create/update license pages | https://www.kielipankki.fi/intra/creating-license-pages/ ]
## [ ] _*+PUHTI*_ Zip the data and the readme and license files
## [ ] _*+PUHTI*_ Compute MD5 checksum for the zip package
# [ ] _*+PUHTI*_ Add the download package, MD5 checksum file and readme and license files to the directory {{/scratch/clarin/download_preview}} on Puhti
# [ ] _*+PUHTI*_ If the package is published as release candidate (during the release candidate stage of the corresponding Korp corpus), add the file RELEASE_CANDIDATE.txt to the directory {{/scratch/clarin/download_preview}} on Puhti
# [ ] _*+TEST*_ Have the package tested
# [ ] _*+CSC*_ Upload the package to the download service or ask someone with the rights to do that
# [ ] _*?LBR*_ Create an LBR record (for a RES corpus, if the corpus does not yet have one)
# [ ] _*+TEST*_ Have it tested again (access rights!)
\\
```

### _shortname_: Announce the publication of the VRT data in Download
```
# [ ] _*+DB*_ In the resource database, change the resource status from upcoming to published
# [ ] _*+META*_ Update the [COMEDI | https://clarino.uib.no/comedi/records] record; add location PID (under Resources) and Availability start date (under Distribution)
# [ ] _*?META*_ Update the [COMEDI | https://clarino.uib.no/comedi/records] record: add relations to previous or parallel versions/variants of the corpus
# [ ] _*+PORTAL*_ Create or update the resource group page
# [ ] _*?META*_ If the package is published as release candidate (during the release candidate stage of the corresponding Korp corpus), add release candidate status to the metadata record and database
# [ ] _*?META*_ If required, create a portal page "shortname: Notes for the user", to inform about found issues in the data. Make sure the metadata record also contains a link to the notes' page (in case the information is only one sentence, add it directly to the metadata description).
# [ ] _*+PORTAL*_ Publish news about the new corpus on the Portal
# [ ] _*+DB*_ Add the Language Bank Publication Date to the [resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_1]
## [ ] _*+META*_ If the package is published as release candidate, add the date when this status can be removed (two weeks from now) to the following story (about removing the release candidate status)
# [ ] _*?SUPPORT*_ Inform the depositor/rightholder and interested researchers about the VRT publication
\\
```

### _shortname_: Clean up after publishing the VRT in Download (remove release candidate status if needed) 
```
# [ ] _*?META*_ If the package was published as release candidate (during the release candidate stage of the corresponding Korp corpus), remove the release candidate status after removing the release candidate status from Korp
## [ ] _*+CSC*_ Remove the file RELEASE_CANDIDATE.txt from the respective download directory
## [ ] _*?META*_ Remove the release candidate status from the metadata record and database
# [ ] _*?CSC*_ Ask Martin to add the data to Kielipankki directory {{/appl/data/kielipankki}} on Puhti (if the corpus is PUB or ACA)
# [ ] _*+PUHTI*_ Remove the download package, MD5 checksum file and readme and license files from the directory {{/scratch/clarin/download_preview}} on Puhti
\\
```
