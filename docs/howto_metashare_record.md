# Maintaining metadata in META-SHARE
## How to create a META-SHARE record

You need the rights to edit in META-SHARE (ask for access from CSC, if you do not have the rights yet). Login to META-SHARE. 
In order to create a new article, open the menu under "Manage Resources" and choose "Manage your own resources" or "Manage all resources".
In the upper left corner, choose "Add Resource +". 
Select a resource type (corpus, tool or lexical resource).
You must fill in all the required fields to be able to save the page. Please see here for the [minimum set of details](https://www.kielipankki.fi/development/creating-metadata-records/) that should be included in a metadata record that is published on META-SHARE. It is possible to edit the article and add information anytime, even when it is already published.
If unsure about some details, it is possible to fill in a kind of a placeholder (e.g. for 'size' you could put '1') and add the needed information later.
You will have to enter the correct name and short name for the resource. Please follow Kielipankki's [Language resource naming conventions](https://www.kielipankki.fi/development/language-resource-naming-conventions/).
Also you should check, whether there are (related) resources with this name in META-SHARE already.
The article needs a PID (Persistant Identifier of this resource). Instructions on how to request a PID can be found from [docs: How to request a PID](howto_request_pid.md).

After saving, the page will be visible only internally (that is, only the person who has created the page will be able to see it) before it is published.

In order to publish an internal resource, open the menu under "Manage Resources" and choose "Manage your own resources" or "Manage all resources".
Click the box of your internal resource to select it.
Select "Action: Ingest selected internal resources".
If you don't get any errors, click the box of the newly ingested resource, and select "Action: Publish selected ingested resources".
Your article is now openly visible and searchable in META-SHARE.

Agreements and licenses: if unsure, ask Mietta!
Note: An organization should never be cited as the author, since in the copyright sense only persons can be 'authors' 

When changing an existing META-SHARE article, add your name as a 'metadata creator', if it is not already there.
Add a short explanation of your change in the field 'revision', this will also change the date in the field 'last updated'.
For more complex explanations on a change add a **CHANGE LOG** with the current date under 'documentation'. For an example see [META-SHARE: lehdet90ff-v1](http://urn.fi/urn:nbn:fi:lb-2016011101)
  
Remember to add a link to the resource's group page via its URN under 'documentation', and name it **Resource group page**. If a resource group page is not created yet, you can add it later. See [docs: Instructions on how to create a resource group page](howto_resource_group_page.md).

The link to the attribution details (citing information) should be added with the name **How to cite**. The link is offered in the column 'Cite' of the list of corpora and can be copied from there. It is a good idea to use the URN instead of the shortname within the citation link, so that it always resolves, even if the name for some reason is changed or misspelled.

Example: The following two links show the same citing information

    https://www.kielipankki.fi/viittaus/?key=nlfcl-sv-korp&lang=en

    https://www.kielipankki.fi/viittaus/?key=urn:nbn:fi:lb-201804041&lang=en


The license's portal page should be referred to via its URN with the name **License**.


In case you find old kitwiki links, only remove them, when there is a corresponding page with the same information in the portal.

Remember to not create roof pages in META-SHARE any more, but 'resource group pages' in the portal. 

To save your additions while editing an article, press 'save and continue editing', so you do not have to search for the article again 
in order to continue editing or to preview the article.

## Create a META-SHARE record by copying an existing one
It is possible to create a META-SHARE record by using an existing page. This is helpful, if another version of the resource already has a record in META-SHARE and all or most of the details are the same. You need the script `clearObjects.sh`, which is stored in JIRA task KP-3693 at the moment.

    - Login to Metashare.
    - Under "Manage Resources" choose "Manage your own resources" or "Manage all resources".
    - Click the box of an existing resource to select it.
    - Select "Action: Export selected resource descriptions to XML" (let's name the file exported.xml).
    - Run the command ./clearObjects.sh exported.xml exported_objects_removed.xml (you can use a different name).
    - Under "Manage Resources" choose "Upload resource descriptions" and upload exported_objects_removed.xml. (You might get ProxyError, but the resource should still be uploaded.)
    - Edit the new resource and add missing objects: Contact person, Metadata creator, Relations etc.
    - Edit any other fields that need to be changed.


## Relations between resources
Relations between resources should be made explicit under the topic 'Relation' in the META-SHARE record. 
Related resources are for example the Korp version and the downloadable version of the same resource. 
Relations between resources are always bilateral and the pairs of relations are fixed (e.g. IsVariantFormOf / IsOriginalFormOf). 

In order to choose the correct type of a relation please see [Kielipankki: Life cycle and Metadata model](https://www.kielipankki.fi/support/life-cycle-and-metadata-model-of-language-resources/).
Make sure you use the correct spelling of the type and be aware of capital letters. 

When you add a related resource in META-SHARE, you can add the title of the corpus in front of the URN. 
The link will still be displayed in META-SHARE, and the relation is much more legible when you can see 
what the target resource is, without clicking on the link. Also, if you need to link to the same resource
later, META-SHARE will suggest it when you type a part of the corpus title.


