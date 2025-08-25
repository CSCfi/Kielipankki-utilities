# The Kielipankki resource database

The database is available in the intranet of Kielipankki: https://www.kielipankki.fi/intra/resource-management/corpora/
(login with uni account, you need the VPN if working remotely).

It is also possible to access the database through https://www.kielipankki.fi/wp-admin/ (login with uni account, you need the VPN if working remotely). 
You can find the database at the bottom of the menu on the left side of the WordPress-window under **Resource Management**.

The database opens the **Corpora** collection by default. You can also switch to the collections of **Resource groups** or **Licenses** by following the links on the top of the page.

A new resource is added by clicking the button 'add new'. Existing entries can be viewed, edited or deleted. 
The menu is shown by mouse-over in front of each entry.

After adding a new entry or editing an existing one, go to the bottom of the form.
If you click “Submit”, your changes will be saved and you will stay on the current page. 
If you click “Submit Parent List”, your changes are saved and you are directed back to the overview of the corpora list https://www.kielipankki.fi/intra/resource-management/corpora/. 
If you select “Parent List”, your changes are NOT saved and you are directed back to the overview of the corpora list. 
The same applies to also the licenses and resource groups pages.

When entering a new resource, the most important information is the shortname. The corpus status is set to 'preliminary'. 

In order to add a corpus to the **list of upcoming resources**, set the status to 'upcoming' and safe the change.

In order to add a corpus to the **list of published resources**, set the status to 'production' and save the change.


The resource-specific **Resource group pages** are automatically filled with their corresponding entries from the database.


The corpus lists are offered in the Kielipankki portal in English:

[The list of published corpora](https://www.kielipankki.fi/corpora/)

[The list of upcoming corpora](https://www.kielipankki.fi/corpora/forthcoming/)


And in Finnish:

[Aineistot](https://www.kielipankki.fi/aineistot/)

[Tulossa olevat aineistot](https://www.kielipankki.fi/aineistot/tulevat/)


## Attribution instructions
Attribution details are created automatically to the portal (with information from the database fields 'Authors' and 'First publication date'), when a resource is added to one of these lists.

Use the attribution details in the format: https://www.kielipankki.fi/viittaus/?key=urn:nbn:fi:lb-2022102101&lang=en (using the URN as identifier!)

The resource-specific attribution instructions are displayed when clicking the icon in the column 'Cite'.


## Support level
Language resources in Kielipankki have one of three different levels of support assigned to them, visible in column 'Support level'.

    A: The resource is under active development. The Language Bank of Finland fixes any issues as soon as possible.
    B: The resource is developed only upon user request. The Language Bank of Finland aims to fix issues concerning the resource, but external contributions may be required.
    C: The resource is available ”as is”. The Language Bank of Finland does not fix nor develop the resource.

Whenever a new resource is entered to the database, a support level should be assigned. For most of the resources this will be support level **B**.


## Licenses
The database offers information on the license of each corpus.
Some corpora are directly available (PUB), some may be accessed by signing in (ACA) or by applying for individual access rights (RES).

After a license is added to the License collection, it is related to its resource via the corpus shortname. 
When you open a corpus entry with 'view' or 'edit', the corresponding license entry will be displayed underneath the corpus entry.
Also the other way round, if you open a license entry, the corresponding corpus entry is shown below.

Note: In the portal lists of corpora (see links above) license information will be visible to the user only after the license status is set to 'available'.



## Link to LBR
Protected corpora can be accessed following the link to LBR (Language Bank Rights) in the 'Apply' column of the portal list of published corpora.

In order to offer a link to LBR for a resource, add the PID of the LBR record to the field 'Lbr Urn' in the corpus database. 

On [https://lbr.csc.fi/](https://lbr.csc.fi/) you can find the correct URN, which is registered for the resource (under kielivarat, copy the link under 'more information')



## Download/Puhti links
All downloadable CLARIN PUB or ACA licensed corpora should be also available in CSC's Puhti computing environment in the directory /appl/data/kielipankki/.
In the corpus entry in the database you can choose the location 'Puhti' additionally to the location 'Download'.


## Resource groups
Corpora are connected with their corresponding resource group via the 'Resource Group ID', which is the 'Group Name' in the entry of a Resource group.
After adding a resource group to the collection of resource groups in the database, the name of the resource group is added to the selection list in the corporas' view.



## Add a tool to the list of tools
The list of tools is offered in English: [tools](https://www.kielipankki.fi/tools/), in Finnish: [työkalut](https://www.kielipankki.fi/tyokalut/) and in Swedish: [verktyg](https://www.kielipankki.fi/verktyg/).

The list of tools is (not yet) implemented in the database, but maintained manually. That means the tables for both languages, English and Finnish, have to be updated separately,
but ideally at about the same time. Go to [Kielipankki.fi/wp-admin](https://www.kielipankki.fi/wp-admin/) (login with uni account, you need the VPN if working remotely).
Go to Table Press, select 'all tables' and choose the table 'tools' for the English version and 'työkalut' for the Finnish version. Add your changes manually, preview and publish.


