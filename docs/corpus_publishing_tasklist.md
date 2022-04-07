
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

The task type marker is an italicized (slanted) and bolded two-character string.
The first character is _+_ for obligatory tasks and _?_ for optional
ones, and the second character indicates the rough type of the task by
one of the following letters:

- _*A*_: administrative
- _*D*_: data processing
- _*K*_: Korp configuration
- _*T*_: testing

It is suggested that you use the section titles as names of the corresponding Jira issues.
If several issues are needed for a given corpus, please replace "_corpusshortname_" 
with the short name of the resource in question (use base name only, excluding "-src" etc.).
This makes it easier to see which resource is addressed in individual Jira tickets.

*Please copy & paste the appropriate portions of the raw text below to the description field 
of the Jira issue in question!*

```
h2. [ ] {_}corpusshortname{_}: Clear the license for the corpus in the Language Bank of Finland
# [ ] _*?A*_ Contact the potential depositor and ask them to submit basic corpus details (preferably via e-form)
# [ ] _*+A*_ Create and publish an initial META-SHARE record (skeletal information only, no promises regarding publication yet)
# [ ] _*+A*_ Ask the rightholder to review the details in the META-SHARE record (shortname and title should be finalized)
# [ ] _*+A*_ Make an initial decision as to whether the resource can potentially be distributed via the Language Bank of Finland
# [ ] _*+A*_ Request a URN for the META-SHARE record
# [ ] _*+A*_ Update the META-SHARE record and inform the depositor about citation practices
# [ ] _*+A*_ Add the corpus to the list of upcoming resources
# [ ] _*+A*_ Add the corpus to the list of licenses
# [ ] _*?A*_ If the size and technical specifications of the corpus seem "non-standard" in some respect, discuss the corpus details in an internal meeting to see if it is technically feasible to publish it in the Language Bank
# [ ] _*?A*_ Provide the depositor with references/advice regarding the technical format and structure of the source data
# [ ] _*?A*_ Clear the license terms and conditions regarding copyrighted material
## [ ] _*?A*_ In case the corpus contains third-party copyrighted material, find out if the depositor has the rights to distribute it via the Language Bank (e.g., explicit license or permission from copyright holders)
## [ ] _*?A*_ When in doubt, bring the case up in a legal meeting
# [ ] _*?A*_ Clear the data protection terms and conditions (PRIV)
## [ ] _*?A*_ Find out who the data controller is, how the depositor has informed the data subjects about purpose and further processing, and ask the depositor to show their data protection information sheet (or the documents that passed ethical review, if applicable)
## [ ] _*?A*_ Obtain (or create) a description of the personal data categories that are included in the corpus
## [ ] _*?A*_ Find out if further risk assessment (or a DPIA) is required (and take action if necessary)
## [ ] _*?A*_ Provide the depositor with further references regarding personal data minimization and safeguards that may be applied prior to submitting the corpus for distribution
# [ ] _*+A*_ Prepare and sign the deposition license agreement
## [ ] _*?A*_ Prepare for a meeting with the depositor (agenda: to discuss the requirements regarding the deposition agreement)
## [ ] _*?A*_ Meet with the depositor/rightholder and take note of the action points
## [ ] _*+A*_ Make the final decision as to whether the resource can be distributed via the Language Bank of Finland (bring the case up in legal meeting, if necessary)
## [ ] _*+A*_ Prepare a draft of the deposition license agreement and send it to corpus owner who should fill in the remaining gaps (ask for legal advice if needed)
## [ ] _*+A*_ Check the final deposition agreement and send it to the rightholder (and to the data controller) and to the head of department at the University of Helsinki for electronic signing
## [ ] _*+A*_ Archive the signed deposition agreement (pdf) in IDA
# [ ] _*+A*_ Publish the end-user license
## [ ] _*+A*_ Create license pages
## [ ] _*?A*_ For a PRIV license, create and translate the pages for data protection terms and conditions and inform the depositor
## [ ] _*+A*_ Request URNs for license pages (and the PRIV condition pages)
## [ ] _*+A*_ Update the list of licenses
\\
h2. [ ] {_}corpusshortname{_}: Prepare for data acquisition
# [ ] _*+A*_ Create/update the META-SHARE record, including the license information
# [ ] _*?A*_ Request a URN for the META-SHARE record, if missing
# [ ] _*+A*_ Update the list of upcoming resources
# [ ] _*+A*_ Allocate internal resources for processing and publishing the corpus in Kielipankki
## [ ] _*?A*_ Ask the depositor/rightholder about their schedule for submitting the data
## [ ] _*+A*_ Bring the further processing steps and required resources up for discussion in an internal meeting
## [ ] _*+A*_ Prioritize and assign further work
\\
h2. [ ] {_}corpusshortname{_}: Acquire source data
# [ ] _*+D*_ Receive, download or harvest the data
# [ ] _*+D*_ Check the data: format and validity
## [ ] _*?D*_ Clean up the data
# [ ] _*+D*_ Package the data for IDA
# [ ] _*+D*_ Upload the data package to IDA
\\
h2. [ ] {_}corpusshortname{_}: Publish source data in Download
# [ ] _*?D*_ Get the data from IDA
# [ ] _*+A*_ Update the META-SHARE record (or create a new record, if missing)
# [ ] _*+A*_ Request access location URN for download version (and check that the URNs for META-SHARE and license pages are available and working)
# [ ] _*+A*_ Check that the corpus is on the list of upcoming resources
# [ ] _*+A*_ Add citation information to the META-SHARE record
# [ ] _*+D*_ Create a download package
## [ ] _*+D*_ Create and add readme and license files
## [ ] _*+D*_ Zip the data and the readme and license files
## [ ] _*+D*_ Compute an MD5 checksum for the zip package
# [ ] _*+D*_ Add the download package, MD5 checksum file and readme and license files to the directory {{/scratch/clarin/download_preview}} on Puhti
# [ ] _*+T*_ Have the package tested
# [ ] _*?A*_ Create an LBR record (for a RES corpus)
# [ ] _*+D*_ Upload the package to the download service (or ask someone with the rights to do that)
# [ ] _*+T*_ Have it tested again (access rights!)
# [ ] _*+A*_ Move the resource from the list of upcoming resources to the list of published resources
# [ ] _*+A*_ Update the META-SHARE record; add location PID
# [ ] _*?A*_ Update the META-SHARE record: add relations to previous or parallel versions/variants of the corpus
# [ ] _*+A*_ Create or update the resource group page, and make sure the META-SHARE record also contains a link to the resource group page
# [ ] _*+A*_ Publish news about the new corpus on the Portal
# [ ] _*?A*_ Inform the depositor/rightholder about the publication
# [ ] _*+D*_ Upload the source package to IDA
## [ ] _*+A*_ Freeze the IDA package
# [ ] _*?D*_ Ask Martin (CSC) to add the data to Kielipankki directory {{/appl/data/kielipankki}} on Puhti if the source data is to be published there
\\
h2. [ ] {_}corpusshortname{_}: Publish in Korp
# [ ] _*?D*_ Get the data from IDA
# [ ] _*+A*_ Create a META-SHARE record
# [ ] _*+A*_ Request URNs (for META-SHARE, Korp, license pages)
# [ ] _*+A*_ Add corpus to the list of upcoming resources
# [ ] _*+A*_ Create license pages
# [ ] _*+A*_ Add citation information to the META-SHARE record
# [ ] _*?D*_ Convert the data to HRT
# [ ] _*?D*_ Convert HRT to VRT (tokenizing)
# [ ] _*?D*_ Convert the data directly to VRT (alternative to HRT->VRT)
# [ ] _*?D*_ Parse the data (for corpora in languages with a parser)
# [ ] _*?D*_ Re-order or group the data (e.g. chapters, articles)
# [ ] _*?D*_ Add additional annotations
## [ ] _*?D*_ Add name annotations
## [ ] _*?D*_ Add sentiment annotations
## [ ] _*?D*_ Add identified languages
# [ ] _*+D*_ Validate the VRT data
# [ ] _*+D*_ Check the positional attributes
## [ ] _*?D*_ Re-order to the commonly used order if necessary
# [ ] _*+D*_ Create a Korp corpus package ({{{}korp-make{}}})
## [ ] _*+D*_ Install the corpus package on the Korp server (or ask someone with the rights to do that)
# [ ] _*+K*_ Add corpus configuration to Korp (currently, a new branch in [Kielipankki-korp-frontend|https://https//github.com/CSCfi/Kielipankki-korp-frontend])
## [ ] _*+K*_ Add the configuration proper to a Korp mode file
## [ ] _*+K*_ Add translations of new attribute names (and values)
## [ ] _*+K*_ Push the branch to GitHub
## [ ] _*+K*_ Create a Korp test instance and install the new configuration branch to it (or ask someone with the rights to do that)
# [ ] _*?D*_ For a non-PUB corpus, add temporary access rights for the people who should test it (with the {{authing/auth}} script on the Korp server)
# [ ] _*+T*_ Test the corpus in Korp (Korp test version) and ask someone else to test it, too
## [ ] _*?A*_ Ask feedback from the corpus owner (depending on how involved they wish to be)
# [ ] _*?D*_ Fix corpus data and re-publish (if needed)
# [ ] _*?K*_ Fix Korp configuration and re-publish (if needed)
# [ ] _*+D*_ Upload the Korp corpus package to IDA
# [ ] _*+K*_ Publish the corpus in Korp as a beta test version
## [ ] _*+K*_ Merge the corpus configuration branch to branch {{master}}
## [ ] _*+K*_ Add news about this new corpus to the Korp newsdesk ([https://github.com/CSCfi/Kielipankki-korp-frontend/tree/news/master])
## [ ] _*+K*_ Install the updated {{master}} branch to production Korp (or ask someone with the rights to do that)
# [ ] _*?A*_ Create an LBR record (for a RES corpus, if the corpus does not yet have one)
# [ ] _*+A*_ Move the corpus from the list of upcoming resources to the list of published resources (add status beta to the name!)
# [ ] _*+A*_ Update META-SHARE record; add location PID
# [ ] _*?A*_ Update the META-SHARE record: add relations to previous or parallel versions/variants of the corpus
# [ ] _*+A*_ Add beta status to META-SHARE record and resource group page
# [ ] _*+A*_ Publish news about this new corpus in the portal
# [ ] _*?A*_ Inform corpus owner and possibly interested researchers on the corpus in Korp and ask them to test it
# [ ] _*?D*_ Fix corpus data based on feedback and re-publish (if needed)
## [ ] _*?D*_ Upload a fixed Korp corpus package to IDA
# [ ] _*?K*_ Fix corpus configuration in Korp and re-publish (if needed)
# [ ] _*+A*_ Remove beta status after two weeks, if no requests for corrections or changes appear during this period
## [ ] _*+K*_ Remove beta status from Korp configuration ({{{}master{}}}), push and install the updated {{master}}
## [ ] _*+A*_ Remove beta status from the META-SHARE record and resource group page
# [ ] _*+A*_ Freeze the IDA package
\\
h2. [ ] {_}corpusshortname{_}: Publish VRT data in Download
# [ ] _*+D*_ Get the data from IDA or extract it from Korp
# [ ] _*+A*_ Create a META-SHARE record
# [ ] _*+A*_ Request URNs (for META-SHARE, download, license pages)
# [ ] _*+A*_ Add the corpus to list of upcoming resources
# [ ] _*+A*_ Create license pages
# [ ] _*+A*_ Add citation information to the META-SHARE record
# [ ] _*+D*_ Create a download package
## [ ] _*+D*_ Create and add readme and license files
## [ ] _*+D*_ Zip the data and the readme and license files
## [ ] _*+D*_ Compute MD5 checksum for the zip package
# [ ] _*+D*_ Add the download package, MD5 checksum file and readme and license files to the directory {{/scratch/clarin/download_preview}} on Puhti
# [ ] _*+T*_ Have the package tested
# [ ] _*+D*_ Upload the package to the download service (or ask someone with the rights to do that)
# [ ] _*?A*_ Create an LBR record (for a RES corpus, if the corpus does not yet have one)
# [ ] _*+T*_ Have it tested again (access rights!)
# [ ] _*+A*_ Move the corpus from the list of upcoming resources to the list of published resources
# [ ] _*+A*_ Update the META-SHARE record; add location PID
# [ ] _*?A*_ Update the META-SHARE record: add relations to previous or parallel versions/variants of the corpus
# [ ] _*+A*_ Create or update the resource group page
# [ ] _*+A*_ Publish news about the new corpus on the Portal
# [ ] _*?A*_ Inform the depositor/rightholder about the VRT publication
# [ ] _*?A*_ If the package was published as beta (during the beta stage of the corresponding Korp corpus), remove the beta status after removing the beta status from Korp
## [ ] _*?D*_ Create a new download package with the beta status removed from the readme file and file names
## [ ] _*?D*_ Compute MD5 checksum for the zip package
## [ ] _*?D*_ Upload the package to the download service (or ask someone with the rights to do that)
## [ ] _*?A*_ Remove beta status from the META-SHARE record and resource group page
# [ ] _*+D*_ Upload the VRT package to IDA
## [ ] _*+A*_ Freeze the IDA package
# [ ] _*?D*_ Ask Martin to add the data to Kielipankki directory {{/appl/data/kielipankki}} on Puhti (if the corpus is PUB or ACA)
\\
```
