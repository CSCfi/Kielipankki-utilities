# Create a resource group page in the portal

Resource group pages are created for all resources (corpora, lexical resources, tools and web services). A resource group page contains all the relevant information about the resource and offers an overview of the latest versions, may it be source, VRT or Korp. 

Tools are mostly accessible via a web interface, or they can be installed via download from e.g. GitHub or Korp. Some tools were developed by member organizations of FIN-CLARIN / CLARIN ERIC. A resource group page offers detailed information about the tool, its usage, links to developers' webpages, user instuctions or download location. 

All resource group pages are linked to from [Kielipankki's resource families page](https://www.kielipankki.fi/corpora/resource-families-fin-clarin/). 

A group page in the portal should be tagged with categories (the particular Clarin resource family), to provide search possibilities in the portal. A resource can belong to more than one resource family. 

Each resource group page has to have a PID. For instructions on how to request a PID, see [docs: how to request a PID](howto_request_pid.md)

The resource group page is linked to from the respective META-SHARE record of the resource as well as from the [list of published corpora](https://www.kielipankki.fi/corpora/) in the portal (column 'Resource group and help') via its PID. (NOTE: Resources and tools not directly offered by Kielipankki, but by a member organization of FIN-CLARIN, might not have a META-SHARE record.)

In the [list of tools](https://www.kielipankki.fi/tools/) the link to the resource group page is added to the column 'Info'.

In order to create a resource group page in the portal, go to [Kielipankki.fi/wp-admin](https://www.kielipankki.fi/wp-admin/) (login with your university account, you need the VPN when working remotely).
It is possible to edit existing pages.
Open the editor for the English and the Finnish template pages on separate browser tabs and create a copy of each page as the starting points for the new resource group pages – click on 'Kopioi uudeksi luonnokseksi':
[kielipankki.fi/corpora/aineistosivumalli/](https://www.kielipankki.fi/corpora/aineistosivumalli/) | 
[kielipankki.fi/aineistot/aineistosivumalli](https://www.kielipankki.fi/aineistot/aineistosivumalli/)
(Or, to start by creating a new blank page, press 'uusi sivu'.)
The first, bold text (document) will be the name of the page (link).
The following bold text will be the headline of the page.

The content of a resource group page is usually:

- The name of the resource (headline)
- A table of all available versions/subcorpora of the resource. The table will be filled automatically with the content from the **corpus database**, based on the resource group shortname. Each version/subcorpus is put to its own row in the table. Links to the particular metadata record, citation information and access location are given.
- A description of the resource containing all relevant details, sometimes also links to related sources outside of Kielipankki. Check the metadata record and take all relevant information from there.
- A PID

In the WordPress page editor, in the window on the right, you should choose one or more of the given categories (resource families). 
If a category is missing, you can add it here (please note, that in this case the missing family has to be added to the corpus database as well, with the help of CSC).

A page created in Kielipankki can be put to 'privat' first. Then it is only visible to the author.

You can check the appearance of your page by pressing the 'preview' button.

Remember to choose the correct language of the page below. Then the other language options on the page are shown correctly.
Generally for each resource a resource group page should be offered in both languages, one in English and one in Finnish. 
For some of the older resources only an English or Finnish version might be available. The other language version has to be created at some point.

After everything is done, the page should be put to 'public' and be published.

The page can be moved in the 'tree view' in the menu on the left (e.g. to the folder 'corpora'). This can also be done after publishing the page.

The PID of the (English) resource group page should then be added to the resource's metadata record in COMEDI and to the corpus database or the list of tools respectively.

After a new resource group is added to the **corpus database**, the particular resource group can be chosen from the dropdown list of the field 'Resource group' within a corpus entry. 
The particular Clarin resource family/families are to be chosen from the selection lists of the fields 'Clarin Resource Family' in English and Finnish.

The [resource families page](https://www.kielipankki.fi/corpora/resource-families-fin-clarin/ "resource families page") will be filled automatically with information from the corpus database.

