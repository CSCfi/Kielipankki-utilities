
# Checklists for tasks in the corpus publishing pipeline

The following lists contain tasks required for publishing a corpus. The
lists are in a rough order in which tasks should be (or typically are)
done.

The appropriate task list can be copied verbatim to the description of
a Jira ticket for publishing (a version of) a corpus, where it will be
rendered as an enumerated list. (The list should be copied when the
description input field is in “Text” mode, not “Visual”.) In the
description field, the list should be adjusted as appropriate for the
corpus in question: for example, LBR records are needed only for RES
corpora.

Each task description is preceded by “[ ]” representing a checkbox and
a task type marker. When you take a task under work, write your name
between the square brackets (“[Name]”). When a task is completed,
replace it with an “[X]”.

The task type marker is an italicized (slanted) two-character string.
The first character is _+_ for obligatory tasks and _?_ for optional
ones, and the second character indicates the rough type of the task by
one of the following letters:

- _A_: administrative
- _D_: data processing
- _K_: Korp configuration
- _T_: testing

It is suggested that you use the section titles as names of the corresponding Jira issues.
Please replace "corpusshortname" with the (base) short name of the resource in question.
This makes it easier to see which resource is addressed in individual Jira tickets.

## corpusshortname: Clear the license for the corpus in the Language Bank of Finland

```
# [ ] _?A_ Contact the potential depositor and ask them to submit basic corpus details (preferably via e-form)
# [ ] _+A_ Create and publish an initial META-SHARE record (skeletal information only, no promises regarding publication yet)
# [ ] _+A_ Ask the rightholder to review the details in the META-SHARE record (shortname and title should be finalized)
# [ ] _+A_ Make an initial decision as to whether the resource can potentially be distributed via the Language Bank of Finland
# [ ] _+A_ Request a URN for the META-SHARE record
# [ ] _+A_ Update the META-SHARE record and inform the depositor about citation practices
# [ ] _+A_ Add the corpus to the list of upcoming resources
# [ ] _+A_ Add the corpus to the list of licenses
# [ ] _?A_ If the size and technical specifications of the corpus seem "non-standard" in some respect, discuss the corpus details in an internal meeting to see if it is technically feasible to publish it in the Language Bank
# [ ] _?A_ Provide the depositor with references/advice regarding the technical format and structure of the source data
# [ ] _?A_ Clear the license terms and conditions regarding copyrighted material 
## [ ] _?A_ In case the corpus contains third-party copyrighted material, find out if the depositor has the rights to distribute it via the Language Bank (e.g., explicit license or permission from copyright holders)
##  [ ] _?A_ When in doubt, bring the case up in a legal meeting
# [ ] _?A_ Clear the data protection terms and conditions (PRIV)
## [ ] _?A_ Find out who the data controller is, how the depositor has informed the data subjects about purpose and further processing, and ask the depositor to show their data protection information sheet (or the documents that passed ethical review, if applicable)
## [ ] _?A_ Obtain (or create) a description of the personal data categories that are included in the corpus
## [ ] _?A_ Find out if further risk assessment (or a DPIA) is required (and take action if necessary)
## [ ] _?A_ Provide the depositor with further references regarding personal data minimization and safeguards that may be applied prior to submitting the corpus for distribution
# [ ] _+A_ Prepare and sign the deposition license agreement
## [ ] _?A_ Prepare for a meeting with the depositor (agenda: to discuss the requirements regarding the deposition agreement)
## [ ] _?A_ Meet with the depositor/rightholder and take note of the action points
## [ ] _+A_ Make the final decision as to whether the resource can be distributed via the Language Bank of Finland (bring the case up in legal meeting, if necessary)
## [ ] _+A_ Prepare a draft of the deposition license agreement and send it to corpus owner who should fill in the remaining gaps (ask for legal advice if needed)
## [ ] _+A_ Check the final deposition agreement and send it to the rightholder (and to the data controller) and to the head of department at the University of Helsinki for electronic signing
## [ ] _+A_ Archive the signed deposition agreement (pdf) in IDA
# [ ] _+A_ Publish the end-user license
## [ ] _+A_ Create license pages
## [ ] _?A_ For a PRIV license, create and translate the pages for data protection terms and conditions and inform the depositor
## [ ] _+A_ Request URNs for license pages (and the PRIV condition pages)
## [ ] _+A_ Update the list of licenses
```

## corpusshortname: Prepare for data acquisition, after the license is cleared
```
# [ ] _+A_ Create/update the META-SHARE record, including the license information
# [ ] _?A_ Request a URN for the META-SHARE record, if missing
# [ ] _+A_ Update the list of upcoming resources
# [ ] _+A_ Allocate internal resources for processing and publishing the corpus in Kielipankki
##  [ ] _?A_ Ask the depositor/rightholder about their schedule for submitting the data
## [ ] _+A_ Bring the further processing steps and required resources up for discussion in an internal meeting
## [ ] _+A_ Prioritize and assign further work
```

## corpusshortname: Acquire source data

```
# [ ] _+D_ Receive, download or harvest the data
# [ ] _+D_ Check the data: format and validity
## [ ] _?D_ Clean up the data
# [ ] _+D_ Package the data for IDA
# [ ] _+D_ Upload the data package to IDA
```

## corpusshortname: Publish source data in Download 

```
# [ ] _?D_ Get the data from IDA
# [ ] _+A_ Update the META-SHARE record (or create a new record, if missing)
# [ ] _+A_ Request access location URN for download version (and check that the URNs for META-SHARE and license pages are available and working) 
# [ ] _+A_ Check that the corpus is on the list of upcoming resources
# [ ] _+A_ Add citation information to the META-SHARE record
# [ ] _+D_ Create a download package
## [ ] _+D_ Create and add readme and license files
## [ ] _+D_ Zip the data and the readme and license files
## [ ] _+D_ Compute an MD5 checksum for the zip package
# [ ] _+D_ Add the download package, MD5 checksum file and readme and license files to the directory {{/scratch/clarin/download_preview}} on Puhti
# [ ] _+T_ Have the package tested
# [ ] _?A_ Create an LBR record (for a RES corpus)
# [ ] _+D_ Upload the package to the download service (or ask someone with the rights to do that)
# [ ] _+T_ Have it tested again (access rights!)
# [ ] _+A_ Move the resource from the list of upcoming resources to the list of published resources
# [ ] _+A_ Update the META-SHARE record; add location PID
# [ ] _?A_ Update the META-SHARE record: add relations to previous or parallel versions/variants of the corpus
# [ ] _+A_ Create or update the resource group page, and make sure the META-SHARE record also contains a link to the resource group page
# [ ] _+A_ Publish news about the new corpus on the Portal
# [ ] _?A_ Inform the depositor/rightholder about the publication
# [ ] _+D_ Upload the source package to IDA
## [ ] _+A_ Freeze the IDA package
# [ ] _?D_ Ask Martin (CSC) to add the data to Kielipankki directory {{/appl/data/kielipankki}} on Puhti if the source data is to be published there
```

## corpusshortname: Publish in Korp

```
# [ ] _?D_ Get the data from IDA
# [ ] _+A_ Create a META-SHARE record
# [ ] _+A_ Request URNs (for META-SHARE, Korp, license pages)
# [ ] _+A_ Add corpus to the list of upcoming resources
# [ ] _+A_ Create license pages
# [ ] _+A_ Add citation information to the META-SHARE record
# [ ] _?D_ Convert the data to HRT
# [ ] _?D_ Convert HRT to VRT (tokenizing)
# [ ] _?D_ Convert the data directly to VRT (alternative to HRT->VRT)
# [ ] _?D_ Parse the data (for corpora in languages with a parser)
# [ ] _?D_ Re-order or group the data (e.g. chapters, articles)
# [ ] _?D_ Add additional annotations
## [ ] _?D_ Add name annotations
## [ ] _?D_ Add sentiment annotations
## [ ] _?D_ Add identified languages
# [ ] _+D_ Validate the VRT data
# [ ] _+D_ Check the positional attributes
## [ ] _?D_ Re-order to the commonly used order if necessary
# [ ] _+D_ Create a Korp corpus package ({{korp-make}})
## [ ] _+D_ Install the corpus package on the Korp server (or ask someone with the rights to do that)
# [ ] _+K_ Add corpus configuration to Korp (currently, a new branch in [Kielipankki-korp-frontend|https://https://github.com/CSCfi/Kielipankki-korp-frontend])
## [ ] _+K_ Add the configuration proper to a Korp mode file
## [ ] _+K_ Add translations of new attribute names (and values)
## [ ] _+K_ Push the branch to GitHub
## [ ] _+K_ Create a Korp test instance and install the new configuration branch to it (or ask someone with the rights to do that)
# [ ] _?D_ For a non-PUB corpus, add temporary access rights for the people who should test it (with the {{authing/auth}} script on the Korp server)
# [ ] _+T_ Test the corpus in Korp (Korp test version) and ask someone else to test it, too
## [ ] _?A_ Ask feedback from the corpus owner (depending on how involved they wish to be)
# [ ] _?D_ Fix corpus data and re-publish (if needed)
# [ ] _?K_ Fix Korp configuration and re-publish (if needed)
# [ ] _+D_ Upload the Korp corpus package to IDA
# [ ] _+K_ Publish the corpus in Korp as a beta test version
## [ ] _+K_ Merge the corpus configuration branch to branch {{master}}
## [ ] _+K_ Add news about this new corpus to the Korp newsdesk (https://github.com/CSCfi/Kielipankki-korp-frontend/tree/news/master)
## [ ] _+K_ Install the updated {{master}} branch to production Korp (or ask someone with the rights to do that)
# [ ] _?A_ Create an LBR record (for a RES corpus, if the corpus does not yet have one)
# [ ] _+A_ Move the corpus from the list of upcoming resources to the list of published resources (add status beta to the name!)
# [ ] _+A_ Update META-SHARE record; add location PID
# [ ] _?A_ Update the META-SHARE record: add relations to previous or parallel versions/variants of the corpus
# [ ] _+A_ Add beta status to META-SHARE record and resource group page
# [ ] _+A_ Publish news about this new corpus in the portal
# [ ] _?A_ Inform corpus owner and possibly interested researchers on the corpus in Korp and ask them to test it
# [ ] _?D_ Fix corpus data based on feedback and re-publish (if needed)
## [ ] _?D_ Upload a fixed Korp corpus package to IDA
# [ ] _?K_ Fix corpus configuration in Korp and re-publish (if needed)
# [ ] _+A_ Remove beta status after two weeks, if no requests for corrections or changes appear during this period
## [ ] _+K_ Remove beta status from Korp configuration ({{master}}), push and install the updated {{master}}
## [ ] _+A_ Remove beta status from the META-SHARE record and resource group page
# [ ] _+A_ Freeze the IDA package
```

## corpusshortname: Publish VRT data in Download

```
# [ ] _+D_ Get the data from IDA or extract it from Korp
# [ ] _+A_ Create a META-SHARE record
# [ ] _+A_ Request URNs (for META-SHARE, download, license pages)
# [ ] _+A_ Add the corpus to list of upcoming resources
# [ ] _+A_ Create license pages
# [ ] _+A_ Add citation information to the META-SHARE record
# [ ] _+D_ Create a download package
## [ ] _+D_ Create and add readme and license files
## [ ] _+D_ Zip the data and the readme and license files
## [ ] _+D_ Compute MD5 checksum for the zip package
# [ ] _+D_ Add the download package, MD5 checksum file and readme and license files to the directory {{/scratch/clarin/download_preview}} on Puhti
# [ ] _+T_ Have the package tested
# [ ] _+D_ Upload the package to the download service (or ask someone with the rights to do that)
# [ ] _?A_ Create an LBR record (for a RES corpus, if the corpus does not yet have one)
# [ ] _+T_ Have it tested again (access rights!)
# [ ] _+A_ Move the corpus from the list of upcoming resources to the list of published resources
# [ ] _+A_ Update the META-SHARE record; add location PID
# [ ] _?A_ Update the META-SHARE record: add relations to previous or parallel versions/variants of the corpus
# [ ] _+A_ Create or update the resource group page
# [ ] _+A_ Publish news about the new corpus on the Portal
# [ ] _?A_ Inform the depositor/rightholder about the VRT publication
# [ ] _?A_ If the package was published as beta (during the beta stage of the corresponding Korp corpus), remove the beta status after removing the beta status from Korp
## [ ] _?D_ Create a new download package with the beta status removed from the readme file and file names
## [ ] _?D_ Compute MD5 checksum for the zip package
## [ ] _?D_ Upload the package to the download service (or ask someone with the rights to do that)
## [ ] _?A_ Remove beta status from the META-SHARE record and resource group page
# [ ] _+D_ Upload the VRT package to IDA
## [ ] _+A_ Freeze the IDA package
# [ ] _?D_ Ask Martin to add the data to Kielipankki directory {{/appl/data/kielipankki}} on Puhti (if the corpus is PUB or ACA)
```
