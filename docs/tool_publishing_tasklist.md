
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
# [ ] _shortname_: Start negotiations with the depositor
# [ ] _shortname_: Enter the new tool to the pipeline
# [ ] _shortname_: Plan the publication process with the depositor
# [ ] _shortname_: Clear the license for the tool
# [ ] _shortname_: Publish the end-user license
# [ ] _shortname_: Publish a tool available outside Kielipankki
# [ ] _shortname_: Acquire and test the original software
# [ ] _shortname_: Publish the source code and/or installer in Download
# [ ] _shortname_: Install the tool in the computing environment
# [ ] _shortname_: Make the tool available via an online interface
# [ ] _shortname_: Review the tool, to continue lifecycle
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

- _*MANAGE*_: general management and coordination of the resource publication process and the related tasks (requires Jira permissions)
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

### _shortname_: Start negotiations with the depositor

```
# [ ] _*+MANAGE*_ Create a Jira Epic issue called "shortname: Publish XXX in Kielipankki"
# [ ] _*?SUPPORT*_ Contact the potential depositor (by email; arrange a meeting if required) 
# [ ] _*?SUPPORT*_ Ask the depositor to submit the basic details of the new tool (e-form: http://urn.fi/urn:nbn:fi:lb-2021121421)
# [ ] _*+MANAGE*_ Insert the first pipeline Story under the Jira Epic and assign it forward
# [ ] _*+MANAGE*_ Copy-paste the content of the e-form as a comment under the Story (tag the person to whom it is assigned)
\\
```

### _shortname_: Enter the new tool to the pipeline

```
# [ ] _*+MANAGE*_ Insert relevant parts of this task list in the resource publication Epic (sections under linked Jira 
# [ ] _*+META*_ Create and publish a preliminary META-SHARE record (skeletal information only) [instructions for creating metadata records | https://www.kielipankki.fi/development/creating-metadata-records/]
# [ ] _*+GITHUB*_ Request a URN for the META-SHARE record
# [ ] _*+GITHUB*_ If needed, request URNs for license pages
# [ ] _*+META*_ Update the META-SHARE record with the metadata URN
\\
```

### _shortname_: Plan the publication process with the depositor

```
# [ ] _*+SUPPORT*_ Ask the rightholder to review the details in the META-SHARE record (finalize shortname and title)
# [ ] _*?SUPPORT*_ Inform the depositor about citation practices, if relevant
# [ ] _*?SUPPORT*_ Provide the depositor with references/advice regarding the technical format and structure of the original tool and any additional material
# [ ] _*?SUPPORT*_ Ask the depositor/rightholder about their schedule for submitting the tool
# [ ] _*?DISCUSS*_ If the size and technical specifications of the tool and any additional material seem "non-standard" in some respect, discuss the corpus details in an internal meeting to see if it is technically feasible to publish it in the Language Bank
\\
```

### _shortname_: Clear the license for the tool

NB: Quite often, especially for tools developed outside Kielipankki, we just offer a link to the license given in the tool's documentation

```
# [ ] _*+MANAGE*_ Add the license type and any other related information to the META-SHARE record
# [ ] _*+MANAGE*_ Add the link of the license page to the META-SHARE record
\\
```

### _shortname_: Publish the end-user license

```
# [ ] _*+PORTAL*_ Create the license pages if required ([how to create license pages)|https://www.kielipankki.fi/intra/creating-license-pages/]
# [ ] _*?PORTAL*_ For a PRIV license, create and translate the pages for data protection terms and conditions and inform the depositor
# [ ] _*?A*_ If required, request URNs for license pages (and the PRIV condition pages)
# [ ] _*+PORTAL*_ Update the license PIDs in the resource database
# [ ] _*+META*_ Create/update the META-SHARE record, including the license information [instructions for creating metadata records | https://www.kielipankki.fi/development/creating-metadata-records/]
# [ ] _*+META*_ In case the license requires Attribution (the BY condition), collect the names of the creators/programmers/significant contributors/rightholders that should be cited, or, if this is impossible, find some other (persistent) reference to the original source of the tool. Add the reference instruction to the META-SHARE record.
# [ ] _*?DISCUSS*_ If the license requires further processing steps and resources from Kielipankki, bring them up for discussion in an internal meeting
\\
```

### _shortname_: Publish a tool available outside Kielipankki
```
# [ ] _*+TEST*_ Check that the access to the tool and its material is working
# [ ] _*+META*_ Create or update the META-SHARE record 
# [ ] _*+GITHUB*_ Request URN for the META-SHARE record and add it to the META-SHARE record
# [ ] _*+GITHUB*_ Request URN for the access location and add it to the META-SHARE record OR add the external access link to the META-SHARE record
# [ ] _*+META*_ Add references to documentation and any other material to the META-SHARE record
# [ ] _*+META*_ Create or update the resource group page and assign it a URN
# [ ] _*+META*_ Add references to documentation and any other material to the resource group page
# [ ] _*+META*_ Link to the tool's resource group page from the list of resource families (http://urn.fi/urn:nbn:fi:lb-2021052505)
# [ ] _*+META*_ Add the new tool to the list of tools in the portal (NOTE: there are separate lists for English, Finnish and Swedish)
\\
```

### _shortname_: Acquire and test the original software

```
# [ ] _*+DATA*_ Receive, download or harvest the tool and any additional material (documentation, user guide ect.)
# [ ] _*+TEST*_ Test the tool: availability and functionality
# [ ] _*+DATA*_ Check the additional material: format and validity
## [ ] _*?DATA*_ Clean up the data if needed
# [ ] _*+DATA*_ Create a simple shortname-orig_yyyymmdd_README.txt for the original data. Include: 1) resource title; 2) PID(s) for the metadata record(s) of the first version(s); 3) link(s) to Jira issue(s).
# [ ] _*+HYSTORE*_ Upload the original data as a zip file (named as shortname-orig_yyyymmdd.zip) and the separate shortname-orig_yyyymmdd_README.txt file to the HFST server, under data/tools/.
\\
```

### _shortname_: Publish the source code and/or installer in Download

```
# [ ] _*?DATA*_ Get the source (or original) tool from IDA, GitHub, or from the HFST server.
# [ ] _*+META*_ Create documentation/user guide for the tool
# [ ] _*+META*_ Update the META-SHARE record (or create a new record, if missing) [instructions for creating metadata records | https://www.kielipankki.fi/development/creating-metadata-records/]
# [ ] _*+GITHUB*_ Request access location URN for download version (and check that the URNs for META-SHARE and license pages are available and working)
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
# [ ] _*+META*_ Update the META-SHARE record: (update and) add the location PID and add the Availability start date (under Distribution)
# [ ] _*?PORTAL*_ If applicable, add the new resource version to the license page of the previous versions [how to create/update license pages | https://www.kielipankki.fi/intra/creating-license-pages/]
# [ ] _*?META*_ Update the META-SHARE record: add relations to previous or parallel versions/variants of the corpus
# [ ] _*+PORTAL*_ Create or update the resource group page, and make sure the META-SHARE record also contains a link to the resource group page.
# [ ] _*+PORTAL*_ Link to the group page from the list of resource families (http://urn.fi/urn:nbn:fi:lb-2021052505)
# [ ] _*?META*_ If required, create a portal page "shortname: Notes for the user", to inform about found issues in the data. Make sure the META-SHARE record also contains a link to the notes' page (in case the information is only one sentence, add it directly to the META-SHARE description).
# [ ] _*+META*_ Add the new tool to the list of tools in the portal (NOTE: there are separate lists for English, Finnish and Swedish)
# [ ] _*+PORTAL*_ Publish news about the new tool on the Portal
# [ ] _*?CSC*_ Ask Martin (CSC) to add the data to Kielipankki directory {{/appl/data/kielipankki}} on Puhti if the source data is to be published there

\\
```

### _shortname_: Install the tool in the computing environment

```
# [ ] _*?DATA*_ Get the source (or original) tool from IDA, GitHub, or from the HFST server.
# [ ] _*+META*_ Create a META-SHARE record [instructions for creating metadata records | https://www.kielipankki.fi/development/creating-metadata-records/]
# [ ] _*+GITHUB*_ Request URNs (for META-SHARE and access location)
# [ ] _*+PORTAL*_ Create/update license pages [how to create/update license pages | https://www.kielipankki.fi/intra/creating-license-pages/]
# [ ] _*+META*_ Add citation information to the META-SHARE record
# [ ] _*?HYSTORE*_ In case intermediate versions need to be maintained at any point, upload the data as a zip file (named as shortname-korp_yyyymmdd.zip) and the separate shortname-korp_yyyymmdd_README.txt file to the HFST server, under data/tools/wip/ (= “work in progress”).
# [ ] _*+META*_ Install the tool in the computing environment
# [ ] _*+TEST*_ Test the tool in the computing environment
# [ ] _*+KORP*_ Publish the tool as a beta test version
# [ ] _*+META*_ Update META-SHARE record; add location PID and Availability start date (under Distribution)
# [ ] _*?META*_ Update the META-SHARE record: add relations to previous or parallel versions/variants of the corpus
# [ ] _*+PORTAL*_ Create or update the resource group page, and make sure the META-SHARE record also contains a link to the resource group page.
# [ ] _*+PORTAL*_ Link to the tool's group page from the list of resource families (http://urn.fi/urn:nbn:fi:lb-2021052505)
# [ ] _*+META*_ Add "beta" status information to META-SHARE record
# [ ] _*+PORTAL*_ Add "beta" status information to the resource group page
# [ ] _*?META*_ If required, create a portal page "shortname: Notes for the user", to inform about found issues in the data. Make sure the META-SHARE record also contains a link to the notes' page (in case the information is only one sentence, add it directly to the META-SHARE description).
# [ ] _*+META*_ Add the new tool to the list of tools in the portal (NOTE: there are separate lists for English, Finnish and Swedish)
# [ ] _*+PORTAL*_ Publish news about this new tool in the portal
# [ ] _*+PUHTI*_ Remove beta status after two weeks, if no requests for corrections or changes appear during this period
## [ ] _*+META*_ Remove beta status from the META-SHARE record and resource group page
\\
```

### _shortname_: Make the tool available via an online interface

```
# [ ] _*?DATA*_ Get the source (or original) tool from IDA, GitHub, or from the HFST server.
# [ ] _*+META*_ Create a META-SHARE record [instructions for creating metadata records | https://www.kielipankki.fi/development/creating-metadata-records/]
# [ ] _*+GITHUB*_ Request URNs (for META-SHARE and access location)
# [ ] _*+PORTAL*_ Create/update license pages [how to create/update license pages | https://www.kielipankki.fi/intra/creating-license-pages/]
# [ ] _*+META*_ Add citation information to the META-SHARE record
# [ ] _*?HYSTORE*_ In case intermediate versions need to be maintained at any point, upload the data as a zip file (named as shortname-vrt_yyyymmdd.zip) and the separate shortname-vrt_yyyymmdd_README.txt file to the HFST server, under data/tools/wip/ (= “work in progress”).
## [ ] _*+PUHTI*_ Create and add any additional material (documentation, user guide ect.)
# [ ] _*+PUHTI*_ Upload the tool and any additional material to the online interface, mark it as beta test version
# [ ] _*+TEST*_ Test the tool on the online interface
# [ ] _*+META*_ Update the META-SHARE record; add location PID and Availability start date (under Distribution)
# [ ] _*?META*_ Update the META-SHARE record: add relations to previous or parallel versions/variants of the tool
# [ ] _*+PORTAL*_ Create or update the resource group page, and make sure the META-SHARE record also contains a link to the resource group page.
# [ ] _*+PORTAL*_ Link to the tool's group page from the list of resource families (http://urn.fi/urn:nbn:fi:lb-2021052505)
# [ ] _*+META*_ Add "beta" status information to META-SHARE record
# [ ] _*+PORTAL*_ Add "beta" status information to the resource group page
# [ ] _*?META*_ If required, create a portal page "shortname: Notes for the user", to inform about found issues in the data. Make sure the META-SHARE record also contains a link to the notes' page (in case the information is only one sentence, add it directly to the META-SHARE description).
# [ ] _*+META*_ Add the new tool to the list of tools in the portal (NOTE: there are separate lists for English, Finnish and Swedish)
# [ ] _*+PORTAL*_ Publish news about the new tool on the Portal
# [ ] _*+PUHTI*_ Remove beta status after two weeks, if no requests for corrections or changes appear during this period
## [ ] _*+META*_ Remove beta status from the META-SHARE record and resource group page
\\
```

### _shortname_: Review the software (or resource), to continue lifecycle

```
# [ ] _*+META*_ Check for new versions of the tool
# [ ] _*+TEST*_ Test the functionality of the tool
# [ ] _*+TEST*_ Test if links to the tool and its documentation are still working
# [ ] _*+META*_ Update the META-SHARE record
\\
```
