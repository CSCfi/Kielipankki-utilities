# Maintain the resource lists in the portal
**NOTE: This page is outdated. Please see the description on [docs: how to maintain resource lists with the corpus database](howto_maintain_resource_lists_database.md)**


The resources offered by Kielipankki are listed in the portal, separated after language corpora and tools.

Lists in English:

[The list of published corpora](https://www.kielipankki.fi/corpora/)

[The list of upcoming corpora](https://www.kielipankki.fi/corpora/forthcoming/)

[The list of tools](https://www.kielipankki.fi/tools/)

Lists in Finnish:

[Aineistot](https://www.kielipankki.fi/aineistot/)

[Tulossa olevat aineistot](https://www.kielipankki.fi/aineistot/tulevat/)

[Työkalut](https://www.kielipankki.fi/aineistot/tyokalut/)


The content of the **corpus lists** (upcoming and published corpora, for both languages) is maintained with the help of an excel sheet, '**KP-Aineistot**', which is under version control in GitHub:
[https://github.com/CSCfi/Kielipankki/tree/master/FIN-CLARIN-Administration](https://github.com/CSCfi/Kielipankki/tree/master/FIN-CLARIN-Administration).

(For instructions on how to maintain the list of tools, please see below)

The excel sheet 'KP-Aineistot' is a complete archive of all corpora available in Kielipankki.
Instructions on how to make changes to the list can also be found on the last tab of the excel sheet.

The excel sheet offers the list of upcoming resources and the list of published resources on different tabs.

You can edit the tabs `src_prod` and `src_new`. The other two tabs `obj_prod` and `obj_new` are created from the former ones automatically.

Remember to always save and push your changes to GitHub.


## Add a corpus to the list of upcoming corpora
Go to GitHub, download the excel sheet 'KP-Aineistot' from there to your computer (remember to delete it from your computer when all is done and download a fresh one every time you want to change something!)
Open the excel and choose the tab `src_new`.
Always add lines to the end.
When adding copied data (e.g. from META-SHARE), first click into the appropriate field in your new line, then add the copied data to the input field above, not to the cell directly (because this would take the text format like bold or html link as well, which is not wanted here).

NOTE: Attribution details are created automatically to the portal (from the columns tekijä etc.), when a resource is added to this list.

When your changes are done, safe the file.
Go to GitHub, refresh the web page to check whether someone else was changing something at the same time.
Upload the changed excel file (upload files; drag and drop).
Commit your changes and add a note about what you have changed.

To publish the data in the portal, go to [Kielipankki.fi/wp-admin](https://www.kielipankki.fi/wp-admin/) (login with uni account, you need the VPN when working remotely).
Go to Table Press, choose 'all tables'.
Choose the table 'new corpora', click on 'import' (above), click 'manual import'.
Go to the excel sheet, mark and copy all (!) rows from the tab `obj_new` and add them to WordPress into the big empty box.
Click 'replace existing table' and select the table 'new corpora'.
Press 'Upload'. Now the changed table is already published, but not yet in alphabetical order!
Go to the top of the table, click 'A - row up' (small triangle). Wait until the order of the lines has changed and save the change.
Upload again and check the content on the [portal page for the upcoming corpora](https://www.kielipankki.fi/corpora/forthcoming/).

## Add a corpus to the list of published resources
Go to GitHub, download the excel sheet 'KP-Aineistot' from there to your computer (remember to delete it from your computer when all is done and download a fresh one every time you want to change something!)
Open the excel and choose the tab `src_prod`.

If you want to move a resource from the list of upcoming resources to the list of published resources, 
copy the wanted line from `src_new` and paste it to `src_prod` (to the end of the list).
Check the pasted line: change cell formats if needed (e.g. remove the colour bubbles), add location URNs, service level, publication date, link to the group page (dokumentaatio).
Delete the respective row from `src_new`.
Go to `obj_new` and remove the 'odd' lines, which are the result of the deletion in `src_new`.
It might be necessary to go to `obj_prod` and copy an existing line to the new one at the bottom to paste the formular there.
Safe the file.
Go to GitHub, refresh the web page to check whether someone else was changing something at the same time.
Upload the changed excel file (upload files; drag and drop).
Commit your changes and add a note about what you have changed.

To publish the data in the portal, go to [Kielipankki.fi/wp-admin](https://www.kielipankki.fi/wp-admin/) (login with uni account, you need the VPN if working remotely).
Go to Table Press, choose 'all tables'. Be aware that you have to update now both tables, 'new corpora' and 'all corpora'.

Choose the table 'new corpora', click on 'import' (above), click 'manual import'.
Go to the excel sheet, mark and copy all (!) rows from the tab `obj_new` and add them to WordPress into the big empty box.
Click 'replace existing table' and select the table 'new corpora'.
Press 'Upload'. Now the changed table is already published, but not yet in alphabetical order!
Go to the top of the table, click 'A - row up' (small triangle). Wait until the order of the lines has changed and save the change.
Upload again and check the content on the [portal page for the upcoming corpora](https://www.kielipankki.fi/corpora/forthcoming/).

To change the table 'all corpora', go to 'import new table' on the left.
In the excel sheet, mark and copy all (!) rows of `obj_prod` and paste to the manual import box.
Click 'replace existing table' and select the table 'all corpora' this time.
Press 'Upload'. Now the changed table is already published, but not yet in alphabetical order!
Go to the top of the table, click 'A - row up' (small triangle). Wait until the order of the lines has changed and save the change.
Upload again and check the content on the [portal page of published corpora](https://www.kielipankki.fi/corpora/). 


## Link to LBR
The corpus list offers information on the license of each corpus.
Some corpora are directly available (PUB), some may be accessed by signing in (ACA) or by applying for individual access rights (RES). 
Protected corpora can be accessed following the link to LBR (Language Bank Rights) in the 'Apply' column.

In order to create links to LBR for resource groups, see the tab `defs` of the KP-Aineistot for details. 

 - Add the URN to the resource group page to the list under the instructions there, change the field name to `URN_NAME` where 'NAME'=shortname of the corpus (e.g. `URN_STT`).
 - On tab `src_prd` add `=LBR&URN_STT&LBR_END` to column G (here `URN_STT` as example)
 - on [https://lbr.csc.fi/](https://lbr.csc.fi/) you can find the correct URN, which is registered for the resource (under kielivarat, copy the link under 'more information')


## Preview
It is possible to test your changes before publishing the edited lists to the portal.

Change the excel sheet 'KP-Aineistot' according to your needs. Then copy your changes to the test tables 22 and 23 (instead of the tables 'new corpora' and 'all corpora) and check their appearance on the [preview page](https://www.kielipankki.fi/intra/preview/) in Kielipankki.


## Download/Puhti links
All downloadable CLARIN PUB or ACA licensed corpora should be also available in CSC's Puhti computing environment in the directory /appl/data/kielipankki/.
Since 25.10.2021 there is a separate column in KP-Aineistot which lists datasets published in Puhti.
The KP-Aineistot is now updated to create Download/Puhti links. To add/remove corpora, they need to be added/removed here:

    https://github.com/CSCfi/Kielipankki/blob/master/hpc_directory/group_vars/all

And then someone with install permissions at CSC needs to run the Ansible script which downloads the data from Korp and extracts it. 
Removal is manual at this point, but can also only be done within CSC.


## Add a tool to the list of tools
The list of tools is offered in English: [tools](https://www.kielipankki.fi/tools/) and in Finnish: [työkalut](https://www.kielipankki.fi/tyokalut/)

The list of tools is maintained manually. That means the tables for both languages, English and Finnish, have to be updated separately,
but ideally at about the same time. Go to [Kielipankki.fi/wp-admin](https://www.kielipankki.fi/wp-admin/) (login with uni account, you need the VPN if working remotely).
Go to Table Press, select 'all tables' and choose the table 'tools' for the English version and 'työkalut' for the Finnish version. Add your changes manually, preview and publish.

