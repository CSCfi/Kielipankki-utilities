# Maintaining metadata in COMEDI
## How to create a metadata record

Every resource to be published in the Language Bank of Finland needs a PID (Persistant Identifier of this resource). Before creating a metadata record, this PID should be requested. Instructions on how to request a PID can be found from [docs: How to request a PID](howto_request_pid.md).

You need the rights to edit in COMEDI (ask for access in the group FIN-CLARIN from CSC, if you do not have the rights yet). Login to [COMEDI](https://clarino.uib.no/comedi/records). 
Open the menu under "CMDI Records" and choose "Create a metadata record".

In order to create a new article, you first have to choose a CMDI profile. For the time being (a new profile is being created) for a corpus, choose: 

    profile: clarin.eu:cr1:p_1361876010571 - resourceInfo / 1.1

For a tool, choose the following profile:

    profile: clarin.eu:cr1:p_1360931019836  - resourceInfo / 1.1

For a lexical conceptual resource, choose the following profile:

    profile: clarin.eu:cr1:p_1355150532312  - resourceInfo / 1.1

Add the identifier for this record, which results from the PID, in the form `lb-yyyymmddxx` (lb stands for language bank), e.g. lb-2025013021.

Press 'Go'. A new metadata record will be created. You will get a notification, that it is not valid yet!

Add a self link, which also results from the resource PID, in the form `urn:nbn:fi:lb-yyyymmddxx`, e.g. urn:nbn:fi:lb-2025013021.

Connect this record to user group: FIN-CLARIN.

The entered content will be saved automatically, even if the record is not yet valid. To make the record valid, you must fill in all the required fields. Please see here for the [minimum set of details](https://www.kielipankki.fi/development/creating-metadata-records/) that should be included in a metadata record that is published in COMEDI. It is possible to edit the article and add or correct information anytime.

If unsure about some details, it is possible to fill in a kind of a placeholder (e.g. for 'size' you could put '1') and add the needed information later.

The **status** of your freshly created metadata record is set automatically to 'in-progress'. You should change the status to 'published' as soon as the main information is added and the record is valid. The resource itself does not have to be published yet, but should at least be in the negotiation phase, have a title and a PID for the metadata.


## Resources
This tab offers the **Resource proxy list**. After a resource is published, the access location should be added under the tab 'Resources' to the Resource proxy list. 
As *Resource type* choose *Resource* for a downloadable corpus and *Search Page* for a resource published in Korp. The resource ID can be set to '_1'. For possible further, alternative access locations for the same resource, use '_2', '_3' etc.
Only after this information is given, VLO will harvest the metadata of this resource and make it available in the VLO service! 

Example:

      Resource proxy list [1]
      Resource [id: _1]: http://urn.fi/urn:nbn:fi:lb-2022090201 
  

## Identification Info

You will have to enter the correct name and short name for the resource. Please follow Kielipankki's [Language resource naming conventions](https://www.kielipankki.fi/development/language-resource-naming-conventions/).
Also you should check, whether there are (related) resources with this name in the Language Bank already (e.g. from the database).
Add the resource name in English and Finnish (and Swedish if needed; add another field to the resource name for this) and add the language information as en, fi, or sv.

Add a resource description. Information for this can be found e.g. from the Jira ticket in question, or from the form (Information about a language resource to Kielipankki).

Start the description with the line:

    In English: This resource will be available [via Korp | for download] in Kielipankki – the Language Bank of Finland. 
    
    In Finnish: Tämä aineisto on tulossa saataville Kielipankin kautta.

Add the resource short name.

For metashare id, you can put: n/a

The identifier results from the resource PID, in the form `http://urn.fi/urn:nbn:fi:lb-yyyymmddxx`, e.g. http://urn.fi/urn:nbn:fi:lb-2025013021.

## Distribution Info

Agreements and licenses: if unsure, ask Mietta!
Note: An organization should never be cited as the author, since in the copyright sense only persons can be 'authors' 


## Contact person
The contact person for the resource data. It is possible to add an already existing person, but check the details for correct contact information and affiliation!


## Metadata info
The person who created the metadata record. It is possible to add an already existing person, but check the details for correct contact information and affiliation!

When changing an existing metadata article, add your name as a 'metadata creator', if it is not already there.
Add a short explanation of your change in the field 'revision'. The 'metadata last date updated' field will automatically be updated by the software.

For more complex explanations on a change add a **CHANGE LOG** with the current date under 'documentation' (see below).

## Resource documentation info
The documentation section in COMEDI offers unstructured and structured fields. This is usually the place to add citation instructions, possibly a CHANGE-LOG, and references to the resource group page and the license page.

The link to the attribution details (citing information) should be added as unstructured documentation item. Add the text **How to cite** before the link to the citation instructions. The link is offered in the column 'Cite' of the [list of corpora](https://www.kielipankki.fi/corpora/) and can be copied from there. You can also create the citation link yourself according to the following model, just exchange the URN of the resource.

Example: The following link shows the citation information for The Swedish sub-corpus of the Classics Library of the National Library of Finland - Kielipankki version

        https://www.kielipankki.fi/viittaus/?key=urn:nbn:fi:lb-201804041&lang=en

For explanations on a change (e.g. in the metadata or license) add a **CHANGE LOG** with the current date, formatted like 2017-07-17 (in the order of year, month and day; ISO standard) in an unstructured field under 'documentation'. For an example see the metadata of [STT](http://urn.fi/urn:nbn:fi:lb-2020031201). For further instructions on how to create a CHANGE LOG, see [how to create a CHANGE LOG](howto_change-log.md).

For info about the resource group page, add a structured documentation item. Add the title: **Resource group page (resource short name)** and Editor: FIN-CLARIN. As URL add the PID for the English version of the resource's group page. If a resource group page is not created yet, you can add it later. See [docs: Instructions on how to create a resource group page](howto_resource_group_page.md).

For info about the license, add another structured documentation item. Add the title: **License/Lisenssi (resource short name, license)**, e.g. License/Lisenssi (fvcc, CC-BY) and Editor: FIN-CLARIN. As URL add the PID for the English version of the resource's license page.

NOTE: Remember to add (+) a resource documentation info when the number is 0/0


## Resource creation info
Add the authors of the resource in the required order. Add contact information and affiliation. It is possible to add an already existing person, but check the details for correct contact information and affiliation!


## Relation info
Relations between resources should be made explicit under the topic 'Relation' in the metadata record. 
Related resources are for example the Korp version and the downloadable version of the same resource. 
Relations between resources are always bilateral and the pairs of relations are fixed (e.g. IsVariantFormOf / IsOriginalFormOf). 

In order to choose the correct type of a relation please see [Kielipankki: Life cycle and Metadata model](https://www.kielipankki.fi/support/life-cycle-and-metadata-model-of-language-resources/).
Make sure you use the correct spelling of the type and be aware of capital letters. 

Add the title of the corpus in front of the URN. 

## Corpus info / Tool service info / Lexical conceptual resource info
This is the place to add information about e.g. media type and size of the resource.

In order to specify the languages of the text(s) included in the resource, the following links might help to find the correct **language codes**:

https://kotoistus.fi/suositukset/suositukset-kielet-fi-koodi/

https://iso639-3.sil.org/code_tables/639/data/all

### Corpus info: Annotation info
The field 'Annotation info' offers the possibility to add detailed information about the annotation methods and tools used to create this specific language resource.

Add information about the used parser, named entities, polarity, etc. (add links when the exact version of the tool is known and a metadata record exists).

A checklist in order to remember which fields to fill in, what to select in each case, and what to write in the free text fields, is supposed to be added and updated here

TO BE EDITED:
- parser
- named entities
- polarity
- language indentification

Here is an example of given annotation information regarding the language identification using HeLI-OTS 2.0., see [suomi24-2021-2023-korp](https://urn.fi/urn:nbn:fi:lb-2024030601)

    Annotation info [1/0-∞]
    Annotation type: other
    Annotated elements: other
    Segmentation level: sentence
    Annotation tool [1/0-∞]
    Target resource name URI: HeLI-OTS 2.0 language identifier, http://urn.fi/urn:nbn:fi:lb-2024040301 



## Create a COMEDI record by cloning an existing one
It is possible to create a COMEDI record by cloning an existing one. This is helpful, if another version of the resource already has a record in COMEDI and all or most of the details are the same. 
- For this, login to COMEDI. 
- Open the menu under "CMDI Records" and choose "Clone a metadata record". 
- Choose the record you want to clone from the list of identifiers. 
- Add the identifier of the new metadata record to be created.
- Remove the self link from the original metadata record and add the new self link (based on the identifier of the new metadata record)
- Edit the new created metadata record: Change at least the resource name(s), description, identifier


