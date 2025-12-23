
# Checklists for tasks in the resource publishing pipeline

After discovering a new resource that should be made available via Kielipankki, 
we need a list of the relevant tasks that must be completed.

In case an already published resource has to be **un-published**, please follow these instructions [docs: howto unpublish a resource](https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_unpublish_corpus.md).

## Overview

1. <a href="#jira-epic">Create an Epic about publishing the new resource</a>
2. <a href="#copy-task-titles">Copy the relevant Jira task titles to the Description of the Epic</a>
3. <a href="#copy-metadata-fields">Copy the metadata fields of the applicable resource versions to the Description of the Epic</a>
4. <a href="#use-checkboxes">Using the checkboxes for monitoring the workflow</a>
5. <a href="#create-stories">Create the Jira Stories of the relevant task lists as issues under the main Epic</a>
   - <a href="#start-the-pipeline">Enter to the pipeline
   - <a href="#publish-source">Publish the source version in Download
   - <a href="#korp">Publish in Korp
   - <a href="#publish-vrt">Publish the VRT version in Download

----

<a name="jira-epic"></a>
### 1. For each new resource (or a new version of an existing resource), create an "Epic" issue on Jira. 
   - The _Epic Name_ of the Jira Epic issue should contain nothing but the shortname(s) of the resource(s) in question. For choosing the shortname see [language resource naming conventions](https://www.kielipankki.fi/development/language-resource-naming-conventions/).
   - The _Summary_ of the Epic (the longer title, displayed on top of the Epic's page) should be composed as follows:
   
    shortname: Publish "XXX" in Kielipankki (Korp/Download/…)
   
   - Replace _shortname_ with the short name of the resource in question (use the "base" name only, excluding "-src" etc.).

   - Replace "XXX" with the common title of the resource group in question, to make the issue easier to find in Jira.
   - In brackets, you may specify the resource variant(s) that is/are to be published during this Epic, according to current plan: just the Download, and/or Korp, etc. 


<a name="copy-task-titles"></a>
### 2. Copy the following list of section titles to the top of the description of the Epic. Remove the sections that are not applicable to or planned for the current resource.

```
Enter a new resource to the pipeline
# [ ]  Start negotiations with the depositor
# [ ]  Enter the new resource to the pipeline
# [ ]  Prepare the preliminary metadata of the resource
# [ ]  Plan the publication process with the depositor
# [ ]  Clear the license for the resource
## [ ]  Archive the signed deposition agreement for the resource
# [ ]  Publish the end-user license
# [ ]  Acquire the original data

Publish the source data in Download
# [ ]  Prepare for publishing the source data in Download
# [ ]  Package and upload the source data
## [ ]  Upload to the download service
## [ ]  Create an LBR record for a RES-licensed corpus
# [ ]  Announce the publication of the source data in Download
# [ ]  Clean up after publishing the source data in Download

Publish the resource in Korp
# [ ] Prepare for publishing the resource in Korp
# [ ]  Convert the data for publishing the resource in Korp
# [ ]  Parse the data for publishing the resource in Korp
# [ ]  Create a Korp corpus package (korp-make)
# [ ]  Create the Korp corpus configuration
# [ ]  Create a Korp test version
## [ ]  Create an LBR record for a RES-licensed corpus
# [ ]  Publish the corpus in Korp as release candidate
# [ ]  Install the corpus package on the Korp server
# [ ]  Announce the publication of the new Korp corpus as release candidate
# [ ]  Fix the data and publish a new release candidate (if needed)
# [ ]  Announce the publication of the new Korp corpus as another release candidate (if needed)
# [ ]  Remove release candidate status
# [ ]  Clean up and document after publishing in Korp
# [ ]  Announce the removal of release candidate status after publishing in Korp

Publish the VRT data in Download
# [ ]  Prepare for publishing the VRT data in Download
# [ ]  Package and upload the VRT data
## [ ]  Upload to the download service
## [ ]  Create an LBR record for a RES-licensed corpus
# [ ]  Announce the publication of the VRT data in Download (as release candidate if needed)
# [ ]  Clean up after publishing the VRT in Download (remove release candidate status if needed) 
```

   - **There is no need to copy-paste the _shortname_ of the resource on all items in this task list!** However, the shortname should be mentioned in the titles of the corresponding Jira issues. 
   - To make sure that the lists are rendered correctly, the text should be pasted when the Jira description input field is in “Text” mode, not “Visual”.


<a name="copy-metadata-fields"></a>
### 3. Add to the description field **all important metadata** (for all versions, as a collection), as soon as they are created (e.g., PIDs are requested, ...), in the following form:


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

----
(If applicable, include the following information about the processing tools – this applies usually at least to Korp and VRT versions:)
     
*Tools used to process the data:*

# [ ] *VRT tools* (_please specify_), http://urn.fi/urn:nbn:fi:lb-2024021502. Annotation type: (_please specify_). Segmentation level: (_please specify_).
# [ ] *UDPipe-LBF* as a tokenizer, http://urn.fi/urn:nbn:fi:lb-201902131. Annotation type: segmentation. Segmentation level: paragraph. 
# [ ] *UDPipe-LBF* as a morpho-syntactic parser, http://urn.fi/urn:nbn:fi:lb-201902131. Annotation type: morphosyntacticAnnotation-posTagging. Segmentation level: sentence. 
# [ ] *TDPP-LBF* as a morpho-syntactic parser, http://urn.fi/urn:nbn:fi:lb-2024021503. Annotation type: morphosyntacticAnnotation-posTagging. Segmentation level: sentence. 
# [ ] *Finnish Tagtools* version 1.6, http://urn.fi/urn:nbn:fi:lb-2024021401. Annotation type: (_please specify_). Segmentation level: (_please specify_)
# [ ] *FiNER*, http://urn.fi/urn:nbn:fi:lb-2024021401. Annotation type: semanticAnnotation-namedEntities. Segmentation level: word
# [ ] *HeLI-OTS* version 2.0, http://urn.fi/urn:nbn:fi:lb-2024040301. Annotation type: language identification. Segmentation level: sentence.

(Please add or remove information as required!)

```

<a name="use-checkboxes"></a>
### 4. Using the checkboxes for monitoring the workflow

Each task description is preceded by “[ ]”, representing a checkbox, and a tag representing the task type. 

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


<a name="create-stories"></a>
### 5. In the Epic, create a "Story" for each of the applicable task list sections which were previously copied to the Epic description. 
  - In case the resource is a completely new one and it has not been decided what should be done with it, just create the first story ("_shortname:_ Start negotiations with the depositor", see the first section of tasks below).
  - Use the corresponding section title in the task list as the name of the Story.
  - Replace "_shortname_" with the short name of the resource in question (use the "base" name only, excluding "-src" etc.). This makes it easier to see which resource is addressed in each individual Jira ticket.
  - Copy & paste the appropriate task list from below to the description field of the Story.
  - In each Story, you may adjust the list items and their order as appropriate for the resource in question. 
  For example, LBR records are only needed for RES licensed corpora. Thus, if you already know the corpus license will not be RES, you may remove or overstrike the LBR-related tasks.


## The task lists for the Stories in Epic

The following lists should contain the tasks required for publishing a corpus. The tasks are in the rough order in which they should typically be completed.

*Recap: For each of the section titles below, create a Story and assign it as "In Epic", providing the name/number of the Epic of the resource in question. Copy & paste the appropriate task lists from below to the description field of the corresponding Jira stories.*


***

<a name="start-the-pipeline"></a>

***Enter a new resource to the pipeline***

### _shortname_: Start negotiations with the depositor

```
# [ ] _*+MANAGE*_ Create a Jira Epic issue with the Epic Name "shortname" and the title "shortname: Publish XXX in Kielipankki (Korp/Download/…)".
# [ ] _*?SUPPORT*_ Contact the potential depositor (by email; arrange a meeting if required) 
# [ ] _*?SUPPORT*_ Ask the depositor to submit the basic details of the new corpus or resource (e-form: [http://urn.fi/urn:nbn:fi:lb-2021121421](http://urn.fi/urn:nbn:fi:lb-2021121421))
# [ ] _*+MANAGE*_ Copy-paste the content of the e-form as a comment under the main Epic.
# [ ] _*+SUPPORT*_ Send a brief feedback email to the depositor, to let them know that we received the information and will get back to them in the near future, regarding the metadata record and the next steps.
# [ ] _*+MANAGE*_ Insert the next pipeline Story under the Jira Epic and assign it forward. If there is something noteworthy in the e-form, add a comment under the new Story, so that it can be discussed, and prioritize accordingly.
\\
```

### _shortname_: Enter the new resource to the pipeline

```
# [ ] _*?DISCUSS*_ If the size and technical specifications of the corpus seem "non-standard" in some respect, discuss the corpus details in an internal meeting to see if it is technically feasible to publish it in the Language Bank
# [ ] _*+MANAGE*_ Insert the relevant parts of the pipeline task list as Jira Stories, each one linked under the main Epic of this resource publication process.
# [ ] _*+MANAGE*_ Add the placeholders for all relevant metadata to the description of the main Epic (take a copy from the model description on the top of this page). Remove all non-relevant parts in the Epic description.
# [ ] _*+MANAGE*_ Make sure that the list of tasks in the Epic description matches the Jira Stories linked under the Epic (i.e., that no Stories are missing).
\\
```

### _shortname_: Prepare the preliminary metadata of the resource

```
# [ ] _*+GITHUB*_ [Request a URN | https://github.com/CSCfi/Kielipankki/tree/master/FIN-CLARIN-Administration] for the metadata record [how to request PIDs | https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_request_pid.md]
# [ ] _*+GITHUB*_ [Request the URNs | https://github.com/CSCfi/Kielipankki/tree/master/FIN-CLARIN-Administration] for the license pages [how to request PIDs | https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_request_pid.md]
# [ ] _*+META*_ In [COMEDI | https://clarino.uib.no/comedi/records], create and publish a preliminary metadata record for the first resource version. Use the information from the e-form, see comments under the main Epic. [Instructions for creating metadata records | https://www.kielipankki.fi/development/creating-metadata-records/ ]
# [ ] _*+META*_ In [COMEDI | https://clarino.uib.no/comedi/records], update the metadata record with the metadata URN.
# [ ] _*+DB*_ Add the [corpus to the resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_1 ] and make sure the resource is displayed on the list of [upcoming corpora | https://www.kielipankki.fi/aineistot/tulevat/ ]
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
\\
```

<a name="license"></a>

### _shortname_: Clear the license for the resource

```
# [ ] _*+DB*_ In the [resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_2 ], create a new (preliminary) license instance for the resource, or link an existing license instance to the resource, if available
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
# [ ] _*+AGREEMENT*_ Make a copy of the [deposition agreement template | https://helsinkifi-my.sharepoint.com/:f:/r/personal/lennes_ad_helsinki_fi/Documents/Kielipankin%20sopimusasiat/DELA%20-%20Sopimuspohjat?csf=1&web=1&e=zRNnQQ ]into a new folder (labeled as _shortname_) and prepare a preliminary version of the documents for discussion
## [ ] _*?AGREEMENT*_ Make arrangements to meet the depositor about the details of the deposition agreement
## [ ] _*?SUPPORT*_ Meet with the depositor/rightholder and take note of the action points
## [ ] _*+LEGAL*_ Make the final decision as to whether the resource can be distributed via the Language Bank of Finland (bring the case up in legal meeting, if necessary)
## [ ] _*+AGREEMENT*_ Prepare the final draft of the deposition license agreement and send it to corpus owner who should fill in the remaining gaps (ask for legal advice if needed)
## [ ] _*+AGREEMENT*_ Check the final deposition agreement, combine all parts into a single pdf file and upload the document to the [UniSign | https://unisign.helsinki.fi/] system for electronic signing by the rightholder (+ the data controller) and finally by the head of department at the University of Helsinki ([How to use UniSign | https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_have_agreement_signed.md ])
# [ ] _*+AGREEMENT*_ Download a copy of the signed deposition agreement from the digital signature system (UniSign) to the shared OneDrive folder.
# [ ] _*+AGREEMENT*_ In this Jira issue, add a comment stating the final license conditions, the rightholder(s), and the final list of the persons to be cited, according to the signed agreement. Update the license label to the description of the main Epic.
# [ ] _*?AGREEMENT*_ Notify the colleagues who are responsible for publishing the license pages and the resource content that the license was confirmed.
# [ ] _*+DB*_ In the [resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_2 ], update the signature date and the license conditions of the resource.
\\
```

### _shortname_: Archive the signed deposition agreement for the resource

```
# [ ] _*+IDA*_ Upload and freeze the signed deposition agreement (or similar proof of the distribution license) as a pdf file (named as _KP_yyyy_AINEISTO_shortname_yyyymmdd.pdf_, according to the date of the last signature in the document) in IDA, under Administration/agreements/shortname. [How to archive signed agreements | https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_archive_signed_agreements.md]
# [ ] _*+HYSTORE*_ Upload the signed deposition agreement (or similar proof of the cleared distribution license) as a pdf file (named as _KP_yyyy_AINEISTO_shortname_yyyymmdd.pdf_, according to the date of the last signature in the document) to the HFST server, under _/data/corpora/agreements/shortname_. [How to archive signed agreements | https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_archive_signed_agreements.md]
# [ ] _*+AGREEMENT*_ Upload the signed deposition agreement (or similar proof of the cleared distribution license) as a pdf file named as _KP_yyyy_AINEISTO_shortname_yyyymmdd.pdf_, according to the date of the last signature in the document; document title _Kielipankki yyyy Aineistosopimus: shortname(s)_, to the [contract register | https://sopimus.helsinki.fi/ ] of the University of Helsinki, under H402 Digitaalisten ihmistieteiden osasto. By default, agreements are not 'confidential'. [How to archive signed agreements |https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_archive_signed_agreements.md]
# [ ] _*+DB*_ In the [resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_2 ], update the deposition agreement locations.
\\
```

### _shortname_: Publish the end-user license

```
# [ ] _*+PORTAL*_ [Create the license pages | https://www.kielipankki.fi/wp-admin/edit.php?post_type=page&page=cms-tpv-page-page ] if required [(how to create license pages) | https://www.kielipankki.fi/intra/creating-license-pages/ ]  
# [ ] _*?PORTAL*_ For a PRIV license, create and translate the pages for data protection terms and conditions and inform the depositor
# [ ] _*?GITHUB*_ If required, [request the URNs] (https://github.com/CSCfi/Kielipankki/tree/master/FIN-CLARIN-Administration) for the PRIV condition pages 
# [ ] _*+PORTAL*_ Update the license PIDs in the [resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_2 ]and make sure the resource in question is linked with the correct license instance in the resource database
# [ ] _*+META*_ Create/update the [COMEDI | https://clarino.uib.no/comedi/records] record, including the license information and the people to be cited, according to the agreement [instructions for creating metadata records | https://www.kielipankki.fi/development/creating-metadata-records/ ]
# [ ] _*+PORTAL*_ In case the resource has a RES license, add the relevant details to the table LBR-katselmointiprosessi ([https://www.kielipankki.fi/wp-admin/admin.php?page=tablepress&action=edit&table_id=37 ]), shown on the intranet page [Katselmointiprosessi |https://www.kielipankki.fi/intra/katselmointiprosessi/ ]
# [ ] _*?DISCUSS*_ If the license requires further processing steps and resources from Kielipankki, bring them up for discussion in an internal meeting.
# [ ] _*?PORTAL*_ After the deposition license agreement has been signed, publish the license page and the data protection terms and conditions.
# [ ] _*+DB*_ In the [resource database | https://www.kielipankki.fi/wp-admin/admin.php?page=wpda_wpdp_1_2 ], update the license status to 'available'.
\\
```

### _shortname_: Acquire the original data

```
# [ ] _*?DATA*_ In case the resource contains personal data (+PRIV) or other confidential information, make sure you [protect the data with appropriate measures | https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_protected_packages.md ]. 
# [ ] _*+DATA*_ Receive, download or harvest the data
# [ ] _*+DATA*_ Check the data: format and validity
## [ ] _*?DATA*_ Clean up the data
# [ ] _*+DATA*_ Create a simple shortname-orig_yyyymmdd_README.txt for the original data, see [instructions| https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_archive_original_data.md ].
# [ ] _*?DATA*_ In case the resource contains personal data (+PRIV) or other confidential information, [include the original zip file(s) in a new, password-protected zip package| https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_protected_packages.md ] for internal storage and transfer. Make sure the [password is shared internally | https://github.com/CSCfi/Kielipankki-passwords/blob/master/howto_manage_corpus_passwords.md ].
# [ ] _*+HYSTORE*_ Upload the original data as a zip file (named as _shortname-orig_yyyymmdd.zip_) and the separate _shortname-orig_yyyymmdd_README.txt_ file to the HFST server, under _data/corpora/originals/_.
# [ ] _*?IDA*_ If the source version (to be published in download) is going to be very different from the original, upload the original data to IDA as a zip file (named as _shortname-orig_yyyymmdd.zip_) and the separate _shortname-orig_yyyymmdd_README.txt_ file, under the folder with the resource group shortname, in lowercase characters. Apply password protection if the license is RES.
# [ ] _*?IDA*_ If applicable, freeze the new files in the original data folder in IDA.
\\
```

***
<a name="publish-source"></a>

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
# [ ] _*?DATA*_ In case the resource contains personal data (+PRIV) or other confidential information, [include the original zip file(s) in a new, password-protected zip package| https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_protected_packages.md ] for internal storage and transfer. Use the [appropriate password| https://github.com/CSCfi/Kielipankki-passwords/blob/master/howto_manage_corpus_passwords.md ].
# [ ] _*+PUHTI*_ Add the download package, MD5 checksum file and readme and license files to the directory {{/scratch/clarin/download_preview}} on Puhti
# [ ] _*+TEST*_ Have the package tested
# [ ] _*?MANAGE*_ If this is a RES-licensed corpus and an LBR application does not yet exist, fill in an instance of the [Jira issue "_shortname_: Create an LBR record for a RES-licensed corpus" | https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/corpus_publishing_tasklist.md#csc_lbr ] and assign it forward to CSC (add label: lb-csc-task and prioritize if needed).
# [ ] _*+MANAGE*_ Have the package uploaded to the download service: fill in an instance of [the Jira issue "_shortname_: Upload to the download service" | https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/corpus_publishing_tasklist.md#csc_upload ] and assign it forward to CSC (add label "lb-csc-task" and prioritize if needed).
# [ ] _*+TEST*_ When uploaded, have the package tested again and check access rights.
\\
```

<a name="csc_upload"></a>
### _shortname_: Upload to the download service

```
Upload the package to the download service. In case the package was encrypted for temporary storage, make sure the package is safely decrypted for the download service.

*Target directory:* https://www.kielipankki.fi/download/shortname…
*Location of the files to be uploaded:* (Typically, a folder 'shortname' under download_preview in Puhti.)
*List of the files to be uploaded:* (corpus package(s), README.txt and LICENSE.txt, maybe RELEASE_CANDIDATE.txt)
*Encrypted* (yes/no) (If using encryption for internal processing, CSC must decrypt the packages for the download service.)
*Description text of the download directory:* (resource (group) name in English)
*Link from the directory description:* (resource group PID)

In case there are subfolders for different versions of the resource, e.g. src and vrt:
*Description text of the subfolder:* (name of the resource version in English)
*Link from the subfolder description:* (metadata PID)

*Description text/title of individual resource packages:* (license label, e.g. CC-BY-NC)
*Link from the resource package description* (PID of the license page in English):
*Access restrictions:* public access / ACA license / RES license (please describe)

```

<a name="csc_lbr"></a>
### _shortname_: Create/update the LBR record for the RES-licensed corpus

(NB: This issue is only required for RES-licensed resources.)
```
Create the LBR record, or update the existing one, according to the information below.

*Title of the resource(s) covered (ENG):*
*Title of the resource(s) covered (FIN):* 
*The PID of the resource group covered by this LBR application:* (the PID of the English resource group page) 
*License label:* (copy of the title of the license page)
*License PID (ENG):*
*License PID (FIN):*
*Is a privacy notice and an estimated end date of research required? (+PRIV):* yes/no
*Additional details of the application (description of the requirements and the approval process if needed):* Please see [LBR-katselmointiprosessi | https://www.kielipankki.fi/wp-admin/admin.php?page=tablepress&action=edit&table_id=37], shown on the intranet page [Katselmointiprosessi |https://www.kielipankki.fi/intra/katselmointiprosessi/ ].




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


***

<a name="korp"></a>
***Publish the resource in Korp***

### _shortname_: Prepare for publishing the resource in Korp

```
# [ ] _*+META*_ Create a [COMEDI | https://clarino.uib.no/comedi/records] record [instructions for creating metadata records | https://www.kielipankki.fi/development/creating-metadata-records/ ]
# [ ] _*+GITHUB*_ Request URNs (for COMEDI, Korp, license pages)
# [ ] _*+DB*_ Add the corpus to the resource database and make sure it is on the list of upcoming resources and citable
# [ ] _*+PORTAL*_ Create/update license pages [how to create/update license pages | https://www.kielipankki.fi/intra/creating-license-pages/ ]
# [ ] _*?META*_ If this is a RES-licensed corpus and an LBR application does not yet exist, create and fill in another instance of [Jira issue "_shortname_: Create an LBR record for a RES-licensed corpus" | https://github.com/CSCfi/Kielipankki-utilities/edit/master/docs/corpus_publishing_tasklist.md#csc_lbr ]
# [ ] _*+META*_ Add citation information to the [COMEDI | https://clarino.uib.no/comedi/records] record
# [ ] _*+PORTAL*_ Create or update the resource group page, and make sure the metadata record also contains a link to the resource group page
\\
```

### _shortname_: Convert the data for publishing the resource in Korp

```
# [ ] _*?DATA*_ Get the source (or original) data from IDA, from the download service, or from the HFST server.
# [ ] _*?HYSTORE*_ In case intermediate versions need to be maintained at any point, upload the data as a zip file (named as shortname-korp_yyyymmdd.zip) and the separate shortname-korp_yyyymmdd_README.txt file to the HFST server, under data/corpora/wip/ (= “work in progress”).
# [ ] _*?DATA*_ In case the resource contains personal data (+PRIV) or other confidential information, [apply the appropriate safeguards| https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_protected_packages.md ] when processing the data. [(How to use passwords)| https://github.com/CSCfi/Kielipankki-passwords/blob/master/howto_manage_corpus_passwords.md ].
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
# [ ] _*+MANAGE*_ Have the corpus package installed on the Korp pre-production server: fill in an instance of [the Jira issue "_shortname_: Install the corpus package on the Korp server" | https://github.com/CSCfi/Kielipankki-utilities/edit/master/docs/corpus_publishing_tasklist.md#csc_korp ] and assign it forward 
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
# [ ] _*?MANAGE*_ For a RES corpus, make sure that there is an LBR application in place (check the Jira issue "_shortname_: Create an LBR record for a RES-licensed corpus")
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
# [ ] _*+MANAGE*_ Have the updated {{master}} branch installed on the production Korp server: fill in an instance of [the Jira issue "_shortname_: Install the corpus package on the Korp server" | https://github.com/CSCfi/Kielipankki-utilities/edit/master/docs/corpus_publishing_tasklist.md#csc_korp ] and assign it forward 
# [ ] _*+GITHUB*_ Add news about this new corpus to the Korp newsdesk ([https://github.com/CSCfi/Kielipankki-korp-frontend/tree/news/master])

\\
```


<a name="csc_korp"></a>
### _shortname_: Install the corpus package on the Korp server

```
# [ ] _*+KORP*_ Fill in the required information regarding the Korp corpus package
# [ ] _*+MANAGE*_ Assign this issue forward to CSC (add label "lb-csc-task" and prioritize as needed).
# [ ] _*+CSC*_ Install the corpus package on the Korp server

Location and instructions for installing the corpus package:

Access restrictions: public access / ACA license / RES license (please describe)


```

### _shortname_: Announce the publication of the new Korp corpus as release candidate

```
# [ ] _*+GITHUB*_ Update the access location URN (path in Korp)
# [ ] _*+TEST*_ Test (or have tested) the resource in production Korp and check access rights.
# [ ] _*+DB*_ In the resource database, change the resource status from upcoming to production (add status "release candidate" to the name!)
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
# [ ] _*+DB*_ Add "release candidate" version status information to the database
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

<a name="publish-vrt"></a>
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
# [ ] _*?DATA*_ In case the resource contains personal data (+PRIV) or other confidential information, [ apply the appropriate safeguards | https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_protected_packages.md ] when processing the data. [(How to use passwords) | https://github.com/CSCfi/Kielipankki-passwords/blob/master/howto_manage_corpus_passwords.md ].
# [ ] _*?HYSTORE*_ In case intermediate versions need to be maintained at any point, upload the data as a zip file (named as shortname-vrt_yyyymmdd.zip) and the separate shortname-vrt_yyyymmdd_README.txt file to the HFST server, under data/corpora/wip/ (= “work in progress”).
# [ ] _*+PUHTI*_ Create a download package
## [ ] _*+PUHTI*_ Create and add the downloadable readme and license files [how to create/update license pages | https://www.kielipankki.fi/intra/creating-license-pages/ ]
## [ ] _*+PUHTI*_ Zip the data and the readme and license files
## [ ] _*+PUHTI*_ Compute MD5 checksum for the zip package
# [ ] _*?DATA*_ In case the resource contains personal data (+PRIV) or other confidential information, [include the original zip file(s) in a new, password-protected zip package| https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/howto_protected_packages.md ] for internal storage and transfer. Use the [appropriate password| https://github.com/CSCfi/Kielipankki-passwords/blob/master/howto_manage_corpus_passwords.md ].
# [ ] _*+PUHTI*_ Add the download package, MD5 checksum file and readme and license files to the directory {{/scratch/clarin/download_preview}} on Puhti
# [ ] _*+PUHTI*_ If the package is published as release candidate (during the release candidate stage of the corresponding Korp corpus), add the file RELEASE_CANDIDATE.txt to the directory {{/scratch/clarin/download_preview}} on Puhti
# [ ] _*+TEST*_ Have the package tested
# [ ] _*?MANAGE*_ If this is a RES-licensed corpus and an LBR application does not yet exist, fill in an instance of the [Jira issue "_shortname_: Create an LBR record for a RES-licensed corpus" | https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/corpus_publishing_tasklist.md#csc_lbr ] and assign it forward to CSC (add label "lb-csc-task" and prioritize if needed).
# [ ] _*+MANAGE*_ Have the package uploaded to the download service: fill in an instance of [the Jira issue "_shortname_: Upload to the download service" | https://github.com/CSCfi/Kielipankki-utilities/blob/master/docs/corpus_publishing_tasklist.md#csc_upload ] and assign it forward to CSC (add label "lb-csc-task" and prioritize if needed).
# [ ] _*+TEST*_ When uploaded, have the package tested again and check access rights.
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

