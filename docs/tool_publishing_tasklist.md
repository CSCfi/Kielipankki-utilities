
# Checklists for tasks in the resource publishing pipeline for TOOLS

After discovering a new *tool/service/piece of software** that needs to be made available via Kielipankki, we need a list of the relevant tasks that must be completed.

### 1. For each new tool (or a new version of an existing resource), create an "Epic" issue on Jira. 
   - Name the Epic as:
   
    shortname: Publish XXX in Kielipankki (Download/Computing environment/Online interface/External/…)
   
   - Replace "_shortname_" with the short name of the resource in question (use the "base" name only, excluding "-src" etc.).
   - Replace "XXX" with the common title of the resource group in question, to make the issue easier to find in Jira.
   - In brackets, you may specify the resource variant(s) that is/are to be published during this Epic, according to current plan: just the Download, and/or Korp, etc. 
   - NB: Both the _Epic Name_ and _Summary_ fields of the Jira Epic issue should contain identical text (= the title of the issue, composed as above).


### 2. Copy the following list of section titles to the description of the Epic. Remove the sections that are not applicable to or planned for the current resource.

```
# [ ] _shortname_: Enter the new tool to the pipeline
# [ ] _shortname_: Clear the license for the tool
# [ ] _shortname_: Publish the end-user license
# [ ] _shortname_: Acquire and test the original software
# [ ] _shortname_: Publish the source code and/or installer in Download
# [ ] _shortname_: Install the tool in the computing environment
# [ ] _shortname_: Make the tool available via an online interface
```

   - Again, replace "_shortname_" with the short name of the resource in question.
   - NB: To make sure that the lists are rendered correctly, the text should be pasted when the Jira description input field is in “Text” mode, not “Visual”.


### 3. In the Epic, create a "Story" for each of the applicable task list sections which were previously copied to the Epic description. 
  - In case the resource is a completely new one and it has not been decided what should be done with it, just create the first story ("_shortname:_ Enter the new tool to the pipeline", see the first section of tasks below).
  - Use the corresponding section title in the task list as the name of the Story.
  - Replace "_shortname_" with the short name of the resource in question (use the "base" name only, excluding "-src" etc.). This makes it easier to see which resource is addressed in each individual Jira ticket.
  - Copy & paste the appropriate task list from below to the description field of the Story.
  - In each Story, you may adjust the list items and their order as appropriate for the resource in question. 


### 4. Each task description is preceded by “[ ]”, representing a checkbox, and a tag representing the task type. 

  - When you start working on an individual task item, write your name between the square brackets (“[Name]”). 
  - When a task is completed, replace "[YourName]" with an “[X]”.
  - When all tasks in a Story are complete, you may edit the description in the main Epic and mark the corresponding section with an [X].

The task category marker is an italicized (slanted) and bolded character string. The first character is _+_ for obligatory tasks and _?_ for optional ones, and the task category markers are:

- _*MANAGE*_: general management and coordination of the corpus publication process and the related tasks (requires Jira permissions)
- _*SUPPORT*_: advising and communicating with the data depositor (requires knowledge of data management practices and the applicable instructions)
- _*META*_: metadata editing & curation (requires META-SHARE permissions)
- _*DISCUSS*_: Decisions about priorities, schedule and distribution of work (often requires a team meeting and/or consultation with leadership)
- _*AGREEMENTS*_: negotiations and administration regarding deposition agreements, license conditions, data protection practices etc. (requires legal knowledge, may require the opinion of a legal expert at UHEL)
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
- _*CSC*_: the task requires administrator privileges of other specific services (at this point, an issue needs to be created and handed over to the CSC team)
- _*TEST*_: testing
- Other platforms can be added in a similar way if required.
	

## The task lists for the Stories in Epic

The following lists should contain the tasks required for publishing a tool. The tasks are in the rough order in which they should typically be completed.

*Recap: For each of the section titles below, create a Story and assign it as "In Epic", providing the name/number of the Epic of the resource in question. Copy & paste the appropriate task lists from below to the description field of the corresponding Jira stories.*


### _shortname_: Enter the new tool to the pipeline

NB: THIS IS A COPY OF THE CORPORA PIPELINE, SHOULD BE EDITED FOR TOOLS!

```
# [ ] _*+MANAGE*_ Make an initial decision on whether the upcoming resource could potentially be distributed
# [ ] _*+MANAGE*_ Create a Jira Epic issue called "shortname: Publish XXX in Kielipankki (Korp/Download/…)" and insert relevant parts of this task list (sections under linked Jira Stories)
# [ ] _*?SUPPORT*_ Contact the potential depositor (by email; arrange a meeting if required) 
# [ ] _*?SUPPORT*_ Ask the depositor to submit the basic details of the new corpus or resource (e-form: http://urn.fi/urn:nbn:fi:lb-2021121421)
# [ ] _*+META*_ Create and publish a preliminary META-SHARE record (skeletal information only) [instructions for creating metadata records | https://www.kielipankki.fi/development/creating-metadata-records/]
# [ ] _*+SUPPORT*_ Ask the rightholder to review the details in the META-SHARE record (finalize shortname and title)
# [ ] _*+GITHUB*_ Request a URN for the META-SHARE record
# [ ] _*+META*_ Update the META-SHARE record with the URN and inform the depositor about citation practices, if relevant
# [ ] _*+DB*_ Add the corpus to the resource database and make sure the resource is displayed on the list of upcoming corpora
# [ ] _*?SUPPORT*_ Provide the depositor with references/advice regarding the technical format and structure of the original data
# [ ] _*?SUPPORT*_ Ask the depositor/rightholder about their schedule for submitting the data
# [ ] _*?DISCUSS*_ If the size and technical specifications of the corpus seem "non-standard" in some respect, discuss the corpus details in an internal meeting to see if it is technically feasible to publish it in the Language Bank
# [ ] _*+DISCUSS*_ Allocate the resources for the technical processing of the corpus in Kielipankki (who shall take care of it?)
\\
```

### _shortname_: Clear the license for the tool

NB: THIS IS A COPY OF THE CORPORA PIPELINE, SHOULD BE EDITED FOR TOOLS!

```
# [ ] _*+DB*_ In the resource database, create a new (preliminary) license for the resource, or link an existing license instance to the resource, if available
# [ ] _*?AGREEMENT*_ Clear the license terms and conditions regarding copyrighted material
## [ ] _*?AGREEMENT*_ In case the corpus contains third-party copyrighted material, find out if the depositor has the rights to distribute it via the Language Bank (e.g., explicit license or permission from copyright holders)
## [ ] _*?LEGAL*_ When in doubt, bring the case up in a legal meeting
# [ ] _*?AGREEMENT*_ Clear the data protection terms and conditions (PRIV)
## [ ] _*?AGREEMENT*_ Find out who the data controller is
## [ ] _*?SUPPORT*_ Find out how the depositor informed the data subjects about the purpose of processing and to what the participants gave their permission/consent (is Kielipankki or similar mentioned?)
## [ ] _*?AGREEMENT*_ Ask the depositor to show their data protection information sheet (or the documents that passed ethical review, if applicable)
## [ ] _*?AGREEMENT*_ Obtain (or create) a description of the personal data categories that are included in the corpus
## [ ] _*?AGREEMENT*_ Find out if some further risk assessment (or a DPIA) was/is required and discuss further actions with the depositor if necessary
## [ ] _*?SUPPORT*_ Provide the depositor with further references regarding personal data minimization and safeguards that may be applied prior to submitting the corpus for distribution
# [ ] _*+AGREEMENT*_ Prepare a preliminary version of the deposition license agreement for discussion
## [ ] _*?AGREEMENT*_ Make arrangements to meet the depositor about the details of the deposition agreement
## [ ] _*?SUPPORT*_ Meet with the depositor/rightholder and take note of the action points
## [ ] _*+LEGAL*_ Make the final decision as to whether the resource can be distributed via the Language Bank of Finland (bring the case up in legal meeting, if necessary)
## [ ] _*+AGREEMENT*_ Prepare the final draft of the deposition license agreement and send it to corpus owner who should fill in the remaining gaps (ask for legal advice if needed)
## [ ] _*+AGREEMENT*_ Check the final deposition agreement, combine all parts into a single pdf file and upload the document to the UniSign system for electronic signing by the rightholder (+ the data controller) and finally by the head of department at the University of Helsinki, https://unisign.helsinki.fi/sign/#/dashboard
## [ ] _*+IDA*_ Upload the signed deposition agreement (or similar proof of the distribution license) as a pdf file (named as shortname_yyyymmdd.pdf, according to the date of the last signature in the document) in IDA, under Administration/agreements/shortname.
## [ ] _*+HYSTORE*_ Upload the signed deposition agreement (or similar proof of the cleared distribution license) as a pdf file (named as shortname_yyyymmdd.pdf, according to the date of the last signature in the document) to the HFST server, under data/corpora/agreements/shortname.
\\
```

### _shortname_: Publish the end-user license

NB: THIS IS A COPY OF THE CORPORA PIPELINE, SHOULD BE EDITED FOR TOOLS!

```
# [ ] _*+PORTAL*_ Create the license pages if required ([how to create license pages)|https://www.kielipankki.fi/intra/creating-license-pages/]
# [ ] _*?PORTAL*_ For a PRIV license, create and translate the pages for data protection terms and conditions and inform the depositor
# [ ] _*?A*_ If required, request URNs for license pages (and the PRIV condition pages)
# [ ] _*+PORTAL*_ Update the license PIDs in the resource database
# [ ] _*+META*_ Create/update the META-SHARE record, including the license information [instructions for creating metadata records | https://www.kielipankki.fi/development/creating-metadata-records/]
# [ ] _*?DISCUSS*_ If the license requires further processing steps and resources from Kielipankki, bring them up for discussion in an internal meeting
\\
```

### _shortname_: Acquire and test the original software

NB: THIS IS A COPY OF THE CORPORA PIPELINE, SHOULD BE EDITED FOR TOOLS!

```
# [ ] _*+DATA*_ Receive, download or harvest the data
# [ ] _*+DATA*_ Check the data: format and validity
## [ ] _*?DATA*_ Clean up the data
# [ ] _*+DATA*_ Create a simple shortname-orig_yyyymmdd_README.txt for the original data. Include: 1) resource title; 2) PID(s) for the metadata record(s) of the first version(s); 3) link(s) to Jira issue(s).
# [ ] _*+IDA*_ Upload the original data as a zip file (named as shortname-orig_yyyymmdd.zip) and the separate shortname-orig_yyyymmdd_README.txt file to IDA, under the folder with the resource group shortname, in lowercase characters.
# [ ] _*+IDA*_ Freeze the new files in the original data folder in IDA
# [ ] _*+HYSTORE*_ Upload the original data as a zip file (named as shortname-orig_yyyymmdd.zip) and the separate shortname-orig_yyyymmdd_README.txt file to the HFST server, under data/corpora/originals/.
\\
```

### _shortname_: Publish the source code and/or installer in Download

```
# [ ] _*?IDA*_ Get the original data from IDA
# [ ] _*+META*_ Update the META-SHARE record (or create a new record, if missing) [instructions for creating metadata records | https://www.kielipankki.fi/development/creating-metadata-records/]
# [ ] _*+GITHUB*_ Request access location URN for download version (and check that the URNs for META-SHARE and license pages are available and working)
# [ ] _*+DB*_ Make sure that the corpus is on the list of upcoming resources and citable, and update the resource database if required
# [ ] _*+META*_ Add citation information to the META-SHARE record
# [ ] _*?HYSTORE*_ In case intermediate versions need to be maintained, upload the data as a zip file (named as shortname-src_yyyymmdd.zip) and the separate shortname-src_yyyymmdd_README.txt file to the HFST server, under data/corpora/wip/ (= “work in progress”).
# [ ] _*+PUHTI*_ Create a download package
# [ ] _*+DATA*_ Create a publishable README.txt for the source data, to be shown to the end-users. Include: 1) resource title; 2) PID; 3) either the license PID, a plain link to the license, or a statement of the rightholder and the known restrictions of use for the source data, 4) any other relevant information regarding the technical structure of the source data, if applicable.
## [ ] _*+PUHTI*_ Create and add the readme and license files [how to create/update license pages | https://www.kielipankki.fi/intra/creating-license-pages/]
## [ ] _*+PUHTI*_ Zip the data and the readme and license files into a package named as shortname-src.zip.
## [ ] _*+PUHTI*_ Compute an MD5 checksum for the zip package
# [ ] _*+PUHTI*_ Add the download package, MD5 checksum file and readme and license files to the directory {{/scratch/clarin/download_preview}} on Puhti
# [ ] _*+TEST*_ Have the package tested
# [ ] _*?LBR*_ Create an LBR record (for a RES corpus)
# [ ] _*+CSC*_ Upload the package to the download service (or ask someone with the rights to do that)
# [ ] _*+TEST*_ Have it tested again (access rights!)
# [ ] _*+DB*_ In the resource database, change the resource status from upcoming to published
# [ ] _*+META*_ Update the META-SHARE record: (update and) add the location PID and add the Availability start date (under Distribution)
# [ ] _*?PORTAL*_ If applicable, add the new resource version to the license page of the previous versions [how to create/update license pages | https://www.kielipankki.fi/intra/creating-license-pages/]
# [ ] _*?META*_ Update the META-SHARE record: add relations to previous or parallel versions/variants of the corpus
# [ ] _*+PORTAL*_ Create or update the resource group page, and make sure the META-SHARE record also contains a link to the resource group page
# [ ] _*?META*_ If required, create a portal page "shortname: Notes for the user", to inform about found issues in the data. Make sure the META-SHARE record also contains a link to the notes' page (in case the information is only one sentence, add it directly to the META-SHARE description).
# [ ] _*+PORTAL*_ Publish news about the new corpus on the Portal
# [ ] _*?SUPPORT*_ Inform the depositor/rightholder about the publication
# [ ] _*?CSC*_ Ask Martin (CSC) to add the data to Kielipankki directory {{/appl/data/kielipankki}} on Puhti if the source data is to be published there

\\
```

### _shortname_: Install the tool in the computing environment

```
# [ ] _*?DATA*_ Get the source (or original) data from IDA, from the download service, or from the HFST server.
# [ ] _*+META*_ Create a META-SHARE record [instructions for creating metadata records | https://www.kielipankki.fi/development/creating-metadata-records/]
# [ ] _*+GITHUB*_ Request URNs (for META-SHARE, Korp, license pages)
# [ ] _*+DB*_ Add the corpus to the resource database and make sure it is on the list of upcoming resources and citable
# [ ] _*+PORTAL*_ Create/update license pages [how to create/update license pages | https://www.kielipankki.fi/intra/creating-license-pages/]
# [ ] _*+META*_ Add citation information to the META-SHARE record
# [ ] _*?HYSTORE*_ In case intermediate versions need to be maintained at any point, upload the data as a zip file (named as shortname-korp_yyyymmdd.zip) and the separate shortname-korp_yyyymmdd_README.txt file to the HFST server, under data/corpora/wip/ (= “work in progress”).
# [ ] _*?DATA*_ Convert the data to HRT
# [ ] _*?DATA*_ Convert HRT to VRT (tokenizing)
# [ ] _*?DATA*_ Convert the data directly to VRT (alternative to HRT->VRT)
# [ ] _*?DATA*_ Parse the data (for corpora in languages with a parser)
# [ ] _*?DATA*_ Re-order or group the data (e.g. chapters, articles)
# [ ] _*?DATA*_ Add additional annotations
## [ ] _*?DATA*_ Add name annotations
## [ ] _*?DATA*_ Add sentiment annotations
## [ ] _*?DATA*_ Add identified languages
# [ ] _*+DATA*_ Validate the VRT data
# [ ] _*+DATA*_ Check the positional attributes
## [ ] _*?DATA*_ Re-order to the commonly used order if necessary
# [ ] _*?HYSTORE*_ In case the data is only published as a scrambled version, upload the unscrambled base data as a zip file (named as shortname-korp-base_yyyymmdd.zip) and the separate shortname-korp-base_yyyymmdd_README.txt file to the HFST server, under data/corpora/korp-base/.
# [ ] _*+DATA*_ Create a Korp corpus package ({{{}korp-make{}}})
## [ ] _*+KORP*_ Install the corpus package on the Korp server (or ask someone with the rights to do that)
# [ ] _*+GITHUB*_ Add corpus configuration to Korp (currently, a new branch in [Kielipankki-korp-frontend|https://https//github.com/CSCfi/Kielipankki-korp-frontend])
## [ ] _*+DATA*_ Add the configuration proper to a Korp mode file
## [ ] _*+DATA*_ Add translations of new attribute names (and values)
## [ ] _*+GITHUB*_ Push the branch to GitHub
## [ ] _*+KORP*_ Create a Korp test instance and install the new configuration branch to it (or ask someone with the rights to do that)
# [ ] _*?KORP*_ For a non-PUB corpus, add temporary access rights for the people who should test it (with the {{authing/auth}} script on the Korp server)
# [ ] _*+TEST*_ Test the corpus in Korp (Korp test version) and ask someone else to test it, too
## [ ] _*?SUPPORT*_ Ask feedback from the corpus owner (depending on how involved they wish to be)
# [ ] _*?DATA*_ Fix corpus data and re-publish (if needed)
# [ ] _*?GITHUB*_ Fix Korp configuration and re-publish (if needed)
# [ ] _*+KORP*_ Publish the corpus in Korp as a beta test version
## [ ] _*+GITHUB*_ Merge the corpus configuration branch to branch {{master}}
## [ ] _*+GITHUB*_ Add news about this new corpus to the Korp newsdesk ([https://github.com/CSCfi/Kielipankki-korp-frontend/tree/news/master])
## [ ] _*+KORP*_ Install the updated {{master}} branch to production Korp (or ask someone with the rights to do that)
# [ ] _*?LBR*_ Create an LBR record (for a RES corpus, if the corpus does not yet have one)
# [ ] _*+DB*_ In the resource database, change the resource status from upcoming to published (add status "beta" to the name!)
# [ ] _*+META*_ Update META-SHARE record; add location PID and Availability start date (under Distribution)
# [ ] _*?META*_ Update the META-SHARE record: add relations to previous or parallel versions/variants of the corpus
# [ ] _*+META*_ Add "beta" status information to META-SHARE record
# [ ] _*+PORTAL*_ Add "beta" status information to the resource group page
# [ ] _*?META*_ If required, create a portal page "shortname: Notes for the user", to inform about found issues in the data. Make sure the META-SHARE record also contains a link to the notes' page (in case the information is only one sentence, add it directly to the META-SHARE description).
# [ ] _*+PORTAL*_ Publish news about this new corpus in the portal
# [ ] _*?SUPPORT*_ Inform corpus owner and possibly interested researchers on the corpus in Korp and ask them to test it
# [ ] _*?DATA*_ Fix corpus data based on feedback and re-publish (if needed)
# [ ] _*?KORP*_ Fix corpus configuration in Korp and re-publish (if needed)
# [ ] _*+KORP*_ Remove beta status after two weeks, if no requests for corrections or changes appear during this period
## [ ] _*+KORP*_ Remove beta status from Korp configuration ({{{}master{}}}), push and install the updated {{master}}
## [ ] _*+META*_ Remove beta status from the META-SHARE record and resource group page
\\
```

### _shortname_: Make the tool available via an online interface

```
# [ ] _*+IDA*_ Get the data from IDA (unless the latest content is available as a Korp version)
# [ ] _*+KORP*_ Extract the data from Korp (unless more recent content can be acquired in VRT format from outside Korp)
# [ ] _*+META*_ Create a META-SHARE record [instructions for creating metadata records | https://www.kielipankki.fi/development/creating-metadata-records/]
# [ ] _*+GITHUB*_ Request URNs (for META-SHARE, download, license pages)
# [ ] _*+DB*_ Add the details of the corpus variant to the resource database, status "upcoming"
# [ ] _*+PORTAL*_ Create/update license pages [how to create/update license pages | https://www.kielipankki.fi/intra/creating-license-pages/]
# [ ] _*+META*_ Add citation information to the META-SHARE record
# [ ] _*?HYSTORE*_ In case intermediate versions need to be maintained at any point, upload the data as a zip file (named as shortname-vrt_yyyymmdd.zip) and the separate shortname-vrt_yyyymmdd_README.txt file to the HFST server, under data/corpora/wip/ (= “work in progress”).
# [ ] _*+PUHTI*_ Create a download package
## [ ] _*+PUHTI*_ Create and add the downloadable readme and license files [how to create/update license pages | https://www.kielipankki.fi/intra/creating-license-pages/]
## [ ] _*+PUHTI*_ Zip the data and the readme and license files
## [ ] _*+PUHTI*_ Compute MD5 checksum for the zip package
# [ ] _*+PUHTI*_ Add the download package, MD5 checksum file and readme and license files to the directory {{/scratch/clarin/download_preview}} on Puhti
# [ ] _*+TEST*_ Have the package tested
# [ ] _*+CSC*_ Upload the package to the download service (or ask someone with the rights to do that)
# [ ] _*?LBR*_ Create an LBR record (for a RES corpus, if the corpus does not yet have one)
# [ ] _*+TEST*_ Have it tested again (access rights!)
# [ ] _*+DB*_ In the resource database, change the resource status from upcoming to published
# [ ] _*+META*_ Update the META-SHARE record; add location PID and Availability start date (under Distribution)
# [ ] _*?META*_ Update the META-SHARE record: add relations to previous or parallel versions/variants of the corpus
# [ ] _*+PORTAL*_ Create or update the resource group page
# [ ] _*?META*_ If required, create a portal page "shortname: Notes for the user", to inform about found issues in the data. Make sure the META-SHARE record also contains a link to the notes' page (in case the information is only one sentence, add it directly to the META-SHARE description).
# [ ] _*+PORTAL*_ Publish news about the new corpus on the Portal
# [ ] _*?SUPPORT*_ Inform the depositor/rightholder about the VRT publication
# [ ] _*?PUHTI*_ If the package was published as beta (during the beta stage of the corresponding Korp corpus), remove the beta status after removing the beta status from Korp
## [ ] _*?PUHTI*_ Create a new download package with the beta status removed from the readme file and file names
## [ ] _*?PUHTI*_ Compute MD5 checksum for the zip package
## [ ] _*?CSC*_ Upload the package to the download service (or ask someone with the rights to do that)
## [ ] _*?META*_ Remove beta status from the META-SHARE record and resource group page
# [ ] _*?CSC*_ Ask Martin to add the data to Kielipankki directory {{/appl/data/kielipankki}} on Puhti (if the corpus is PUB or ACA)
\\
```